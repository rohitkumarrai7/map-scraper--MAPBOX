#!/usr/bin/env python3
"""
Google Maps Scraper & Cold Email Automation - Startup Script
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        import selenium
        import pandas
        import openai
        import requests
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def check_data_directory():
    """Ensure data directory exists"""
    if not os.path.exists('data'):
        print("📁 Creating data directory...")
        os.makedirs('data')
        print("✅ Data directory created")

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Google Maps Scraper & Cold Email Automation...")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("⏳ Starting server...")
    
    try:
        # Start the Flask app
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("🗺️  Google Maps Scraper & Cold Email Automation")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Cannot start application due to missing dependencies")
        return
    
    # Check data directory
    check_data_directory()
    
    print()
    print("📋 Quick Start Guide:")
    print("1. The web interface will open automatically")
    print("2. Use Page 1 for Google Maps scraping")
    print("3. Use Page 2 for cold email automation")
    print("4. Press Ctrl+C to stop the application")
    print()
    
    # Ask if user wants to open browser automatically
    try:
        open_browser = input("🌐 Open browser automatically? (y/n): ").strip().lower()
        if open_browser == 'y':
            print("🌐 Opening browser in 3 seconds...")
            time.sleep(3)
            webbrowser.open('http://localhost:5000')
    except KeyboardInterrupt:
        pass
    
    print()
    start_application()

if __name__ == "__main__":
    main() 