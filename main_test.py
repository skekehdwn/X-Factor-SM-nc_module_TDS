from datetime import datetime
from common.core.Dashboard import daily_plug_in as CTDPI
#from common.core.Tanium.Vul import minutely_plug_in as CTVMPI
import urllib3
import logging
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main() :

    CTDPI()


if __name__ == "__main__":

    with open("setting.json", encoding="UTF-8") as f:
        SETTING = json.loads(f.read())
    LOGFD = SETTING['PROJECT']['LOG']['directory']
    LOGFNM = SETTING['PROJECT']['LOG']['fileName']
    LOGFF = SETTING['PROJECT']['LOG']['fileFormat']
    TU = SETTING['CORE']['Tanium']['COREUSE'].lower()
    CMU = SETTING['CORE']['Tanium']['CYCLE']['MINUTELY']['USE'].lower()
    CMT = SETTING['CORE']['Tanium']['CYCLE']['MINUTELY']['TIME']
    CDU = SETTING['CORE']['Tanium']['CYCLE']['DAILY']['USE'].lower()
    TVU = SETTING['CORE']['Tanium']['PROJECT']['VUL']['USE'].lower()

    today = datetime.today().strftime("%Y%m%d")
    logFile = LOGFD + LOGFNM + today + LOGFF
    logFormat = '%(levelname)s, %(asctime)s, %(message)s'
    logDateFormat = '%Y%m%d%H%M%S'
    logging.basicConfig(filename=logFile, format=logFormat, datefmt=logDateFormat, level=logging.DEBUG)
    logging.info('common Started')
    main()
    logging.info('common Finished')