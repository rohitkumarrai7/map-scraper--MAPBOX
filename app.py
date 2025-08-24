from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
import csv
from datetime import datetime
import threading
import time
from werkzeug.utils import secure_filename
import pandas as pd

# Import the scraper modules
from integrated_scraper import (
    create_driver, scroll_to_load_results, count_available_results,
    scrape_results, save_to_csv, save_to_json, convert_scraped_data_to_dict_format
)
from email_extractor import EmailExtractor
from free_email_extractor import FreeEmailExtractor
from email_sender import EmailSender
from config import BROWSER_CONFIG, SELENIUM_CONFIG

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Global variables to store scraping status and results
scraping_status = {
    'is_running': False,
    'progress': 0,
    'message': '',
    'results': [],
    'total_found': 0,
    'scraped_count': 0
}

# Global email sender instance
email_sender = None

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """Landing page with scraping functionality"""
    return render_template('index.html')

@app.route('/email')
def email_page():
    """Cold emailing page"""
    # Get list of available data files from data directory
    data_files = []
    data_dir = 'data'
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith(('.csv', '.json')) and 'scraped_data' in file:
                data_files.append(file)
    
    return render_template('email.html', data_files=data_files)

@app.route('/api/start-scraping', methods=['POST'])
def start_scraping():
    """API endpoint to start scraping process"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({'error': 'Scraping is already running'}), 400
    
    data = request.get_json()
    
    # Extract parameters
    search_query = data.get('search_query', '').replace(' ', '+')
    browser_type = data.get('browser_type', 'firefox')
    headless_mode = data.get('headless_mode', False)
    storage_format = data.get('storage_format', 'csv')
    email_extraction = data.get('email_extraction', 'skip')
    perplexity_api_key = data.get('perplexity_api_key', '')
    max_results = data.get('max_results', 50)
    
    if not search_query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Reset status
    scraping_status = {
        'is_running': True,
        'progress': 0,
        'message': 'Initializing scraper...',
        'results': [],
        'total_found': 0,
        'scraped_count': 0
    }
    
    # Start scraping in background thread
    thread = threading.Thread(
        target=run_scraping,
        args=(search_query, browser_type, headless_mode, storage_format, 
              email_extraction, perplexity_api_key, max_results)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started successfully'})

def run_scraping(search_query, browser_type, headless_mode, storage_format, 
                email_extraction, perplexity_api_key, max_results):
    """Background function to run the scraping process"""
    global scraping_status
    
    try:
        scraping_status['message'] = 'Creating browser driver...'
        driver = create_driver(browser_type, headless_mode)
        
        scraping_status['message'] = 'Navigating to Google Maps...'
        driver.get(f"https://www.google.com/maps/search/{search_query}")
        
        query_display = search_query.replace("+", " ")
        scraping_status['message'] = 'Loading search results...'
        scroll_to_load_results(driver, query_display)
        
        scraping_status['message'] = 'Counting available results...'
        total_results = count_available_results(driver, query_display)
        scraping_status['total_found'] = total_results
        
        if total_results == 0:
            scraping_status['message'] = 'No results found'
            scraping_status['is_running'] = False
            return
        
        scraping_status['message'] = f'Scraping {min(max_results, total_results)} results...'
        scraped_data = scrape_results(driver, query_display, min(max_results, total_results))
        scraping_status['scraped_count'] = len(scraped_data)
        
        if not scraped_data:
            scraping_status['message'] = 'No data was scraped'
            scraping_status['is_running'] = False
            return
        
        # Save basic data
        scraping_status['message'] = 'Saving scraped data...'
        if storage_format == 'json':
            filename = save_to_json(scraped_data, query_display)
        else:
            filename = save_to_csv(scraped_data, query_display)
        
        # Email extraction if requested
        if email_extraction != 'skip':
            scraping_status['message'] = 'Starting email extraction...'
            
            if email_extraction == 'api' and perplexity_api_key:
                extractor = EmailExtractor(perplexity_api_key)
                enhanced_data = extractor.process_scraped_data(scraped_data, delay=2)
                
                if storage_format == 'json':
                    # Update JSON file with email data
                    with open(filename, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    for i, place in enumerate(json_data['places']):
                        if i < len(enhanced_data):
                            place['email'] = enhanced_data[i]['email']
                            place['background'] = enhanced_data[i]['background']
                            place['extraction_status'] = enhanced_data[i]['extraction_status']
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                else:
                    extractor.save_enhanced_data_to_csv(enhanced_data, query_display)
            
            elif email_extraction == 'free':
                dict_scraped_data = convert_scraped_data_to_dict_format(scraped_data)
                free_extractor = FreeEmailExtractor(headless=headless_mode, browser_type=browser_type)
                
                try:
                    free_results = free_extractor.process_scraped_data_free(dict_scraped_data, delay=15)
                    scraping_status['message'] = f'Free email extraction completed: {free_results["processed"]} processed'
                except Exception as e:
                    scraping_status['message'] = f'Error in free email extraction: {str(e)}'
                finally:
                    free_extractor.close()
        
        scraping_status['message'] = f'Scraping completed! Saved {len(scraped_data)} results to {filename}'
        scraping_status['results'] = scraped_data
        scraping_status['progress'] = 100
        
    except Exception as e:
        scraping_status['message'] = f'Error during scraping: {str(e)}'
    finally:
        scraping_status['is_running'] = False
        if 'driver' in locals():
            driver.quit()

@app.route('/api/scraping-status')
def get_scraping_status():
    """API endpoint to get current scraping status"""
    return jsonify(scraping_status)

@app.route('/api/send-cold-email', methods=['POST'])
def send_cold_email():
    """API endpoint to send cold emails"""
    global email_sender
    
    data = request.get_json()
    
    file_path = data.get('file_path')
    email_type = data.get('email_type', 'partnership')
    sender_email = data.get('sender_email')
    sender_name = data.get('sender_name')
    smtp_email = data.get('smtp_email')
    smtp_password = data.get('smtp_password')
    delay_between_emails = data.get('delay_between_emails', 30)
    openai_api_key = data.get('openai_api_key')
    edited_content = data.get('edited_content', [])
    
    if not all([file_path, sender_email, sender_name, smtp_email, smtp_password, openai_api_key]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Check if file exists in data directory
    data_file_path = os.path.join('data', file_path)
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    
    try:
        # Initialize email sender
        email_sender = EmailSender(openai_api_key)
        
        # Campaign configuration
        campaign_config = {
            'email_type': email_type,
            'sender_email': sender_email,
            'sender_name': sender_name,
            'smtp_credentials': {
                'email': smtp_email,
                'password': smtp_password
            },
            'delay_between_emails': delay_between_emails,
            'edited_content': edited_content
        }
        
        # Start campaign in background thread
        def campaign_callback(status):
            global email_sender
            email_sender.campaign_status = status
        
        thread = threading.Thread(
            target=email_sender.run_email_campaign,
            args=(data_file_path, campaign_config, campaign_callback)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'message': 'Email campaign started successfully',
            'status': 'running'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error starting campaign: {str(e)}'}), 500

@app.route('/api/email-campaign-status')
def get_email_campaign_status():
    """Get email campaign status"""
    global email_sender
    
    if email_sender is None:
        return jsonify({
            'is_running': False,
            'status_message': 'No campaign running'
        })
    
    return jsonify(email_sender.get_campaign_status())

@app.route('/api/stop-email-campaign', methods=['POST'])
def stop_email_campaign():
    """Stop email campaign"""
    global email_sender
    
    if email_sender:
        email_sender.stop_campaign()
        return jsonify({'message': 'Campaign stopped successfully'})
    
    return jsonify({'error': 'No campaign running'}), 400

@app.route('/api/generate-email-content', methods=['POST'])
def generate_email_content():
    """Generate email content for a specific business"""
    data = request.get_json()
    
    business_data = data.get('business_data')
    email_type = data.get('email_type', 'partnership')
    openai_api_key = data.get('openai_api_key')
    
    if not all([business_data, openai_api_key]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        email_sender = EmailSender(openai_api_key)
        content = email_sender.generate_email_content(business_data, email_type)
        
        return jsonify({
            'subject': content['subject'],
            'body': content['body'],
            'word_count': content.get('word_count', 0),
            'generated_at': content.get('generated_at', datetime.now().isoformat())
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating content: {str(e)}'}), 500

@app.route('/api/generate-all-email-content', methods=['POST'])
def generate_all_email_content():
    """Generate email content for all businesses in a file"""
    data = request.get_json()
    
    file_path = data.get('file_path')
    email_type = data.get('email_type', 'partnership')
    openai_api_key = data.get('openai_api_key')
    
    if not all([file_path, openai_api_key]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Check if file exists in data directory
    data_file_path = os.path.join('data', file_path)
    if not os.path.exists(data_file_path):
        return jsonify({'error': 'Data file not found'}), 404
    
    try:
        # Load data
        if file_path.endswith('.json'):
            with open(data_file_path, 'r', encoding='utf-8') as f:
                data_content = json.load(f)
                businesses = data_content.get('places', [])
        else:
            import pandas as pd
            df = pd.read_csv(data_file_path)
            businesses = df.to_dict('records')
        
        # Generate content for first 5 businesses (for preview)
        email_sender = EmailSender(openai_api_key)
        generated_content = []
        
        for i, business in enumerate(businesses[:5]):  # Limit to first 5 for preview
            try:
                content = email_sender.generate_email_content(business, email_type)
                generated_content.append({
                    'business': business,
                    'content': content
                })
            except Exception as e:
                generated_content.append({
                    'business': business,
                    'content': {
                        'subject': f"Partnership Opportunity for {business.get('title', 'Business')}",
                        'body': f"Hi {business.get('title', 'Business')} team,\n\nI hope this email finds you well. I came across your business and was impressed by your work.\n\nI believe we could create a valuable partnership that would benefit both our companies.\n\nWould you be interested in a brief call to discuss potential collaboration opportunities?\n\nBest regards,\n[Your Name]",
                        'word_count': 0,
                        'error': str(e)
                    }
                })
        
        return jsonify({
            'generated_content': generated_content,
            'total_businesses': len(businesses)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating content: {str(e)}'}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download scraped data files"""
    try:
        file_path = os.path.join('data', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/preview-data/<filename>')
def preview_data(filename):
    """Preview scraped data files"""
    try:
        file_path = os.path.join('data', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            return jsonify(df.to_dict('records'))
        elif filename.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify(data)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 