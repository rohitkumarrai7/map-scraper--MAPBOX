from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException
import time
import os
import csv
import json
from datetime import datetime
from email_extractor import EmailExtractor
from free_email_extractor import FreeEmailExtractor

def save_to_csv(data, search_query):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_data_{timestamp}.csv"
    
    # Create data directory if it doesn't exist
    import os
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    file_path = os.path.join(data_dir, filename)

    with open(file_path, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Rating & Reviews", "Address", "Website", "Phone", "Search Query"])
        
        data_with_query = [row + [search_query] for row in data]
        writer.writerows(data_with_query)

    print(f"Basic scraped data saved to {file_path}")
    return filename

def save_to_json(data, search_query):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped_data_{timestamp}.json"
    
    # Create data directory if it doesn't exist
    import os
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    file_path = os.path.join(data_dir, filename)
    
    json_data = {
        "search_query": search_query,
        "scraped_at": datetime.now().isoformat(),
        "total_results": len(data),
        "places": []
    }
    
    for row in data:
        place = {
            "title": row[0],
            "rating_and_reviews": row[1], 
            "address": row[2],
            "website": row[3],
            "phone": row[4]
        }
        json_data["places"].append(place)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=2, ensure_ascii=False)
    
    print(f"Basic scraped data saved to {file_path}")
    return filename

def count_available_results(driver, query):
    try:
        elem_results = driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
        return len(elem_results)
    except Exception as e:
        print(f"Error counting results: {e}")
        return 0

def get_user_scraping_choice(total_results):
    print(f"\n=== Results Found: {total_results} ===")
    
    while True:
        print("\nHow many results would you like to scrape?")
        print(f"1. All results ({total_results})")
        print("2. Custom number")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == '1':
            return total_results
        elif choice == '2':
            while True:
                try:
                    custom_count = int(input(f"Enter number of results to scrape (1-{total_results}): ").strip())
                    if 1 <= custom_count <= total_results:
                        return custom_count
                    else:
                        print(f"Please enter a number between 1 and {total_results}")
                except ValueError:
                    print("Please enter a valid number")
        else:
            print("Please enter 1 or 2")

def get_browser_mode_choice():
    """Get user preference for browser mode"""
    print("\n=== Browser Mode Selection ===")
    while True:
        print("Choose browser mode:")
        print("1. Visible browser (default)")
        print("2. Headless mode (runs in background)")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == '1' or choice == '':
            return False  # Not headless
        elif choice == '2':
            return True   # Headless
        else:
            print("Please enter 1 or 2")

def get_browser_choice():
    """Get user preference for browser type"""
    print("\n=== Browser Selection ===")
    while True:
        print("Choose browser:")
        print("1. Firefox (default)")
        print("2. Chrome")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == '1' or choice == '':
            return 'firefox'
        elif choice == '2':
            return 'chrome'
        else:
            print("Please enter 1 or 2")

def get_email_extraction_choice():
    """Get user preference for email extraction method"""
    print("\n=== Email Extraction Method ===")
    while True:
        print("Choose email extraction method:")
        print("1. 🆓 Free Route (ChatGPT Web Automation)")
        print("   - Uses ChatGPT web interface")
        print("   - Completely free")
        print("   - May require manual login")
        print("   - Slower processing")
        print("")
        print("2. 💰 API Route (Perplexity API)")
        print("   - Uses Perplexity API")
        print("   - Costs money per request")
        print("   - Faster and more reliable")
        print("   - Automated processing")
        print("")
        print("3. ❌ Skip email extraction")
        
        choice = input("Enter your choice (1, 2, or 3): ").strip()
        
        if choice == '1':
            return 'free'
        elif choice == '2':
            return 'api'
        elif choice == '3':
            return 'skip'
        else:
            print("Please enter 1, 2, or 3")

def setup_browser_options(browser_type, headless):
    """Setup browser options based on type and mode"""
    
    if browser_type == 'firefox':
        options = webdriver.FirefoxOptions()
        
        # Common options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Headless mode
        if headless:
            options.add_argument("--headless")
            print("🔧 Firefox will run in headless mode (background)")
        else:
            print("🔧 Firefox will run in visible mode")
            
        # Additional options for better performance in headless mode
        if headless:
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
    else:  # Chrome
        options = webdriver.ChromeOptions()
        
        # Common options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        
        # Headless mode
        if headless:
            options.add_argument("--headless")
            print("🔧 Chrome will run in headless mode (background)")
        else:
            print("🔧 Chrome will run in visible mode")
            
        # Additional options for better performance in headless mode
        if headless:
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-images")  # Disable images for faster loading
            
        # User agent to avoid detection
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    return options

