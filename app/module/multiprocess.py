#-*- coding: utf-8 -*-
# 메인 소스
# lib 사용
from bs4 import BeautifulSoup
from urllib.request import urlopen
from multiprocessing import Pool, current_process
import time
import pymysql
import urllib
import os
# 만든 module import
import outputfile
import Errorlog
import conf
import imagehash

# config 설정 추출 모듈 사용
timeconfig = conf.timeget()
autodelete = conf.autodelete()
hash_image = conf.hashimage()
dbconfig = conf.dbget()             
conn = pymysql.connect(host=dbconfig['host'], port=dbconfig['port'], user=dbconfig['user'], passwd=dbconfig['passwd'], db=dbconfig['db'], charset=dbconfig['charset'])
cur = conn.cursor()
time_ = time.time()

# 공유마당 페이지 끝번호 추출
def endpage(url):
    html = urlopen(url, timeout=5)
    source = html.read()
    html.close
    soup = BeautifulSoup(source, 'html5lib')
    select = soup.find(class_='i end')
    endpage_ = select.a.get('href')
    endpage_ = endpage_[-5:]
    return int(endpage_)

# 파일안 이미지 갯수 확인
def file_len():
    for files in os.walk('../../Output/img'):
        return int(len(files[2]))              

# 파일안 이미지명 추출
def file_delete(dirname):
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        os.remove(full_filename)

# 모든 데이터 삭제 함수
def alldelete():
    file_delete('../../Output/img')
    file_delete('../../Output/ccl')
    file_delete('../../Output/thumbnail')

    print('image information delete . . .')
    cur.execute('DELETE FROM crawler;')

    print('image hash delete . . .')
    cur.execute('DELETE FROM encoded_image;')

    print('image hashzip delete . . .')
    cur.execute('DELETE FROM encoded_image_longblob;')

    print('image hash license delete . . .')
    cur.execute('DELETE FROM encoded_license;')

    print('image hash thumbnail delete . . .')
    cur.execute('DELETE FROM encoded_thumbnail;')
    
    conn.commit()
    Errorlog.deletelog()
    print('모든 데이터 삭제 완료')

# 세부정보 제목 확인
def cktitle(title):
    if title == "UCI":
        return "uci"
    elif title == u"ICN":
        return "icn"
    elif title == "저작자":
        return "author"
    elif title == u"공표일자(년도)":
        return "publicate_date"
    elif title == "창작일자(년도)":
        return "create_date"
    elif title == "공표국가":
        return "publicate_contry"
    elif title == "분류(장르)":
        return "classification"
    elif title == "원문제공":
        return "original_text"
    elif title == "요약정보":
        return "summary_info"
    elif title == "추가사항":
        return "details"
    elif title == "관련태그":
        return "relation_tag"
    elif title == "발행자":
        return "publisher"
    elif title == "발행일자":
        return "publish_date"
    elif title == "기여자":
        return "contributor"
    elif title == "저작물명 대체제목":
        return "alternate_title"
    elif title == "저작물 파일유형":
        return "substitute"
    elif title == "저작물 속성":
        return "attribute"
    elif title == "수집연계유형":
        return "collect_type"
    elif title == "수집연계대상명":
        return "collect_target"
    elif title == "수집연계URL":
        return "collect_url"
    elif title == "주언어":
        return "main_language"
    elif title == "원저작물유형":
        return "original_type"
    elif title == "원저작물창작일":
        return "original_date"
    elif title == "원저작물크기":
        return "original_size"
    elif title == "원저작물소장처":
        return "original_collection"
    elif title == "공동저작자":
        return "public_author"
    else:
        return "err"

