#-*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pymysql
import urllib
import os
import re

conn = pymysql.connect(host='127.0.0.1', port=3307, user='root', passwd='a1234', db='bucketlist', charset='utf8')
cur = conn.cursor()


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
    print(license)
    print(file)
    filepath = "./ccl/" + str(file[1])     # 이미지명만 추출해서 라이선스 이미지를 저장할 경로 삽입
    resultlins(license, filepath)           # 라이선스 이미지 중복 체크
    return filepath


def information(inserturl, name, path, id_):
    url = inserturl
    html = urlopen(url)
    source = html.read()                            # 소스를 읽는다
    html.close()                                    # 모두 진행한 후 close 해준다

    name = name.replace("'", "\\'")                 #' 이 SQL 문자구분에 문제가 생길수도 있으니 \ 삽입
    soup = BeautifulSoup(source, "html5lib")
    selecttable = soup.find(class_='tb_bbs tbType')
    selectimg = soup.find(class_='copyD')
    table = selecttable.find_all('tr')
    lins = selectimg.find('img').get('src')
    lins = "https://gongu.copyright.or.kr" + lins
    lins = cklicense(lins)                                        # 라이센스 이미지 중복체크 및 저장 경로설정
    into_ = "(_id,filename,path,license,"                        # DB에 저장할 컬럼
    value = "('" + id_ + "','" + name + "','" + path + "','" + lins + "',"      # DB에 저장할 값
    count = 4                               # 값들의 갯수 체크 (_id , filename , path , license는 이미 있으므로 4부터 시작)
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
    return query                                     # 쿼리 전송


def selectid(url):
    Search = str(re.search(r"wrtSn=\d{4,10}", url).group())                     # 이미지 고유번호 추출
    title = re.sub("[^0-9]", "", Search)                                        # 번호만 추출
    filename = "./img/" + str(title) + ".PNG"                                   # img저장 경로 설정
    return {'path': filename, 'id_': title}


def ckimg(imgpath, filename, query):
    result = os.path.exists(filename)                               # 중복된 이미지가 있는지 없는지 확인
    if not result:
        urllib.request.urlretrieve(imgpath, filename)                       # 이미지 폴더에 저장 (저장할 이미지 추출, 저장할 폴더 경로)
        print("query : %s " % query)
        print("이미지 저장 성공 filename : %s" % filename)
        cur.execute(query)              #DB 삽입
        print("DB  입력완료")
        conn.commit()                   #DB commit
    else:
        print("이미 저장된 이미지 입니다.")
    return result


def Crawling(i, index):
    count = 0
    realcount = 0
    while i <= index:
        url = "https://gongu.copyright.or.kr/gongu/wrt/wrtCl/listWrt.do?menuNo=200023&viewType=&wrtTy=4&sortSe=&usePurps=&usageRange=&depth2At=Y&copyType_2d=&searchWrd=&pageIndex=%d" % i
        html = urlopen(url)
        source = html.read()
        html.close()

        soup = BeautifulSoup(source, "html5lib")
        select = soup.find(class_="bbsPhoto")   # div class 확인

        li = select.find_all('li')              # li태그만 추출

        for val in li:
            realcount += 1                          # 전체 카운트 인덱싱
            img = val.find('img').get('src')        # img태그의 src 추출
            href = val.a.get('href')                # li 태그의 href 추출
            realimg = "https://gongu.copyright.or.kr" + img  # 공유마당 뒷 url 입력
            realhref = "https://gongu.copyright.or.kr" + href
            imgtitle = val.get_text().strip()       # li태그의 텍스트 모두 추출후 공백 지우기
            filename = selectid(realhref)           # selectid 함수로 가서 고유id 추출
            print("img : %s" % realimg)
            print("href : %s" % realhref)
            print("page : %d" % i)
            query = information(realhref, imgtitle, filename['path'], filename['id_'])  # 상세정보 추출
            createimg = ckimg(realimg, filename['path'], query)                          # 폴더 내 중복 이미지 체크 후 DB insert

            if not createimg:                                                             # DB삽입 성공시 성공한 갯수 count
                count += 1
            print("-----------------------------------------------------------------------------------------------")
        print("----------------------------------------------------")
        print("           %d 페이지 모두 크롤링 완료                   " % i)
        print("----------------------------------------------------")
        i += 1
    print("크롤링완료 새로운 이미지 : (%d/%d)" % (count, realcount))
    print("크롤링한 페이지 %d page" % (i-1))

# -----------------------------------------------------------------------------------------------------------------------------------------------


def main():
    result_cr = True
    while result_cr:
        input_Ch = input("(1 = 1 ~ 입력값 ｜ 2 = 입력값 ~ 입력값) \n >>")
        if int(input_Ch) == 1:
            result_cr = False
            input_end = input('크롤링페이지 갯수 >>')
            Crawling(1, int(input_end))
        elif int(input_Ch) == 2:
            result_cr = False
            input_start = input('크롤링 시작 페이지 >> ')
            input_end = input('크롤링페이지 갯수 >> ')
            Crawling(int(input_start), int(input_end))
        else:
            print("1 과 2중에 하나만 입력해주세요")

main()