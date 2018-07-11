import pymysql
import base64
import gzip
from tqdm import tqdm

conn = pymysql.connect(host='127.0.0.1', port=3307, user='root', passwd='a1234', db='bucketlist', charset='utf8')
cur = conn.cursor()

def test():
    # _id와 hash_를 한꺼번에 가지고 오면 오래걸려 따로 구분 
    query = "SELECT _id FROM encoded_image_longblob"
    cur.execute(query)          
    data_blob = cur.fetchall()          #데이터 불러오기
    #   tqbm 모듈을 사용해 현재까지 작업량 체크
    bar = tqdm(data_blob)
    for a in bar:
        id_ = a
        imagesave(id_)


def imagesave(id_):
    query = "SELECT hash_ FROM encoded_image_longblob where _id = %s" % id_
    cur.execute(query)
    data = cur.fetchone()
    for a in data:
        hashzip = a
    hash_ = gzip.decompress(hashzip)    # 압축해제
    path = '../../Output/hash/blob/%s.png' % id_
    with open(path, "wb") as fh:
        fh.write(base64.decodebytes(hash_))     #디코딩 후 저장


if __name__ == '__main__':
    test()