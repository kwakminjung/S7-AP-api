import asyncio
import traceback
from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import httpx

from app.services.login import login
from app.config import DEVICES_PAGE, WIDE_MANAGEMENT_PAGE, AP_TEMPLATE_PAGE
from app.services.scraper import redirect_by_js, save_template_data
from app.services.get_data import get_aplist_json, get_template_json

TEMPLATE_SCRAPE_INTERVAL = 120

driver = None
scrape_lock = asyncio.Lock()
background_task = None


def _get_active_template_numbers() -> list[str]:
    try:
        response = httpx.get("http://aplist-api:8000/ews/aplist", timeout=10)
        data = response.json()
        if data.get("status") != "success":
            return []
        numbers = set()
        for ap in data.get("data", []):
            t = ap.get("Template")
            if t and str(t).strip().isdigit():  # 숫자만 통과
                numbers.add(str(t))
        return sorted(numbers)
    except Exception as e:
        print(f"failed to get aplist: {e}")
        return []


async def template_scrape_loop():
    global driver
    while True:
        await asyncio.sleep(TEMPLATE_SCRAPE_INTERVAL)
        if not driver:
            print("template_scrape_loop: driver not available, skipping")
            continue

        async with scrape_lock:
            try:
                template_numbers = await asyncio.to_thread(_get_active_template_numbers)
                if not template_numbers:
                    print("template_scrape_loop: no active templates found, skipping")
                    continue

                print(f"template_scrape_loop: scraping templates {template_numbers}")
                result = await asyncio.to_thread(save_template_data, driver, template_numbers)
                print(f"template_scrape_loop: done -> {result}")

            except Exception as e:
                print(f"template_scrape_loop: error: {e}")
                print(traceback.format_exc())


@asynccontextmanager
async def template_lifespan(router: APIRouter):
    global driver, background_task

    print("template_api: lifespan started")
    try:
        driver = login()
        if driver:
            redirect_by_js(driver, DEVICES_PAGE, frame_name="up")
            WebDriverWait(driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it("main")
            )
            driver.switch_to.default_content()
            redirect_by_js(driver, WIDE_MANAGEMENT_PAGE, frame_name="main")
            driver.get(AP_TEMPLATE_PAGE)
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "sel_Template"))
            )
            print("template_api: ready")

            async with scrape_lock:
                template_numbers = _get_active_template_numbers()
                if template_numbers:
                    print(f"template_api: initial scrape for {template_numbers}")
                    await asyncio.to_thread(save_template_data, driver, template_numbers)
                else:
                    print("template_api: no active templates at startup (aplist.csv not ready yet)")

            background_task = asyncio.create_task(template_scrape_loop())
        else:
            print("template_api: login failed")

    except Exception as e:
        print(f"template_api: startup error: {e}")
        print(traceback.format_exc())

    yield

    print("template_api: shutting down")
    if background_task:
        background_task.cancel()
    if driver:
        driver.quit()


router = APIRouter(prefix='/ews')


@router.get("/template/{template_number}")
async def get_template(template_number: str):
    data = get_template_json(template_number)
    if data.get("status") != "success":
        raise HTTPException(status_code=404, detail=data.get("message"))
    return data


@router.get("/template")
async def get_all_templates():
    data = get_template_json()
    if data.get("status") != "success":
        raise HTTPException(status_code=500, detail=data.get("message"))
    return data