import os
from dotenv import load_dotenv

load_dotenv()

WIFI_CONTROLLER = os.getenv("WIFI_CONTROLLER")
ADM_NAME = os.getenv("ADM_NAME")
ADM_PWD = os.getenv("ADM_PWD")

DEVICES_PAGE = os.getenv("DEVICES_PAGE")
WIDE_MANAGEMENT_PAGE = os.getenv("WIDE_MANAGEMENT_PAGE")

TABLE_SELECTOR = os.getenv("TABLE_SELECTOR")