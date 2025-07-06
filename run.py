#!/usr/bin/env python3
"""
AI Job Aggregator - Danish AI Consultancy Jobs
Run script to start the application
"""

import sys
import os
import subprocess
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import requests
        import bs4
        import selenium
        import pandas
        import sqlalchemy
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def setup_chrome_check():
    """Check if Chrome is available"""
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Test Chrome WebDriver
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.quit()
        print("✓ Chrome WebDriver is working")
        return True
    except Exception as e:
        print(f"✗ Chrome WebDriver issue: {e}")
        print("Please ensure Chrome browser is installed")
        return False

def main():
    """Main function to run the application"""
    print("🤖 AI Job Aggregator - Danish AI Consultancy Jobs")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Chrome setup
    if not setup_chrome_check():
        print("⚠️  Chrome WebDriver not available. Some scraping features may not work.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Start the application
    print("\n🚀 Starting AI Job Aggregator...")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("🔄 Automatic scraping scheduled for 9 AM daily")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Import and run the app
        from app.main import app
        import uvicorn
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=False
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 AI Job Aggregator stopped")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()