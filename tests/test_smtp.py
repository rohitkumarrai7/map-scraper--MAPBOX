import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_smtp_connection(smtp_email, smtp_password):
    """
    Test SMTP connection with Gmail
    
    Args:
        smtp_email (str): Gmail address
        smtp_password (str): App password or regular password
    
    Returns:
        dict: Test results
    """
    print(f"🧪 Testing SMTP connection for: {smtp_email}")
    
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = smtp_email
        message["To"] = smtp_email  # Send to self for testing
        message["Subject"] = "SMTP Test - Google Maps Scraper"
        
        body = """
        This is a test email from the Google Maps Scraper application.
        
        If you receive this email, your SMTP settings are working correctly!
        
        You can now use the cold email feature in the web application.
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Create SMTP session
        print("🔌 Connecting to Gmail SMTP server...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            print("✅ Connected to Gmail SMTP server")
            
            print("🔐 Attempting to login...")
            server.login(smtp_email, smtp_password)
            print("✅ Login successful!")
            
            print("📤 Sending test email...")
            text = message.as_string()
            server.sendmail(smtp_email, smtp_email, text)
            print("✅ Test email sent successfully!")
            
            return {
                'success': True,
                'message': 'SMTP connection and email sending successful!',
                'details': 'Test email sent to your own address'
            }
            
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"❌ Authentication failed: {e}"
        print(error_msg)
        return {
            'success': False,
            'error': 'Authentication failed',
            'details': str(e),
            'suggestion': 'Make sure you are using an App Password, not your regular Gmail password. Enable 2FA and generate an App Password in your Google Account settings.'
        }
        
    except smtplib.SMTPException as e:
        error_msg = f"❌ SMTP error: {e}"
        print(error_msg)
        return {
            'success': False,
            'error': 'SMTP error',
            'details': str(e)
        }
        
    except Exception as e:
        error_msg = f"❌ Unexpected error: {e}"
        print(error_msg)
        return {
            'success': False,
            'error': 'Unexpected error',
            'details': str(e)
        }

def main():
    """Main function to run SMTP test"""
    print("🧪 === Gmail SMTP Test ===")
    print("This will test your Gmail SMTP settings for the cold email feature.")
    print()
    
    # Get SMTP credentials
    smtp_email = input("Enter your Gmail address: ").strip()
    smtp_password = input("Enter your Gmail App Password: ").strip()
    
    if not smtp_email or not smtp_password:
        print("❌ Email and password are required!")
        return
    
    print()
    result = test_smtp_connection(smtp_email, smtp_password)
    
    print()
    print("📊 === Test Results ===")
    if result['success']:
        print("✅ SMTP Test PASSED!")
        print(f"📝 {result['message']}")
        print(f"ℹ️  {result['details']}")
        print()
        print("🎉 Your SMTP settings are working correctly!")
        print("You can now use the cold email feature in the web application.")
    else:
        print("❌ SMTP Test FAILED!")
        print(f"🚨 Error: {result['error']}")
        print(f"📝 Details: {result['details']}")
        if 'suggestion' in result:
            print(f"💡 Suggestion: {result['suggestion']}")
        print()
        print("🔧 Please fix your SMTP settings before using the cold email feature.")

if __name__ == "__main__":
    main() 