def create_driver(browser_type, headless):
    """Create and return a WebDriver instance"""
    
    options = setup_browser_options(browser_type, headless)
    
    try:
        if browser_type == 'firefox':
            driver = webdriver.Firefox(options=options)
        else:  # Chrome
            driver = webdriver.Chrome(options=options)
            
        driver.implicitly_wait(10)
        
        # Set window size for headless mode
        if headless:
            driver.set_window_size(1920, 1080)
            
        print(f"✅ {browser_type.capitalize()} browser initialized successfully")
        return driver
        
    except Exception as e:
        print(f"❌ Error initializing {browser_type} browser: {e}")
        print("Make sure you have the appropriate WebDriver installed:")
        if browser_type == 'firefox':
            print("- Firefox: Install geckodriver")
        else:
            print("- Chrome: Install chromedriver")
        raise

def scroll_to_load_results(driver, query):
    wait = WebDriverWait(driver, 10)
    
    try:
        divSideBar = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"div[aria-label='Results for {query}']"))
        )
        
        print("📜 Scrolling to load all results...")
        keepScrolling = True
        scroll_attempts = 0
        max_scroll_attempts = 50
        
        while keepScrolling and scroll_attempts < max_scroll_attempts:
            divSideBar.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            divSideBar.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
            
            try:
                html = driver.find_element(By.TAG_NAME, "html").get_attribute('outerHTML')
                if "You've reached the end of the list." in html:
                    keepScrolling = False
                    print("✅ Reached end of results.")
            except:
                pass
            
            scroll_attempts += 1
            if scroll_attempts % 10 == 0:
                print(f"📜 Scrolled {scroll_attempts} times...")
                
    except TimeoutException:
        print("⚠️  Could not find results sidebar, continuing anyway...")

def safe_click_element(driver, element, max_attempts=3):
    wait = WebDriverWait(driver, 10)
    
    for attempt in range(max_attempts):
        try:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
            
            wait.until(EC.element_to_be_clickable(element))
            element.click()
            time.sleep(2)
            return True
            
        except (ElementClickInterceptedException, StaleElementReferenceException) as e:
            print(f"🔄 Click attempt {attempt + 1} failed: {e}")
            if attempt < max_attempts - 1:
                time.sleep(1)
            else:
                return False
        except Exception as e:
            print(f"❌ Unexpected error during click: {e}")
            return False
    
    return False

def extract_place_info(driver):
    wait = WebDriverWait(driver, 5)
    
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob')))
    except TimeoutException:
        print("⚠️  Place details didn't load in time")
    
    try:
        title = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob').text
    except:
        title = "N/A"

    try:
        rating_div = driver.find_element(By.CSS_SELECTOR, 'div.F7nice')
        
        rating_text = "N/A"
        review_count = "N/A"
        
        try:
            rating_element = rating_div.find_element(By.CSS_SELECTOR, 'span[aria-hidden="true"]')
            rating_text = rating_element.text
        except:
            pass
        
        try:
            review_element = rating_div.find_element(By.CSS_SELECTOR, 'span[aria-label*="reviews"]')
            review_count = review_element.text
        except:
            try:
                full_text = rating_div.text
                import re
                review_match = re.search(r'\((\d+(?:,\d+)*)\)', full_text)
                if review_match:
                    review_count = f"({review_match.group(1)})"
            except:
                pass
        
        if rating_text != "N/A" and review_count != "N/A":
            rating = f"{rating_text} {review_count}"
        elif rating_text != "N/A":
            rating = rating_text
        elif review_count != "N/A":
            rating = review_count
        else:
            rating = rating_div.text if rating_div.text.strip() else "N/A"
            
    except:
        rating = "N/A"

    try:
        address = driver.find_element(By.CSS_SELECTOR, 'div.Io6YTe.fontBodyMedium.kR99db.fdkmkc').text
    except:
        address = "N/A"

    try:
        website = driver.find_element(By.CSS_SELECTOR, 'div.rogA2c.ITvuef').text
    except:
        website = "N/A"

    try:
        phone = driver.find_element(By.CSS_SELECTOR, 'button[data-item-id^="phone"] .Io6YTe').text
    except:
        phone = "N/A"

    return [title, rating, address, website, phone]

