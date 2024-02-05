import requests
import json
import logging
from common.input.Session import plug_in as session
from tanium import NodeField, Meta, SensorField, SensorSchema, CacheQuery
import time

with open("setting.json", encoding="UTF-8") as f:
    SETTING = json.loads(f.read())
APIURL = SETTING['CORE']['Tanium']['INPUT']['API']['URL']
CSP = SETTING['CORE']['Tanium']['INPUT']['API']['PATH']['Sensor']
APIUNM = SETTING['CORE']['Tanium']['INPUT']['API']['username']
APIPWD = SETTING['CORE']['Tanium']['INPUT']['API']['password']
PROGRESS = SETTING['PROJECT']['PROGRESSBAR'].lower()


class NCsmOnlineQuery(CacheQuery):
    computer_id = SensorField(sensor="Computer ID")
    computer_name = SensorField(sensor="Computer Name")
    client_ip = SensorField(sensor="Tanium Client IP Address")
    operating_system = SensorField(sensor="Operating System")


    _meta = Meta(
        fields=[
            "computer_id",
            "computer_name",
            "client_ip",
            "operating_system",
        ],
    )


def plug_in(type):
    logger = logging.getLogger(__name__)
    try:
        SK = session()
        if type == 'online':
            #CSID = '4383'
            CSID = SETTING['CORE']['Tanium']['INPUT']['API']['SensorID']['ONLINE']
        CSH = {'session': SK}
        CSU = APIURL + CSP + CSID
        CSR = requests.post(CSU, headers=CSH, verify=False)
        # time.sleep(60)
        CSRT = CSR.content.decode('utf-8', errors='ignore')
        CSRJ = json.loads(CSRT)
        #CSRJD = NCsmOnlineQuery.objects.to_list_value()
        #print(NCsmOnlineQuery.objects.get_graphql_endpoints())


        CSRJD = CSRJ['data']
        #print(CSRJD)
        dataList = []
        DATA_list = CSRJD['result_sets'][0]['rows']

        for d in DATA_list:  # index 제거
            DL = []
            for i in d['data']:
                DL.append(i)
            dataList.append(DL)
        logger.info('Tanium API Sensor 호출 성공')
        logger.info('Sensor ID : ' + str(CSID))
        #print(dataList)

        return dataList
    except Exception as ex:
        import traceback
        traceback.print_exc()
        logger.warning('Tanium API Sensor 호출 Error 발생')
        logger.warning('Sensor ID : ' + str(CSID))
