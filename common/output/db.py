from datetime import datetime, timedelta
from pprint import pprint
import pytz
import psycopg2
import json
import logging

with open("setting.json", encoding="UTF-8") as f:
    SETTING = json.loads(f.read())
DBHOST = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['HOST']
DBPORT = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['PORT']
DBNM = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['NAME']
DBUNM = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['USER']
DBPWD = SETTING['CORE']['Tanium']['OUTPUT']['DB']['PS']['PWD']

def before():
    #모듈,웹 세팅값이 없을 경우 생성하고 있을경우엔 최근 값으로 세팅값을 저장한다.
    local_tz = pytz.timezone('Asia/Seoul')
    # UTC 시간대를 사용하여 현재 시간을 얻음
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    # 현재 시간대로 시간 변환
    now = utc_now.astimezone(local_tz)
    logger = logging.getLogger(__name__)
    try:
        Conn = psycopg2.connect(
            'host={0} port={1} dbname={2} user={3} password={4}'.format(DBHOST, DBPORT, DBNM, DBUNM, DBPWD))
        Cur = Conn.cursor()

        # 아이템 값 확인 쿼리 실행
        items = ["discover_module", "discover_web", "ver_module", "ver_web", "hot_module", "hot_web"]
        #query = "SELECT item, item_count FROM common_daily_statistics_log WHERE item IN %s"
        #query = "SELECT item, item_count FROM common_daily_statistics_log WHERE item IN %s ORDER BY statistics_collection_date DESC LIMIT 1"

        query = "SELECT item, item_count FROM common_daily_statistics_log WHERE (item, statistics_collection_date) IN (SELECT item, MAX(statistics_collection_date) AS max_date FROM common_daily_statistics_log WHERE item IN %s GROUP BY item)"

        Cur.execute(query, (tuple(items),))


        # 결과 가져오기
        rows = Cur.fetchall()

        # 중복된 아이템 값 처리
        prev_date = "2023-11-26"  # 이전에 사용한 아이템 값을 확인할 날짜
        existing_items = {row[0]: row[1] for row in rows}
        new_items = [item for item in items if item not in existing_items]
        print(existing_items)
        #print(new_items)

        # 중복된 아이템 값 insert
        for item, count in existing_items.items():
            # 중복된 아이템 값을 그대로 사용하여 insert하는 로직을 추가하세요.
            # 예를 들어, INSERT 쿼리를 사용하여 중복된 아이템 값을 추가할 수 있습니다.
            insert_query = "INSERT INTO common_daily_statistics_log (classification, item, item_count, statistics_collection_date) VALUES (%s, %s, %s, %s)"
            Cur.execute(insert_query, ('settings', item, count, now))
            Conn.commit()
            print(f"중복된 아이템 '{item}'를 count 값 {count}로 추가하였습니다.")

        # 중복되지 않은 아이템 값 insert

        for item in new_items:
            if item not in existing_items:
                if item == 'discover_module' or item == 'discover_web' :
                    count = 150
                if item == 'ver_module' or item == 'ver_web' :
                    count = 19044
                if item == 'hot_module' or item == 'hot_web' :
                    count = 90
                # 중복되지 않은 아이템 값을 기본 count 값으로 insert하는 로직을 추가하세요.
                # 예를 들어, INSERT 쿼리를 사용하여 새로운 아이템 값을 추가할 수 있습니다.
                insert_query = "INSERT INTO common_daily_statistics_log (classification, item, item_count, statistics_collection_date) VALUES (%s, %s, %s, %s)"
                Cur.execute(insert_query, ('settings', item, count, now))
                Conn.commit()
                print(f"새로운 아이템 '{item}'를 count 값 {count}로 추가하였습니다.")

        # 연결 종료
        Cur.close()
        Conn.close()
        logger.info('Statistics Table INSERT connection 성공')
    except ConnectionError as e:
        logger.warning('Statistics Table INSERT connection 실패')
        logger.warning('Error : ' + str(e))



def after():
    #웹에서 설정으로 바꾼 모듈세팅값으로 모듈 구동 후에 웹세팅값을 변경한다
    logger = logging.getLogger(__name__)
    try:
        Conn = psycopg2.connect(
            'host={0} port={1} dbname={2} user={3} password={4}'.format(DBHOST, DBPORT, DBNM, DBUNM, DBPWD))
        Cur = Conn.cursor()

        update_query = """
            UPDATE common_daily_statistics_log
            SET item_count = (
                SELECT item_count
                FROM common_daily_statistics_log
                WHERE item = 'ver_module'
                ORDER BY statistics_collection_date DESC
                LIMIT 1
            )
            WHERE item = 'ver_web'
            AND statistics_collection_date = (
                SELECT MAX(statistics_collection_date)
                FROM common_daily_statistics_log
                WHERE item = 'ver_web'
            )
        """
        Cur.execute(update_query)
        Conn.commit()

        print("item 'hot_web'의 값이 ver_module 값으로 업데이트되었습니다.")

        update_hot_query = """
            UPDATE common_daily_statistics_log
            SET item_count = (
                SELECT item_count
                FROM common_daily_statistics_log
                WHERE item = 'hot_module'
                ORDER BY statistics_collection_date DESC
                LIMIT 1
            )
            WHERE item = 'hot_web'
            AND statistics_collection_date = (
            SELECT MAX(statistics_collection_date)
            FROM common_daily_statistics_log
            WHERE item = 'ver_web'
        )

        """

        Cur.execute(update_hot_query)
        Conn.commit()

        print("item 'hot_web'의 값이 hot_module의 값으로 업데이트되었습니다.")

        # discover_module의 값으로 discover_web의 item을 업데이트하는 쿼리 실행
        update_discover_query = """
            UPDATE common_daily_statistics_log 
            SET item_count = (
                SELECT item_count
                FROM common_daily_statistics_log
                WHERE item = 'discover_module'
                ORDER BY statistics_collection_date DESC
                LIMIT 1
            )
            WHERE item = 'discover_web'
            AND statistics_collection_date = (
                SELECT MAX(statistics_collection_date)
                FROM common_daily_statistics_log
                WHERE item = 'ver_web'
            )
        """

        Cur.execute(update_discover_query)
        Conn.commit()
        print("item 'hot_web'의 값이 discover_module 값으로 업데이트되었습니다.")

        # 연결 종료
        Cur.close()
        Conn.close()
        logger.info('Statistics Table INSERT connection 성공')
    except ConnectionError as e:
        logger.warning('Statistics Table INSERT connection 실패')
        logger.warning('Error : ' + str(e))






