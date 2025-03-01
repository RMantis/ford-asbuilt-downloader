from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import easyocr
import time
import os
import traceback
import argparse
import datetime

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

def initialize_browser():
    """Initialize and configure Chrome browser"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run in headless mode (no browser window)
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Set download directory to current directory / asbuilt_downloads
    download_dir = os.path.join(os.getcwd(), "asbuilt_downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    return webdriver.Chrome(options=chrome_options), download_dir

def handle_country_selection(driver, wait):
    """Handle country and language selection if needed"""
    if "SetCountry" in driver.current_url:
        print("Handling country selection page...")
        
        # Select United States (153) as country
        country_select = Select(wait.until(EC.presence_of_element_located((By.NAME, "selectedCountry"))))
        country_select.select_by_value("153")
        
        # Wait for the page to update the language dropdown after country selection
        print("Waiting for language options to load...")

        # Wait for language dropdown to become interactive
        wait.until(EC.element_to_be_clickable((By.NAME, "selectedLanguage")))
        
        time.sleep(2)  # Wait for the page to update

        # Select American English (EN-US) as language
        language_select = Select(driver.find_element(By.NAME, "selectedLanguage"))
        language_select.select_by_value("EN-US")
        
        # Submit the form
        submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-default")))
        submit_button.click()
        
        # Wait for the page to load
        wait.until(EC.url_contains("/AsBuilt"))
        return True
    return False

def solve_captcha(driver, wait, max_attempts=5):
    """Solve CAPTCHA with multiple attempts if needed"""
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"CAPTCHA attempt {attempt} of {max_attempts}...")
        
        # Get the CAPTCHA image
        captcha_img = wait.until(EC.presence_of_element_located((By.ID, "dntCaptchaImg")))
        captcha_img.screenshot('temp_captcha.png')
                
        # Solve CAPTCHA using EasyOCR
        result = reader.readtext('temp_captcha.png', detail=0, allowlist='0123456789')
        captcha_text = result[0] if result else ""
        
        # Cleanup the CAPTCHA image
        if os.path.exists('temp_captcha.png'):
            os.remove('temp_captcha.png')
        
        print(f"CAPTCHA text recognized: {captcha_text}")
        
        # Fill the CAPTCHA input
        captcha_input = wait.until(EC.presence_of_element_located((By.ID, "DNTCaptchaInputText")))
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)
        
        # Submit the form
        print("Submitting the form...")
        form = wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        form.submit()
        
        # Wait until the result page loads
        wait.until(EC.url_contains("/AsBuilt/Details"))
        
        # Check if CAPTCHA failed
        if is_captcha_failed(driver):
            print("CAPTCHA validation failed! Retrying...")
            
            # Go back to AsBuilt page for next attempt
            driver.get("https://www.motorcraftservice.com/AsBuilt")
            
            # Re-enter the VIN
            vin_input = wait.until(EC.presence_of_element_located((By.ID, "VIN")))
            vin_input.clear()
            vin_input.send_keys(driver.current_vin)  # Using stored VIN
        else:
            return True
            
    return False

def is_captcha_failed(driver):
    """Check if the CAPTCHA validation failed by looking for error message"""
    try:
        error_messages = driver.find_elements(By.ID, "pnlCaptcha")
        for error in error_messages:
            if "The Security Code you entered did not match" in error.text:
                return True
        return False
    except:
        return False

def download_file(driver, wait, download_dir, vin):
    """Trigger the download and wait for the file"""
    # Submit the download form
    print("Submitting the download form...")
    form = wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
    form.submit()

    # Check for file existence in download directory with timeout
    print("Waiting for download to complete...")
    download_path = os.path.join(download_dir, f"{vin}.ab")
    
    # Wait for download with timeout
    download_timeout = 10  # seconds
    start_time = time.time()
    while not os.path.exists(download_path) and time.time() - start_time < download_timeout:
        time.sleep(0.5)
        
    if os.path.exists(download_path):
        print(f"Download complete for VIN {vin}!")
        return True
    else:
        print(f"Download timed out for VIN {vin}!")
        return False

def process_vin(driver, wait, download_dir, vin):
    """Process a single VIN"""
    # Check if file already exists
    download_path = os.path.join(download_dir, f"{vin}.ab")
    if os.path.exists(download_path):
        print(f"VIN {vin} already downloaded, skipping...")
        return True
    
    try:
        # Store the current VIN in the driver object for reference in other functions
        driver.current_vin = vin
        
        print(f"Processing VIN: {vin}")
        
        # Navigate to AsBuilt page (if not first VIN)
        if getattr(driver, 'initialized', False):
            driver.get("https://www.motorcraftservice.com/AsBuilt")
        else:
            driver.get("https://www.motorcraftservice.com/AsBuilt")
            driver.initialized = True
        
        # Handle country selection if needed
        handle_country_selection(driver, wait)
        
        # Input the VIN
        print(f"Entering VIN: {vin}")
        vin_input = wait.until(EC.presence_of_element_located((By.ID, "VIN")))
        vin_input.clear()
        vin_input.send_keys(vin)
        
        # Solve CAPTCHA
        captcha_success = solve_captcha(driver, wait)
        if not captcha_success:
            print(f"Failed to solve CAPTCHA for VIN {vin} after multiple attempts. Skipping...")
            return False
            
        # Download the file
        return download_file(driver, wait, download_dir, vin)
        
    except Exception as e:
        print(f"Error processing VIN {vin}: {str(e)}")
        traceback.print_exc()
        return False

def process_all_vins(vin_file):
    """Process all VINs from the specified VIN file"""
    results = {"success": 0, "failed": 0, "skipped": 0}
    
    # Create a timestamped log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{timestamp}.log"
    
    with open(log_filename, 'w') as log:
        log.write(f"AsBuilt Download Run - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write("="*50 + "\n")
        
        # Read all VINs from file
        try:
            with open(vin_file, 'r') as file:
                vins = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            error_msg = f"Error: VIN file '{vin_file}' not found."
            print(error_msg)
            log.write(error_msg + "\n")
            return
        except Exception as e:
            error_msg = f"Error reading VIN file: {str(e)}"
            print(error_msg)
            log.write(error_msg + "\n")
            return
        
        print(f"Found {len(vins)} VINs to process")
        print(f"Logging to: {log_filename}")
        
        # Initialize browser once for all VINs
        driver, download_dir = initialize_browser()
        wait = WebDriverWait(driver, 10)
        
        try:
            # Process each VIN with the same browser session
            for vin in vins:
                start_time = time.time()
                
                # Check if already downloaded
                download_path = os.path.join(download_dir, f"{vin}.ab")
                if os.path.exists(download_path):
                    status = "SKIPPED"
                    results["skipped"] += 1
                    elapsed_time = 0.0
                else:
                    # Process the VIN
                    success = process_vin(driver, wait, download_dir, vin)
                    elapsed_time = time.time() - start_time
                    
                    status = "SUCCESS" if success else "FAILED"
                    if success:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                
                # Log result
                log_message = f"{vin} - {status}" + (f" - {elapsed_time:.1f}s" if status != "SKIPPED" else "")
                print(log_message)
                log.write(log_message + "\n")
                
        finally:
            # Clean up
            if os.path.exists('temp_captcha.png'):
                os.remove('temp_captcha.png')
            driver.quit()
        
        # Write summary
        summary = f"\nSummary: {results['success']} successful, {results['failed']} failed, {results['skipped']} skipped"
        log.write(summary + "\n")
        print(summary)
        print(f"Log file saved as: {log_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Ford AsBuilt files from a list of VINs")
    parser.add_argument("vin_file", help="Path to the text file containing VINs (one per line)")
    args = parser.parse_args()
    
    process_all_vins(args.vin_file)
