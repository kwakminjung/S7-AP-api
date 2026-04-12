import asyncio
import traceback
from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from app.services.login import login
from app.config import DEVICES_PAGE, WIDE_MANAGEMENT_PAGE, AP_TEMPLATE_PAGE
from app.services.scraper import redirect_by_js, redirect_to_template_config, get_template_radio

driver = None
scrape_lock = asyncio.Lock()

@asynccontextmanager
async def template_lifespan(router: APIRouter):
    global driver
    print("template_api: lifespan started")
    try:
        print("template_api: logging in...")
        driver = login()
        print(f"template_api: driver={driver}")
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
            print("template_api: sel_Template loaded")
            print("template_api: ap template page ready")
        else:
            print("template_api: login failed! browser was not launched.")
    except Exception as e:
        print(f"template_api: startup error occurred: {e}")
        print(traceback.format_exc())

    yield

    print("template_api: router shut down")
    if driver:
        driver.quit()
        print("template_api: Selenium browser shut down")

router = APIRouter(prefix='/ews')

@router.get("/internal/template/{template_number}")
async def get_template_data(template_number: str):
    if not driver:
        raise HTTPException(status_code=500, detail="browser is not initialized")

    async with scrape_lock:
        try:
            print(f"template_api: '{template_number}' scraping...")
            driver.switch_to.default_content()
            
            success = await asyncio.to_thread(redirect_to_template_config, driver, template_number)
            if not success:
                raise HTTPException(status_code=404, detail=f"cannot redirect template {template_number}")
            
            template_data = await asyncio.to_thread(get_template_radio, driver)
            
            if not template_data:
                raise HTTPException(status_code=500, detail="cannot read data")
                
            print(f"template_api: template '{template_number}' scraping complete")
            print(f"template_api: scraped data: {template_data}")
            
            return {
                "status": "success",
                "template_number": template_number,
                "data": template_data
            }
        
        except HTTPException:
            raise

        except Exception as e:
            print(f"template_api scraping error: {e}")
            print(traceback.print_exc())
            raise HTTPException(status_code=500, detail="scraping error")
            
        finally:
            print("redirect to template page")
            try:
                driver.switch_to.default_content()
                driver.get(AP_TEMPLATE_PAGE)
            except Exception as e:
                print(f"Failed to redirect to template page: {e}")