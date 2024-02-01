import json

from confluent_kafka import Consumer, KafkaError
import psycopg2


#계정 : nch.tanium.tadmin

#환경 DEV/QA/STG/LIVE

#법인
#NCK - (주)엔씨소프트
#DINOS - (주)엔씨다이노스
#NCITS - (주)엔씨아이티에스
#NCSS - (주)엔씨소프트서비스
#NCCF - NC문화재단
#KLAP - (주)클렙

#토픽
#임직원	[dev./qa./stg./없음]korea.[companyCode].employee
#임직원 전체	[dev./qa./stg./없음]korea.[companyCode].employee.entire
#부서	[dev./qa./stg./없음]korea.[companyCode].department
#부서 전체	[dev./qa./stg./없음]korea.[companyCode].department.entire
#발령	[dev./qa./stg./없음]korea.[companyCode].actchange
#오류	[dev./qa./stg./없음]korea.gis.mbwkr.errors

#DEV/QA 환경 : 172.20.5.26:9092,172.20.5.97:9092,172.20.5.98:9092
#비번 : MwSxXdsfA16LJ (DEV), iZU0biWFH8XK9 (QA)

#STG 환경 : 172.20.5.94:9092,172.20.5.100:9092,172.20.5.101:9092
#비번 : ScaRNSs80iFLo (STG)
#LIVE 환경 : 172.20.5.231:9092,172.20.5.232:9092,172.20.5.233:9092

#비번 : mb475g4dvGQzQ (LIVE)

