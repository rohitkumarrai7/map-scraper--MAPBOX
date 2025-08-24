import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import openai
import json
import time
import threading
from datetime import datetime
import os

class EmailSender:
    def __init__(self, openai_api_key, smtp_config=None):
        """
        Initialize EmailSender with OpenAI API key and SMTP configuration
        
        Args:
            openai_api_key (str): OpenAI API key for content generation
            smtp_config (dict): SMTP configuration for sending emails
        """
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
        # Default SMTP configuration (Gmail)
        self.smtp_config = smtp_config or {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'use_tls': True
        }
        
        self.campaign_status = {
            'is_running': False,
            'total_emails': 0,
            'sent_emails': 0,
            'failed_emails': 0,
            'current_progress': 0,
            'status_message': '',
            'errors': []
        }
    
    def generate_email_content(self, business_data, email_type="partnership"):
        """
        Generate personalized email content using OpenAI
        
        Args:
            business_data (dict): Business information from scraped data
            email_type (str): Type of email (partnership, service, etc.)
            
        Returns:
            dict: Generated email content with subject and body
        """
        try:
            business_name = business_data.get('title', 'Business')
            address = business_data.get('address', '')
            website = business_data.get('website', '')
            phone = business_data.get('phone', '')
            background = business_data.get('background', '')
            rating = business_data.get('rating_and_reviews', '')
            
            # If no background, create one from available data
            if not background or background == 'N/A' or background == '':
                background = f"{business_name} is a professional business"
                if address:
                    background += f" located at {address}"
                if website and website != 'N/A':
                    background += f" with website {website}"
                if rating and rating != ' ':
                    background += f". They have a rating of {rating}"
                background += ". They provide high-quality services in their industry and have established a strong reputation in their local market."
            
            # Create context for OpenAI
            context = f"""
            Business Information:
            - Name: {business_name}
            - Address: {address}
            - Website: {website}
            - Phone: {phone}
            - Rating: {rating}
            - Background: {background}
            
            Email Type: {email_type}
            """
            
            # Generate subject line
            subject_prompt = f"""
            Generate a compelling email subject line for a {email_type} outreach to {business_name}.
            The subject should be professional, personalized, and under 60 characters.
            Return only the subject line, nothing else.
            """
            
            subject_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional email marketing expert."},
                    {"role": "user", "content": subject_prompt}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            subject = subject_response.choices[0].message.content.strip()
            
            # Generate email body with 300 word limit
            body_prompt = f"""
            Write a professional {email_type} outreach email for {business_name}.
            
            Business Context: {context}
            
            Requirements:
            - Personalized and relevant to their business
            - Professional tone
            - Include a clear call-to-action
            - MAXIMUM 300 words (strict limit)
            - Use their business name naturally
            - Mention their location or specific details if available
            - Use the background information to personalize the content
            - Keep it concise but engaging
            
            Format the email with proper greeting, body, and closing.
            """
            
            body_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional business development expert. Always keep emails under 300 words."},
                    {"role": "user", "content": body_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            body = body_response.choices[0].message.content.strip()
            
            # Ensure word limit
            words = body.split()
            if len(words) > 300:
                body = ' '.join(words[:300]) + '...'
            
            return {
                'subject': subject,
                'body': body,
                'word_count': len(body.split()),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'subject': f"Partnership Opportunity for {business_name}",
                'body': f"Hi {business_name} team,\n\nI hope this email finds you well. I came across your business at {address} and was impressed by your work.\n\nI believe we could create a valuable partnership that would benefit both our companies.\n\nWould you be interested in a brief call to discuss potential collaboration opportunities?\n\nBest regards,\n[Your Name]",
                'word_count': 0,
                'error': str(e)
            }
    
    def send_email(self, to_email, subject, body, from_email, from_name, smtp_credentials):
        """
        Send email using SMTP
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            body (str): Email body
            from_email (str): Sender email address
            from_name (str): Sender name
            smtp_credentials (dict): SMTP login credentials
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_config['smtp_server'], self.smtp_config['smtp_port']) as server:
                if self.smtp_config['use_tls']:
                    server.starttls(context=context)
                
                # Login to SMTP server
                server.login(smtp_credentials['email'], smtp_credentials['password'])
                
                # Send email
                text = msg.as_string()
                server.sendmail(from_email, to_email, text)
                
            return True
            
        except Exception as e:
            print(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def run_email_campaign(self, data_file, campaign_config, callback=None):
        """
        Run email campaign with automatic content generation
        
        Args:
            data_file (str): Path to scraped data file
            campaign_config (dict): Campaign configuration
            callback (function): Callback function for progress updates
        """
        self.campaign_status = {
            'is_running': True,
            'total_emails': 0,
            'sent_emails': 0,
            'failed_emails': 0,
            'current_progress': 0,
            'status_message': 'Starting campaign...',
            'errors': []
        }
        
        try:
            # Load data
            self.campaign_status['status_message'] = 'Loading data...'
            if callback:
                callback(self.campaign_status)
            
            if data_file.endswith('.json'):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    businesses = data.get('places', [])
            else:
                import pandas as pd
                df = pd.read_csv(data_file)
                businesses = df.to_dict('records')
            
            # Filter businesses with email addresses
            email_businesses = []
            for business in businesses:
                if business.get('email') and business['email'] != 'N/A':
                    email_businesses.append(business)
            
            self.campaign_status['total_emails'] = len(email_businesses)
            self.campaign_status['status_message'] = f'Found {len(email_businesses)} businesses with email addresses'
            
            if callback:
                callback(self.campaign_status)
            
            if len(email_businesses) == 0:
                self.campaign_status['status_message'] = 'No businesses with email addresses found'
                self.campaign_status['is_running'] = False
                if callback:
                    callback(self.campaign_status)
                return
            
            # Process each business
            for i, business in enumerate(email_businesses):
                if not self.campaign_status['is_running']:
                    break
                
                self.campaign_status['status_message'] = f'Processing {business.get("title", "Business")} ({i+1}/{len(email_businesses)})'
                self.campaign_status['current_progress'] = int((i / len(email_businesses)) * 100)
                
                if callback:
                    callback(self.campaign_status)
                
                try:
                    # Check if we have edited content for this business
                    edited_content = campaign_config.get('edited_content', [])
                    email_content = None
                    
                    # Look for edited content for this business index
                    for edited in edited_content:
                        if edited.get('index') == i:
                            email_content = {
                                'subject': edited.get('subject', ''),
                                'body': edited.get('body', '')
                            }
                            break
                    
                    # If no edited content, generate new content
                    if not email_content:
                        email_content = self.generate_email_content(business, campaign_config.get('email_type', 'partnership'))
                    
                    # Send email
                    success = self.send_email(
                        to_email=business['email'],
                        subject=email_content['subject'],
                        body=email_content['body'],
                        from_email=campaign_config['sender_email'],
                        from_name=campaign_config['sender_name'],
                        smtp_credentials=campaign_config['smtp_credentials']
                    )
                    
                    if success:
                        self.campaign_status['sent_emails'] += 1
                    else:
                        self.campaign_status['failed_emails'] += 1
                        self.campaign_status['errors'].append(f"Failed to send to {business.get('title', 'Unknown')}")
                    
                    # Delay between emails
                    time.sleep(campaign_config.get('delay_between_emails', 30))
                    
                except Exception as e:
                    self.campaign_status['failed_emails'] += 1
                    self.campaign_status['errors'].append(f"Error processing {business.get('title', 'Unknown')}: {str(e)}")
                
                # Update progress
                self.campaign_status['current_progress'] = int(((i + 1) / len(email_businesses)) * 100)
                if callback:
                    callback(self.campaign_status)
            
            # Campaign completed
            self.campaign_status['status_message'] = f'Campaign completed! Sent: {self.campaign_status["sent_emails"]}, Failed: {self.campaign_status["failed_emails"]}'
            self.campaign_status['is_running'] = False
            
            if callback:
                callback(self.campaign_status)
                
        except Exception as e:
            self.campaign_status['status_message'] = f'Campaign error: {str(e)}'
            self.campaign_status['is_running'] = False
            self.campaign_status['errors'].append(str(e))
            if callback:
                callback(self.campaign_status)
    
    def stop_campaign(self):
        """Stop the running email campaign"""
        self.campaign_status['is_running'] = False
        self.campaign_status['status_message'] = 'Campaign stopped by user'
    
    def get_campaign_status(self):
        """Get current campaign status"""
        return self.campaign_status.copy() 