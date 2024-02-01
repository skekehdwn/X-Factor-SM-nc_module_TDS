
import time

def count() :
    run = True
    count = 0
    running = '\\'
    while run :
        if count == 0 :
            running = '\\'
        elif count == 1 :
            running = '|'
        elif count == 2 :
            running = '/'
        elif count == 3 :
            running = 'ㅡ'
        elif count == 4 :
            running = '|'
        print('common is running....{}'.format(running), end='\r')
        time.sleep(0.5)
        count = count +1
        if count == 4 :
            count = 0