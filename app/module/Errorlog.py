
# error log 삽입 및 삭제 모듈

# 에러 후처리 완료 후 로그 삭제
def deletelog():
    with open('../../log/error_log.txt', 'w+t') as file:
        for i in file:
            print('delete log', i)
# 에라 발생시 로그 삽입 
def errorurl(url_):
    with open('../../log/error_log.txt', 'a') as file:
        file.write(str(url_) + '\n')