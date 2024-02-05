import logging

import urllib3
import json

from common.input.UserInput import plug_in as userinput
from common.output.model import plug_in_discover as discover_db
from common.output.model import plug_in_minutely as user_db, cache
from common.output.model import plug_in_daily as daily_db
from common.output.db import before as dash_setting_before
from common.output.db import after as dash_setting_after
from common.output.model import plug_in_purchase as purchase_db
from common.output.model import plug_in_security as security_db
from common.output.model import plug_in_online as online_db
from common.core.Statistics import Minutely_statistics, Daily_statistics
from common.input.online import plug_in as onlineinput

# from common.core.Statistics import chassis_type as chassis_input
# from common.core.Statistics import os_type as os_input
# from common.core.Statistics import win_ver as win_ver_input

# from common.common.Transform.IdleAssetDataframe import plug_in as idle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("setting.json", encoding="UTF-8") as f:
    SETTING = json.loads(f.read())


logger = logging.getLogger()
def minutely_plug_in():
    try:
        dash_setting_before()
        user_asset = userinput('common')
        user_input = user_db(user_asset)
        online_asset  = onlineinput('online')
        online_input  = online_db(online_asset)
        cache()

    # service_asset = userinput('service')
    # service_input = service_db(service_asset)
    #purchase_asset = userinput('purchase')
    #purchase_input = purchase_db(purchase_asset)
    #security_asset = userinput('security')
    #security_input = security_db(security_asset)
    # # print(security_asset)

        Minutely_statistics()
        Daily_statistics()
        dash_setting_after()
    except Exception as e:
        logger.warning('정시 인풋 error' + str(e))

def daily_plug_in():
    user_asset = userinput('daily')
    user_input = daily_db(user_asset)

def discover_plug_in():
    discover_db()
