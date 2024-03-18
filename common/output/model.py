import json
import logging
import smtplib
import psycopg2
from django.db import transaction
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.db.models import Q
from django.http import HttpResponse
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from ..models import *
from .preprocessing import plug_in as PROC
import pytz
from datetime import datetime, timedelta
logger = logging.getLogger()

def plug_in_minutely(data):
    a = 0
    try:
        #print(data)
        # Xfactor_Service.objects.all().delete()
        # Xfactor_Purchase.objects.all().delete()
        # Xfactor_Security.objects.all().delete()
        # Xfactor_Common.objects.all().delete()
        proc_data = PROC(data)
        for d in proc_data:
            #hw_list = []
            sw_list = []
            sw_ver_list = []
            sw_ver_install_list = []
            sw_ver_lastrun_list = []
            hot_list = []
            hotdate_list = []
            chr_list = []
            chr_ver_list = []
            edg_list = []
            edg_ver_list = []
            fir_list = []
            fir_ver_list = []

            logged_name_id = d[49][0]['text'].replace('NC-KOREA\\','')
            try:
                logged_name_id = Xfactor_ncdb.objects.get(userId=logged_name_id)
            except Exception as e:
                custom_object = Xfactor_ncdb()
                custom_object.userId = logged_name_id
                custom_object.save()
                logged_name_id = Xfactor_ncdb.objects.get(userId=logged_name_id)

            # 현재 시간대 객체 생성, 예시: "Asia/Seoul"
            local_tz = pytz.timezone('Asia/Seoul')
            # UTC 시간대를 사용하여 현재 시간을 얻음
            utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
            # 현재 시간대로 시간 변환
            now = utc_now.astimezone(local_tz)
            index_now = now.strftime('%Y-%m-%d-%H')
            computer_id = ''
            tds_computer_id = d[0][0]['text']
            node_computer_id = d[-2][0]['text']
            if tds_computer_id not in ['[no results]', 'unconfirmed']:
                computer_id = tds_computer_id
            elif node_computer_id not in ['unconfirmed']:
                computer_id = node_computer_id
            else:
                continue

            new_user_date_str = ''
            last_seen_data = d[-1][0]['text']
            last_registration_time = d[-3][0]['text']
            if last_seen_data not in ['unconfirmed']:
                new_user_date_str = last_seen_data
            elif last_registration_time not in ['[no results]', '', 'unconfirmed']:
                new_user_date_str = last_registration_time + 'Z'
            else:
                continue
            #print(a)
            # print(last_seen_data, last_registration_time)
            new_user_date = datetime.strptime(new_user_date_str, '%Y-%m-%dT%H:%M:%SZ')
            new_user_date = new_user_date.astimezone(local_tz) + timedelta(hours=9)
            format_date = new_user_date.strftime("%Y-%m-%d %H:%M:%S")
            #print(format_date)
            new_user_date_index_now = new_user_date.strftime('%Y-%m-%d-%H')
            #print(index_now)
            # for h in range(len(d[9])):
            #     hw_list.append(d[9][h]['text'])
            for s in range(len(d[14])):
                sw_list.append(d[14][s]['text'])
                sw_ver_list.append(d[15][s]['text'])
                sw_ver_install_list.append(d[16][s]['text'])
                sw_ver_lastrun_list.append(d[17][s]['text'])
            for i in range(len(d[20])):
                hot_list.append(d[20][i]['text'])
                hotdate_list.append(d[21][i]['text'])
            for c in range(len(d[43])):
                chr_list.append(d[43][c]['text'])
                chr_ver_list.append(d[44][c]['text'])
            for e in range(len(d[45])):
                edg_list.append(d[45][e]['text'])
                edg_ver_list.append(d[46][e]['text'])
            for f in range(len(d[47])):
                fir_list.append(d[47][f]['text'])
                fir_ver_list.append(d[48][f]['text'])
            # xfactor_user = Xfactor_Common()
            # xfactor_user_log = Xfactor_Common_log()
            defaults = {
                'computer_name': d[1][0]['text'],
                'ip_address': d[2][0]['text'],
                'mac_address': d[3][0]['text'],
                'chassistype': d[4][0]['text'],
                'os_simple': d[5][0]['text'],
                'os_total': d[6][0]['text'].replace('Microsoft ', ''),
                'os_version': d[7][0]['text'],
                'os_build': d[8][0]['text'],
                'hw_cpu' : d[9][0]['text'],
                'hw_ram' : d[10][0]['text'],
                'hw_mb' : d[11][0]['text'],
                'hw_disk' : d[12][0]['text'],
                'hw_gpu' : d[13][0]['text'],
                #'hw_list': str(hw_list).replace('"','').replace(",","<br>").replace('\'','').replace('[','').replace(']',''),
                'sw_list': str(sw_list).replace('"','').replace('!','<br>').replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_ver_list': str(sw_ver_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_install' : str(sw_ver_install_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_lastrun' : str(sw_ver_lastrun_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'first_network' : d[18][0]['text'],
                'last_network' : d[19][0]['text'],
                'hotfix': str(hot_list).replace("''", '').replace("' ", '').replace("'", '').replace(",", "<br>").replace('[', '').replace(']', ''),
                'hotfix_date': str(hotdate_list).replace("''", '').replace("' ", '').replace("'", '').replace(",", "<br>").replace('[', '').replace(']', ''),
                'subnet' : d[22][0]['text'],
                'essential1': d[23][0]['text'],
                'essential2': new_user_date_index_now,
                'essential3': False,
                'essential4': d[26][0]['text'],
                'essential5': d[27][0]['text'],
                'mem_use': d[28][0]['text'],
                'disk_use': d[29][0]['text'],
                't_cpu': d[30][0]['text'],
                'security1': d[31][0]['text'],
                'security1_ver': d[32][0]['text'],
                'security2': d[33][0]['text'],
                'security2_ver': d[34][0]['text'],
                'security3': d[35][0]['text'],
                'security3_ver': d[36][0]['text'],
                'security4': d[37][0]['text'],
                'security4_ver': d[38][0]['text'],
                'security5': d[39][0]['text'],
                'security5_ver': d[40][0]['text'],
                'uuid': d[41][0]['text'],
                'multi_boot': d[42][0]['text'],
                'ext_chr': str(chr_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_chr_ver': str(chr_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_edg': str(edg_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_edg_ver': str(edg_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_fir': str(fir_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_fir_ver': str(fir_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'logged_name_id': logged_name_id,
                'user_date': new_user_date,
            }
            xfactor_common, created = Xfactor_Common.objects.update_or_create(computer_id=computer_id, defaults=defaults)
            # xfactor_common.save()
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning('정시 미닛틀리 error' + str(e))
        print(e)
    return HttpResponse("Data saved successfully!")
        # xfactor_user = XFactor_User(
        # computer_id = d[0][0]['text'],
        # computer_name = d[1][0]['text'],
        # ip_address = d[2][0]['text'],
        # mac_address = d[3][0]['text'],
        # chasisstype = d[4][0]['text'],
        # os_simple = d[5][0]['text'],
        # os_total = d[6][0]['text'],
        # os_version = d[7][0]['text'],
        # os_build = d[8][0]['text'],
        # hw_list = d[9][0]['text'],
        # sw_list = d[10][0]['text'])
        # xfactor_user.save()

# def plug_in_service(data):
#
#     # 현재 시간대 객체 생성, 예시: "Asia/Seoul"
#     local_tz = pytz.timezone('Asia/Seoul')
#     # UTC 시간대를 사용하여 현재 시간을 얻음
#     utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
#     # 현재 시간대로 시간 변환
#     now = utc_now.astimezone(local_tz)
#     #now = now.replace(minute=0, second=0, microsecond=0)
#     proc_data = PROC(data)
#     for d in proc_data:
#         computer_id = d[0][0]['text']
#         try:
#             common_id = Xfactor_Common.objects.get(computer_id=computer_id)
#         except Exception as e:
#             print(computer_id)
#             print(e)
#             print("미닛틀리 예외발생")
#             continue  # 다음 for문으로 넘어감
#         defaults = {
#             'essential1': d[1][0]['text'],
#             'essential2': d[2][0]['text'],
#             'essential3': d[3][0]['text'],
#             'essential4': d[4][0]['text'],
#             'essential5': d[5][0]['text'],
#             'subnet': d[6][0]['text'],
#             'mem_use': d[7][0]['text'],
#             'disk_use': d[8][0]['text'],
#             't_cpu': d[9][0]['text'],
#             'user_date': now
#         }
#         computer_id = common_id.computer_id
#         xfactor_service, created = Xfactor_Service.objects.update_or_create(computer_id=computer_id, defaults=defaults)
#     return HttpResponse("Data saved successfully!")


def plug_in_purchase(data):
    # 현재 시간대 객체 생성, 예시: "Asia/Seoul"
    local_tz = pytz.timezone('Asia/Seoul')
    # UTC 시간대를 사용하여 현재 시간을 얻음
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    # 현재 시간대로 시간 변환
    now = utc_now.astimezone(local_tz)
    #now = now.replace(minute=0, second=0, microsecond=0)
    proc_data = PROC(data)
    for d in proc_data:
        computer_id = d[0][0]['text']
        try:
            common_id = Xfactor_Common.objects.get(computer_id=computer_id)
        except Exception as e:
            print(computer_id)
            print(e)
            print("미닛틀리 예외발생")
            continue  # 다음 for문으로 넘어감
        defaults = {
            'mem_use': d[1][0]['text'],
            'disk_use': d[2][0]['text'],
            'user_date': now
        }
        computer_id = common_id.computer_id
        xfactor_purchase, created = Xfactor_Purchase.objects.update_or_create(computer_id=computer_id, defaults=defaults)
    return HttpResponse("Data saved successfully!")


def plug_in_security(data):
    # 현재 시간대 객체 생성, 예시: "Asia/Seoul"
    local_tz = pytz.timezone('Asia/Seoul')
    # UTC 시간대를 사용하여 현재 시간을 얻음
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    # 현재 시간대로 시간 변환
    now = utc_now.astimezone(local_tz)
    #now = now.replace(minute=0, second=0, microsecond=0)
    proc_data = PROC(data)
    for d in proc_data:
        chr_list = []
        chr_ver_list = []
        edg_list = []
        edg_ver_list = []
        fir_list = []
        fir_ver_list = []
        computer_id = d[0][0]['text']
        try:
            common_id = Xfactor_Common.objects.get(computer_id=computer_id)

        except Exception as e:
            print(computer_id)
            print(e)
            print("미닛틀리 예외발생")
            continue  # 다음 for문으로 넘어감
        for c in range(len(d[15])):
            chr_list.append(d[15][c]['text'])
            chr_ver_list.append(d[16][c]['text'])
        for e in range(len(d[17])):
            edg_list.append(d[17][e]['text'])
            edg_ver_list.append(d[18][e]['text'])
        for f in range(len(d[19])):
            fir_list.append(d[19][f]['text'])
            fir_ver_list.append(d[20][f]['text'])
        defaults = {
            'security1': d[1][0]['text'],
            'security1_ver': d[2][0]['text'],
            'security2': d[3][0]['text'],
            'security2_ver': d[4][0]['text'],
            'security3': d[5][0]['text'],
            'security3_ver': d[6][0]['text'],
            'security4': d[7][0]['text'],
            'security4_ver': d[8][0]['text'],
            'security5': d[9][0]['text'],
            'security5_ver': d[10][0]['text'],
            'uuid': d[11][0]['text'],
            'multi_boot': d[12][0]['text'],
            'first_network': d[13][0]['text'],
            'last_boot': d[14][0]['text'],
            'ext_chr': str(chr_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
            'ext_chr_ver': str(chr_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
            'ext_edg': str(edg_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
            'ext_edg_ver': str(edg_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
            'ext_fir': str(fir_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
            'ext_fir_ver': str(fir_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
            'user_date': now
        }
        computer_id = common_id.computer_id
        xfactor_security, created = Xfactor_Security.objects.update_or_create(computer_id=computer_id, defaults=defaults)
        # xfactor_security, created = Xfactor_Security.objects.update_or_create(computer=common_id,  **defaults)
        # xfactor_security = Xfactor_Security.objects.create(computer=common_id, **defaults)
        # xfactor_security.save()
    return HttpResponse("Data saved successfully!")



def plug_in_daily(data):
    try:
        proc_data = PROC(data)
        for d in proc_data:
            #hw_list = []
            sw_list = []
            sw_ver_list = []
            sw_ver_install_list = []
            sw_ver_lastrun_list = []
            hot_list = []
            hotdate_list = []
            chr_list = []
            chr_ver_list = []
            edg_list = []
            edg_ver_list = []
            fir_list = []
            fir_ver_list = []

            logged_name_id = d[49][0]['text'].replace('NC-KOREA\\','')
            try:
                logged_name_id = Xfactor_ncdb.objects.get(userId=logged_name_id)
            except Exception as e:
                #logged_name_id = d[49][0]['text'].replace('NC-KOREA\\', '')
                logged_name_id = None

            # 현재 시간대 객체 생성, 예시: "Asia/Seoul"
            local_tz = pytz.timezone('Asia/Seoul')
            # UTC 시간대를 사용하여 현재 시간을 얻음
            utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
            # 현재 시간대로 시간 변환
            now = utc_now.astimezone(local_tz)
            now = now.replace(minute=10, second=0, microsecond=0)
            #print(now)
            for s in range(len(d[14])):
                sw_list.append(d[14][s]['text'])
                sw_ver_list.append(d[15][s]['text'])
                sw_ver_install_list.append(d[16][s]['text'])
                sw_ver_lastrun_list.append(d[17][s]['text'])
            for i in range(len(d[20])):
                hot_list.append(d[20][i]['text'])
                hotdate_list.append(d[21][i]['text'])
            for c in range(len(d[43])):
                chr_list.append(d[43][c]['text'])
                chr_ver_list.append(d[44][c]['text'])
            for e in range(len(d[45])):
                edg_list.append(d[45][e]['text'])
                edg_ver_list.append(d[46][e]['text'])
            for f in range(len(d[47])):
                fir_list.append(d[47][f]['text'])
                fir_ver_list.append(d[48][f]['text'])
            # xfactor_user = Xfactor_Common()
            # xfactor_user_log = Xfactor_Common_log()
            computer_id = d[0][0]['text']
            defaults = {
                'computer_name': d[1][0]['text'],
                'ip_address': d[2][0]['text'],
                'mac_address': d[3][0]['text'],
                'chassistype': d[4][0]['text'],
                'os_simple': d[5][0]['text'],
                'os_total': d[6][0]['text'].replace('Microsoft ', ''),
                'os_version': d[7][0]['text'],
                'os_build': d[8][0]['text'],
                'hw_cpu' : d[9][0]['text'],
                'hw_ram' : d[10][0]['text'],
                'hw_mb' : d[11][0]['text'],
                'hw_disk' : d[12][0]['text'],
                'hw_gpu' : d[13][0]['text'],
                'sw_list': str(sw_list).replace('"','').replace('!','<br>').replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_ver_list': str(sw_ver_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_install' : str(sw_ver_install_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_lastrun' : str(sw_ver_lastrun_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'first_network' : d[18][0]['text'],
                'last_network' : d[19][0]['text'],
                'hotfix': str(hot_list).replace("''", '').replace("' ", '').replace("'", '').replace(",", "<br>").replace('[', '').replace(']', ''),
                'hotfix_date': str(hotdate_list).replace("''", '').replace("' ", '').replace("'", '').replace(",", "<br>").replace('[', '').replace(']', ''),
                'subnet' : d[22][0]['text'],
                'essential1': d[23][0]['text'],
                'essential2': d[24][0]['text'],
                'essential3': d[25][0]['text'],
                'essential4': d[26][0]['text'],
                'essential5': d[27][0]['text'],
                'mem_use': d[28][0]['text'],
                'disk_use': d[29][0]['text'],
                't_cpu': d[30][0]['text'],
                'security1': d[31][0]['text'],
                'security1_ver': d[32][0]['text'],
                'security2': d[33][0]['text'],
                'security2_ver': d[34][0]['text'],
                'security3': d[35][0]['text'],
                'security3_ver': d[36][0]['text'],
                'security4': d[37][0]['text'],
                'security4_ver': d[38][0]['text'],
                'security5': d[39][0]['text'],
                'security5_ver': d[40][0]['text'],
                'uuid': d[41][0]['text'],
                'multi_boot': d[42][0]['text'],
                'ext_chr': str(chr_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_chr_ver': str(chr_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_edg': str(edg_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_edg_ver': str(edg_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_fir': str(fir_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_fir_ver': str(fir_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'logged_name_id': logged_name_id,
                'user_date': now
            }
            xfactor_common_log = Xfactor_Daily.objects.create(computer_id=computer_id, **defaults)
            xfactor_common_log.save()
    except Exception as e:
        logger.warning('정시 데일리 error' + str(e))
        print(d)
        print(e)
    return HttpResponse("Data saved successfully!")

def cache():
    if Xfactor_Common.objects.exists():
        common_objects = Xfactor_Common.objects.all()
        local_tz = pytz.timezone('Asia/Seoul')
        # UTC 시간대를 사용하여 현재 시간을 얻음
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        # 현재 시간대로 시간 변환
        now = utc_now.astimezone(local_tz)
        index_now = now.strftime('%Y-%m-%d-%H')
        for common in common_objects:
            try:
                # Xfactor_Common 객체와 동일한 필드 값을 가진 Xfactor_Common_Cache 객체를 생성합니다.
                cache = Xfactor_Common_Cache(
                    computer_id=common.computer_id,
                    computer_name=common.computer_name,
                    ip_address=common.ip_address,
                    mac_address=common.mac_address,
                    chassistype=common.chassistype,
                    os_simple=common.os_simple,
                    os_total=common.os_total,
                    os_version=common.os_version,
                    os_build=common.os_build,
                    hw_cpu=common.hw_cpu,
                    hw_ram=common.hw_ram,
                    hw_mb=common.hw_mb,
                    hw_disk=common.hw_disk,
                    hw_gpu=common.hw_gpu,
                    sw_list=common.sw_list,
                    sw_ver_list=common.sw_ver_list,
                    sw_install=common.sw_install,
                    sw_lastrun=common.sw_lastrun,
                    first_network=common.first_network,
                    last_network=common.last_network,
                    hotfix=common.hotfix,
                    hotfix_date=common.hotfix_date,
                    subnet=common.subnet,
                    memo=common.memo,
                    essential1=common.essential1,
                    essential2=index_now,
                    essential3=common.essential3,
                    essential4=common.essential4,
                    essential5=common.essential5,
                    mem_use=common.mem_use,
                    disk_use=common.disk_use,
                    t_cpu=common.t_cpu,
                    security1=common.security1,
                    security1_ver=common.security1_ver,
                    security2=common.security2,
                    security2_ver=common.security2_ver,
                    security3=common.security3,
                    security3_ver=common.security3_ver,
                    security4=common.security4,
                    security4_ver=common.security4_ver,
                    security5=common.security5,
                    security5_ver=common.security5_ver,
                    uuid=common.uuid,
                    multi_boot=common.multi_boot,
                    ext_chr=common.ext_chr,
                    ext_chr_ver=common.ext_chr_ver,
                    ext_edg=common.ext_edg,
                    ext_edg_ver=common.ext_edg_ver,
                    ext_fir=common.ext_fir,
                    ext_fir_ver=common.ext_fir_ver,
                    logged_name_id=common.logged_name_id,
                    cache_date=common.user_date,
                    user_date=timezone.now()
                )
                # Xfactor_Common_Cache 객체를 데이터베이스에 저장합니다.
                cache.save()
            except Exception as e:
                logger.warning('정시 캐시 error' + str(e))
                # Xfactor_Common 객체가 존재하지 않는 경우, 빈 필드를 가진 Xfactor_Common_Cache 객체를 생성합니다.
                #cache = Xfactor_Common_Cache()
                #cache.save()
                continue
    print("cache success")


# def plug_in_discover():
#     with open("setting.json", encoding="UTF-8") as f:
#         SETTING = json.loads(f.read())
#     Mail_Id = SETTING['PROJECT']['MAIL']['ID']
#     Mail_Pw = SETTING['PROJECT']['MAIL']['PW']
#
#
#     local_tz = pytz.timezone('Asia/Seoul')
#     today = timezone.now().astimezone(local_tz)
#     today_150_ago = today - timedelta(days=10)
#     today_180_ago = today_150_ago - timedelta(days=10)
#     #전체 mac_address 구하기
#     all_mac_addresses = set(Xfactor_Common.objects.filter(user_date__gte=today_150_ago).values_list('mac_address', flat=True))
#
#     discover_asset = Xfactor_Common.objects.filter(
#         Q(user_date__gte=today_180_ago) & Q(user_date__lte=today_150_ago)
#     )
#     #discover_asset = discover_asset
#     manager_id = Mail_Id
#     manager_pw = Mail_Pw
#
#     for d in discover_asset:
#         to_email = d.logged_name_id.email
#         user_id = d.logged_name_id.userId
#         user_name = d.logged_name_id.userName
#         mac_address = d.mac_address
#         ip_address = d.ip_address
#         computer_name = d.computer_name
#
#         msg = MIMEMultipart()
#         msg['From'] = manager_id
#         msg['To'] = to_email
#         msg['Subject'] = "장기 미접속 자산 알람"
#         days_since_first_date = (today - d.user_date).days
#         #print(days_since_first_date)
#         if days_since_first_date in (150, 165, 172, 176, 179,19,17,16,15,14,13,12,11) :
#             try:
#                 if mac_address in all_mac_addresses:
#                     #print(f"이 자산은 중복됨 {mac_address}")
#                     continue
#                 # print(user_id)
#                 # print(days_since_first_date)
#                 # print(to_email)
#                 # print("-----------------------------")
#
#
#                 body = ""
#                 body += "<font face='Malgun Gothic' size='4'>안녕하세요.</font><br>"
#                 body += "<font face='Malgun Gothic' size='4'>"
#                 body += f"{user_name}님의 장비가 장기간 네트워크 연결이 안되고 있어 안내메일 드립니다.<br>"
#                 body += "180일동안 네트워크 연결이 없으면 (외부인터넷 포함) 장비등록이 풀려 재택근무에 사용을 할 수 없습니다.<br>"
#                 body += "재등록 과정을 거쳐야하는 불편이 있을 수 있으니<br>"
#                 body += "180일이 지나기전에 네트워크에 접속하여 기기 상태를 확인해주세요.<br><br>"
#
#                 # HTML 테이블 생성
#                 body += "<table border='1' cellpadding='5'>"
#                 body += "<tr><th>항목</th><th>내용</th></tr>"
#                 body += f"<tr><td>사용자계정</td><td>{user_id}</td></tr>"
#                 body += f"<tr><td>장비명</td><td>{computer_name}</td></tr>"
#                 body += f"<tr><td>IP주소</td><td>{ip_address}</td></tr>"
#                 body += f"<tr><td>미사용일수</td><td>{days_since_first_date}일</td></tr>"
#                 body += "</table>"
#
#                 body += "</font><br><font face='Malgun Gothic' size='4'>문의사항은 스마트워크 DL로 부탁드립니다.</font>"
#                 body += "</font><br><font face='Malgun Gothic' size='4'>감사합니다.</font>"
#                 msg.attach(MIMEText(body, 'html'))
#
#                 server = smtplib.SMTP('smtp.office365.com', 587)
#                 server.starttls()
#                 server.login(msg['From'], manager_pw)  # 이메일 계정 비밀번호
#                 server.send_message(msg)
#                 server.quit()
#                 print(f"메일이 성공적으로 발송되었습니다: {to_email}")
#
#             except Exception as e:
#                 #print(f"메일 발송 실패 : {e}")
#                 logger.warning(f"메일 발송 실패 {to_email}: {e}")

def plug_in_online(data):
    try:
        Xfactor_Common.objects.update(essential3=False)
        #proc_data = PROC(data)
        proc_data = data
        computer_id_list = []
        for d in proc_data:
            computer_id = d[0][0]['text']
            if computer_id == 'unconfirmed':
                print("unconfirmed")
                pass
            elif computer_id == None:
                print("None")
                pass
            elif computer_id == '':
                print("whitespace")
                pass
            Xfactor_Common.objects.filter(computer_id=computer_id).update(essential3=True)

    # 위에꺼안되면이걸로 변경할 것
    # try:
    #     Xfactor_Common.objects.update(essential3=False)
    #     proc_data = PROC(data)
    #     computer_id_list = []
    #     for d in proc_data:
    #         computer_id = d[0][0]['text']
    #         Xfactor_Common.objects.filter(computer_id=computer_id).update(essential3=True)

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning('Online error' + str(e))
        print(e)
    return HttpResponse("Data saved successfully!")







###NC용 메일발송기능
def plug_in_discover():
    with open("setting.json", encoding="UTF-8") as f:
        SETTING = json.loads(f.read())
    Mail_Id = SETTING['PROJECT']['MAIL']['ID']
    Mail_Pw = SETTING['PROJECT']['MAIL']['PW']

    local_tz = pytz.timezone('Asia/Seoul')
    today = timezone.now().astimezone(local_tz)
    discover_current = Daily_Statistics_log.objects.filter(item='discover_module').order_by('-statistics_collection_date').values_list('item_count', flat=True).first()

    # 메일링 테스트
    # discover_current =30

    today_150_ago = today - timedelta(days=discover_current)
    today_180_ago = today_150_ago - timedelta(days=30)

    # 전체 mac_address 구하기
    all_mac_addresses = set(Xfactor_Common.objects.filter(user_date__gte=today_150_ago).values_list('mac_address', flat=True))

    discover_asset = Xfactor_Common.objects.filter(
        Q(user_date__gte=today_180_ago) & Q(user_date__lte=today_150_ago)
    ).exclude(os_simple='Mac')
    # discover_asset = discover_asset
    # manager_id = Mail_Id
    manager_id = 'smartwork@ncsoft.com'
    manager_pw = Mail_Pw
    print(discover_asset)
    for d in discover_asset:
        to_email = d.logged_name_id.email
        # to_email = 'handlake2k@ncsoft.com'
        user_id = d.logged_name_id.userId
        user_name = d.logged_name_id.userName
        mac_address = d.mac_address
        ip_address = d.ip_address
        computer_name = d.computer_name

        msg = MIMEMultipart()
        msg['From'] = manager_id
        msg['To'] = to_email
        msg['Subject'] = "장기 미접속 자산 알람"
        days_since_first_date = (today - d.user_date).days

        if days_since_first_date in (discover_current, discover_current + 15, discover_current + 22, discover_current + 26, discover_current + 29):
            try:
                if mac_address in all_mac_addresses:
                    # print(f"이 자산은 중복됨 {mac_address}")
                    continue
                # print(user_id)
                # print(days_since_first_date)
                # print(to_email)
                # print("-----------------------------")

                # body = f"{user_id}을 사용하는 컴퓨터가 미관리중입니다. 컴퓨터를 체크해 주시길 바랍니다."
                body = ""
                body += "<font face='Malgun Gothic' size='4'>안녕하세요.</font><br>"
                body += "<font face='Malgun Gothic' size='4'>"
                body += f"{user_name}님의 장비가 장기 미접속 자산으로 분류될 수 있어 안내메일 드립니다.<br><br>"
                body += "*장기 미접속 자산이란?<br>"
                body += "180일동안 Office 365의 어떠한 서비스도 이용하지 않으면 장기미접속 자산으로 분류됩니다.<br>"
                body += "장기미접속 자산으로 분류되면 재택근무에 사용을 할 수 없습니다.<br>"
                body += "재택근무에 사용하기 위해서는 기기 재등록이 필요하게 되므로<br>"
                body += "180일이 지나기전에 o365 서비스에 접속해주세요.(아웃룩, 팀즈등)<br><br>"
                body += "180일이 지나서 기기재등록이 필요하면 아래 Link를 참고해주세요.<br>"
                body += "<기기등록 및 삭제방법> https://helpit.ncsoft.com/board/guide/36<br>"
                body += "<br>"

                # HTML 테이블 생성
                body += "<장기미접속 PC정보>"
                body += "<table border='1' cellpadding='5'>"
                body += "<tr><th>항목</th><th>내용</th></tr>"
                body += f"<tr><td>사용자계정</td><td>{user_id}</td></tr>"
                body += f"<tr><td>장비명</td><td>{computer_name}</td></tr>"
                body += f"<tr><td>IP주소</td><td>{ip_address}</td></tr>"
                body += f"<tr><td>미사용일수</td><td>{days_since_first_date}일</td></tr>"
                body += "</table>"

                body += "</font><br><font face='Malgun Gothic' size='4'>문의사항은 스마트워크 DL로 부탁드립니다.</font>"
                body += "</font><br><font face='Malgun Gothic' size='4'>감사합니다.</font>"
                msg.attach(MIMEText(body, 'html'))

                # server = smtplib.SMTP('smtp.office365.com', 587)
                # server.starttls()
                # server.login(msg['From'], manager_pw)  # 이메일 계정 비밀번호
                # server.send_message(msg)

                server = smtplib.SMTP('172.20.0.126', 25)
                server.sendmail(msg['From'], to_email, msg.as_string())
                server.quit()
                print(f"메일이 성공적으로 발송되었습니다: {to_email}")

            except Exception as e:
                # print(f"메일 발송 실패 : {e}")
                logger.warning(f"메일 발송 실패 {to_email}: {e}")


def plug_in_raw(data):
    a = 0
    try:
        with open("setting.json", encoding="UTF-8") as f:
            SETTING = json.loads(f.read())
        HOST = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['HOST']
        USER = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['USER']
        PWD = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['PWD']
        DATABASE = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['NAME']

        config = {
            'host': HOST,
            'user': USER,
            'password': PWD,
            'database': NAME
        }
        #print(data)
        # Xfactor_Service.objects.all().delete()
        # Xfactor_Purchase.objects.all().delete()
        # Xfactor_Security.objects.all().delete()
        # Xfactor_Common.objects.all().delete()
        #proc_data = PROC(data)
        for d in data:
            #hw_list = []
            sw_list = []
            sw_ver_list = []
            sw_ver_install_list = []
            sw_ver_lastrun_list = []
            hot_list = []
            hotdate_list = []
            chr_list = []
            chr_ver_list = []
            edg_list = []
            edg_ver_list = []
            fir_list = []
            fir_ver_list = []

            logged_name_id = d[49][0]['text'].replace('NC-KOREA\\','')
            # try:
            #     logged_name_id = Xfactor_ncdb.objects.get(userId=logged_name_id)
            # except Exception as e:
            #     custom_object = Xfactor_ncdb()
            #     custom_object.userId = logged_name_id
            #     custom_object.save()
            #     logged_name_id = Xfactor_ncdb.objects.get(userId=logged_name_id)

            # 현재 시간대 객체 생성, 예시: "Asia/Seoul"
            local_tz = pytz.timezone('Asia/Seoul')
            # UTC 시간대를 사용하여 현재 시간을 얻음
            utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
            # 현재 시간대로 시간 변환
            now = utc_now.astimezone(local_tz)
            index_now = now.strftime('%Y-%m-%d-%H')
            computer_id = ''
            tds_computer_id = d[0][0]['text']
            node_computer_id = d[-2][0]['text']

            #computer_id = node_computer_id

            if tds_computer_id not in ['']:
                computer_id = tds_computer_id
            elif node_computer_id not in ['']:
                computer_id = node_computer_id
            else:
                computer_id = 'Error'

            new_user_date_str = ''
            last_seen_data = d[-1][0]['text']
            last_registration_time = d[-3][0]['text']
            if last_seen_data not in ['', None]:
                new_user_date_str = last_seen_data
            elif last_registration_time not in ['[no results]', '', None]:
                new_user_date_str = last_registration_time + 'Z'
            else:
                new_user_date_str = 'Error'
            #print(a)
            # print(last_seen_data, last_registration_time)
            #new_user_date = datetime.strptime(new_user_date_str, '%Y-%m-%dT%H:%M:%SZ')
            #new_user_date = new_user_date.astimezone(local_tz)
            #new_user_date_index_now = new_user_date.strftime('%Y-%m-%d-%H')
            #print(index_now)
            # for h in range(len(d[9])):
            #     hw_list.append(d[9][h]['text'])
            for s in range(len(d[14])):
                sw_list.append(d[14][s]['text'])
                sw_ver_list.append(d[15][s]['text'])
                sw_ver_install_list.append(d[16][s]['text'])
                sw_ver_lastrun_list.append(d[17][s]['text'])
            for i in range(len(d[20])):
                hot_list.append(d[20][i]['text'])
                hotdate_list.append(d[21][i]['text'])
            for c in range(len(d[43])):
                chr_list.append(d[43][c]['text'])
                chr_ver_list.append(d[44][c]['text'])
            for e in range(len(d[45])):
                edg_list.append(d[45][e]['text'])
                edg_ver_list.append(d[46][e]['text'])
            for f in range(len(d[47])):
                fir_list.append(d[47][f]['text'])
                fir_ver_list.append(d[48][f]['text'])
            # xfactor_user = Xfactor_Common()
            # xfactor_user_log = Xfactor_Common_log()
            defaults = {
                'computer_id': computer_id,
                'computer_name': d[1][0]['text'],
                'ip_address': d[2][0]['text'],
                'mac_address': d[3][0]['text'],
                'chassistype': d[4][0]['text'],
                'os_simple': d[5][0]['text'],
                'os_total': d[6][0]['text'].replace('Microsoft ', ''),
                'os_version': d[7][0]['text'],
                'os_build': d[8][0]['text'],
                'hw_cpu' : d[9][0]['text'],
                'hw_ram' : d[10][0]['text'],
                'hw_mb' : d[11][0]['text'],
                'hw_disk' : d[12][0]['text'],
                'hw_gpu' : d[13][0]['text'],
                #'hw_list': str(hw_list).replace('"','').replace(",","<br>").replace('\'','').replace('[','').replace(']',''),
                'sw_list': str(sw_list).replace('"','').replace('!','<br>').replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_ver_list': str(sw_ver_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_install' : str(sw_ver_install_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'sw_lastrun' : str(sw_ver_lastrun_list).replace("!","<br>").replace('\'','').replace('[','').replace(']','').replace(', ',''),
                'first_network' : d[18][0]['text'],
                'last_network' : d[19][0]['text'],
                'hotfix': str(hot_list).replace("''", '').replace("' ", '').replace("'", '').replace(",", "<br>").replace('[', '').replace(']', ''),
                'hotfix_date': str(hotdate_list).replace("''", '').replace("' ", '').replace("'", '').replace(",", "<br>").replace('[', '').replace(']', ''),
                'subnet' : d[22][0]['text'],
                'essential1': d[23][0]['text'],
                'essential2': now,
                'essential3': False,
                'essential4': d[26][0]['text'],
                'essential5': d[27][0]['text'],
                'mem_use': d[28][0]['text'],
                'disk_use': d[29][0]['text'],
                't_cpu': d[30][0]['text'],
                'security1': d[31][0]['text'],
                'security1_ver': d[32][0]['text'],
                'security2': d[33][0]['text'],
                'security2_ver': d[34][0]['text'],
                'security3': d[35][0]['text'],
                'security3_ver': d[36][0]['text'],
                'security4': d[37][0]['text'],
                'security4_ver': d[38][0]['text'],
                'security5': d[39][0]['text'],
                'security5_ver': d[40][0]['text'],
                'uuid': d[41][0]['text'],
                'multi_boot': d[42][0]['text'],
                'ext_chr': str(chr_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_chr_ver': str(chr_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_edg': str(edg_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_edg_ver': str(edg_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_fir': str(fir_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'ext_fir_ver': str(fir_ver_list).replace("['', '", '').replace(", '', ", "<br>").replace("''", '').replace("' ", '').replace("'", '').replace(", ", "<br>").replace('[', '').replace(']', ''),
                'logged_name': logged_name_id,
                'user_date': new_user_date_str,
            }
            #factor_common, created = Xfactor_Common.objects.update_or_create(computer_id=computer_id, defaults=defaults)
            # xfactor_common.save()
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            sql = """
                INSERT INTO common_xfactor_raw_common (
                    computer_id, computer_name, ip_address, mac_address, chassistype, os_simple, os_total, os_version, os_build,
                    hw_cpu, hw_ram, hw_mb, hw_disk, hw_gpu, sw_list, sw_ver_list, sw_install, sw_lastrun,
                    first_network, last_network, hotfix, hotfix_date, subnet, essential1, essential2, essential3,
                    essential4, essential5, mem_use, disk_use, t_cpu, security1, security1_ver, security2,
                    security2_ver, security3, security3_ver, security4, security4_ver, security5, security5_ver,
                    uuid, multi_boot, ext_chr, ext_chr_ver, ext_edg, ext_edg_ver, ext_fir, ext_fir_ver,
                    logged_name, user_date
                ) VALUES (
                    %(computer_id)s ,%(computer_name)s, %(ip_address)s, %(mac_address)s, %(chassistype)s, %(os_simple)s, %(os_total)s,
                    %(os_version)s, %(os_build)s, %(hw_cpu)s, %(hw_ram)s, %(hw_mb)s, %(hw_disk)s, %(hw_gpu)s,
                    %(sw_list)s, %(sw_ver_list)s, %(sw_install)s, %(sw_lastrun)s, %(first_network)s, %(last_network)s,
                    %(hotfix)s, %(hotfix_date)s, %(subnet)s, %(essential1)s, %(essential2)s, %(essential3)s,
                    %(essential4)s, %(essential5)s, %(mem_use)s, %(disk_use)s, %(t_cpu)s, %(security1)s, %(security1_ver)s,
                    %(security2)s, %(security2_ver)s, %(security3)s, %(security3_ver)s, %(security4)s, %(security4_ver)s,
                    %(security5)s, %(security5_ver)s, %(uuid)s, %(multi_boot)s, %(ext_chr)s, %(ext_chr_ver)s, %(ext_edg)s,
                    %(ext_edg_ver)s, %(ext_fir)s, %(ext_fir_ver)s, %(logged_name)s, %(user_date)s
                )
            """
            cursor.execute(sql, defaults)
            conn.commit()
            #rows = cursor.fetchone()
            #print("----------------------성공----")
        return 1
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning('로우데이터 error' + str(e))
        print(e)
    return HttpResponse("로우데이터 saved successfully!")

