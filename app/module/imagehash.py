#       이미지 해시 모듈
import base64
import pymysql
import gzip


# 이미지를 인코딩해서 해시 화 후 DB저장
def hash_image(id_,name, imgpath,cur,conn):
    with open(imgpath, 'rb') as img:
        try: 
            # 이미지 인코딩
            img_en = base64.b64encode(img.read())
            # byte type -> str type
            # img_de = img_en.decode("utf-8")
            # byte type 압축 후 db저장 
            img_zip = hashzip(img_en)
            #   DB insert
            query_blob = 'INSERT INTO encoded_image_longblob values("'+id_+'","'+name+'",%s)'
            # query_text = 'INSERT INTO encoded_image values("'+id_+'","'+name+'",%s)'
            cur.execute(query_blob, (img_zip))
            # cur.execute(query_text, (img_de))
            # conn.commit()
        except pymysql.err.DataError:
            print('인코딩 길이 맞지 않음. ( txt파일에 저장 )')
            # image_txt(name,img_de)
        except pymysql.err.IntegrityError:
            print('이미 저장 되어있는 인코더')
        except Exception as err:
            print('hash sql error : '+ err)

# 해시화 된 이미지 압축
def hashzip(encode_):
    longtext = encode_          # 인코딩 되어있는 이미지 
    data = gzip.compress(longtext)     # 압축화
    return data


def hash_thumbnail(id_,name, imgpath,cur,conn):
    with open(imgpath, 'rb') as img:
        try: 
            # 이미지 인코딩
            img_en = base64.b64encode(img.read())
            # byte type > str type
            img_de = img_en.decode("utf-8")
            id_ = id_[:-4]
            qurey = 'insert into encoded_thumbnail values("'+id_+'","'+name+'",%s)'
            cur.execute(qurey, (img_de))
            # conn.commit()
        except pymysql.err.DataError:
            print('인코딩 길이 맞지 않음. ( pass )')
            thumbnail_txt(name,img_de)
        except pymysql.err.IntegrityError:
            print('이미 저장 되어있는 인코더')
        except Exception as err:
            print('hash sql error : '+ err)


def hash_license(id_, filename, imgpath,cur,conn):
    print(imgpath)
    with open(imgpath, 'rb') as img:
        try: 
            # 이미지 인코딩
            img_en = base64.b64encode(img.read())
            # byte type > str type
            img_de = img_en.decode("utf-8")
            # img_de = hashzip(img_en)
            #   DB insert
            id_ = id_[:-4]   # 확장자삭제 
            query = 'insert into encoded_license values("'+id_+'","'+filename+'", %s)'
            cur.execute(query, (img_de))
            conn.commit()
        except pymysql.err.DataError:
            license_txt(filename, img_de)
            print('인코딩 길이 맞지 않음. ( pass )')
        except pymysql.err.IntegrityError:
            print('이미 저장 되어있는 인코더')
        except Exception as err:
            print('hash sql error : '+ err)
        # imagesave(img_en,id_)       


# 인코딩 된 이미지를 다시 디코딩 하여 이미지로 변환
def imagesave(cur):
    print('이미지화 시작 . . .')
    cur.execute('SELECT _id,hash_ FROM encoded_image')
    data = cur.fetchall()
    for id_, encode_ in data:
        str(id_)
        img_re = encode_.encode()
        path = '../../Output/hash/image/%s.png' % id_
        with open(path, "wb") as fh:
            fh.write(base64.decodebytes(img_re))
    print('이미지화 완료.')
    licensesave(cur)


# 라이선스 이미지화 
def licensesave(cur):
    print('라이선스 이미지화 시작 . . .')
    cur.execute('SELECT license,hash_ FROM encoded_license')
    data = cur.fetchall()
    for id_, encode_ in data:
        str(id_)
        img_re = encode_.encode()
        path = '../../Output/hash/license/%s.png' % id_
        with open(path, 'wb') as file:
            file.write(base64.decodebytes(img_re))
    print('라이선스 이미지화 완료.')
    thumbnailsave(cur)


def thumbnailsave(cur):
    print('썸네일 이미지화 시작 . . . ')
    cur.execute('SELECT _id,hash_ FROM encoded_thumbnail')
    data = cur.fetchall()
    for id_, encode_ in data:
        str(id_)
        img_re = encode_.encode()
        path = '../../Output/hash/thumbnail/%s.png' % id_
        with open(path, 'wb') as file:
            file.write(base64.decodebytes(img_re))
    print('썸네일 이미지화 완료.')


# DB에 저장 되지않은 해시 txt파일에 저장
def image_txt(filename, encode_):
    with open('../../log/hashimage_log.txt', 'a') as file:
        file.write(filename +'(hash) :  \n'+str(encode_) + '\n\n\n')
        print('image hash txt파일 입력완료')

def license_txt(filename, encode_):
    with open('../../log/hashlicense_log.txt', 'a') as file:
        file.write(filename +'(hash) :  \n'+str(encode_) + '\n\n\n')
        print('license hash txt파일 입력완료')

def thumbnail_txt(filename, encode_):
    with open('../../log/hashthumbnail_log.txt', 'a') as file:
        file.write(filename +'(hash) :  \n'+str(encode_) + '\n\n\n')
        print('thumbnail hash txt파일 입력완료')   



# TEST
if __name__ == '__main__':
    name = 'test'
    imagetext = 'test'
    licensetext = 'test'
    thumbnailtext = 'test'

    image_txt(name,imagetext)
    license_txt(name,licensetext)
    thumbnail_txt(name,thumbnailtext)