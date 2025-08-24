# config.py - Configuration file for the Maps Scraper

# Perplexity API Configuration
PERPLEXITY_CONFIG = {
    'base_url': 'https://api.perplexity.ai/chat/completions',
    'model': 'sonar',
    'timeout': 30,
    'default_delay': 2,  # Delay between API calls in seconds
}

# Selenium Configuration
SELENIUM_CONFIG = {
    'implicit_wait': 10,
    'page_load_timeout': 30,
    'max_scroll_attempts': 50,
    'max_click_attempts': 3,
    'default_window_size': (1920, 1080),  # For headless mode
}

# Browser Configuration
BROWSER_CONFIG = {
    'default_browser': 'firefox',  # 'firefox' or 'chrome'
    'default_headless': False,     # True for headless mode by default
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# File Settings
FILE_CONFIG = {
    'timestamp_format': '%Y%m%d_%H%M%S',
    'csv_encoding': 'utf-8',
    'json_indent': 2,
}

# CSV Headers
CSV_HEADERS = {
    'basic': ["Title", "Rating & Reviews", "Address", "Website", "Phone", "Search Query"],
    'enhanced': [
        "Title", "Rating & Reviews", "Address", "Website", 
        "Phone", "Email", "Background", "Search Query", "Extraction Status"
    ]
}

# Firefox Options
FIREFOX_OPTIONS = {
    'common': [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
    ],
    'headless': [
        "--headless",
        "--disable-gpu",
        "--window-size=1920,1080",
    ],
    'performance': [
        "--disable-images",
        "--disable-javascript",  # Use carefully, may break functionality
        "--disable-plugins",
        "--disable-java",
        "--disable-flash",
    ]
}

# Chrome Options
CHROME_OPTIONS = {
    'common': [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
    ],
    'headless': [
        "--headless",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--virtual-time-budget=2000",
    ],
    'performance': [
        "--disable-images",
        "--disable-javascript",  # Use carefully, may break functionality
        "--no-zygote",
        "--single-process",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-sync",
    ],
    'stealth': [
        "--disable-blink-features=AutomationControlled",
        "--exclude-switches=enable-automation",
        "--useAutomationExtension=false",
    ]
}

# CSS Selectors (in case Google changes them, easier to update)
SELECTORS = {
    'results_sidebar': "div[aria-label='Results for {query}']",
    'result_items': 'div.Nv2PK',
    'clickable_link': 'a',
    'title': 'h1.DUwDvf.lfPIob',
    'rating_div': 'div.F7nice',
    'rating_value': 'span[aria-hidden="true"]',
    'review_count': 'span[aria-label*="reviews"]',
    'address': 'div.Io6YTe.fontBodyMedium.kR99db.fdkmkc',
    'website': 'div.rogA2c.ITvuef',
    'phone': 'button[data-item-id^="phone"] .Io6YTe',
    'end_of_results': "You've reached the end of the list.",
}

# API Rate Limiting
RATE_LIMIT_CONFIG = {
    'requests_per_minute': 20,
    'retry_attempts': 3,
    'retry_delay': 5,
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file_enabled': True,
    'console_enabled': True,
    'emojis_enabled': True,  # Enable emoji logging for better UX
}

# Headless Mode Configuration
HEADLESS_CONFIG = {
    'window_size': (1920, 1080),
    'timeout_multiplier': 1.5,  # Increase timeouts in headless mode
    'extra_wait_time': 2,       # Additional wait time for elements
    'screenshot_on_error': True, # Take screenshot on error in headless mode
    'save_page_source': True,   # Save page source on error
}