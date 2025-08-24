# 🗺️ Google Maps Scraper & Cold Email Automation

A professional Flask-based web application that combines Google Maps business data scraping with AI-powered cold email automation. This tool helps businesses find potential clients and automatically generate personalized outreach emails.

## ✨ Features

### 🔍 **Web Scraping**
- **Google Maps Integration**: Scrape business data from Google Maps search results
- **Flexible Browser Support**: Works with Firefox and Chrome (visible or headless mode)
- **Data Extraction**: Captures business names, addresses, websites, phone numbers, and ratings
- **Real-time Progress**: Live progress tracking during scraping operations
- **Multiple Formats**: Save data in CSV or JSON format

### 📧 **Cold Email Automation**
- **AI-Powered Content Generation**: Uses OpenAI API to create personalized email content
- **Background Integration**: Leverages scraped business background for personalized messaging
- **Multiple Email Types**: Partnership, collaboration, and custom email templates
- **SMTP Integration**: Send emails directly through Gmail SMTP
- **Preview & Edit**: Review and edit generated content before sending
- **Campaign Management**: Start, stop, and monitor email campaigns

### 🎯 **Key Capabilities**
- **Two-Page Interface**: Separate pages for scraping and email automation
- **Real-time Status Updates**: Live progress tracking for both scraping and email campaigns
- **Data Management**: Preview, download, and manage scraped data files
- **Professional UI**: Modern, responsive interface built with Bootstrap 5
- **Error Handling**: Comprehensive error handling and user feedback

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Firefox or Chrome browser
- Gmail account (for email sending)
- OpenAI API key (for content generation)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Google-Maps-Scrapper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install browser drivers**
   - **Firefox**: Download [GeckoDriver](https://github.com/mozilla/geckodriver/releases)
   - **Chrome**: Download [ChromeDriver](https://chromedriver.chromium.org/)
   - Add drivers to your system PATH

4. **Set up Gmail App Password**
   - Enable 2-Factor Authentication on your Gmail account
   - Generate an App Password for "Mail"
   - Use this App Password instead of your regular password

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the web interface**
   - Open your browser and go to `http://localhost:5000`
   - Use Page 1 for scraping, Page 2 for cold email automation

## 📁 Project Structure

```
Google-Maps-Scrapper/
├── app.py                          # Main Flask application
├── integrated_scraper.py           # Core scraping functionality
├── email_extractor.py              # Perplexity AI email extraction
├── free_email_extractor.py         # Microsoft Copilot email extraction
├── email_sender.py                 # OpenAI email generation & SMTP sending
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── data/                           # Scraped data storage
│   ├── scraped_data_*.json        # JSON format data
│   └── scraped_data_*.csv         # CSV format data
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── index.html                  # Scraping page
│   └── email.html                  # Cold email page
├── utils/                          # Utility scripts
│   └── fix_background_fields.py    # Background field management
└── tests/                          # Test scripts
    └── test_smtp.py                # SMTP connection testing
```

## 🎮 Usage Guide

### Page 1: Web Scraping

1. **Enter Search Query**: Type your search term (e.g., "plumbers in New York")
2. **Choose Browser**: Select Firefox or Chrome
3. **Select Mode**: Choose visible or headless mode
4. **Storage Format**: Select CSV or JSON output
5. **Email Extraction**: Choose API (paid) or Free method
6. **Start Scraping**: Click "Start Scraping" and monitor progress
7. **Download Results**: Download your scraped data when complete

### Page 2: Cold Email Automation

1. **Select Data File**: Choose a scraped data file from the dropdown
2. **Configure SMTP**: Enter your Gmail credentials
3. **Enter OpenAI API Key**: Provide your OpenAI API key for content generation
4. **Choose Email Type**: Select partnership, collaboration, or custom
5. **Generate Content**: Click "Generate & Preview Content" to create personalized emails
6. **Review & Edit**: Preview and edit the generated content
7. **Start Campaign**: Click "Start Auto Campaign" to send emails

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI API Key (required for email generation)
OPENAI_API_KEY=your_openai_api_key_here

# Perplexity API Key (optional, for email extraction)
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

### SMTP Configuration
The application uses Gmail SMTP with the following settings:
- **Server**: smtp.gmail.com
- **Port**: 465 (SSL)
- **Authentication**: Gmail App Password required

## 🧪 Testing

### Test SMTP Connection
```bash
python tests/test_smtp.py
```

### Fix Background Fields
If your scraped data is missing background fields:
```bash
python utils/fix_background_fields.py
```

## 📊 Data Formats

### JSON Format
```json
{
  "search_query": "plumbers in new york",
  "scraped_at": "2025-08-03T01:11:38.784986",
  "total_results": 14,
  "places": [
    {
      "title": "RR Plumbing Roto-Rooter",
      "rating_and_reviews": "4.8 (1,454)",
      "address": "450 7th Ave Ste B, New York, NY 10123",
      "website": "rotorooter.com",
      "phone": "+1 212-687-1215",
      "email": "N/A",
      "background": "RR Plumbing Roto-Rooter located at 450 7th Ave Ste B, New York, NY 10123, United States with website rotorooter.com with rating 4.8 (1,454). They provide high-quality services in their industry and have established a strong reputation in their local market."
    }
  ]
}
```

### CSV Format
```csv
Title,Rating & Reviews,Address,Website,Phone,Search Query
RR Plumbing Roto-Rooter,4.8 (1,454),450 7th Ave Ste B New York NY,rotorooter.com,+1 212-687-1215,plumbers in new york
```

## 🔒 Security & Privacy

- **API Keys**: Store API keys securely and never commit them to version control
- **SMTP Credentials**: Use Gmail App Passwords instead of regular passwords
- **Data Privacy**: Scraped data is stored locally and not shared
- **Rate Limiting**: Built-in delays to respect service providers' rate limits

## 🐛 Troubleshooting

### Common Issues

1. **Browser Driver Issues**
   - Ensure browser drivers are installed and in PATH
   - Update drivers to match your browser version

2. **SMTP Authentication Errors**
   - Use Gmail App Password, not regular password
   - Enable 2-Factor Authentication on Gmail

3. **OpenAI API Errors**
   - Verify your API key is correct
   - Check your OpenAI account balance

4. **Scraping Failures**
   - Try different browser (Firefox/Chrome)
   - Use visible mode for debugging
   - Check internet connection

### Error Messages

- **"Failed to decode response from marionette"**: Browser driver issue, try restarting
- **"Authentication failed"**: SMTP credentials issue, check App Password
- **"No module named 'openai'"**: Install dependencies with `pip install -r requirements.txt`

## 📈 Recent Updates

### Version 2.0 (Current)
- ✅ **Flask Web Interface**: Complete web-based UI
- ✅ **AI Email Generation**: OpenAI-powered content creation
- ✅ **SMTP Integration**: Direct email sending capability
- ✅ **Background Field Management**: Automatic background generation
- ✅ **Professional Organization**: Clean project structure
- ✅ **Comprehensive Testing**: SMTP and functionality testing tools

### Version 1.0 (Previous)
- Basic terminal-based scraping
- Manual email extraction
- Limited automation capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Please:
- Respect websites' terms of service
- Follow email marketing regulations
- Use responsibly and ethically
- Comply with local laws and regulations

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Built with ❤️ using Python, Flask, Selenium, and OpenAI**