# PostgreSQL에 데이터 저장
def save_to_postgresql(data):
    # PostgreSQL 연결 설정
    pg_config = {
        'dbname': 'ncsm_dev',
        'user': 'postgres',
        'password': 'psql',
        'host': '172.20.161.129',
        'port': '5432'
    }
    conn = psycopg2.connect(**pg_config)
    cursor = conn.cursor()
    # SQL 쿼리를 사용하여 데이터를 PostgreSQL에 저장
    try:
        user_id = data.get('userId')
        user_name = data.get('userName')

        # userId가 이미 있는지 확인
        cursor.execute('SELECT COUNT(*) FROM common_xfactor_ncdb WHERE "userId" = %s', (user_id,))
        result = cursor.fetchone()

        # userId가 없는 경우: 새로운 레코드를 추가
        if result[0] == 0:
            cursor.execute("""
                INSERT INTO common_xfactor_ncdb ("companyCode", "userName", "userNameEn", "userId", "email", "empNo", "joinDate", "retireDate", "deptCode", "deptName", "managerUserName", "managerUserId", "managerEmpNo")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (data.get('companyCode'), user_name, data.get('userNameEn'), user_id, data.get('email'), data.get('empNo'), data.get('joinDate'), data.get('retireDate'), data.get('deptCode'), data.get('deptName'), data.get('managerUserName'), data.get('managerUserId'), data.get('managerEmpNo')))
        elif result[0] == 1:
            # userId가 있는 경우: common_xfactor_ncdb 테이블의 레코드를 업데이트
            cursor.execute("""
                UPDATE common_xfactor_ncdb
                SET "userName" = %s,
                    "userNameEn" = %s,
                    "email" = %s,
                    "empNo" = %s,
                    "joinDate" = %s,
                    "retireDate" = %s,
                    "deptCode" = %s,
                    "deptName" = %s,
                    "managerUserName" = %s,
                    "managerUserId" = %s,
                    "managerEmpNo" = %s
                WHERE "userId" = %s
            """, (user_name, data.get('userNameEn'), data.get('email'), data.get('empNo'), data.get('joinDate'), data.get('retireDate'), data.get('deptCode'), data.get('deptName'), data.get('managerUserName'), data.get('managerUserId'), data.get('managerEmpNo'), user_id))

        # today = date.today()
    #
    #     cursor.execute("""INSERT INTO common_xfactor_ncdb ("companyCode", "userName", "userNameEn", "userId", "email", "empNo", "joinDate", "retireDate", "deptCode", "deptName", "managerUserName", "managerUserId", "managerEmpNo")
    #                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #                       ON CONFLICT ("userId") DO UPDATE SET
    #                       "userName" = CASE
    #                           WHEN EXCLUDED."retireDate" < %s THEN EXCLUDED."userName" || ' 퇴사자'
    #                           ELSE EXCLUDED."userName"
    #                       END,
    #                       "userNameEn" = EXCLUDED."userNameEn",
    #                       "email" = EXCLUDED."email",
    #                       "empNo" = EXCLUDED."empNo",
    #                       "joinDate" = EXCLUDED."joinDate",
    #                       "retireDate" = EXCLUDED."retireDate",
    #                       "deptCode" = EXCLUDED."deptCode",
    #                       "deptName" = EXCLUDED."deptName",
    #                       "managerUserName" = EXCLUDED."managerUserName",
    #                       "managerUserId" = EXCLUDED."managerUserId",
    #                       "managerEmpNo" = EXCLUDED."managerEmpNo" """,
    #                    (data.get('companyCode'), data.get('userName'), data.get('userNameEn'), data.get('userId'), data.get('email'), data.get('empNo'), data.get('joinDate'), data.get('retireDate'), data.get('deptCode'), data.get('deptName'), data.get('managerUserName'), data.get('managerUserId'), data.get('managerEmpNo'), today))
    #     cursor.execute("""INSERT INTO common_xfactor_ncdb ("companyCode", "userName", "userNameEn", "userId", "email", "empNo", "joinDate", "retireDate", "deptCode", "deptName", "managerUserName", "managerUserId", "managerEmpNo")
    #                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    #                     , (data.get('companyCode'), data.get('userName'), data.get('userNameEn'), data.get('userId'), data.get('email'), data.get('empNo'), data.get('joinDate'), data.get('retireDate'), data.get('deptCode'), data.get('deptName'), data.get('managerUserName'), data.get('managerUserId'), data.get('managerEmpNo')))
    except Exception as e:
        print(e)
    conn.commit()
    cursor.close()
    conn.close()



def retire(messages):
    pg_config = {
        'dbname': 'ncsm_dev',
        'user': 'postgres',
        'password': 'psql',
        'host': '172.20.161.129',
        'port': '5432'
    }
    # pg_config = {
    #     'dbname': 'ncsm',
    #     'user': 'postgres',
    #     'password': 'psql',
    #     'host': 'localhost',
    #     'port': '5432'
    # }
    conn = psycopg2.connect(**pg_config)
    cursor = conn.cursor()
    # SQL 쿼리를 사용하여 데이터를 PostgreSQL에 저장
    # 데이터베이스에서 모든 userId 가져오기
    cursor.execute('SELECT "userId" FROM common_xfactor_ncdb WHERE "userName" NOT LIKE %s', ('%퇴사자%',))
    all_user_ids = cursor.fetchall()


    for user_id in all_user_ids:
        if user_id[0] not in messages:
            if user_id[0].lower().startswith('itsupport') or user_id[0].lower().startswith('erpdev'):
                continue
            else:
                print(user_id[0])
                cursor.execute("""
                        UPDATE common_xfactor_ncdb
                        SET "userName" = "userName" || '(퇴사자)'
                        WHERE "userId" = %s
                    """, (user_id[0],))
                conn.commit()
        else:
            continue



def Kafka_Con():
    # messages = ['user','root','DESKTOP-VVFTLAT\win10-3','DESKTOP-91AR93O\sec','YJKIM\Kim','SKCHOI\sk']
    # print(messages)
    # retire(messages)
    # pg_config = {
    #     'dbname': 'ncsm',
    #     'user': 'postgres',
    #     'password': 'psql',
    #     'host': '172.20.161.64',
    #     'port': '5432'
    # }
    # conn = psycopg2.connect(**pg_config)
    # cursor = conn.cursor()
    # try:
    #     cursor.execute("TRUNCATE TABLE common_xfactor_ncdb")
    # except Exception as e:
    #     print(e)

    print("Kafka 연결1")
    # Kafka 설정
    kafka_config = {
        'bootstrap.servers': '172.20.5.232:9092',  # Kafka 브로커 IP와 포트
        'group.id': 'nch.itservice.tanium',
        'auto.offset.reset': 'earliest',
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanism': 'SCRAM-SHA-512',
        'sasl.username': 'nch.tanium.tadmin',
        'sasl.password': 'mb475g4dvGQzQ',
        'enable.auto.commit': False
    }
    # Kafka 토픽 설정
    kafka_topic = 'korea.nck.employee.entire'
    print("Kafka 연결2")
    #[dev./qa./stg./없음]korea.[companyCode].employee.entire

    # Kafka 소비자 생성
    consumer = Consumer(kafka_config)
    consumer.subscribe([kafka_topic])
    print("Kafka 연결3")
    messages = []
    while True:
        msg = consumer.poll(10.0)
        if msg is None:
            consumer.close()
            break
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print('Reached end of partition')
            else:
                print('Error while consuming message: {}'.format(msg.error()))
        else:
            # Kafka에서 받은 메시지를 처리
            data = msg.value().decode('utf-8')
            message = json.loads(data)
            payload = message['payload']

            save_to_postgresql(payload)
            messages.append(payload['userId'])
    # 소비자 종료
    consumer.close()
    retire(messages)
    print("Kafka 퇴사자 처리 완료")
