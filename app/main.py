from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import Response
from contextlib import asynccontextmanager
import asyncio


from app.login import login
from app.scraper import save_aplist_data, redirect_by_js

from app.config import DEVICES_PAGE, WIDE_MANAGEMENT_PAGE
from app.get_data import get_aplist_json
from app.scraper import get_ap_user_data

driver = None
scrape_lock = asyncio.Lock()

async def aplist_scrape():
    global driver
    while True:
        if driver:
            async with scrape_lock:
                print("starting data scrape...")
                result = await asyncio.to_thread(save_aplist_data, driver)
                print("data scrape completed:", result)
            
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global driver
    
    driver = login()
    
    background_task = None
    if driver:
        print("login successful")

        redirect_by_js(driver, DEVICES_PAGE, frame_name="up")
        print("redirected to devices page")
        
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

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content="", media_type="image/x-icon")