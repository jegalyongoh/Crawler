# conf 데이터 출력 소스
import configparser

cfg = configparser.ConfigParser()
cfg.read("../../conf/com.conf")


def dbget():
    host = cfg.get('DB', 'host')
    port = cfg.get('DB', 'port')
    user = cfg.get('DB', 'user')
    passwd = cfg.get('DB', 'passwd')
    db = cfg.get('DB', 'db')
    charset = cfg.get('DB', 'charset')
    print('DB : ')
    print(host)
    print(port)
    print(user)
    print(passwd)
    print(db)
    print(charset)


def pathget():
    thumbnail = cfg.get('path', 'output_thumbnail')
    image = cfg.get('path', 'output_image')
    lisense = cfg.get('path', 'output_lisense')
    print('path : ')
    print(thumbnail)
    print(image)
    print(lisense)


def timeget():
    page = cfg.get('sleeptime', 'page')
    image = cfg.get('sleeptime', 'image')
    finish_page = cfg.get('sleeptime', 'end_page')
    error_page = cfg.get('sleeptime', 'error_page')
    print('time :')
    print('page',page)
    print('image',image)
    print('finish_page',finish_page)
    print('error_page',error_page)

def autodelete():
    data = cfg.get('autodelete', 'boolean')
    print(data)

if __name__ == '__main__':
    dbget()
    pathget()
    timeget()
    autodelete()