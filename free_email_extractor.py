import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class FreeEmailExtractor:
    def __init__(self, headless=False, browser_type='firefox'):
        """
        Initialize the Free Email Extractor using Copilot web interface
        
        Args:
            headless (bool): Whether to run browser in headless mode
            browser_type (str): 'firefox' or 'chrome'
        """
        self.headless = headless
        self.browser_type = browser_type
        self.driver = None
        self.wait = None
        
        print(f"🤖 Initializing Copilot Email Extractor...")
        print(f"   Browser: {browser_type.capitalize()}")
        print(f"   Mode: {'Headless' if headless else 'Visible'}")
        
        self.setup_driver()
    
    def setup_driver(self):
        """Setup the WebDriver with appropriate options"""
        try:
            if self.browser_type == 'firefox':
                options = webdriver.FirefoxOptions()
                
                # Common options
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                
                # Headless mode
                if self.headless:
                    options.add_argument("--headless")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--window-size=1920,1080")
                    print("🔧 Firefox will run in headless mode")
                else:
                    print("🔧 Firefox will run in visible mode")
                
                self.driver = webdriver.Firefox(options=options)
                
            else:  # Chrome
                options = webdriver.ChromeOptions()
                
                # Common options
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-extensions")
                
                # Headless mode
                if self.headless:
                    options.add_argument("--headless")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--window-size=1920,1080")
                    print("🔧 Chrome will run in headless mode")
                else:
                    print("🔧 Chrome will run in visible mode")
                
                # User agent to avoid detection
                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                
                self.driver = webdriver.Chrome(options=options)
            
            # Set implicit wait and window size
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, 60)  # Increased for Copilot response times
            
            if self.headless:
                self.driver.set_window_size(1920, 1080)
            else:
                self.driver.maximize_window()
            
            print("✅ Browser initialized successfully for Copilot automation")
            
        except Exception as e:
            print(f"❌ Error initializing browser: {e}")
            raise
    
    def navigate_to_copilot(self):
        """Navigate to Copilot website"""
        try:
            print("🌐 Navigating to Copilot...")
            self.driver.get("https://copilot.microsoft.com")
            
            # Wait for page to load
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print("✅ Successfully navigated to Copilot")
            time.sleep(5)  # Give page time to fully load
            
            return True
            
        except Exception as e:
            print(f"❌ Error navigating to Copilot: {e}")
            return False
    
    def handle_popup_modals(self):
        """Handle cookie/privacy modals and other popups"""
        try:
            print("🔍 Checking for popup modals...")
            
            # Common selectors for modals and accept buttons
            modal_selectors = [
                "button:contains('Accept')",
                "button:contains('Got it')",
                "button:contains('Continue')",
                "button[id*='accept']",
                "button[class*='accept']",
                "[data-testid='accept-button']",
                "button:contains('I agree')",
                ".modal button",
                "[role='dialog'] button"
            ]
            
            for selector in modal_selectors:
                try:
                    # Wait briefly for modal to appear
                    modal_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    if modal_button.is_displayed():
                        print(f"✅ Found and clicking modal button: {selector}")
                        modal_button.click()
                        time.sleep(2)
                        return True
                        
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"⚠️  Error with modal selector {selector}: {e}")
                    continue
            
            print("✅ No popup modals detected or already handled")
            return True
            
        except Exception as e:
            print(f"⚠️  Error checking popup modals: {e}")
            return True  # Continue anyway
    
    def find_chat_input(self):
        """Find and return the Copilot chat input element"""
        print("🔍 Looking for Copilot chat input field...")
        
        # Copilot-specific selectors - updated with correct ID and fallbacks
        input_selectors = [
            '#userInput',  # Primary selector based on your XPath
            'textarea#userInput',  # More specific version
            'textarea[id="userInput"]',  # Alternative syntax
            'textarea[aria-label="Message Copilot"]',  # Original fallback
            'textarea[placeholder*="Ask me anything"]',
            'textarea[data-testid="chat-input"]',
            'textarea[class*="chat-input"]',
            'div[contenteditable="true"][role="textbox"]',
            'textarea[placeholder*="Message"]',
            '#chat-input',
            '.chat-input textarea'
        ]
        
        for selector in input_selectors:
            try:
                input_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                
                if input_element.is_displayed() and input_element.is_enabled():
                    print(f"✅ Found Copilot chat input: {selector}")
                    return input_element
                    
            except TimeoutException:
                continue
            except Exception as e:
                print(f"⚠️  Error with selector {selector}: {e}")
                continue
        
        # Fallback: try any visible textarea
        try:
            print("🔍 Trying general textarea search...")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for textarea in textareas:
                if textarea.is_displayed() and textarea.is_enabled():
                    aria_label = textarea.get_attribute("aria-label")
                    placeholder = textarea.get_attribute("placeholder")
                    if aria_label or placeholder:
                        print(f"✅ Found textarea - aria-label: {aria_label}, placeholder: {placeholder}")
                        return textarea
        except:
            pass
        
        print("❌ Could not find Copilot chat input field")
        return None
    
    def create_email_search_prompt(self, business_data):
        """Create a structured prompt for Copilot to search for business emails"""
        
        prompt = f"""Please help me find contact email addresses for this business using web search.

**Business Details:**
- Name: {business_data.get('title', 'N/A')}
- Address: {business_data.get('address', 'N/A')}
- Website: {business_data.get('website', 'N/A')}
- Phone: {business_data.get('phone', 'N/A')}

**Task:**
Search the web for this business and find their email addresses. Look on their website, business directories, social media profiles, and other online sources.

**Response Format:**
Please respond with ONLY this exact JSON format:

{{
    "business_name": "{business_data.get('title', 'N/A')}",
    "email": "found-email@example.com",
    "background": "Brief description of what this business does",
    "search_status": "success",
    "source": "where you found the email"
}}

If no email is found, use "N/A" for email and set search_status to "failed".

Start your web search now."""

        return prompt
    
    def input_prompt_to_copilot(self, business_data):
        """Input the email search prompt to Copilot"""
        try:
            print(f"📝 Preparing prompt for: {business_data.get('title', 'Unknown Business')}")
            
            # Find the chat input
            input_element = self.find_chat_input()
            if not input_element:
                return False
            
            # Create the prompt
            prompt = self.create_email_search_prompt(business_data)
            
            print("⌨️  Typing prompt into Copilot...")
            
            # Clear any existing text
            input_element.clear()
            time.sleep(1)
            
            # Input the prompt
            input_element.send_keys(prompt)
            
            print("✅ Prompt entered successfully")
            print(f"📊 Prompt length: {len(prompt)} characters")
            
            # Wait a moment for the text to be processed
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error inputting prompt: {e}")
            return False
    
    def send_message(self):
        """Send the message in Copilot"""
        try:
            print("📤 Looking for send button...")
            
            # Copilot-specific send button selectors - updated with correct classes
            send_selectors = [
                'button.rounded-submitButton',  # Primary selector from your CSS path
                'button[class*="rounded-submitButton"]',  # Alternative syntax
                'button.size-10.rounded-xl',  # Additional class combination
                'button[class*="bg-stone-800"]',  # Dark theme button
                'button[class*="dark:bg-slate-600"]',  # Another theme variant
                'button[aria-label="Send message"]',  # Aria label fallback
                'button[data-testid="send-button"]',  # Data attribute fallback
                'button svg[class*="send"]',
                'button[title*="Send"]',
                '.send-button',
                '[role="button"][aria-label*="Send"]'
            ]
            
            for selector in send_selectors:
                try:
                    send_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    if send_button.is_displayed() and send_button.is_enabled():
                        print(f"✅ Found send button: {selector}")
                        
                        # Scroll button into view and wait
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", send_button)
                        time.sleep(1)
                        
                        # Try JavaScript click first (more reliable)
                        try:
                            self.driver.execute_script("arguments[0].click();", send_button)
                            print("📤 Message sent successfully (JavaScript click)")
                            time.sleep(2)  # Wait for message to be processed
                            return True
                        except:
                            # Fallback to regular click
                            send_button.click()
                            print("📤 Message sent successfully (regular click)")
                            time.sleep(2)
                            return True
                        
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"⚠️  Error with send selector {selector}: {e}")
                    continue
            
            # Try using Enter key as alternative
            print("🔍 Trying Enter key method...")
            input_element = self.find_chat_input()
            if input_element:
                try:
                    # Focus on input first
                    input_element.click()
                    time.sleep(0.5)
                    input_element.send_keys(Keys.RETURN)
                    print("📤 Message sent using Enter key")
                    time.sleep(2)
                    return True
                except Exception as e:
                    print(f"⚠️  Enter key method failed: {e}")
            
            # Last resort: try XPath
            print("🔍 Trying XPath method...")
            try:
                xpath_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/main/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div[2]/div[2]/button"))
                )
                
                if xpath_button.is_displayed() and xpath_button.is_enabled():
                    print("✅ Found send button via XPath")
                    self.driver.execute_script("arguments[0].click();", xpath_button)
                    print("📤 Message sent successfully (XPath + JavaScript)")
                    time.sleep(2)
                    return True
                    
            except Exception as e:
                print(f"⚠️  XPath method failed: {e}")
            
            print("❌ Could not find or click send button")
            return False
            
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def wait_for_response(self, timeout=45):
        """Wait for Copilot response with dynamic DOM checks"""
        try:
            print(f"⏳ Waiting for Copilot response (timeout: {timeout}s)...")
            
            # Look for response indicators
            response_indicators = [
                '[data-testid="chat-message"]',
                '.chat-message',
                '[role="group"]',  # Copilot often uses role="group" for messages
                '.response-message',
                '[class*="message"]',
                '[class*="response"]'
            ]
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check for typing indicator first
                try:
                    typing_indicators = [
                        '[class*="typing"]',
                        '[class*="loading"]',
                        '.dots',
                        '[aria-label*="typing"]'
                    ]
                    
                    for indicator in typing_indicators:
                        if self.driver.find_elements(By.CSS_SELECTOR, indicator):
                            print("⌨️  Copilot is typing...")
                            break
                            
                except:
                    pass
                
                # Check for actual response
                for selector in response_indicators:
                    try:
                        messages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if len(messages) >= 2:  # At least user message + bot response
                            print("✅ Response detected!")
                            return True
                    except:
                        continue
                
                time.sleep(2)  # Check every 2 seconds
            
            print(f"⏰ Response timeout after {timeout} seconds")
            return False
            
        except Exception as e:
            print(f"❌ Error waiting for response: {e}")
            return False
    
    def extract_response_content(self):
        """Extract the response content from Copilot"""
        try:
            print("📖 Extracting response content...")
            
            # Selectors for response content
            content_selectors = [
                '[data-testid="chat-message"]:last-child',
                '.chat-message:last-child',
                '[role="group"]:last-child',
                '.response-message:last-child',
                '[class*="message"]:last-child div',
                '[class*="response"]:last-child'
            ]
            
            for selector in content_selectors:
                try:
                    response_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if response_element and response_element.text.strip():
                        content = response_element.text.strip()
                        print(f"✅ Found response content: {len(content)} characters")
                        print(f"📝 Preview: {content[:100]}...")
                        return content
                except:
                    continue
            
            # Fallback: get all visible text from the page and try to find JSON
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                # Look for JSON patterns in the text
                json_pattern = r'\{[^{}]*"business_name"[^{}]*\}'
                matches = re.finditer(json_pattern, page_text, re.DOTALL)
                
                for match in matches:
                    potential_json = match.group()
                    if len(potential_json) > 50:  # Reasonable JSON length
                        print(f"✅ Found potential JSON response via regex")
                        return potential_json
                        
            except:
                pass
            
            print("❌ Could not extract response content")
            return None
            
        except Exception as e:
            print(f"❌ Error extracting response: {e}")
            return None
    
    def parse_response_to_data(self, response_content, business_data):
        """Parse Copilot response into structured data"""
        try:
            print("🔍 Parsing response content...")
            
            # First try to parse as JSON
            try:
                # Clean the response
                cleaned_content = response_content.strip()
                
                # Remove markdown formatting if present
                cleaned_content = re.sub(r'```json\s*', '', cleaned_content)
                cleaned_content = re.sub(r'```\s*$', '', cleaned_content)
                
                # Find JSON content
                if '{' in cleaned_content and '}' in cleaned_content:
                    start = cleaned_content.find('{')
                    end = cleaned_content.rfind('}') + 1
                    json_part = cleaned_content[start:end]
                    
                    data = json.loads(json_part)
                    
                    return {
                        'email': data.get('email', 'N/A'),
                        'background': data.get('background', 'N/A'),
                        'status': 'success' if data.get('search_status') == 'success' else 'failed',
                        'source': data.get('source', 'Copilot search')
                    }
                    
            except json.JSONDecodeError:
                print("⚠️  JSON parsing failed, trying fallback extraction...")
            
            # Fallback: regex extraction
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, response_content)
            
            # Extract potential background info (first 200 chars of meaningful text)
            background = 'N/A'
            if len(response_content) > 100:
                # Remove common phrases and get business description
                clean_text = re.sub(r'(I found|Here is|The email|Contact|Search results)', '', response_content)
                background = clean_text[:200].strip() if clean_text.strip() else 'N/A'
            
            return {
                'email': emails[0] if emails else 'N/A',
                'background': background,
                'status': 'success' if emails else 'failed',
                'source': 'Copilot search (regex extracted)'
            }
            
        except Exception as e:
            print(f"❌ Error parsing response: {e}")
            return {
                'email': 'N/A',
                'background': 'N/A',
                'status': 'parse_error',
                'source': 'Error',
                'error': str(e)
            }
    
    def process_business_for_email(self, business_data):
        """Process a single business for email extraction"""
        try:
            print(f"\n🏢 === Processing: {business_data.get('title', 'Unknown')} ===")
            
            # Input the prompt
            if not self.input_prompt_to_copilot(business_data):
                print("❌ Failed to input prompt")
                return None
            
            # Send the message
            if not self.send_message():
                print("❌ Failed to send message")
                return None
            
            # Wait for response
            if not self.wait_for_response(timeout=45):
                print("❌ No response received within timeout")
                return {
                    'email': 'N/A',
                    'background': 'N/A',
                    'status': 'timeout',
                    'source': 'Timeout'
                }
            
            # Extract response content
            response_content = self.extract_response_content()
            if not response_content:
                print("❌ Could not extract response content")
                return {
                    'email': 'N/A',
                    'background': 'N/A',
                    'status': 'no_content',
                    'source': 'No content'
                }
            
            # Parse the response
            parsed_data = self.parse_response_to_data(response_content, business_data)
            
            print(f"✅ Successfully processed: {business_data.get('title', 'Unknown')}")
            print(f"📧 Email found: {parsed_data['email']}")
            
            return parsed_data
            
        except Exception as e:
            print(f"❌ Error processing business: {e}")
            return {
                'email': 'N/A',
                'background': 'N/A',
                'status': 'error',
                'source': 'Error',
                'error': str(e)
            }
    
    def process_scraped_data_free(self, scraped_data, delay=45):
        """
        Process scraped data using free Copilot method
        
        Args:
            scraped_data (list): List of business data dictionaries
            delay (int): Delay between each business processing (default 45s)
        
        Returns:
            dict: Processing results with extracted emails
        """
        
        print(f"\n🆓 === Starting FREE Email Extraction with Copilot ===")
        print(f"📊 Total businesses to process: {len(scraped_data)}")
        print(f"⏱️  Estimated time: {len(scraped_data) * (delay + 45) / 60:.1f} minutes")
        
        # Navigate to Copilot
        if not self.navigate_to_copilot():
            print("❌ Failed to navigate to Copilot")
            return {'success': False, 'error': 'Navigation failed'}
        
        # Handle any popup modals
        # self.handle_popup_modals()
        
        # Wait for user interaction if needed and not headless
        if not self.headless:
            input("\n🔐 Please complete any setup if required, then press Enter to continue...")
        
        results = {
            'success': True,
            'processed': 0,
            'failed': 0,
            'businesses': []
        }
        
        # Process each business
        for i, business in enumerate(scraped_data, 1):
            print(f"\n📋 Processing {i}/{len(scraped_data)}")
            
            # Convert list format to dict if needed
            if isinstance(business, list):
                business_data = {
                    'title': business[0] if len(business) > 0 else 'N/A',
                    'rating_and_reviews': business[1] if len(business) > 1 else 'N/A',
                    'address': business[2] if len(business) > 2 else 'N/A',
                    'website': business[3] if len(business) > 3 else 'N/A',
                    'phone': business[4] if len(business) > 4 else 'N/A'
                }
            else:
                business_data = business
            
            # Process the business
            extraction_result = self.process_business_for_email(business_data)
            
            if extraction_result and extraction_result['status'] in ['success', 'failed']:
                results['processed'] += 1
                print(f"✅ Successfully processed: {business_data.get('title', 'Unknown')}")
            else:
                results['failed'] += 1
                print(f"❌ Failed to process: {business_data.get('title', 'Unknown')}")
            
            # Store the result
            business_result = {
                'title': business_data.get('title', 'N/A'),
                'rating_and_reviews': business_data.get('rating_and_reviews', 'N/A'),
                'address': business_data.get('address', 'N/A'),
                'website': business_data.get('website', 'N/A'),
                'phone': business_data.get('phone', 'N/A'),
                'email': extraction_result['email'] if extraction_result else 'N/A',
                'background': extraction_result['background'] if extraction_result else 'N/A',
                'extraction_status': extraction_result['status'] if extraction_result else 'error',
                'source': extraction_result.get('source', 'Unknown') if extraction_result else 'Unknown',
                'timestamp': datetime.now().isoformat()
            }
            
            results['businesses'].append(business_result)
            
            # Add delay between businesses (except for the last one)
            if i < len(scraped_data):
                print(f"⏳ Waiting {delay} seconds before next business...")
                time.sleep(delay)
        
        print(f"\n🎉 === Email Extraction Complete ===")
        print(f"✅ Successfully processed: {results['processed']}")
        print(f"❌ Failed to process: {results['failed']}")
        
        # Count successful email extractions
        successful_emails = len([b for b in results['businesses'] if b['email'] != 'N/A'])
        print(f"📧 Emails found: {successful_emails}")
        
        return results
    
    def close(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                print("🔒 Copilot browser closed")
        except Exception as e:
            print(f"⚠️  Error closing browser: {e}")

# Test function
def test_copilot_email_extractor():
    """Test the Copilot email extractor with sample data"""
    
    print("🧪 === Testing Copilot Email Extractor ===")
    
    # Get user preferences
    headless_choice = input("Run in headless mode? (y/n): ").strip().lower() == 'y'
    browser_choice = input("Choose browser (1=Firefox, 2=Chrome): ").strip()
    browser_type = 'chrome' if browser_choice == '2' else 'firefox'
    
    # Sample business data
    sample_data = [
        {
            'title': 'Starbucks Coffee',
            'rating_and_reviews': '4.5 (123)',
            'address': '123 Main St, New York, NY 10001',
            'website': 'www.starbucks.com',
            'phone': '555-1234'
        }
    ]
    
    # Initialize extractor
    extractor = FreeEmailExtractor(headless=headless_choice, browser_type=browser_type)
    
    try:
        # Process the sample data
        results = extractor.process_scraped_data_free(sample_data, delay=30)
        
        print(f"\n📊 === Test Results ===")
        print(f"Success: {results['success']}")
        print(f"Processed: {results['processed']}")
        print(f"Failed: {results['failed']}")
        
        if results['businesses']:
            for business in results['businesses']:
                print(f"\n🏢 {business['title']}")
                print(f"📧 Email: {business['email']}")
                print(f"📝 Background: {business['background'][:100]}...")
                print(f"✅ Status: {business['extraction_status']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None
        
    finally:
        extractor.close()

if __name__ == "__main__":
    test_copilot_email_extractor()