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
        description='YouTube Channel Auto-List - Discover rising YouTube channels'
    )
    parser.add_argument(
        '--region',
        type=str,
        default=os.getenv('DEFAULT_REGION', 'JP'),
        choices=['JP', 'US', 'EN', 'ES', 'PT', 'BR'],
        help='Target region (default: JP)'
    )
    parser.add_argument(
        '--lang',
        type=str,
        default=None,
        help='Language code (default: auto-detected from region)'
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
    return parser.parse_args()

def main():
    """Main process"""
    args = parse_arguments()
    
    # Get configuration for the region
    region_config = Config.get_region_config(args.region)
    if args.lang:
        region_config['language'] = args.lang
    
    # Get API credentials
    api_keys = Config.get_api_keys()
    service_account_json = Config.get_google_credentials()
    
    if not api_keys['youtube']:
        print("Error: YOUTUBE_API_KEY is not set")
        sys.exit(1)
        
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
    
    print(f"Region: {args.region}")
    print(f"Language: {region_config['language']}")
    print(f"Number of keywords: {len(keywords)}")
    print(f"Configuration: {region_config}")
    
    # Initialize YouTube scraper with region config
    scraper = YouTubeScraper(
        api_key=api_keys['youtube'],
        region=args.region,
        config=region_config,
        api_keys=api_keys
    )
    
    # Process keywords and filter channels
    for keyword in keywords:
        try:
            scraper.process_keyword(keyword)
        except Exception as e:
            print(f"Error processing keyword '{keyword}': {e}")
            continue
    
    # Get filtered channels
    filtered_channels = scraper.get_filtered_channels()
    print(f"\nChannels matching criteria: {len(filtered_channels)}")
    
    if filtered_channels:
        # Generate output filename with region and date
        date_str = datetime.now().strftime('%Y%m%d')
        
        if args.output_format == 'sheets':
            # Write to Google Sheets
            try:
                writer = SheetsWriter(service_account_json)
                spreadsheet_name = f'YouTube Channels - {args.region} - {date_str}'
                spreadsheet_url = writer.write_channels_data(
                    spreadsheet_name,
                    filtered_channels
                )
                print(f"\nData written to spreadsheet: {spreadsheet_url}")
            except Exception as e:
                print(f"Error writing to spreadsheet: {e}")
                sys.exit(1)
                
        elif args.output_format == 'json':
            # Write to JSON file
            import json
            filename = f'rising_channels_{args.region}_{date_str}.json'
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(filtered_channels, f, ensure_ascii=False, indent=2)
            print(f"\nData written to: {filename}")
            
        elif args.output_format == 'csv':
            # Write to CSV file
            import csv
            filename = f'rising_channels_{args.region}_{date_str}.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if filtered_channels:
                    writer = csv.DictWriter(f, fieldnames=filtered_channels[0].keys())
                    writer.writeheader()
                    writer.writerows(filtered_channels)
            print(f"\nData written to: {filename}")
            
        # Also generate keyword analysis CSV
        if scraper.keyword_metrics:
            keyword_filename = f'hot_keywords_{args.region}_{date_str}.csv'
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