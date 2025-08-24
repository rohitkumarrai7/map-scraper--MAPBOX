import requests
import json
import time
from datetime import datetime

class EmailExtractor:
    def __init__(self, api_key):
        """
        Initialize the EmailExtractor with Perplexity API key
        
        Args:
            api_key (str): Your Perplexity API key
        """
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test API key on initialization
        self.test_api_connection()
    
    def test_api_connection(self):
        """Test if the API key is working"""
        test_payload = {
            "model": "sonar",
            "messages": [
                {"role": "user", "content": "Hello, just testing the connection. Please respond with 'OK'."}
            ],
            "max_tokens": 30
        }
        
        try:
            print("Testing Perplexity API connection...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print("✓ Perplexity API connection successful!")
                return True
            else:
                print(f"✗ API connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ API connection test failed: {e}")
            return False
    
    def extract_email_and_background(self, company_name, address, website="N/A", phone="N/A"):
        """
        Extract email and background information for a company using Perplexity API
        
        Args:
            company_name (str): Name of the company
            address (str): Company address
            website (str): Company website (optional)
            phone (str): Company phone (optional)
            
        Returns:
            dict: Contains 'email' and 'background' fields
        """
        
        # Construct a more specific search query
        search_query = f"""Find the contact email address and business background information for "{company_name}" located at {address}."""
        
        if website != "N/A" and website and website.strip():
            search_query += f" Their website is: {website}."
        if phone != "N/A" and phone and phone.strip():
            search_query += f" Their phone number is: {phone}."
            
        search_query += """
        
Please provide:
1. Email address (if available, otherwise "N/A")
1(a) If email address is not found on first try try one more time and search deeper.
2. Brief background about the business (what they do, specialties, etc.)

Return the information in the following JSON format only:
{
    "Email": "email@example.com or N/A",
    "Background": "Brief description of the business"
}
"""
        
        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a business research assistant. Find contact information and background details about businesses. Always respond with valid JSON format only, no additional text or explanations."
                },
                {
                    "role": "user",
                    "content": search_query
                }
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        try:
            print(f"Making API request for: {company_name}")
            print(f"Search query: {search_query[:100]}...")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            print(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"API Response received: {result}")
                
                content = result['choices'][0]['message']['content']
                print(f"Content received: {content}")
                
                # Parse the JSON response
                try:
                    # Clean the response in case it has markdown formatting
                    cleaned_content = content.replace('```json', '').replace('```', '').strip()
                    
                    # Try to find JSON content if it's embedded in text
                    if '{' in cleaned_content and '}' in cleaned_content:
                        start = cleaned_content.find('{')
                        end = cleaned_content.rfind('}') + 1
                        json_part = cleaned_content[start:end]
                    else:
                        json_part = cleaned_content
                    
                    print(f"Attempting to parse JSON: {json_part}")
                    data = json.loads(json_part)
                    
                    email = data.get('Email', 'N/A')
                    background = data.get('Background', 'N/A')
                    
                    # Clean up the data
                    if email and email.lower().strip() in ['n/a', 'not available', 'not found', '']:
                        email = 'N/A'
                    if background and background.lower().strip() in ['n/a', 'not available', 'not found', '']:
                        background = 'N/A'
                    
                    print(f"✓ Successfully extracted - Email: {email}, Background: {background[:50]}...")
                    
                    return {
                        'email': email,
                        'background': background,
                        'status': 'success'
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"✗ JSON parsing error for {company_name}: {e}")
                    print(f"Raw content: {content}")
                    
                    # Fallback: try to extract information manually
                    email = 'N/A'
                    background = content[:200] if content else 'N/A'  # Use first 200 chars as background
                    
                    return {
                        'email': email,
                        'background': background,
                        'status': 'json_error',
                        'error': str(e),
                        'raw_response': content
                    }
            else:
                print(f"✗ API request failed for {company_name}: {response.status_code}")
                print(f"Error response: {response.text}")
                return {
                    'email': 'N/A',
                    'background': 'N/A',
                    'status': 'api_error',
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error for {company_name}: {e}")
            return {
                'email': 'N/A',
                'background': 'N/A',
                'status': 'request_error',
                'error': str(e)
            }
    
    def process_scraped_data(self, scraped_data, delay=3):
        """
        Process a list of scraped data and extract emails/backgrounds for each
        
        Args:
            scraped_data (list): List of scraped company data
            delay (int): Delay between API calls to avoid rate limiting
            
        Returns:
            list: Enhanced data with email and background information
        """
        enhanced_data = []
        
        print(f"Processing {len(scraped_data)} companies for email extraction...")
        
        for i, company in enumerate(scraped_data, 1):
            print(f"\n--- Processing {i}/{len(scraped_data)}: {company[0]} ---")
            
            # Extract email and background
            email_info = self.extract_email_and_background(
                company_name=company[0],  # Title
                address=company[2],       # Address
                website=company[3],       # Website
                phone=company[4]          # Phone
            )
            
            # Add the enhanced information to the original data
            enhanced_company = {
                'title': company[0],
                'rating_and_reviews': company[1],
                'address': company[2],
                'website': company[3],
                'phone': company[4],
                'email': email_info['email'],
                'background': email_info['background'],
                'extraction_status': email_info['status']
            }
            
            # Add error details if available
            if 'error' in email_info:
                enhanced_company['error_details'] = email_info['error']
            if 'raw_response' in email_info:
                enhanced_company['raw_api_response'] = email_info['raw_response']
            
            enhanced_data.append(enhanced_company)
            
            print(f"✓ Completed processing: {company[0]}")
            
            # Add delay to avoid rate limiting
            if i < len(scraped_data):  # Don't delay after the last item
                print(f"Waiting {delay} seconds before next request...")
                time.sleep(delay)
        
        print("\n=== Email extraction completed! ===")
        
        # Print summary
        successful = len([c for c in enhanced_data if c['extraction_status'] == 'success'])
        failed = len(enhanced_data) - successful
        print(f"Summary: {successful} successful, {failed} failed extractions")
        
        return enhanced_data
    
    def save_enhanced_data_to_csv(self, enhanced_data, search_query, filename=None):
        """
        Save enhanced data to CSV file
        
        Args:
            enhanced_data (list): Enhanced data with email and background
            search_query (str): Original search query
            filename (str): Optional custom filename
        """
        import csv
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_data_{timestamp}.csv"
        
        with open(filename, mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Title", "Rating & Reviews", "Address", "Website", 
                "Phone", "Email", "Background", "Search Query", "Extraction Status"
            ])
            
            for company in enhanced_data:
                writer.writerow([
                    company['title'],
                    company['rating_and_reviews'],
                    company['address'],
                    company['website'],
                    company['phone'],
                    company['email'],
                    company['background'],
                    search_query,
                    company['extraction_status']
                ])
        
        print(f"Enhanced data saved to {filename}")
    
    def save_enhanced_data_to_json(self, enhanced_data, search_query, filename=None):
        """
        Save enhanced data to JSON file
        
        Args:
            enhanced_data (list): Enhanced data with email and background
            search_query (str): Original search query
            filename (str): Optional custom filename
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_data_{timestamp}.json"
        
        json_data = {
            "search_query": search_query,
            "scraped_at": datetime.now().isoformat(),
            "total_results": len(enhanced_data),
            "extraction_summary": {
                "successful": len([c for c in enhanced_data if c['extraction_status'] == 'success']),
                "failed": len([c for c in enhanced_data if c['extraction_status'] != 'success'])
            },
            "places": enhanced_data
        }
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(json_data, file, indent=2, ensure_ascii=False)
        
        print(f"Enhanced data saved to {filename}")
        print(f"File contains {len(enhanced_data)} places with enhanced information")

# Example usage and testing functions
def test_email_extractor():
    """Test function to verify EmailExtractor functionality"""
    
    # Replace with your actual Perplexity API key
    API_KEY = "pplx....................."
    
    extractor = EmailExtractor(API_KEY)
    
    # Test with sample data
    sample_data = [
        ["Starbucks", "4.5 (123)", "123 Main St, New York, NY", "www.starbucks.com", "555-1234"],
        ["Local Cafe", "4.2 (89)", "456 Oak Ave, Los Angeles, CA", "N/A", "555-5678"]
    ]
    
    enhanced_data = extractor.process_scraped_data(sample_data)
    
    # Save results
    extractor.save_enhanced_data_to_csv(enhanced_data, "test cafes")
    extractor.save_enhanced_data_to_json(enhanced_data, "test cafes")
    
    return enhanced_data

if __name__ == "__main__":
    # Run test if executed directly
    test_email_extractor()
