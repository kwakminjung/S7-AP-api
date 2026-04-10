import os
import csv
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from app.config import TABLE_SELECTOR

def _wait_for_page_ready(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def _wait_for_select_options(driver, element_id, timeout=10):
    def options_loaded(d):
        try:
            el = d.find_element(By.ID, element_id)
            return len(Select(el).options) > 1
        except Exception:
            return False
    WebDriverWait(driver, timeout).until(options_loaded)

def redirect_by_js(driver, js, frame_name=None):
    try:
        driver.switch_to.default_content()
        if frame_name:
            driver.switch_to.frame(frame_name)

        driver.execute_script(js)
        _wait_for_page_ready(driver)

        driver.switch_to.default_content()
        return True
    except Exception as e:
        print(f"failed to redirect {js} page: {e}")
        return False

def redirect_to_template_config(driver, template_number: str):
    try:
        driver.switch_to.default_content()

        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sel_Template"))
        )
        Select(select_element).select_by_value(str(template_number))

        config_xpath = "//tr[@id='radio_item']//a[contains(@class, 'button')]"
        config_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, config_xpath))
        )
        config_btn.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "rf"))
        )

        return True

    except TimeoutException:
        print(f"timeout: template {template_number} page did not load in time")
        return False
    except Exception as e:
        print(f"failed to redirect to template {template_number}: {e}")
        print(traceback.format_exc())
        return False

def _get_select_text(driver, element_id):
    el = driver.find_element(By.ID, element_id)
    return Select(el).first_selected_option.text

def get_template_radio(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "rf"))
        )

        radio_data = {
            "radio":                _get_select_text(driver, "rf"),
            "wlan_mode":            _get_select_text(driver, "mode"),
            "channel_bandwidth":    _get_select_text(driver, "channelwidth"),
            "channel":              _get_select_text(driver, "channel"),
            "tx_power":             _get_select_text(driver, "txpower"),
            "airtime_fairness":     _get_select_text(driver, "airtime_fairness"),
            "band_steering":        _get_select_text(driver, "bandsteering"),
            "basic_rate":           _get_select_text(driver, "basic_rate"),
            "ofdma":                _get_select_text(driver, "ofdma"),
            "interference_detection": driver.find_element(By.ID, "interference_detection").get_attribute("value"),
            "beacon_interval":        driver.find_element(By.ID, "beacon").get_attribute("value"),
            "minimum_signal_allowed": driver.find_element(By.ID, "min_signal_allowed").get_attribute("value"),
            "bss_coloring":           driver.find_element(By.ID, "he_bss_color").get_attribute("value"),
        }
        return radio_data

    except Exception as e:
        print(f"failed to get template radio data: {e}")
        print(traceback.format_exc())
        return None

def get_ap_user_data(driver, ap_name):
    try:
        main_window = driver.current_window_handle
    except Exception as e:
        print("browser is not valid")
        return None

    ap_user_data = None

    try:
        driver.switch_to.default_content()
        driver.switch_to.frame("main")

        button_xpath = (
            f"//tr[td[3][normalize-space(.)='{ap_name}']]"
            f"/td[9]//*[self::input or self::a or self::button]"
        )
        
        detail_button = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        detail_button.click()

        WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) > 1)

        for window_handle in driver.window_handles:
            if window_handle != main_window:
                driver.switch_to.window(window_handle)
                break

        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, TABLE_SELECTOR))
        )
        
        ap_user_data = []
        rows = table.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            cols = row.find_elements(By.CSS_SELECTOR, "th, td")
            if len(cols) > 0:
                row_data = [col.text.strip() for col in cols[:-1]]
                
                if any(row_data):
                    ap_user_data.append(row_data)
                    
        print(f"extracted ap user data for {ap_name}: {ap_user_data} : {len(ap_user_data)} items")

    except Exception as e:
        print(f"failed to extract/scrape specific ap data for {ap_name}: {e}")
        
    finally:
        try:
            handles = driver.window_handles
            for handle in handles:
                if handle != main_window:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(main_window)
        except Exception as e:
            print(f"failed session restore: {e}")

    return ap_user_data

def save_aplist_data(driver):

    try:
        driver.switch_to.default_content()
        driver.switch_to.frame("main")

        table = driver.find_element(By.CSS_SELECTOR, TABLE_SELECTOR)
        rows = table.find_elements(By.TAG_NAME, "tr")

        table_data = []
        for row in rows:
            cols = row.find_elements(By.CSS_SELECTOR, "th, td")
            cols_text = [col.text.strip() for col in cols]
            if cols_text:
                filtered_cols = cols_text[1:9] + cols_text[11:14]
                table_data.append(filtered_cols)
        
        save_dir = "/workspace/app/data"
        os.makedirs(save_dir, exist_ok=True)

        tmp_path = os.path.join(save_dir, "aplist_tmp.csv")
        file_path = os.path.join(save_dir, "aplist.csv")

        with open(tmp_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(table_data)

        os.replace(tmp_path, file_path)

        return f"Data saved to {file_path} ({len(table_data)} rows)"

    except Exception as e:
        print(f"failed to scrape aplist data: {e}")
        return None