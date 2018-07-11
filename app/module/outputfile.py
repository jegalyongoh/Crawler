# 산출물 로컬 저장 경로지정 모듈
from PIL import Image
import os
import urllib
import re
import conf
import pymysql
# 바이너리 모듈 사용
import imagehash


# com.conf 에 있는 설정 parser
config = conf.pathget()
thumbnail_ = config['thumbnail']
image_ = config['image'] 
license_ = config['lisense']

#이미지 저장 및 DB저장
def saveinfo(imghref, file_path, query, url,cur,conn,fileid_,file_name):
    result = os.path.exists(file_path)                               # 중복된 이미지가 있는지 없는지 확인
    if not result:
        try:
            cur.execute(query)              #DB 삽입     
            
            urllib.request.urlretrieve(imghref, file_path)  # 이미지 폴더에 저장 (저장할 이미지 추출, 저장할 폴더 경로)
            thumbnail(file_path,file_name,cur,conn)                             # 썸네일
            imagehash.hash_image(fileid_,file_name,file_path,cur,conn)      # 이미지해시화
            conn.commit()   #DB commit
        except pymysql.err.InternalError:
            print('error : 새로운 컬럼 필요! 예외 처리했습니다.')
            print(query)
            print(url)
            result = True
        except pymysql.err.IntegrityError:
            print('error : 이미지가 이미 DB에 저장되어있습니다 ')
            urllib.request.urlretrieve(imghref, file_path)
            thumbnail(file_path,file_name,cur,conn)
            imagehash.hash_image(fileid_,file_name,file_path,cur,conn)
            print("이미지 저장 완료 file_path : %s" % file_path)
            # print(query)
        except pymysql.err.DataError:
            print("error : 데이터 길이가 맞지 않습니다..")
            print(query)
            print(url)
            result = True
        except pymysql.err.ProgrammingError:
            print("error : 이미지 정보가 부족합니다 예외처리하겠습니다.")
            print(url)
            # print(query)
            result = True
        except Exception as ex:
            print("saveinfo error : ", ex)
            # print(query)
            result = True
    else:
        print("이미 저장된 이미지 입니다." + url)
    return result

# 썸네일 
def thumbnail(path,name,cur,conn):
    try:
        size = 136, 100                 # 136 , 100 으로 이미지크기설정
        image = Image.open(path)            # 이미지오픈
        image.thumbnail(size)               # 썸메일
        file = os.path.split(path)          # file[0] = ../../Output/img  file[1] = 123456.png
        filename = str(file[1])
        thumbnail_path = thumbnail_ + filename       # file[1] = 이미지명만 추출
        image.save(thumbnail_path)                      # 썸네일 이미지 저장
        imagehash.hash_thumbnail(filename, name, thumbnail_path, cur, conn)
    except Exception as ex:
        print("error : 썸네일 오류 .. 확인해주세요", ex)
        print(path)

# 라이선스 중복체크
def resultlins(file_id, name, licensepath, path, cur, conn):
    result = os.path.exists(path)                   # 폴더안에 이미지 중복 체크 exists 함수
    if not result:
        print("새로운 라이센스 발견 CREATE : %s" % path)
        urllib.request.urlretrieve(licensepath, path)               # 이미지 저장
        imagehash.hash_license(file_id,name,path,cur,conn)
        
# 라이선스 이미지명 추출
def cklicense(license, lins_name,cur ,conn):
    file = os.path.split(license)           # 이미지 명만 추출하기위해 배열로 나눔 split 함수
    file_id = str(file[1])
    filepath = license_ + file_id     # 이미지명만 추출해서 라이선스 이미지를 저장할 경로 삽입
    resultlins(file_id, lins_name, license, filepath, cur, conn)           # 라이선스 이미지 중복 체크
    return filepath

# 이미지 이미지명 추출 
def selectid(url):
    Search = str(re.search(r"wrtSn=\d{4,10}", url).group())   # 이미지 고유번호 추출
    title = re.sub("[^0-9]", "", Search)            # 번호만 추출
    filename = image_ + str(title) + ".PNG"     # img저장 경로 및 이미지명 설정
    return {'path': filename, 'id_': title}

# conf 테스트 
if __name__ == '__main__':
    print(config)
    print(thumbnail_)
    print(image_)
    print(license_)