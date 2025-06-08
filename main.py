#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime
from youtube_scraper import YouTubeScraper
from sheets_writer import SheetsWriter
from config import Config

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='YouTube Channel Auto-List - Discover rising YouTube channels (US/English only)'
    )
    parser.add_argument(
        '--keywords-file',
        type=str,
        default='keywords.txt',
        help='Path to keywords file (default: keywords.txt)'
    )
    parser.add_argument(
        '--output-format',
        type=str,
        default='sheets',
        choices=['sheets', 'json', 'csv'],
        help='Output format (default: sheets)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    return parser.parse_args()

def main():
    """Main process"""
    args = parse_arguments()
    
    # Set up logging
    import logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get configuration (fixed to US)
    region_config = Config.get_region_config('US')
    
    # Get API credentials (only for keyword research)
    api_keys = Config.get_api_keys()
    service_account_json = Config.get_google_credentials()
    
    if args.output_format == 'sheets' and not service_account_json:
        print("Error: GOOGLE_SERVICE_ACCOUNT_JSON is not set")
        sys.exit(1)
    
    # Load keywords file
    try:
        with open(args.keywords_file, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Keywords file '{args.keywords_file}' not found")
        sys.exit(1)
    
    print(f"Region: US (English-only)")
    print(f"Language: {region_config['language']}")
    print(f"Number of keywords: {len(keywords)}")
    print(f"Configuration:")
    print(f"  - Min subscribers: {region_config['min_subs']}")
    print(f"  - Max subscribers: {region_config['max_subs']}")
    print(f"  - Max videos: {region_config['max_videos']}")
    print(f"  - Search limit: {region_config['search_limit']}")
    
    # Initialize YouTube scraper (no API key needed)
    scraper = YouTubeScraper(
        api_key=None,  # Not used anymore
        region='US',
        config=region_config,
        api_keys=api_keys
    )
    
    # Analyze channels based on keywords
    print("\nStarting web scraping (this may take several minutes)...")
    filtered_channels = scraper.analyze_channels(keywords)
    print(f"\nChannels matching criteria: {len(filtered_channels)}")
    
    if filtered_channels:
        # Generate output filename with date
        date_str = datetime.now().strftime('%Y%m%d')
        
        if args.output_format == 'sheets':
            # Write to Google Sheets
            try:
                writer = SheetsWriter(service_account_json)
                spreadsheet_name = f'YouTube Channels - US - {date_str}'
                spreadsheet_url = writer.write_channels_data(
                    spreadsheet_name,
                    filtered_channels
                )
                print(f"\nData written to spreadsheet: {spreadsheet_url}")
            except Exception as e:
                error_msg = str(e)
                logging.error(f"Error writing to spreadsheet: {error_msg}")
                
                # Provide helpful error messages
                if "'id'" in error_msg:
                    print("\nError: Failed to write channel data to spreadsheet.")
                    print("This may be due to missing channel ID information.")
                    print("Consider using --output-format json or csv as a workaround.")
                elif "Drive API" in error_msg or "SERVICE_DISABLED" in error_msg:
                    print("\nError: Google Drive API is not enabled.")
                    print("Please enable it at: https://console.cloud.google.com/apis/library/drive.googleapis.com")
                else:
                    print(f"\nError writing to spreadsheet: {error_msg}")
                
                # Fallback to JSON output
                print("\nAttempting to save data as JSON instead...")
                try:
                    import json
                    fallback_filename = f'rising_channels_US_{date_str}_fallback.json'
                    with open(fallback_filename, 'w', encoding='utf-8') as f:
                        json.dump(filtered_channels, f, ensure_ascii=False, indent=2)
                    print(f"Data saved to: {fallback_filename}")
                except Exception as fallback_e:
                    print(f"Failed to save fallback JSON: {fallback_e}")
                    
                sys.exit(1)
                
        elif args.output_format == 'json':
            # Write to JSON file
            import json
            filename = f'rising_channels_US_{date_str}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(filtered_channels, f, ensure_ascii=False, indent=2)
            print(f"\nData written to: {filename}")
            
        elif args.output_format == 'csv':
            # Write to CSV file
            import csv
            filename = f'rising_channels_US_{date_str}.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if filtered_channels:
                    writer = csv.DictWriter(f, fieldnames=filtered_channels[0].keys())
                    writer.writeheader()
                    writer.writerows(filtered_channels)
            print(f"\nData written to: {filename}")
            
        # Also generate keyword analysis CSV
        if hasattr(scraper, 'keyword_metrics') and scraper.keyword_metrics:
            keyword_filename = f'hot_keywords_US_{date_str}.csv'
            import csv
            with open(keyword_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['keyword', 'search_volume', 'competition', 'score'])
                writer.writeheader()
                # Filter keywords with score >= 6
                hot_keywords = [k for k in scraper.keyword_metrics if k.get('score', 0) >= 6]
                writer.writerows(hot_keywords)
            print(f"Keyword analysis written to: {keyword_filename}")
    else:
        print("No channels found matching the criteria")

if __name__ == '__main__':
    main()