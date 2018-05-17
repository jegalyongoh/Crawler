#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
from PIL import Image
from multiprocessing import Pool, current_process
import time
import pymysql
import urllib
import os
import re
import zipfile

conn = pymysql.connect(host='127.0.0.1', port=3307, user='root', passwd='a1234', db='bucketlist', charset='utf8')
cur = conn.cursor()
time_ = time.time()


def endpage(url):
    html = urlopen(url, timeout=5)
    source = html.read()
    html.close
    soup = BeautifulSoup(source, 'html5lib')
    select = soup.find(class_='i end')
    endpage_ = select.a.get('href')
    endpage_ = endpage_[-5:]
    return int(endpage_)


def file_len():
    for root, dirs, files in os.walk('./img'):
        return int(len(files))              # 파일안 갯수 확인


def zipfile_(result, file_path):                # 현재 사용하지 않음
    if result:
        zip = zipfile.ZipFile('D:\PyCharm Community Edition 2017.2\html\example/image_file.zip', 'a')

        for folder, subfolders, files in os.walk('D:\PyCharm Community Edition 2017.2\html\example\img'):
            for file in files:
                zip.write(os.path.join(folder, file),  # 파일 이름
                        os.path.relpath(os.path.join(folder, file), 'D:\PyCharm Community Edition 2017.2\html\example\img'),
                        # 압축 파일의 이름(Default : 파일 이름과 같음)
                        compress_type=zipfile.ZIP_DEFLATED)  # 압축 타입
        for file_s in file_path:
            os.remove('./img/' + file_s)


def file_search(dirname):
    filenames = os.listdir(dirname)
    for filename in filenames:
        full_filename = os.path.join(dirname, filename)
        os.remove(full_filename)


def alldelete():
    file_search('./img')
    file_search('./ccl')
    file_search('./thumbnail')
    cur.execute('DELETE FROM crawler;')
    conn.commit()
    deleteerror_log()
    print('완료')


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


def resultlins(licensepath, path):
    result = os.path.exists(path)                   # 폴더안에 이미지 중복 체크 exists 함수
    if not result:
        urllib.request.urlretrieve(licensepath, path)               # 이미지 저장
        print("새로운 라이센스 발견 CREATE : %s" % path)


def cklicense(license):
    file = os.path.split(license)           # 이미지 명만 추출하기위해 배열로 나눔 split 함수
    filepath = "./ccl/" + str(file[1])     # 이미지명만 추출해서 라이선스 이미지를 저장할 경로 삽입
    resultlins(license, filepath)           # 라이선스 이미지 중복 체크
    return filepath


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
        lins = cklicense(lins)                                        # 라이센스 이미지 중복체크 및 저장 경로설정
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
        return {'query': query, 'image': image}                                     # 쿼리 전송
    except AttributeError:                                                      #에러일시 에러전송
        return {'query': "error", 'image': "error"}
    except Exception as ex:
        print('세부정보 에러 : ', ex)
        return {'query': "error", 'image': "error"}


def thumbnail(path):
    try:
        size = 136, 100                 # 136 , 100 으로 이미지크기설정
        image = Image.open(path)            # 이미지오픈
        image.thumbnail(size)               # 썸메일
        file = os.path.split(path)          # file[0] = ./img/  file[1] = 123456.png
        thumbnail_path = "./thumbnail/" + file[1]       # 이미지명만 추출
        image.save(thumbnail_path)                      # 썸네일 이미지 저장
    except Exception as ex:
        print("error : 썸네일 오류 .. 확인해주세요", ex)
        print(path)


def selectid(url):
    Search = str(re.search(r"wrtSn=\d{4,10}", url).group())                     # 이미지 고유번호 추출
    title = re.sub("[^0-9]", "", Search)                                        # 번호만 추출
    filename = "./img/" + str(title) + ".PNG"                                   # img저장 경로 설정
    return {'path': filename, 'id_': title}


def errorurl(url_):
    with open('./error_log.txt', 'a') as file:
        file.write(str(url_) + '\n')


def ck_Number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def readerror():
    index = 0
    with open('./error_log.txt', 'r') as file:
        for i in file:
            if ck_Number(i):
                print('전체 페이지 크롤링은 5초정도 쉽니다..(url.timeout 에러 방지) page : ', i)
                time.sleep(5)
                in_ = Crawling(int(i))
                index += in_[1]             # return 받은 크롤링 완료한 이미지 갯수 0 : 에러로인해 못받은 이미지 갯수
            else:
                filename = selectid(i)  # selectid 함수로 가서 고유id 추출
                info_ = information(i, filename['path'], filename['id_'])  # 상세정보 추출
                createimg = ckimg(info_['image'], filename['path'], info_['query'], i)  # 폴더 내 중복 이미지 체크 후 DB insert
                if createimg:
                    print('오류 재발생 확인 바랍니다. href :', i)
                else:
                    print('이미지 다운로드 완료')
                    index += 1

    print('새로받은 이미지 : %d 개' % index)
    deleteerror_log()


