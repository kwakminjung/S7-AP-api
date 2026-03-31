import os
import csv
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from app.config import TABLE_SELECTOR

def redirect_to_template_config(driver, template_number:str):
    try:
        driver.switch_to.default_content()
        
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sel_Template"))
        )
        Select(select_element).select_by_value(str(template_number))

        time.sleep(2)

        config_xpath = "//tr[@id='radio_item']//a[contains(@class, 'button')]"
        config_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, config_xpath))
        )
        config_btn.click()
        
        time.sleep(2)
        return True

    except Exception as e:
        print(f"failed to {template_number} template page redirection")
        print(f"error: {e}")
        print(traceback.format_exc())
        return False

def redirect_by_js(driver, js, frame_name=None):
    try:
        driver.switch_to.default_content()

        if frame_name:
            driver.switch_to.frame(frame_name)
        
        driver.execute_script(js)
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        driver.switch_to.default_content()
        return True
    except Exception as e:
        print(f"failed to redirect {js} page: {e}")
        return False

def get_template_radio(driver):
    radio_data = {}
    try:
        radio = Select(driver.find_element(By.ID, "rf"))
        radio_data["radio"] = radio.first_selected_option.text
        
        wlan_mode = Select(driver.find_element(By.ID, "mode"))
        radio_data["wlan_mode"] = wlan_mode.first_selected_option.text
        
        channel_bandwidth = Select(driver.find_element(By.ID, "channelwidth"))
        radio_data["channel_bandwidth"] = channel_bandwidth.first_selected_option.text
        
        channel = Select(driver.find_element(By.ID, "channel"))
        radio_data["channel"] = channel.first_selected_option.text
        
        tx_power = Select(driver.find_element(By.ID, "txpower"))
        radio_data["tx_power"] = tx_power.first_selected_option.text
        
        airtime_fairness = Select(driver.find_element(By.ID, "airtime_fairness"))
        radio_data["airtime_fairness"] = airtime_fairness.first_selected_option.text
        
        band_steering = Select(driver.find_element(By.ID, "bandsteering"))
        radio_data["band_steering"] = band_steering.first_selected_option.text
        
        basic_rate = Select(driver.find_element(By.ID, "basic_rate")) # Multicast/Broadcast Rate
        radio_data["basic_rate"] = basic_rate.first_selected_option.text
        
        ofdma = Select(driver.find_element(By.ID, "ofdma"))
        radio_data["ofdma"] = ofdma.first_selected_option.text

        radio_data["interference_detection"] = driver.find_element(By.ID, "interference_detection").get_attribute("value")
        radio_data["beacon_interval"] = driver.find_element(By.ID, "beacon").get_attribute("value")
        radio_data["minimum_signal_allowed"] = driver.find_element(By.ID, "min_signal_allowed").get_attribute("value")
        radio_data["bss_coloring"] = driver.find_element(By.ID, "he_bss_color").get_attribute("value")

        return radio_data

    except Exception as e:
        print(f"failed to get template radio data {e}")
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

        button_xpath = f"//tr[td[3][normalize-space(.)='{ap_name}']]/td[9]//*[self::input or self::a or self::button]"
        
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
        
        current_dir = os.path.dirname(os.path.abspath(__file__))

        save_dir = os.path.join(current_dir, "data")
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