# 세부정보 크롤링
def information(url, path, id_):
    try:
        html = urlopen(url, timeout=5)
        source = html.read()                            # 소스를 읽는다
        html.close()                                    # 모두 진행한 후 close 해준다

        soup = BeautifulSoup(source, "html5lib")
        selecttitles = soup.find(class_='tit_txt3 mt0')
        selecttable = soup.find(class_='tb_bbs tbType')
        selectlins = soup.find(class_='copyD')
        selectimg = soup.find(class_='imgD')
        name = selecttitles.get_text().strip()
        name = name.replace("'", "\\'")  # ' 이 SQL 문자구분에 문제가 생길수도 있으니 \ 삽입
        table = selecttable.find_all('tr')
        lins = selectlins.find('img').get('src')
        lins_name = selectlins.get_text().strip()
        lins = "https://gongu.copyright.or.kr" + lins
        lins = outputfile.cklicense(lins, lins_name, cur, conn)                                        # 라이센스 이미지 중복체크 및 저장 경로설정
        image = selectimg.find('img').get('src')
        image = "https://gongu.copyright.or.kr" + image

        into_ = "(_id,filename,path,license,license_name,"                        # DB에 저장할 컬럼
        value = "('" + id_ + "','" + name + "','" + path + "','" + lins + "','" + lins_name + "',"      # DB에 저장할 값
        count = 0                               # 값들의 갯수 체크 (_id , filename , path , license는 이미 있으므로 4부터 시작)
        for tab in table:
            th = tab.find('th')             # 테이블 중에서 th만 추출
            td = tab.find('td')             # 테이블 중에서 td만 추출
            [s.extract() for s in td('script')]         # script 태그는 제외
            thtext = th.get_text().strip()                  # th내에 text는 추출하고 공백 제거
            into_ += cktitle(thtext) + ","                  # 값을 넣을 컬럼위치 체크
            tdtext = td.get_text(" ", strip='True')         # td안에서 텍스트 추출 공백이 있을시 띄어쓰기 하나로 변환
            tdtext = tdtext.replace("'", "\\'")             # ' 이 SQL 문자구분에 문제가 생길수도 있으니 \ 삽입
            value += "'"+tdtext+"',"                        # DB 인서트를 위해 value값 저장
            count += 1                                       # 컬럼갯수 확인
        into_ += "col_size)"                                # 컬럼갯수를 넣을 컬럼 확보 후 괄호 닫기
        value += str(count) + ")"                       # 마지막으로 갯수삽입 후 괄호 닫기
        query = "INSERT INTO crawler"+into_+" values"+value+""      # 쿼리문 작성
        return {'query': query, 'image': image, 'fileid' : id_,'file_name' : name}                                     # 쿼리 전송
    except AttributeError:                                                      #에러일시 에러전송
        return {'query': "error", 'image': "error", 'fileid' :"error",'file_name' : "error"}
    except Exception as ex:
        print('세부정보 에러 : ', ex)
        return {'query': "error", 'image': "error", 'fileid' : "error",'file_name' : "error"}

# 에러 로그가 숫자 인지 문자인지 확인 
def ck_Number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# 후처리 함수
def readerror():
    index = 0
    with open('../../log/error_log.txt', 'r') as file:
        for i in file:
            # 숫자일시 페이지 전체 크롤링
            if ck_Number(i):
                print('전체 페이지 크롤링은 %0.2f초정도 쉽니다..(url.timeout 에러 방지) page : %d' % (timeconfig['error_page'], int(i)))
                time.sleep(timeconfig['error_page'])
                in_ = Crawling(int(i))
                index += in_[1]             # return 받은 크롤링 완료한 이미지 갯수 --- in_[0] = 에러로인해 못받은 이미지 갯수
            else:
                filename = outputfile.selectid(i)  # selectid 함수로 가서 고유id 추출
                info_ = information(i, filename['path'], filename['id_'])  # 상세정보 추출
                createimg = outputfile.saveinfo(info_['image'], filename['path'], info_['query'], i,cur,conn,info_['fileid'], info_['file_name'])  # 폴더 내 중복 이미지 체크 후 DB insert
                if createimg:
                    print('오류 재발생 확인 바랍니다. href :', i)
                else:
                    print('이미지 다운로드 완료')
                    index += 1
    print('새로받은 이미지 : %d 개' % index)
    Errorlog.deletelog()

