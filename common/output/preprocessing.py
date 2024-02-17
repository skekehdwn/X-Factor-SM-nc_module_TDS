import json
import logging
from datetime import datetime
import re

from common.models import Xfactor_Common


def plug_in(data):
    # print("전처리 데이터")
    # print(data)
    logger = logging.getLogger(__name__)
    try:
        for d in data:
            for j in range(len(d)):
                if (
                    not d[j][0]['text'] is None
                    and 'result' not in d[j][0]['text']
                    and 'TSE' not in d[j][0]['text']
                    and 'Can not determine' not in d[j][0]['text']
                    and 'hash' not in d[j][0]['text']
                    and 'Unknown' not in d[j][0]['text']
                    and d[j][0]['text'] != ''
                ):
                    d[j][0]['text'] = d[j][0]['text']
                else:
                    value_list = Xfactor_Common.objects.filter(computer_id=d[0][0]['text']).values('computer_name', 'ip_address', 'mac_address', 'chassistype', 'os_simple')
                    # if j == 1:
                    #     d[j][0]['text'] = value_list[0]['computer_name']
                    # elif j == 2:
                    #     d[j][0]['text'] = value_list[0]['ip_address']
                    # elif j == 3:
                    #     d[j][0]['text'] = value_list[0]['mac_address']
                    # elif j == 4:
                    #     d[j][0]['text'] = value_list[0]['chassistype']
                    # elif j == 5:
                    #     d[j][0]['text'] = value_list[0]['os_simple']
                    # else:
                    d[j][0]['text'] = 'unconfirmed'
        logger.info('Preprocessing.py -  성공')
        return data
    except Exception as e:
        logger.warning('Preprocessing_Dashboard.py - Error 발생')
        logger.warning('Error : ' + str(e))

