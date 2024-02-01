import requests
import json
import logging

with open("setting.json", encoding="UTF-8") as f:
    SETTING = json.loads(f.read())
APIURL = SETTING['CORE']['Tanium']['INPUT']['API']['URL']
SKP = SETTING['CORE']['Tanium']['INPUT']['API']['PATH']['SessionKey']
APIUNM = SETTING['CORE']['Tanium']['INPUT']['API']['username']
APIPWD = SETTING['CORE']['Tanium']['INPUT']['API']['password']

def plug_in() :
    logger = logging.getLogger(__name__)
    try:
        SKH = '{"username": "'+APIUNM+'", "domain": "", "password": "'+APIPWD+'"}'
        SKURL = APIURL + SKP
        SKR = requests.post(SKURL, data=SKH, verify=False)
        SKRC = SKR.status_code
        SKRT = SKR.content.decode('utf-8', errors='ignore')
        SKRJ = json.loads(SKRT)
        SK = SKRJ['data']['session']
        logger.info('Tanium API Session Key 호출 성공')
        logger.info('Session Key : '+str(SK))
        return SK
    except :
        logger.warning('Tanium API Session Key 호출 Error 발생')