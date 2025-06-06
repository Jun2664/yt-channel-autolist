# YouTube Channel Auto-List (US/English Edition)

[![Python Version](https://img.shields.io/badge/python-3.11%2B%20|%203.12-blue)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions)](https://github.com/Jun2664/yt-channel-autolist/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📖 Project Overview

YouTube Channel Auto-List is a Python tool that automatically discovers, analyzes, and filters rapidly growing YouTube channels suitable for business partnerships. This version focuses exclusively on US/English content and uses web scraping instead of YouTube Data API to overcome API limitations.

### 🎯 Problems Solved

- **API Limitations**: No more YouTube Data API quota restrictions
- **Scale**: Can analyze 300+ channels per run (vs API limits)
- **Region Accuracy**: Searches from US perspective for authentic results
- **Language Focus**: English-only content for US market targeting
- **Quality Control**: Filters out low-subscriber and personal vlog channels

### 🚀 Key Features

- **Web Scraping**: Uses Selenium with undetected-chromedriver for reliable data collection
- **Anti-Detection**: Random user agents, delays, and browser fingerprint masking
- **English-Only Filter**: Automatic language detection to ensure English content
- **Subscriber Filtering**: Configurable min/max subscriber thresholds
- **Personal Branding Detection**: AI-powered detection of vlog/personal channels
- **Keyword Intelligence**: Extracts trending keywords from successful channels
- **Multiple Export Formats**: Google Sheets, JSON, or CSV output

### 📊 Use Cases

1. **Marketing Teams**: Find influencer partners in the US market
2. **Brand Managers**: Identify channels for product promotions
3. **Content Creators**: Competitive analysis and trend research
4. **Agencies**: Automated channel research for clients

## 🛠️ Setup Guide

### Prerequisites

- Python 3.11+ (Python 3.12 is supported with setuptools>=68)
- Chrome/Chromium browser
- pip or Poetry for package management
- Google Cloud account (for Sheets export only)

**Note for Python 3.12 users**: Python 3.12 removed the `distutils` module from the standard library. This project includes `setuptools>=68` in requirements.txt which provides a compatibility layer for packages that still depend on `distutils` (like undetected-chromedriver 3.5.4).

### 1. Clone Repository

```bash
git clone https://github.com/Jun2664/yt-channel-autolist.git
cd yt-channel-autolist
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Chrome Driver

The tool uses undetected-chromedriver which will automatically download the appropriate Chrome driver. Ensure you have Chrome or Chromium installed on your system.

### 4. Google Sheets Setup (Optional)

If you want to export to Google Sheets:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable these APIs:
   - Google Sheets API
   - Google Drive API
3. Create a service account and download the JSON key
4. Set the environment variable:
   ```bash
   export GOOGLE_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'
   ```

### 5. Configure Environment

Create a `.env` file or set environment variables:

```bash
# Scraping Configuration
US_MIN_SUBS=100              # Minimum subscriber count
US_MAX_SUBS=50000           # Maximum subscriber count
US_MAX_VIDEOS=30            # Maximum video count
SEARCH_LIMIT=1000           # Max channels to analyze per search
REQUEST_DELAY=2             # Delay between requests (seconds)

# Scraper Settings
USE_UNDETECTED_DRIVER=true  # Use undetected-chromedriver
SCRAPER_HEADLESS=true       # Run in headless mode
USER_AGENT_ROTATION=true    # Rotate user agents
MAX_RETRIES=3               # Max retry attempts
PAGE_TIMEOUT=30             # Page load timeout (seconds)

# Optional: Keyword Research APIs
VIDIQ_API_KEY=your_key_here
TUBEBUDDY_API_KEY=your_key_here
```

## 🎮 Usage

### Basic Usage

```bash
python main.py
```

### Command Line Options

```bash
# Use custom keywords file
python main.py --keywords-file my_keywords.txt

# Export to JSON
python main.py --output-format json

# Export to CSV
python main.py --output-format csv

# Enable debug logging
python main.py --debug
```

### Keywords File Format

Create a `keywords.txt` file with one keyword per line:

```
tech reviews
gaming setup
productivity tips
cooking tutorials
fitness motivation
```

## 📁 Output Formats

### Google Sheets (Default)
- Automatically creates a new spreadsheet
- Formats data with headers and filters
- Includes all channel metrics and analysis

### JSON Format
- Comprehensive data structure
- Includes all metadata and metrics
- File: `rising_channels_US_YYYYMMDD.json`

### CSV Format
- Tabular format for easy analysis
- Compatible with Excel/Google Sheets
- File: `rising_channels_US_YYYYMMDD.csv`

## ⚙️ Configuration Options

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| Min Subscribers | US_MIN_SUBS | 100 | Minimum subscriber count |
| Max Subscribers | US_MAX_SUBS | 50,000 | Maximum subscriber count |
| Max Videos | US_MAX_VIDEOS | 30 | Maximum video count |
| Spread Rate Min | US_SPREAD_RATE_MIN | 2.0 | Minimum view/subscriber ratio |
| Spread Rate Max | US_SPREAD_RATE_MAX | 6.0 | Maximum view/subscriber ratio |
| Channel Age | US_CHANNEL_AGE_DAYS | 60 | Maximum channel age in days |
| Search Limit | SEARCH_LIMIT | 1,000 | Max channels per search |
| Request Delay | REQUEST_DELAY | 2 | Seconds between requests |

## 🔒 Anti-Detection Features

1. **Undetected ChromeDriver**: Bypasses basic bot detection
2. **Random User Agents**: Rotates through real browser user agents
3. **Human-like Delays**: Random delays between 1-3 seconds
4. **Browser Fingerprinting**: Removes webdriver property
5. **Headless Mode**: Optional headless operation

## 🚨 Important Notes

- **Rate Limiting**: The tool includes delays to avoid being blocked
- **Public Data Only**: Only scrapes publicly available information
- **No Login Required**: Works without YouTube account
- **Resource Usage**: Selenium requires more resources than API calls
- **Execution Time**: Expect 30-60 minutes for 300 channels

## 🐛 Troubleshooting

### Chrome Driver Issues
- Ensure Chrome/Chromium is installed
- The tool auto-downloads matching driver version

### Language Detection Errors
- Some channels may be incorrectly filtered
- Check logs with `--debug` flag

### Timeout Errors
- Increase PAGE_TIMEOUT environment variable
- Check internet connection stability

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📮 Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues first
- Provide debug logs when reporting bugs