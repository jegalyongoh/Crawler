#-*- coding: utf-8 -*-
#config 데이터 parser 모듈
import configparser
cfg = configparser.ConfigParser()
# config 대상 설정
cfg.read("../../conf/com.conf", encoding='UTF8')

# DB설정 parser
def dbget():
    
    host = cfg.get('DB', 'host')        
    port = cfg.get('DB', 'port')
    user = cfg.get('DB', 'user')
    passwd = cfg.get('DB', 'passwd')
    db = cfg.get('DB', 'db')
    charset = cfg.get('DB', 'charset')
    data = {'host':host, 'port':int(port), 'user':user, 'passwd':passwd, 'db':db,'charset':charset}
    return data

# 저장경로 parser
def pathget():
    thumbnail = cfg.get('path', 'output_thumbnail')     # 썸네일 저장경로
    image = cfg.get('path', 'output_image')             # 이미지 저장경로
    lisense = cfg.get('path', 'output_lisense')         # 라이선스 저장경로
    data = {'thumbnail' : thumbnail, 'image':image, 'lisense':lisense}
    return data


#대기시간 parser
def timeget():
    page = cfg.get('sleeptime', 'ongpage_sleeptime')                 # 1page 당 대기시간
    image = cfg.get('sleeptime', 'oneimage_sleeptime')               # 한개의 이미지당 대기시간
    finish_page = cfg.get('sleeptime', 'crawler_sleeptime')      # 2000페이지당 대기시간
    error_page = cfg.get('sleeptime', 'errorpage_sleeptime')     # 에러 후처리 대기시간
    data = {'page':float(page), 'image':float(image), 'finish_page':float(finish_page), 'error_page':float(error_page)}
    return data


#자동 삭제 parser
def autodelete():
    data = cfg.get('autodelete', 'autodelete_plog')
    if data=='TRUE':
        data = True
    else :
        data = False
    return data

# 해시 이미지화 여부 parser
def hashimage():
    data = cfg.get('hashimage', 'hashimage_plog')
    if data=='TRUE':
        data = True
    else :
        data = False
    return data

def all():
    dbs = dbget()
    pathgets = pathget()
    timegets = timeget()
    autodeletes = autodelete()
    hashimages = hashimage()
    data = {'db' : dbs, 'path' : pathgets, 'time' : timegets, 'autodelete_plog' : autodeletes, 'hashimage' : hashimages}
    return data
# TEST
if __name__ == '__main__':
    print(dbget())
    print(pathget())
    print(timeget())
    print(autodelete())