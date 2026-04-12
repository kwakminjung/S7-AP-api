from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import Response
from contextlib import asynccontextmanager
import asyncio
import httpx

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from app.services.login import login
from app.config import DEVICES_PAGE, WIDE_MANAGEMENT_PAGE, TEMPLATE_API_HOST, TEMPLATE_API_PORT

from app.services.scraper import save_aplist_data, redirect_by_js, get_ap_user_data
from app.services.get_data import get_aplist_json

from app.services.dns_cache import dns_cache

driver = None
scrape_lock = asyncio.Lock()
template_priority = asyncio.Event()
template_priority.set()

background_task = None

async def recover_session():
    global driver
    print("attempting session recovery...")
    
    if driver:
        try:
            driver.quit()
        except:
            pass
            
    driver = await asyncio.to_thread(login)
    
    if driver:
        print("session recovery login successful, navigating to pages...")
        await asyncio.to_thread(redirect_by_js, driver, DEVICES_PAGE, frame_name="up")
        
        await asyncio.to_thread(
            lambda: WebDriverWait(driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it("main")
            )
        )
        await asyncio.to_thread(driver.switch_to.default_content)
        
        await asyncio.to_thread(redirect_by_js, driver, WIDE_MANAGEMENT_PAGE, frame_name="main")
        print("session recovery successful")
        return True
    else:
        print("failed to recover session")
        return False

async def aplist_scrape():
    global driver
    while True:
        if driver:
            await template_priority.wait()
            async with scrape_lock:
                print("starting data scrape...")
                try:
                    result = await asyncio.to_thread(save_aplist_data, driver)
                    print("data scrape completed:", result)

                    if result is None:
                        await recover_session()

                except Exception as e:
                    print(f"scraping error {e}")
            
        await asyncio.sleep(10)

@asynccontextmanager
async def aplist_lifespan(router: APIRouter):
    global driver, background_task
    
    driver = login()
    
    if driver:
        print("login successful")
        redirect_by_js(driver, DEVICES_PAGE, frame_name="up")
        print("redirected to devices page")
        
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it("main")
        )
        driver.switch_to.default_content()
        
        redirect_by_js(driver, WIDE_MANAGEMENT_PAGE, frame_name="main")
        print("redirected to wide management page")
        
        background_task = asyncio.create_task(aplist_scrape())
    else:
        print("login failed! browser was not launched.")
    yield

    print("server shut down")
    if background_task:
        background_task.cancel()
    if driver:
        driver.quit()

router = APIRouter(prefix='/ews')

@router.get("/aplist")
async def get_aplist():
    data = get_aplist_json()
    return data

@router.get("/aplist/{ap_name}")
async def get_aplist_by_name(ap_name: str):
    data = get_aplist_json()

    if data.get("status") != "success":
        raise HTTPException(status_code=500, detail="cannot read data")
    
    ap_list = data.get("data", [])
    for ap in ap_list:
        if ap_name in ap.get("Name", ""):
            return {
                "status": "success",
                "data": ap
            }
    
    raise HTTPException(status_code=404, detail=f"'{ap_name}' not found in data")

@router.get("/aplist/{ap_name}/users")
async def get_ap_users(ap_name: str):
    async with scrape_lock:
        if not driver:
            raise HTTPException(status_code=500, detail="browser not available")
        
        user_data = await asyncio.to_thread(get_ap_user_data, driver, ap_name)
        if user_data is None:
            raise HTTPException(status_code=404, detail=f"'{ap_name}' not found in data")
        
        return {
            "status": "success",
            "data": user_data
        }

@router.get("/aplist/{ap_name}/template")
async def get_ap_template(ap_name: str):
    template_priority.clear()
    async with scrape_lock:
        pass
    
    try:
        data = get_aplist_json()
        if data.get("status") != "success":
            raise HTTPException(status_code=500, detail="cannot read data")
        
        target_ap = None
        for ap in data.get("data", []):
            if ap_name in ap.get("Name", ""):
                target_ap = ap
                break

        if not target_ap:
            raise HTTPException(status_code=404, detail=f"'{ap_name}' not found in data")

        template_number = target_ap.get("Template")
        if not template_number:
            raise HTTPException(status_code=404, detail=f"template number not found for '{ap_name}'")

        timeout_settings = httpx.Timeout(60.0, connect=30.0)

        try:
            ip = await dns_cache.resolve(TEMPLATE_API_HOST)
            template_server_url = f"http://{ip}:{TEMPLATE_API_PORT}/ews/internal/template/{template_number}"
            print(f"[template] connecting to {template_server_url}")

            async with httpx.AsyncClient(timeout=timeout_settings) as client:
                response = await client.get(
                    template_server_url,
                    headers={"Host": TEMPLATE_API_HOST}
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"cannot found '{ap_name}'")
                else:
                    raise HTTPException(status_code=500, detail="occur template_api server error")
        except httpx.RequestError as e:
            print(f"template request error: {repr(e)}")
            raise HTTPException(status_code=500, detail=f"failed to connect: {repr(e)}")
        except Exception as e:
            print(f"unexpected error: {repr(e)}")
            import traceback
            print(traceback.format_exc())
            raise
    finally:
        template_priority.set()