def deleteerror_log():
    with open('./error_log.txt', 'w+t') as file:
        for i in file:
            print('delete log', i)


def ckimg(imgpath, filename, query, url):
    result = os.path.exists(filename)                               # 중복된 이미지가 있는지 없는지 확인
    if not result:
        try:
            cur.execute(query)              #DB 삽입
            conn.commit()                   #DB commit
            urllib.request.urlretrieve(imgpath, filename)  # 이미지 폴더에 저장 (저장할 이미지 추출, 저장할 폴더 경로)
            thumbnail(filename)                             # 썸네일
        except pymysql.err.InternalError:
            print('error : 새로운 컬럼 필요! 예외 처리했습니다.')
            print(query)
            print(url)
            result = True
        except pymysql.err.IntegrityError:
            print('error : 이미지가 이미 DB에 저장되어있습니다 ')
            urllib.request.urlretrieve(imgpath, filename)
            thumbnail(filename)
            print("이미지 저장 완료 filename : %s" % filename)
        except pymysql.err.DataError:
            print("error : 데이터 길이가 맞지 않습니다..")
            print(query)
            print(url)
            result = True
        except pymysql.err.ProgrammingError:
            print("error : 이미지 정보가 부족합니다 예외처리하겠습니다.")
            print(url)
            result = True
        except Exception as ex:
            print("ckimg error : ", ex)
            result = True
    else:
        print("이미 저장된 이미지 입니다." + url)
    return result


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
            filename = selectid(realhref)           # selectid 함수로 가서 고유id 추출
            info_ = information(realhref, filename['path'], filename['id_'])  # 상세정보 추출
            createimg = ckimg(info_['image'], filename['path'], info_['query'], realhref)      # 폴더 내 중복 이미지 체크 후 DB insert
            if not createimg:                                                             # DB삽입 성공시 성공한 갯수 count
                count += 1                                                 # 완료 갯수 ++
            else:
                error_ += 1                                                # error 발생
                errorurl(realhref)
        print("----------------------------------------------------")
        print("           %d 페이지 완료                          " % i)
        print("          process : {0}                           ".format(current_process().name))
        print("        새로운 이미지 : (%d/%d)             " % (count, realcount))
        print("----------------------------------------------------")
    except Exception as ex:
        print('page error : ', ex)
        errorurl(i)
        error_ += 9                                 # 페이지 에러발생
    time.sleep(0.5)
    return [int(error_), int(count)]            # 에러갯수 및 완료한 갯수 return

# -----------------------------------------------------------------------------------------------------------------------------------------------


def main(url_):
    pro = True
    start = 1
    end = 2000
    plus = 2000
    real_end = int(endpage(url_)) + 1
    while pro:
        values_ = 0
        error_value = 0
        process_time = time.time()
        p = Pool(6)
        p.daemon = True
        try:
           process = p.imap(Crawling, range(start, end))
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
            print("(%s ~ %s) 페이지 크롤링 완료" % (str(start), str(end - 1)))
            print("걸린 시간 : %0.2f 초" % (time.time() - process_time))
            print("다운받은 이미지 : %d" % (int(values_)))
            print("오류로 인해 받지 못한 이미지 : %d" % int(error_value))
            print('폴더 내에 있는 파일 갯수 : %d' % file_len())
            print("5초 쉬었다 오류가 발생한 파일 다시 크롤링. . . ")
            time.sleep(5)
            readerror()
        if end == real_end+1:
            pro = False
        else:
            print("---------------30초 쉬었다 다시 시작--------------- ")
            time.sleep(30)
            start += plus
            end += plus
            if end > real_end:
                end = real_end+1


if __name__ == '__main__':
    indexing = int(input('1: 시작  2: 모두지우기 >>>> '))
    if indexing == 1:
        url = "https://gongu.copyright.or.kr/gongu/wrt/wrtCl/listWrt.do?wrtTy=4&menuNo=200023&depth2At=Y"
        main(url)
        print("==============================모든 페이지 크롤링 완료=================================  ")
        print("%0.2f 초" % (time.time() - time_))
        print('폴더 내에 있는 파일 갯수 : %d' % file_len())

    elif indexing == 2:
        alldelete()