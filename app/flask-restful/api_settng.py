# -- coding: utf-8 --
from flask_restful import Resource,reqparse
from flask import request, json,jsonify
import base64
import gzip
import pymysql
import sys
sys.path.append("..")
from module import conf

dbconfig = conf.dbget()             
conn = pymysql.connect(host=dbconfig['host'], port=dbconfig['port'], user=dbconfig['user'], passwd=dbconfig['passwd'], db=dbconfig['db'], charset=dbconfig['charset'])
cur = conn.cursor()
curs = conn.cursor(pymysql.cursors.DictCursor)

# Crawler 설정 api
class settingparser(Resource):
    def get(self):
        if request.method == 'GET':
            data = conf.all()
            print('Crawler setting 열람')
            return json.dumps(data, sort_keys=False)

# data 개수 api
class datacount(Resource):
    def get(self):
        if request.method == 'GET':
            query = "SELECT count(*) from crawler"
            cur.execute(query)
            cnt = cur.fetchone()
            print('데이터 개수 열람')
            return json.dumps({'file' : cnt})

# 범위에 따른 데이터 api
class rangedata(Resource):
    def get(self):
        if request.method == 'GET':
            parser = reqparse.RequestParser()
            parser.add_argument('start', type=int)
            parser.add_argument('end', type=int) 
            args = parser.parse_args()
            start = args['start']
            end = args['end']
            query = 'SELECT crawler.*, encoded_image_longblob.hash_ from crawler inner join encoded_image_longblob ON crawler._id = encoded_image_longblob._id limit %s, %s;'
            curs.execute(query, (start, end))
            datas = curs.fetchall()
            result = {}
            for a in range(len(datas)):
                hash_ = gzip.decompress(datas[a]['hash_'])
                images = hash_.decode("utf-8")
                del datas[a]['hash_']
                result[a] = {'info' : datas[a], 'hashs' : str(images)}
            print('범위에 따른 데이터 api 열람')
            return json.dumps(result)
            

# 라이선스 해시 api
class licesnsehash(Resource):
    def get(self):
        if request.method == 'GET':
            parser = reqparse.RequestParser()
            parser.add_argument('_id', type=str)
            args = parser.parse_args()
            id_ = args['_id']
            query = 'SELECT license_name from crawler where _id = %s'
            cur.execute(query, (id_))
            data = cur.fetchone()
            for a in data:
                filename = a
            query = 'SELECT * from encoded_license where license_name = "%s"' % filename
            curs.execute(query)
            result = curs.fetchone()
            images= result['hash_']
            del result['hash_']
            print('라이선스 해시 api 열람')
            return json.dumps({'info' : result , 'hash' : str(images)})

# 모든 이미지 데이터 api
class imagesall(Resource):
    def get(self):
        if request.method == 'GET':
            query = 'SELECT * FROM crawler'
            cur.execute(query)
            columns =tuple([ d[0] for d in cur.description])
            rows = cur.fetchall()
            result = []
            values = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            for text in result:
                values.append(text)
            print('모든 이미지 api 열람')
            return json.dumps(values,ensure_ascii=False, sort_keys=False)

# 이미지 세부정보 api
class imageinfo(Resource):
    def get(self):
            parser = reqparse.RequestParser()
            parser.add_argument('_id', type=str)
            args = parser.parse_args()
            key = args['_id']
            query = 'SELECT * FROM crawler where _id = %s' % key
            curs.execute(query)
            result = curs.fetchall()
            print('세부정보 api 열람')
            return json.dumps(result, ensure_ascii=False, sort_keys=False)

# 라이선스 세부정보 api
class licenseinfo(Resource):
    def get(self):
        if request.method == 'GET':
            parser = reqparse.RequestParser()
            parser.add_argument('_id', type=str)
            args = parser.parse_args()
            id_ = args['_id']
            query = 'SELECT license,license_name from crawler where _id = %s' % id_
            cur.execute(query)
            columns =tuple([ d[0] for d in cur.description])
            rows = cur.fetchall()
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            print('license infomation api 열람')
            return json.dumps(result, ensure_ascii=False)

# 썸네일 해시 api 
class thumbnailhash(Resource):
    def get(self):
        if request.method == 'GET':
            parser = reqparse.RequestParser()
            parser.add_argument('_id', type=str)
            args = parser.parse_args()
            id_ = args['_id']
            query = 'SELECT * from encoded_thumbnail where _id = %s' % id_
            cur.execute(query)
            columns =tuple([ d[0] for d in cur.description])
            rows = cur.fetchall()
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            print('thumbnail hash api 열람')
            return json.dumps(result, ensure_ascii=False)

# 이미지 해시 api
class imageshash(Resource):
    def get(self):
        if request.method == 'GET':
            parser = reqparse.RequestParser()
            parser.add_argument('_id', type=str)
            args = parser.parse_args()
            id_ = args['_id']
            query = 'SELECT * from encoded_image_longblob where _id = %s' % id_
            curs.execute(query)
            result = curs.fetchone()
            hash_ = gzip.decompress(result['hash_'])
            images = hash_.decode("utf-8")
            del result['hash_']
            print('image hash api 열람')
            return json.dumps({'info' : result , 'hash' : str(images)})

# 이미지 삭제 api
class deleteimg(Resource):
    def delete(self):
        if request.method == 'DELETE':
            parser = reqparse.RequestParser()
            parser.add_argument('_id', type=str)
            args = parser.parse_args()
            key = args['_id']
            query = 'delete from crawler where _id = %s' % key
            print(query)
            try:
                cur.execute(query)
                conn.commit()
                print('delete complete key > \t  '+ key)
                delete_result = True
            except Exception as err:
                print('ERROR ! : ', err)
                delete_result = False
            return json.dumps({"id" : key , "result" : delete_result})

# 이미지 업데이트 api 
class updateimg(Resource):
    def put(self):
        if request.method == 'PUT':
            parser = reqparse.RequestParser()
            parser.add_argument('_id', type=str)
            parser.add_argument('col', type=str)
            parser.add_argument('value', type=str)
            args = parser.parse_args()
            key = args['_id']
            cols = args['col']
            value = args['value']
            query = 'update crawler SET %s = "%s" where _id = %s' % (cols, value, key)
            try :
                cur.execute(query) 
                conn.commit()
                # print(query)
                checkup = True
            except Exception as err :
                print("UPDATE ERROR ! ", err)
                checkup = False

            return json.dumps({'_id' : key, 'result' : checkup})
def test():
    print('test')

if __name__  == "__main__":
    test()