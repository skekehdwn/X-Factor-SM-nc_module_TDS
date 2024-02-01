import json
import logging
from datetime import datetime
import re


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
                ):
                    d[j][0]['text'] = d[j][0]['text']
                else:
                    d[j][0]['text'] = 'unconfirmed'
        logger.info('Preprocessing.py -  성공')
        return data
    except Exception as e:
        logger.warning('Preprocessing_Dashboard.py - Error 발생')
        logger.warning('Error : ' + str(e))

