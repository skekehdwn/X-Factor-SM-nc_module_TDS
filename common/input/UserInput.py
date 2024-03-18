import requests
import json
import logging
from common.input.Session import plug_in as session
from tanium import NodeField, Meta, SensorField, SensorSchema, CacheQuery, QuestionQuery

import time

with open("setting.json", encoding="UTF-8") as f:
    SETTING = json.loads(f.read())

APIURL = SETTING['CORE']['Tanium']['INPUT']['API']['URL']
CSP = SETTING['CORE']['Tanium']['INPUT']['API']['PATH']['Sensor']
APIUNM = SETTING['CORE']['Tanium']['INPUT']['API']['username']
APIPWD = SETTING['CORE']['Tanium']['INPUT']['API']['password']
PROGRESS = SETTING['PROJECT']['PROGRESSBAR'].lower()


class NCsmLiveQuery(CacheQuery):
    computer_id = SensorField(sensor="Computer ID")
    computer_name = SensorField(sensor="Computer Name")
    client_ip = SensorField(sensor="Tanium Client IP Address")
    mac_address = SensorField(sensor="MAC Address")
    chassi_type = SensorField(sensor="ncsm_chassi_type")
    os_platform = SensorField(sensor="OS Platform")
    os = SensorField(sensor="ncsm_os")
    hw = SensorField(sensor="ncsm_hw")
    software = SensorField(sensor="ncsm_software")
    first_network = SensorField(sensor="ncsm_first_network")
    last_network = SensorField(sensor="ncsm_last_network")
    hotfix = SensorField(sensor="ncsm_hotfix")
    subnet = SensorField(sensor="ncsm_subnet")
    service = SensorField(sensor="ncsm_service")
    disk_consumption = SensorField(sensor="ncsm_disk_consumption")
    memory_consumption = SensorField(sensor="ncsm_memory_consumption")
    tcpu = SensorField(sensor="ncsm_tcpu")
    security = SensorField(sensor="ncsm_security")
    uuid = SensorField(sensor="ncsm_UUID")
    multiboot = SensorField(sensor="ncsm_multiboot")
    ext_chr = SensorField(sensor="ncsm_ext_chr")
    ext_edg = SensorField(sensor="ncsm_ext_edg")
    ext_fir = SensorField(sensor="ncsm_ext_fir")
    logged_in_users = SensorField(sensor="Logged In Users")

    _meta = Meta(
        fields=[
            "computer_id",
            "computer_name",
            "client_ip",
            "mac_address",
            "chassi_type",
            "os_platform",
            "os",
            "hw",
            "software",
            "first_network",
            "last_network",
            "hotfix",
            "subnet",
            "service",
            "disk_consumption",
            "memory_consumption",
            "tcpu",
            "security",
            "uuid",
            "multiboot",
            "ext_chr",
            "ext_edg",
            "ext_fir",
            "logged_in_users",
        ],
    )


class NCsmStagingOSPython(SensorSchema):
    os_type = SensorField(sensor="OS type")
    os_version = SensorField(sensor="OS version")
    os_build = SensorField(sensor="OS build")

    _meta = Meta(fields=["os_type", "os_version", "os_build"])


class NCsmStagingHWPython(SensorSchema):
    hw_cpu = SensorField(sensor="hw_cpu")
    hw_ram = SensorField(sensor="hw_ram")
    hw_mb = SensorField(sensor="hw_mb")
    hw_disk = SensorField(sensor="hw_disk")
    hw_gpu = SensorField(sensor="hw_gpu")

    _meta = Meta(fields=["hw_cpu", "hw_ram", "hw_mb", "hw_disk", "hw_gpu"])


class NCsmStagingSoftwarePython(SensorSchema):
    sw_name = SensorField(sensor="sw_name")
    sw_version = SensorField(sensor="sw_version")
    sw_installdate = SensorField(sensor="sw_installdate")
    sw_lastrundate = SensorField(sensor="sw_lastrundate")

    _meta = Meta(fields=["sw_name", "sw_version", "sw_installdate", "sw_lastrundate"])


class NCsmStagingHotfixPython(SensorSchema):
    id = SensorField(sensor="ID")
    date = SensorField(sensor="Date")

    _meta = Meta(fields=["id", "date"])


class NCsmStagingServicePython(SensorSchema):
    essential1 = SensorField(sensor="essential1")
    essential2 = SensorField(sensor="essential2")
    essential3 = SensorField(sensor="essential3")
    essential4 = SensorField(sensor="essential4")
    essential5 = SensorField(sensor="essential5")

    _meta = Meta(fields=["essential1", "essential2", "essential3", "essential4", "essential5"])


