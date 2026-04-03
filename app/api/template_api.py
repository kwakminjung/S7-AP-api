import asyncio
import traceback
from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException

from app.services.login import login
from app.config import DEVICES_PAGE, WIDE_MANAGEMENT_PAGE, AP_TEMPLATE_PAGE
from app.services.scraper import redirect_by_js, redirect_to_template_config, get_template_radio

driver = None
scrape_lock = asyncio.Lock()

@asynccontextmanager
async def template_lifespan(router: APIRouter):
    global driver
    try:
        driver = login()
        
        if driver:
            print("template_api: login successful")

            redirect_by_js(driver, DEVICES_PAGE, frame_name="up")
            print("template_api: devices page")

            redirect_by_js(driver, WIDE_MANAGEMENT_PAGE, frame_name="main")
            print("template_api: wide management page")

            driver.get(AP_TEMPLATE_PAGE)
            print("template_api: ap template page")
            
        else:
            print("template_api: login failed! browser was not launched.")
    except Exception as e:
        print(f"template_api: startup error occurred: {e}")
        print(traceback.format_exc())

    yield

    print("template_api: router shut down")
    if driver:
        driver.quit()
        print("template_api: Selenium brower shut down")

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