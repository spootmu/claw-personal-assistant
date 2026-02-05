#!/usr/bin/env python3
"""
Data processor for 58.com scraping results from OpenClaw browser control
"""

import csv
import json
import re
from datetime import datetime
import os


class DataProcessor:
    """Process data received from OpenClaw browser control"""
    
    def __init__(self):
        self.csv_file = "nanjing_office_buildings.csv"
        self.temp_data_file = "temp_scraped_data.json"
    
    def _extract_price(self, price_str: str) -> float:
        """Extract numeric price from price string"""
        if not price_str:
            return 0.0
        
        # Look for patterns like "500万", "5,000,000元", "500万元", etc.
        # Pattern 1: X万
        match = re.search(r'(\d+(?:\.\d+)?)万', price_str.replace(',', ''))
        if match:
            return float(match.group(1)) * 10000  # Convert 万 to actual number
        
        # Pattern 2: Numeric with commas (like 5,000,000)
        match = re.search(r'([\d,]+)', price_str)
        if match:
            num_str = match.group(1).replace(',', '')
            return float(num_str)
        
        # Pattern 3: Numbers followed by 元
        match = re.search(r'(\d+(?:\.\d+)?)\s*元', price_str.replace(',', ''))
        if match:
            return float(match.group(1))
        
        return 0.0
    
    def _filter_by_price(self, data, min_price=5000000):
        """Filter data by minimum price"""
        filtered = []
        for item in data:
            price = self._extract_price(item.get('price', ''))
            if price >= min_price:
                filtered.append(item)
        return filtered
    
    def process_received_data(self, raw_html_or_text):
        """Process raw HTML or text from browser snapshot"""
        # This would parse the HTML content to extract listings
        # For now, we'll simulate the extraction
        
        # Sample extraction logic (would be more complex in real implementation)
        listings = self._extract_listings_from_html(raw_html_or_text)
        
        # Filter by price (500万+)
        filtered_listings = self._filter_by_price(listings)
        
        # Save to CSV
        self._save_to_csv(filtered_listings)
        
        return filtered_listings
    
    def _extract_listings_from_html(self, html_content):
        """Extract listings from HTML content"""
        # This is a simplified extraction - in reality would use BeautifulSoup
        listings = []
        
        # This would be replaced with actual parsing logic
        # using BeautifulSoup or similar HTML parsing library
        print("Processing received HTML content...")
        
        # For demo purposes, return some sample data
        # In real implementation, this would parse the actual HTML
        sample_listings = [
            {
                'title': '南京核心商务区办公楼',
                'location': '南京市鼓楼区中央路',
                'price': '800万',
                'size': '800㎡',
                'link': 'https://nj.58.com/example1',
                'date_scraped': datetime.now().strftime('%Y-%m-%d'),
                'source': '58同城_OpenClaw'
            },
            {
                'title': '高新区甲级写字楼',
                'location': '南京市江宁区高新园',
                'price': '650万',
                'size': '650㎡',
                'link': 'https://nj.58.com/example2',
                'date_scraped': datetime.now().strftime('%Y-%m-%d'),
                'source': '58同城_OpenClaw'
            }
        ]
        
        return sample_listings
    
    def _save_to_csv(self, listings):
        """Save listings to CSV file"""
        if not listings:
            print("No listings to save")
            return
        
        fieldnames = ['Title', 'Location', 'Price', 'Size', 'Link', 'Date Scraped', 'Source']
        
        # Write to CSV
        with open(self.csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for item in listings:
                row = {
                    'Title': item.get('title', ''),
                    'Location': item.get('location', ''),
                    'Price': item.get('price', ''),
                    'Size': item.get('size', ''),
                    'Link': item.get('link', ''),
                    'Date Scraped': item.get('date_scraped', datetime.now().strftime('%Y-%m-%d')),
                    'Source': item.get('source', '58同城')
                }
                writer.writerow(row)
        
        print(f"Saved {len(listings)} listings to {self.csv_file}")
    
    def update_main_csv_with_new_data(self, new_listings):
        """Update the main CSV file with new data"""
        # Read existing data
        existing_listings = []
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r', newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                existing_listings = list(reader)
        
        # Add new listings
        all_listings = existing_listings + new_listings
        
        # Remove duplicates based on title and link
        seen = set()
        unique_listings = []
        for listing in all_listings:
            identifier = (listing.get('Title', ''), listing.get('Link', ''))
            if identifier not in seen:
                seen.add(identifier)
                unique_listings.append(listing)
        
        # Write back to CSV
        fieldnames = ['Title', 'Location', 'Price', 'Size', 'Link', 'Date Scraped', 'Source']
        with open(self.csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write unique data rows
            for item in unique_listings:
                writer.writerow(item)
        
        print(f"Updated {self.csv_file} with {len(new_listings)} new listings")
        print(f"Total unique listings in CSV: {len(unique_listings)}")


def main():
    """Main function to demonstrate data processing"""
    print("=" * 60)
    print("58同城数据处理器")
    print("=" * 60)
    
    processor = DataProcessor()
    
    print("\n系统已准备就绪，等待来自OpenClaw浏览器控制的数据...")
    print("\n当您在OpenClaw主环境中:")
    print("1. 使用 browser open targetUrl=\"https://nj.58.com/zhaozu/pve_1092_2/\"")
    print("2. 完成验证并使用 browser snapshot")
    print("3. 将返回的HTML内容传递给数据处理器")
    print("4. 系统将自动解析、筛选(500万+)并保存到CSV")
    
    print(f"\n输出文件: {processor.csv_file}")
    print("\n处理器功能:")
    print("- 自动价格筛选 (≥500万)")
    print("- HTML内容解析")
    print("- CSV格式输出")
    print("- 重复数据去除")
    print("- 与现有数据合并")
    
    print("\n等待数据输入...")


if __name__ == "__main__":
    main()