def scrape_results(driver, search_query, max_results=None):
    wait = WebDriverWait(driver, 10)
    
    print(f"🚀 Starting to scrape results (limit: {max_results if max_results else 'all'})...")
    time.sleep(3)
    
    data = []
    processed_urls = set()
    
    try:
        elem_results = driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
        total_available = len(elem_results)
        
        results_to_process = min(max_results, total_available) if max_results else total_available
        
        print(f"📊 Found {total_available} results, will process {results_to_process}")
        
        for i in range(results_to_process):
            try:
                elem_results = driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
                
                if i >= len(elem_results):
                    print(f"⚠️  Result {i + 1} no longer available, stopping...")
                    break
                    
                result = elem_results[i]
                
                print(f"🔍 Processing result {i + 1}/{results_to_process}")
                
                clickable_elements = result.find_elements(By.CSS_SELECTOR, 'a')
                if not clickable_elements:
                    print(f"⚠️  No clickable element found in result {i + 1}")
                    continue
                
                query_result = clickable_elements[0]
                
                try:
                    href = query_result.get_attribute('href')
                    if href in processed_urls:
                        print(f"⏭️  Skipping duplicate result {i + 1}")
                        continue
                    processed_urls.add(href)
                except:
                    pass
                
                if safe_click_element(driver, query_result):
                    print(f"✅ Successfully clicked result {i + 1}")
                    
                    place_info = extract_place_info(driver)
                    data.append(place_info)
                    print(f"📋 Extracted info for: {place_info[0]}")
                    
                    time.sleep(1)
                else:
                    print(f"❌ Failed to click result {i + 1}, skipping...")
                    continue
                    
            except Exception as e:
                print(f"❌ Error processing result {i + 1}: {e}")
                continue
    
    except Exception as e:
        print(f"❌ Error finding results: {e}")
    
    print(f"🎉 Scraping completed. Extracted {len(data)} places.")
    return data

def convert_scraped_data_to_dict_format(scraped_data):
    """Convert scraped data from list format to dictionary format for email extraction"""
    dict_data = []
    for row in scraped_data:
        business_dict = {
            'title': row[0] if len(row) > 0 else 'N/A',
            'rating_and_reviews': row[1] if len(row) > 1 else 'N/A',
            'address': row[2] if len(row) > 2 else 'N/A',
            'website': row[3] if len(row) > 3 else 'N/A',
            'phone': row[4] if len(row) > 4 else 'N/A'
        }
        dict_data.append(business_dict)
    return dict_data