class NCsmStagingSecurityPython(SensorSchema):
    security1 = SensorField(sensor="security1")
    security1_ver = SensorField(sensor="security1_ver")
    security2 = SensorField(sensor="security2")
    security2_ver = SensorField(sensor="security2_ver")
    security3 = SensorField(sensor="security3")
    security3_ver = SensorField(sensor="security3_ver")
    security4 = SensorField(sensor="security4")
    security4_ver = SensorField(sensor="security4_ver")
    security5 = SensorField(sensor="security5")
    security5_ver = SensorField(sensor="security5_ver")

    _meta = Meta(
        fields=[
            "security1",
            "security1_ver",
            "security2",
            "security2_ver",
            "security3",
            "security3_ver",
            "security4",
            "security4_ver",
            "security5",
            "security5_ver",
        ]
    )


class NCsmStagingExtPython(SensorSchema):
    extension_name = SensorField(sensor="Extension Name")
    version = SensorField(sensor="Version")

    _meta = Meta(fields=["extension_name", "version"])


class NCsmStagingExtFirPython(SensorSchema):
    extension = SensorField(sensor="Extension")
    version = SensorField(sensor="Version")

    _meta = Meta(fields=["extension", "version"])


class NCsmStagingQuery(CacheQuery):
    computer_id = SensorField(sensor="Computer ID")
    computer_name = SensorField(sensor="Computer Name")
    client_ip = SensorField(sensor="Tanium Client IP Address_python")
    mac_address = SensorField(sensor="MAC Address")
    chassi_type = SensorField(sensor="ncsm_chassi_type_python")
    os_platform = SensorField(sensor="OS Platform_python")

    os = NCsmStagingOSPython(sensor="ncsm_os_python")
    hw = NCsmStagingHWPython(sensor="ncsm_hw_python")
    software = NCsmStagingSoftwarePython(sensor="ncsm_software_python", many=True)

    first_network = SensorField(sensor="ncsm_first_network_python")
    last_network = SensorField(sensor="ncsm_last_network_python")

    hotfix = NCsmStagingHotfixPython(sensor="ncsm_hotfix_python")

    subnet = SensorField(sensor="ncsm_subnet_python")

    service = NCsmStagingServicePython(sensor="ncsm_service_python")

    disk_consumption = SensorField(sensor="ncsm_disk_consumption_python")
    memory_consumption = SensorField(sensor="ncsm_memory_consumption_python")
    tcpu = SensorField(sensor="ncsm_tcpu_python")

    security = NCsmStagingSecurityPython(sensor="ncsm_security_python")

    uuid = SensorField(sensor="ncsm_UUID_python")
    multiboot = SensorField(sensor="ncsm_multiboot_python")

    ext_chr = NCsmStagingExtPython(sensor="ncsm_ext_chr", many=True)
    ext_edg = NCsmStagingExtPython(sensor="ncsm_ext_edg", many=True)
    ext_fir = NCsmStagingExtFirPython(sensor="ncsm_ext_fir", many=True)

    logged_in_users = SensorField(sensor="Logged In Users")

    last_registration_time = SensorField(sensor='Last Registration Time')
    computer_id_test = NodeField(sensor='computerID')

    last_seen = NodeField(sensor='eidLastSeen')

    _meta = Meta(
        fields=[
            "computer_id",
            "computer_name",
            "client_ip",
            "mac_address",
            "chassi_type",
            "os_platform",
            "os",
            "hw",
            "software",
            "first_network",
            "last_network",
            "hotfix",
            "subnet",
            "service",
            "disk_consumption",
            "memory_consumption",
            "tcpu",
            "security",
            "uuid",
            "multiboot",
            "ext_chr",
            "ext_edg",
            "ext_fir",
            "logged_in_users",
            "last_registration_time",
            "computer_id_test",
            "last_seen",
        ],
    )


class NCsmQuestionQuery(QuestionQuery):
    computer_id = SensorField(sensor="Computer ID")

    _meta = Meta(
        fields=[
            "computer_id",
        ],
    )


def plug_in(type):
    logger = logging.getLogger(__name__)
    try:
        #SK = session()
        if type == 'common':
            CSID = SETTING['CORE']['Tanium']['INPUT']['API']['SensorID']['COMMON']
        elif type == 'service':
            CSID = SETTING['CORE']['Tanium']['INPUT']['API']['SensorID']['SERVICE']
        elif type == 'purchase':
            CSID = SETTING['CORE']['Tanium']['INPUT']['API']['SensorID']['PURCHASE']
        elif type == 'security':
            CSID = SETTING['CORE']['Tanium']['INPUT']['API']['SensorID']['SECURITY']
        elif type == 'daily':
            CSID = SETTING['CORE']['Tanium']['INPUT']['API']['SensorID']['DAILY']
        # CSH = {'session': SK}
        # CSU = APIURL + CSP + CSID
        # CSR = requests.post(CSU, headers=CSH, verify=False)
        # # time.sleep(60)
        # CSRT = CSR.content.decode('utf-8', errors='ignore')
        # CSRJ = json.loads(CSRT)
        CSRJD = NCsmStagingQuery.objects.to_list_value()

        CSRJD = CSRJD['data']
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