# 페이지 크롤링
def Crawling(i):
    error_ = 0
    count = 0
    realcount = 0
    try:
        url_ = "https://gongu.copyright.or.kr/gongu/wrt/wrtCl/listWrt.do?menuNo=200023&viewType=&wrtTy=4&sortSe=&use" \
              "Purps=&usageRange=&depth2At=Y&copyType_2d=&searchWrd=&pageIndex=%d" % i
        html = urlopen(url_, timeout=5)
        source = html.read()
        html.close()

        soup = BeautifulSoup(source, "html5lib")
        select = soup.find(class_="bbsPhoto")   # div class 확인

        li = select.find_all('li')              # li태그만 추출

        for val in li:
            realcount += 1                          # 전체 카운트 인덱싱
            href = val.a.get('href')                # li 태그의 href 추출
            realhref = "https://gongu.copyright.or.kr" + href
            filename = outputfile.selectid(realhref)           # selectid 함수로 가서 고유id 추출
            info_ = information(realhref, filename['path'], filename['id_'])  # 상세정보 추출
            createimg = outputfile.saveinfo(info_['image'], filename['path'], info_['query'], realhref,cur,conn, info_['fileid'], info_['file_name'])      # 폴더 내 중복 이미지 체크 후 DB insert
            if not createimg:                                                             # DB삽입 성공시 성공한 갯수 count
                count += 1                                                 # 완료 갯수 ++
            else:
                error_ += 1                                                # error 발생
                Errorlog.errorurl(realhref)
        print("----------------------------------------------------")
        print("           %d 페이지 완료                          " % i)
        print("          process : {0}                           ".format(current_process().name))
        print("        새로운 이미지 : (%d/%d)             " % (count, realcount))
        print("----------------------------------------------------")
    except Exception as ex:
        print('page error : ', ex)
        Errorlog.errorurl(i)
        error_ += 9                                 # 페이지 에러발생
    finally:
        time.sleep(timeconfig['image'])
        return [int(error_), int(count)]            # 에러갯수 및 완료한 갯수 return


def main(url_):
    pro = True
    start = 1
    end = 500
    plus = 500
    # real_end = int(endpage(url_))
    real_end = 1500
    while pro:
        values_ = 0
        error_value = 0
        process_time = time.time()
        p = Pool(6)
        p.daemon = True
        try:
           process = p.imap(Crawling, range(start, end+1))
        except Exception as ex:
            print('pool error : ', ex)
        for er, co in process:
            error_value += int(er)
            values_ += int(co)
        p.terminate()

        try:
            p.join()
        except KeyboardInterrupt:
            print('end')
        finally:
            print("================================ end ==================================")
            print("(%s ~ %s) 페이지 크롤링 완료" % (str(start), str(end)))
            print("걸린 시간 : %0.2f 초" % (time.time() - process_time))
            print("다운받은 이미지 : %d" % (int(values_)))
            print("오류로 인해 받지 못한 이미지 : %d" % int(error_value))
            print('폴더 내에 있는 파일 갯수 : %d' % file_len())
            print("%0.2f초 쉬었다 오류가 발생한 파일 다시 크롤링. . . " % timeconfig['error_page'])
            time.sleep(timeconfig['error_page'])
            readerror()
        if end == real_end:
            pro = False
        else:
            print("---------------%0.2f초 쉬었다 다시 시작--------------- " % timeconfig['finish_page'])
            time.sleep(timeconfig['finish_page'])
            start = end+1
            end += plus
            
            if end > real_end:
                end = real_end


if __name__ == '__main__':
    if autodelete:
        # 모든데이터 삭제
        alldelete()
    elif hash_image:
        # 해시화되어 있는 이미지 이미지로 변환
        imagehash.imagesave(cur)
    else:
        # 크롤러 작동
        url = "https://gongu.copyright.or.kr/gongu/wrt/wrtCl/listWrt.do?wrtTy=4&menuNo=200023&depth2At=Y"
        main(url)
        print("==============================모든 페이지 크롤링 완료=================================  ")
        print("%0.2f 초" % (time.time() - time_))
        print('폴더 내에 있는 파일 갯수 : %d' % file_len())
        