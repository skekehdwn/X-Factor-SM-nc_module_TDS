from datetime import datetime

from common.core.Dashboard import daily_plug_in as CTDPI
from common.core.Dashboard import minutely_plug_in as CTMPI
from common.core.Dashboard import discover_plug_in as DCPI
from common.core.Kafka import Kafka_Con, save_to_postgresql
from common.core.dataCollection import job
from common.etc.thread import count as count
import urllib3
import threading
import logging
import time
import json
from common.etc.logger import date_handler
from apscheduler.schedulers.background import BlockingScheduler


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

run_main = True
MinuitTime = 0
result_list = []

def minutely() :
    try:
        now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print('\rminutely', end ="")
        print(now)
        CTMPI()
        logger.info('Minutely CMU Module Succesed!!')
    except Exception as e:
        logger.warning('Minutely CMU Module Fail' +str(e))


def daily():
    try:
        now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print('\rdaily', end ="")
        print(now)
        CTDPI()
        logger.info('Daily CDU common Succeeded!')
    except Exception as e:
        logger.warning('Daily CDU common Fail' +str(e))

def kafka():
    try:
        now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print('\rdaily', end ="")
        print(now)
        Kafka_Con()
        logger.info('Kafka Succeeded!')
    except Exception as e:
        logger.warning('Kafka Fail' +str(e))

def discover():
    try:
        now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print('\rdiscover', end ="")
        print(now)
        DCPI()
        logger.info('미관리자산 메일 알람 발송 Succeeded!')
    except Exception as e:
        logger.warning('미관리자산 메일발송 Fail' +str(e))

# def weekly():
#     try:
#         now = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
#         print('\rweekly Alarm Mail', end ="")
#         print(now)
#         DCPI()
#         logger.info('weekly Alarm Mail Succeed 성공')
#     except Exception as e:
#         logger.warning('weekly Fail' + str(e))


def main():
    try :
        #job()
        CTMPI()
        #CTDPI()
        #DCPI()
        # Kafka_Con()
        # Kafka_Con()
        logger.info('Tanium Minutely common 성공')
        print('Tanium Minutely common 성공')

    except Exception as e :
        print()
        # if AUTOCREATEUSE == 'false' :
        #     if '이름의 릴레이션(relation)이 없습니다' in str(e) :
        #         print('{} 테이블이 없습니다'.format(str(e).strip('오류:').split('이름의 릴레이션')[0]))
        #         print('테이블을 생성하시거나 AUTOCREATE를 True로 변경해주세요')
        #         quit()
        #     elif 'does not exist' in str(e) :
        #         print('{} 테이블이 없습니다'.format(str(e).strip('relation ').split('does not exist')[0]))
        #         print('테이블을 생성하시거나 AUTOCREATE를 True로 변경해주세요')
        #         quit()
        #     else :
        #         print(str(e))

    print("스케쥴링을 시작하겠습니다.")

    for i in reversed(range(3)) :
        print("...........{}".format(i + 1), end="\r")
        time.sleep(1)

    CDTH="21"
    CDTM="09"
    thread.start()
    sched = BlockingScheduler(timezone='Asia/Seoul')
    #실제
    # sched.add_job(minutely, 'cron', minute='*/5', second='10', misfire_grace_time=None)  # seconds='3'
    # sched.add_job(daily, 'cron', minute='*/10', second='10', misfire_grace_time=None)

    #test용
    # sched.add_job(minutely, 'cron', hour=CDTH, minute=CDTM, second='10', misfire_grace_time=None)  # seconds='3'
    sched.add_job(minutely, 'cron', hour='0-23', minute='00', second='10', misfire_grace_time=None)  # seconds='3'
    #sched.add_job(daily, 'cron', hour='0-23', minute='10',  second='20', misfire_grace_time=None)
    #sched.add_job(kafka, 'cron', hour='16', minute='30',  second='20' , misfire_grace_time=None)
    #sched.add_job(discover, 'cron', hour=10, minute=30, second=0, misfire_grace_time=None)
    #sched.add_job(job, 'cron', hour='0-23', minute=00, second=0, misfire_grace_time=None)

    logger.info('Start the Scheduling~')
    sched.start()

if __name__ == "__main__":
    with open("setting.json", encoding="UTF-8") as f:
        SETTING = json.loads(f.read())
    CUSTOMER = SETTING['PROJECT']['CUSTOMER']
    

    PTD = SETTING['PROJECT']['TEST']['DAILY'].lower()
    TU = SETTING['CORE']['Tanium']['COREUSE'].lower()
    CMU = SETTING['CORE']['Tanium']['CYCLE']['MINUTELY']['USE'].lower()
    CMT = SETTING['CORE']['Tanium']['CYCLE']['MINUTELY']['TIME']
    CDU = SETTING['CORE']['Tanium']['CYCLE']['DAILY']['USE'].lower()
    CDTH = SETTING['CORE']['Tanium']['CYCLE']['DAILY']['TIME']['hour']
    CDTM = SETTING['CORE']['Tanium']['CYCLE']['DAILY']['TIME']['minute']
    TVU = SETTING['CORE']['Tanium']['PROJECT']['VUL']['USE'].lower()

    # today = datetime.today().strftime("%Y%m%d")
    # logFile = LOGFD + LOGFNM + today + LOGFF
    # logFormat = '%(levelname)s, %(asctime)s, %(message)s'
    # logDateFormat = '%Y%m%d%H%M%S'
    # # logging.basicConfig(filename=logFile, format=logFormat, datefmt=logDateFormat, level=logging.DEBUG)
    # # file_handler = RotatingFileHandler(filename='log/log.log', maxBytes=1024*1024*100, backupCount=10)

    # # Create a file handler that rotates log files by date
    # # date_handler = TimedRotatingFileHandler(filename='log/log.log', when='midnight', interval=1, backupCount=10, encoding='utf-8')
    # # date_handler.suffix = '%Y%m%d.log'
    # # Create a console handler

    # # Create a logging format
    # formatter = logging.Formatter('%(levelname)s, %(asctime)s, %(message)s')
    # # file_handler.setFormatter(formatter)
    # # date_handler.setFormatter(formatter)
    # # console_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)
    logger.addHandler(date_handler())
    logger.info('common Started')
    
    thread = threading.Thread(target=count)
    thread.daemon = True
    main()
    logger.info('common Finished')


