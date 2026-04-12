import os
from dotenv import load_dotenv

load_dotenv()

WIFI_CONTROLLER = os.getenv("WIFI_CONTROLLER")
ADM_NAME = os.getenv("ADM_NAME")
ADM_PWD = os.getenv("ADM_PWD")

DEVICES_PAGE = os.getenv("DEVICES_PAGE")
WIDE_MANAGEMENT_PAGE = os.getenv("WIDE_MANAGEMENT_PAGE")
AP_TEMPLATE_PAGE = os.getenv("AP_TEMPLATE_PAGE")

TABLE_SELECTOR = os.getenv("TABLE_SELECTOR")

TEMPLATE_API_HOST = os.getenv("TEMPLATE_API_HOST", "template-api.default.svc.cluster.local.")
TEMPLATE_API_PORT = int(os.getenv("TEMPLATE_API_SVC_PORT", "8000"))