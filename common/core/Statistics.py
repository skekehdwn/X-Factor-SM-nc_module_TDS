
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# import django
# django.setup()
import logging
from ..models import *
from django.db.models.functions import Cast
from django.db.models import Count, Q, F, Max, BigIntegerField
import pytz
import time
from datetime import datetime, timedelta, timezone

logger = logging.getLogger()

#구분데이터 통계
def Minutely_statistics() :
    try:
        Daily_Statistics.objects.all().delete()
        local_tz = pytz.timezone('Asia/Seoul')
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        now = utc_now.astimezone(local_tz)
        time = now - timedelta(minutes=60)

        user = Xfactor_Common.objects.filter(user_date__gte=time)
        #service = Xfactor_Service.objects.filter(user_date__gte=time)
        #user = Xfactor_Common.objects.exclude(computer_id='unconfirmed').filter(user_date__gte=time)
        users = user.values('chassistype').annotate(count=Count('chassistype'))
        for user_data in users:
            classification = 'chassis_type'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['chassistype']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        #os_type OS종류
        users = user.values('os_simple').annotate(count=Count('os_simple'))
        #print(users)
        for user_data in users:
            classification = 'os_simple'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        # 일주일전 캐시데이터 조회 값
        seven_days_ago = now - timedelta(days=7)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)

        # chassis_type_cache 캐시 섀시타입
        users = user_cache.values('chassistype').annotate(count=Count('chassistype'))
        for user_data in users:
            classification = 'chassis_type_cache'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['chassistype']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()


        #os_type_cache 캐시 OS종류
        users = user_cache.values('os_simple').annotate(count=Count('os_simple'))
        #print(users)
        for user_data in users:
            classification = 'os_simple_cache'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()


        #win_ver 윈도우버전
        users = user.filter(Q(os_simple='Windows')).values('os_total').annotate(count=Count('os_total'))
        for user_data in users:
            classification = 'win_os_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_total']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        #subnet 대역별
        users = user.values('subnet').annotate(count=Count('subnet'))
        inCount = 0
        outCount = 0
        vCount = 0
        for user_data in users:
            if user_data['subnet'] in ['172.18.16.0/21', '172.18.24.0/21',  '172.18.32.0/22', '172.18.40.0/22', '172.18.48.0/21', '172.18.56.0/22', '172.18.64.0/21', '172.18.72.0/22'\
                , '172.18.88.0/21', '172.18.96.0/21', '172.18.104.0/22', '172.20.16.0/21', '172.20.40.0/22', '172.20.48.0/21', '172.20.56.0/21', '172.20.64.0/22', '172.20.68.0/22', '172.20.78.0/23', '172.20.8.0/21', '사내망']:
                inCount += user_data['count']
            elif user_data['subnet'] in ['172.21.224.0/20', 'VPN']:
                vCount += user_data['count']
            else :
                outCount += user_data['count']
        daily_statistics, created = Daily_Statistics.objects.get_or_create(
            classification='subnet',
            item='사내망',
            defaults={'item_count': inCount}
        )
        daily_statistics.save()

        daily_statistics, created = Daily_Statistics.objects.get_or_create(
            classification='subnet',
            item='VPN',
            defaults={'item_count': vCount}
        )
        daily_statistics.save()

        daily_statistics, created = Daily_Statistics.objects.get_or_create(
            classification='subnet',
            item='외부망',
            defaults={'item_count': outCount}
        )
        daily_statistics.save()

        # 보안패치 필요여부 모듈
        nec_item = 0
        unnec_item = 0
        uncon_item = 0
        three_months_ago = datetime.now() - timedelta(days=90)
        user = Xfactor_Common.objects.filter(user_date__gte=time, os_simple='Windows')
        users = user.values('hotfix_date')
        for patch_user in users:
            date_strings = patch_user['hotfix_date'].split('<br> ')
            date_objects = []
            for date_str in date_strings:
                try:
                    date_obj = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
                    date_objects.append(date_obj)
                except ValueError:
                    continue
            if date_objects:
                latest_date = max(date_objects)

                if latest_date < three_months_ago:
                    nec_item += 1
                    # print(latest_date)
                elif latest_date >= three_months_ago:
                    unnec_item += 1
                    # print(latest_date)
                else:
                    uncon_item += 1

        classification = 'hotfix'
        item_nec = "보안패치 필요"
        item_unnec = "보안패치 불필요"
        item_uncon = "unconfirmed"
        hotfix_unnecessery, created = Daily_Statistics.objects.get_or_create(
            classification=classification,
            item=item_unnec,
            defaults={'item_count': unnec_item}
        )
        hotfix_unnecessery.save()

        hotfix_necessery, created = Daily_Statistics.objects.get_or_create(
            classification=classification,
            item=item_nec,
            defaults={'item_count': nec_item}
        )
        hotfix_necessery.save()

        hotfix_unconfirmed, created = Daily_Statistics.objects.get_or_create(
            classification=classification,
            item=item_uncon,
            defaults={'item_count': uncon_item}
        )
        hotfix_unconfirmed.save()


        #미관리 제외 나머지 자산
        date_150_days_ago = now - timedelta(days=150)
        cover_user=Xfactor_Common.objects.filter(user_date__gte=date_150_days_ago)
        count = cover_user.count()
        classification = 'discover'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = '접속 자산'
        item_count = count
        daily_statistics, created = Daily_Statistics.objects.get_or_create(
            classification=classification,
            item=item,
            defaults={'item_count': item_count}
        )
        daily_statistics.save()


        #150일 미관리자산
        date_150_days_ago = now - timedelta(days=150)
        discover_user=Xfactor_Common.objects.filter(user_date__lt=date_150_days_ago)
        count = discover_user.count()
        classification = 'discover'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = '장기 미접속 자산'
        item_count = count
        daily_statistics, created = Daily_Statistics.objects.get_or_create(
            classification=classification,
            item=item,
            defaults={'item_count': item_count}
        )
        daily_statistics.save()

        #Office 버전별 통계
        user = Xfactor_Common.objects.filter(user_date__gte=time)
        service_user = user.values('essential5').annotate(count=Count('essential5'))
        for user_data in service_user:
            classification = None  # 초기값 설정
            if user_data['essential5'].startswith('Office'):
                if user_data['essential5'].startswith('Office 365'):
                    classification = 'office_ver_365'
                else :
                    classification = 'office_ver'
            else:
                #print("aa")
                classification = 'office_ver_mac'
            #classification = 'office_ver'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['essential5']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        # cpu 사용량
        services = user.values('t_cpu').annotate(count=Count('t_cpu'))
        for service_data in services:
            classification = 't_cpu'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = service_data['t_cpu']
            item_count = service_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        # os버전별 자산 현황
        user = Xfactor_Common.objects.filter(user_date__gte=time)
        users = user.filter(Q(os_simple='Windows')).values('os_total', 'os_build').annotate(count=Count('os_simple')).order_by('-count')[:6]
        #print(users)
        for user_data in users:
            classification = 'win_os_build'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            if user_data['os_total'] == 'unconfirmed':
                continue
            else:
                item = user_data['os_total'] + ' ' + user_data['os_build']
                item_count = user_data['count']
                daily_statistics, created = Daily_Statistics.objects.get_or_create(
                    classification=classification,
                    item=item,
                    defaults={'item_count': item_count}
                )
            daily_statistics.save()

        # 업데이트 필요 통계
        users = user.filter(Q(os_simple='Windows'), os_build__gte='19044').values('os_simple', 'os_build').annotate(count=Count('os_simple'))
        #print(users)
        classification = 'os_version_up'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = 'new'
        item_count = sum(item['count'] for item in users)
        daily_statistics, created = Daily_Statistics.objects.get_or_create(
            classification=classification,
            item=item,
            defaults={'item_count': item_count}
        )
        daily_statistics.save()
        # 업데이트 필요 통계
        users = user.filter(Q(os_simple='Windows'), os_build__lt='19044').values('os_simple', 'os_build').annotate(count=Count('os_simple'))
        #print(users)
        classification = 'os_version_up'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = 'old'
        item_count = sum(item['count'] for item in users)
        daily_statistics, created = Daily_Statistics.objects.get_or_create(
            classification=classification,
            item=item,
            defaults={'item_count': item_count}
        )
        daily_statistics.save()


        # online window
        user = Xfactor_Common.objects.filter(user_date__gte=time)
        users = user.filter(Q(chassistype='Notebook')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Notebook_chassis_online'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        # online mac
        user = Xfactor_Common.objects.filter(user_date__gte=time)
        users = user.filter(Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Desktop_chassis_online'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        # online other
        user = Xfactor_Common.objects.filter(user_date__gte=time)
        users = user.exclude(Q(chassistype='Notebook') | Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Other_chassis_online'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()


        # total window
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Notebook')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Notebook_chassis_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        # total mac
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Desktop_chassis_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

        # total other
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        users = user_cache.exclude(Q(chassistype='Notebook') | Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Other_chassis_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics, created = Daily_Statistics.objects.get_or_create(
                classification=classification,
                item=item,
                defaults={'item_count': item_count}
            )
            daily_statistics.save()

    except Exception as e :
        logger.warning('Minutely error' + str(e))
        logger.warning('Minutely error' + str(item))

    print("Minutely Statistics Success")



def Daily_statistics() :
    try:
        #print("daily start")
        #chassis_type 섀시타입
        #local_tz = pytz.timezone('Asia/Seoul')
        #utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        local_tz = pytz.timezone('Asia/Seoul')
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        now = utc_now.astimezone(local_tz)
        start_of_today = now.replace(minute=0, second=0, microsecond=0)
        #print(start_of_today)
        seven_days_ago = start_of_today - timedelta(days=7)
        # end_of_today = start_of_today + timedelta(days=1)

        time = now - timedelta(minutes=60)


        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)

        users = user.values('chassistype').annotate(count=Count('chassistype'))
        for user_data in users:
            classification = 'chassis_type'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['chassistype']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()
        print("os simple시작")
        #os_type OS종류
        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)
        users = user.values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'os_simple'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        #win_ver 윈도우버전
        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)
        users = user.filter(Q(os_simple='Windows')).values('os_total').annotate(count=Count('os_total'))
        for user_data in users:
            classification = 'win_os_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_total']
            item_count = user_data['count']
            daily_statistics_log= Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()
        print("대역별 시작")
        #subnet 대역별

        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)
        users = user.values('subnet').annotate(count=Count('subnet'))
        inCount = 0
        outCount = 0
        vCount = 0
        unCount = 0
        for user_data in users:
            if user_data['subnet'] in ['172.18.16.0/21', '172.18.24.0/21', '172.18.32.0/22', '172.18.40.0/22', '172.18.48.0/21', '172.18.56.0/22', '172.18.64.0/21', '172.18.72.0/22' \
                    , '172.18.88.0/21', '172.18.96.0/21', '172.18.104.0/22', '172.20.16.0/21', '172.20.40.0/22', '172.20.48.0/21', '172.20.56.0/21', '172.20.64.0/22', '172.20.68.0/22', '172.20.78.0/23', '172.20.8.0/21', '사내망']:
                inCount += user_data['count']
            elif user_data['subnet'] in ['172.21.224.0/20', 'VPN']:
                vCount += user_data['count']
            elif user_data['subnet'] in ['unconfirmed', '' , 'Other']:
                unCount += user_data['count']
            else:
                outCount += user_data['count']
        daily_statistics_log = Daily_Statistics_log(
            classification='subnet',
            item='사내망',
            item_count=inCount
        )
        daily_statistics_log.save()

        daily_statistics_log = Daily_Statistics_log(
            classification='subnet',
            item='VPN',
            item_count=vCount
        )
        daily_statistics_log.save()

        daily_statistics_log = Daily_Statistics_log(
            classification='subnet',
            item='외부망',
            item_count= outCount
        )
        daily_statistics_log.save()

        daily_statistics_log = Daily_Statistics_log(
            classification='subnet',
            item='미확인',
            item_count=unCount
        )
        daily_statistics_log.save()
        print("보안패치 시작")
        #보안패치 필요여부 모듈
        nec_item = 0
        unnec_item = 0
        hot_current = Daily_Statistics_log.objects.filter(item='hot_module').order_by('-statistics_collection_date').values_list('item_count', flat=True).first()


        three_months_ago = datetime.now() - timedelta(days=hot_current)
        users = user.values('hotfix_date')
        for user in users:
            date_strings=user['hotfix_date'].split('<br> ')
            date_objects = []
            for date_str in date_strings:
                try:
                    date_obj = datetime.strptime(date_str, '%m/%d/%Y %H:%M:%S')
                    date_objects.append(date_obj)
                except ValueError:
                    continue
            if date_objects:
                latest_date = max(date_objects)
                if latest_date < three_months_ago:
                    nec_item += 1
                else:
                    unnec_item += 1
        classification = 'hotfix'
        item_nec = "necessery"
        item_unnec = "unncessery"

        hotfix_necessery_log= Daily_Statistics_log(
            classification=classification,
            item=item_nec,
            item_count=nec_item
        )
        hotfix_necessery_log.save()

        hotfix_unnecessery_log = Daily_Statistics_log(
            classification=classification,
            item=item_unnec,
            item_count=unnec_item
        )
        hotfix_unnecessery_log.save()
        print("미관리 시작")
        # 150일 미관리 제외 전체 자산
        date_150_days_ago = start_of_today - timedelta(days=150)

        # 중복된 mac_address를 가진 레코드를 필터링합니다.
        filtered_user = Xfactor_Common.objects.values('mac_address').annotate(max_user_date=Max('user_date')).distinct()
        # 가장 최근 날짜인 레코드를 선택합니다.
        latest_records = []
        # for item in filtered_user:
        #     mac_address = item['mac_address']
        #     max_user_date = item['max_user_date']
        #     record = Xfactor_Common.objects.filter(mac_address=mac_address, user_date=max_user_date).first()
        #     if record:
        #         latest_records.append(record)
        # count = sum(1 for record in latest_records if record.user_date >= date_150_days_ago)
        count=0
        # 예전코드
        # date_150_days_ago = start_of_today - timedelta(days=7)
        # discover_user=Xfactor_Common.objects.filter(user_date__gte=date_150_days_ago)
        # count = discover_user.count()
        classification = 'discover'  # 분류 정보를 원하시는 텍스트로 변경해주세요.

        item = '150_day'
        daily_statistics_log = Daily_Statistics_log(
            classification=classification,
            item=item,
            item_count = count
        )
        daily_statistics_log.save()


        #150일 미관리자산
        discover_current = Daily_Statistics_log.objects.filter(item='discover_module').order_by('-statistics_collection_date').values_list('item_count', flat=True).first()
        date_150_days_ago = start_of_today - timedelta(days=discover_current)
        date_180_days_ago = date_150_days_ago - timedelta(days=30)

        # # 중복된 mac_address를 가진 레코드를 필터링합니다.
        # filtered_user = Xfactor_Common.objects.values('mac_address').annotate(max_user_date=Max('user_date')).distinct()
        # # 가장 최근 날짜인 레코드를 선택합니다.
        # latest_records = []
        # for item in filtered_user:
        #     mac_address = item['mac_address']
        #     max_user_date = item['max_user_date']
        #     record = Xfactor_Common.objects.filter(mac_address=mac_address, user_date=max_user_date).first()
        #     if record:
        #         latest_records.append(record)
        # count = sum(1 for record in latest_records if date_180_days_ago <= record.user_date < date_150_days_ago)

        filtered_records = Xfactor_Common.objects.filter(user_date__gt=date_180_days_ago, user_date__lte=date_150_days_ago)
        base = Xfactor_Common.objects.filter(user_date__gte=date_150_days_ago)
        base_mac_addresses = base.values_list('mac_address', flat=True)
        user = filtered_records.exclude(mac_address__in=base_mac_addresses)

        count = user.count()
        #print(count)


        # 예전코드
        # date_150_days_ago = start_of_today - timedelta(days=7)
        # discover_user = Xfactor_Common.objects.filter(user_date__lt=date_150_days_ago)
        # count = discover_user.count()
        classification = 'discover'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = '150_day_ago'

        daily_statistics_log = Daily_Statistics_log(
            classification=classification,
            item=item,
            item_count = count
        )
        daily_statistics_log.save()

        print("오피스 시작")
        #Office 버전별 통계

        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)
        service_user = user.values('essential5').annotate(count=Count('essential5'))
        for user_data in service_user:
            classification = None  # 초기값 설정
            if user_data['essential5'].startswith('Office'):
                if user_data['essential5'].startswith('Office 365'):
                    classification = 'office_ver_365'
                else:
                    classification = 'office_ver'
            else:
                classification = 'office_ver_mac'

            #classification = 'office_ver'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['essential5']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()
        print("CPU 시작")
        # cpu 사용량

        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)

        services = user.values('t_cpu').annotate(count=Count('t_cpu'))
        for service_data in services:
            classification = 't_cpu'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = service_data['t_cpu']
            item_count = service_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()
        print("os 6개 시작")
        # os버전별 자산 현황
        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)
        users = user.filter(Q(os_simple='Windows'), Q(os_total__contains='Windows')).values('os_total', 'os_build').annotate(count=Count('os_simple')).order_by('-count')[:6]
        for user_data in users:
            # if user_data['os_total'] == 'unconfirmed':
            #     continue
            classification = 'win_os_build'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_total'] + ' ' + user_data['os_build']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()
        print("업데이트 핫픽스 시작")
        # 업데이트 필요 통계
        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today).exclude(os_build__in=['' ,'unconfirmed'])
        user = Xfactor_Common.objects.filter(essential3=True).exclude(os_build__in=['' ,'unconfirmed'])


        ver_current = Daily_Statistics_log.objects.filter(item='ver_module').order_by('-statistics_collection_date').values_list('item_count', flat=True).first()
        users = user.annotate(os_build_cast=Cast('os_build', BigIntegerField())).filter(os_simple='Windows', os_build_cast__gte=ver_current).exclude(os_total='unconfirmed').values('os_simple', 'os_build').annotate(count=Count('os_simple'))
        classification = 'os_version_up'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = 'new'
        item_count = sum(item['count'] for item in users)
        daily_statistics_log = Daily_Statistics_log(
            classification=classification,
            item=item,
            item_count=item_count
        )
        daily_statistics_log.save()
        # 업데이트 필요 통계
        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today).exclude(os_build__in=['', 'unconfirmed'])
        user = Xfactor_Common.objects.filter(essential3=True).exclude(os_build__in=['', 'unconfirmed'])

        #user = Xfactor_Daily.objects.filter(user_date__gte=time)
        #user = Xfactor_Common_Cache.objects.filter(cache_date__gte=time)
        users = user.annotate(os_build_cast=Cast('os_build', BigIntegerField())).filter(os_simple='Windows', os_build_cast__lt=ver_current).exclude(os_total='unconfirmed').values('os_simple', 'os_build').annotate(count=Count('os_simple'))
        classification = 'os_version_up'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = 'old'
        item_count = sum(item['count'] for item in users)
        daily_statistics_log = Daily_Statistics_log(
            classification=classification,
            item=item,
            item_count=item_count
        )
        daily_statistics_log.save()

        print("구분값  시작")
        # online window
        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)
        users = user.filter(Q(chassistype='Notebook')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Notebook_chassis_online'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # online mac
        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)
        users = user.filter(Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Desktop_chassis_online'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # online other
        #user = Xfactor_Common.objects.filter(user_date__gte=start_of_today)
        user = Xfactor_Common.objects.filter(essential3=True)
        users = user.exclude(Q(chassistype='Desktop') | Q(chassistype='Notebook')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Other_chassis_online'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # total window
        #user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today).filter(cache_date__gte=start_of_today)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Notebook')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Notebook_chassis_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # total mac
        #user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Desktop_chassis_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # total other
        #user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)

        users = user_cache.exclude(Q(chassistype='Notebook') | Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Other_chassis_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # notebook total
        #user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Notebook')).values('os_simple').annotate(count=Count('os_simple'))
        classification = 'Notebook_chassis_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = 'Notebook'
        item_count = sum(item['count'] for item in users)
        daily_statistics_log = Daily_Statistics_log(
            classification=classification,
            item=item,
            item_count=item_count
        )
        daily_statistics_log.save()

        # desktop total
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        classification = 'Desktop_chassis_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = 'Desktop'
        item_count = sum(item['count'] for item in users)
        daily_statistics_log = Daily_Statistics_log(
            classification=classification,
            item=item,
            item_count=item_count
        )
        daily_statistics_log.save()

        #-------------------------------------

        # total window
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Notebook')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Notebook_os_cache_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # total mac
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Desktop_os_cache_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # total other
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.exclude(Q(chassistype='Notebook') | Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        for user_data in users:
            classification = 'Other_cache_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = user_data['os_simple']
            item_count = user_data['count']
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

        # notebook total
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Notebook')).values('os_simple').annotate(count=Count('os_simple'))
        classification = 'Notebook_cache_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = 'Notebook'
        item_count = sum(item['count'] for item in users)
        daily_statistics_log = Daily_Statistics_log(
            classification=classification,
            item=item,
            item_count=item_count
        )
        daily_statistics_log.save()

        # desktop total
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today, cache_date__gte=seven_days_ago)
        user_cache = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        #user_cache = Xfactor_Common_Cache.objects.filter(user_date__gte=time).filter(cache_date__gte=seven_days_ago)
        users = user_cache.filter(Q(chassistype='Desktop')).values('os_simple').annotate(count=Count('os_simple'))
        classification = 'Desktop_cache_total'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
        item = 'Desktop'
        item_count = sum(item['count'] for item in users)
        daily_statistics_log = Daily_Statistics_log(
            classification=classification,
            item=item,
            item_count=item_count
        )
        daily_statistics_log.save()

        print("필수보안프로그렘  시작")
        #보안프로그램 개수
        count_list = []
        #user = Xfactor_Common_Cache.objects.filter(user_date__gte=start_of_today).filter(cache_date__gte=seven_days_ago)
        user = Xfactor_Common.objects.filter(user_date__gte=seven_days_ago)
        security_program = ['cososys', 'symantec', 'cbr', 'cbc', 'mcafee']
        cososys_count = user.filter(security1='True ').count()
        symantec_count = user.filter(security2='True ').count()
        cbr_count = user.filter(security3='True ').count()
        cbc_count = user.filter(security4='True ').count()
        mcafee_count = user.filter(security5='True ').count()
        count_list = cososys_count, symantec_count, cbr_count, cbc_count, mcafee_count
        for i, count_data in enumerate(count_list):
            classification = 'security_count'  # 분류 정보를 원하시는 텍스트로 변경해주세요.
            item = security_program[i]
            item_count = count_data
            daily_statistics_log = Daily_Statistics_log(
                classification=classification,
                item=item,
                item_count=item_count
            )
            daily_statistics_log.save()

    except Exception as e :
        logger.warning('Daily error' + str(e))
        logger.warning('Daily error' + str(item))

    print("daily Statistics Success")