def main():
    print("🗺️  === Google Maps Scraper with Enhanced Email Extraction ===")
    print()
    
    # Get user preferences
    browser_type = get_browser_choice()
    headless_mode = get_browser_mode_choice()
    
    storage_choice = input("Choose storage format (1 for CSV, 2 for JSON): ").strip()
    query = input("Enter the search query with location: ").replace(" ", "+")
    
    # Get email extraction preference
    email_extraction_method = get_email_extraction_choice()
    
    # Get API key if needed
    perplexity_api_key = None
    if email_extraction_method == 'api':
        perplexity_api_key = input("Enter your Perplexity API key: ").strip()
        if not perplexity_api_key:
            print("❌ No API key provided. Switching to free method.")
            email_extraction_method = 'free'
    
    if not headless_mode:
        print("⚠️  While scraping, do not close/minimize the browser window.")
    else:
        print("🤖 Running in headless mode - browser will not be visible.")
    
    time.sleep(1)

    # Create driver with selected options
    driver = create_driver(browser_type, headless_mode)
    
    try:
        print(f"🌐 Navigating to Google Maps...")
        driver.get(f"https://www.google.com/maps/search/{query}")
        
        query_display = query.replace("+", " ")
        
        scroll_to_load_results(driver, query_display)
        
        total_results = count_available_results(driver, query_display)
        
        if total_results == 0:
            print("❌ No results found. Exiting...")
            return
        
        results_to_scrape = get_user_scraping_choice(total_results)
        
        scraped_data = scrape_results(driver, query_display, results_to_scrape)
        
        if not scraped_data:
            print("❌ No data was scraped. Exiting...")
            return
        
        print(f"\n🎯 === Phase 1 Complete: Scraped {len(scraped_data)} places ===")
        
        # Save basic data first
        if storage_choice == '2':
            basic_filename = save_to_json(scraped_data, query_display)
        else:
            basic_filename = save_to_csv(scraped_data, query_display)
        
        # Phase 2: Email extraction based on chosen method
        if email_extraction_method == 'api':
            print(f"\n💰 === Phase 2: Starting API Email Extraction ===")
            
            extractor = EmailExtractor(perplexity_api_key)
            enhanced_data = extractor.process_scraped_data(scraped_data, delay=2)
            
            # Handle API extraction results (existing code)
            if storage_choice == '2':
                print("\n📝 === Updating JSON file with API email extraction results ===")
                
                with open(basic_filename, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                for i, place in enumerate(json_data['places']):
                    if i < len(enhanced_data):
                        place['email'] = enhanced_data[i]['email']
                        place['background'] = enhanced_data[i]['background']
                        place['extraction_status'] = enhanced_data[i]['extraction_status']
                        place['extraction_method'] = 'api'
                        if 'error_details' in enhanced_data[i]:
                            place['error_details'] = enhanced_data[i]['error_details']
                
                successful_extractions = len([c for c in enhanced_data if c['extraction_status'] == 'success'])
                json_data['extraction_summary'] = {
                    'method': 'api',
                    'successful': successful_extractions,
                    'failed': len(enhanced_data) - successful_extractions
                }
                
                with open(basic_filename, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Updated JSON file {basic_filename} with API email extraction results")
            else:
                extractor.save_enhanced_data_to_csv(enhanced_data, query_display)
            
            successful_extractions = len([c for c in enhanced_data if c['extraction_status'] == 'success'])
            
        elif email_extraction_method == 'free':
            print(f"\n🆓 === Phase 2: Starting FREE Email Extraction ===")
            print("📝 Note: This will open a separate ChatGPT browser window")
            
            # Get headless preference for ChatGPT browser
            if not headless_mode:  # If main scraper is visible, ask for ChatGPT mode
                chatgpt_headless = input("Run ChatGPT automation in headless mode? (y/n): ").strip().lower() == 'y'
            else:
                chatgpt_headless = headless_mode  # Use same mode as main scraper
            
            # Convert scraped data to dictionary format
            dict_scraped_data = convert_scraped_data_to_dict_format(scraped_data)
            
            # Initialize free email extractor
            free_extractor = FreeEmailExtractor(headless=chatgpt_headless, browser_type=browser_type)
            
            try:
                # Process with free method
                free_results = free_extractor.process_scraped_data_free(dict_scraped_data, delay=15)
                
                if storage_choice == '2':
                    print("\n📝 === Updating JSON file with FREE email extraction progress ===")
                    
                    with open(basic_filename, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Add phase 1 results
                    for i, place in enumerate(json_data['places']):
                        place['extraction_method'] = 'free'
                        place['extraction_status'] = 'phase1_complete'
                        place['phase1_processed'] = i < free_results['processed']
                        place['notes'] = 'Phase 1 complete - prompt sent to ChatGPT. Phase 2 will parse responses.'
                    
                    json_data['extraction_summary'] = {
                        'method': 'free',
                        'phase': 1,
                        'processed': free_results['processed'],
                        'failed': free_results['failed'],
                        'notes': 'Phase 1 complete. Phase 2 (response parsing) not yet implemented.'
                    }
                    
                    with open(basic_filename, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Updated JSON file {basic_filename} with FREE email extraction Phase 1 results")
                
                successful_extractions = free_results['processed']
                
            except Exception as e:
                print(f"❌ Error in free email extraction: {e}")
                successful_extractions = 0
                
            finally:
                free_extractor.close()
        
        else:  # Skip email extraction
            print("\n⏭️  === Email extraction skipped ===")
            successful_extractions = 0
        
        # Final summary
        print(f"\n📊 === Final Summary ===")
        print(f"🔍 Total places found: {total_results}")
        print(f"📋 Places scraped: {len(scraped_data)}")
        
        if email_extraction_method != 'skip':
            print(f"📧 Email extraction method: {email_extraction_method.upper()}")
            if email_extraction_method == 'free':
                print(f"✅ Phase 1 completed: {successful_extractions} businesses processed")
                print(f"📝 Note: Phase 2 (response parsing) will be implemented next")
            else:
                print(f"✅ Successful email extractions: {successful_extractions}")
                print(f"❌ Failed extractions: {len(scraped_data) - successful_extractions}")
        else:
            print("📧 Email extraction: Skipped")
        
    except Exception as e:
        print(f"❌ An error occurred during scraping: {e}")
    finally:
        driver.quit()
        print("🔒 Main browser closed. Session ended.")

if __name__ == "__main__":
    main()