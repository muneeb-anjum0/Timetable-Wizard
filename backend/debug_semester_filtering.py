#!/usr/bin/env python3
"""Debug script to check semester filtering issues"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json

def debug_semester_filtering():
    """Debug semester filtering to see what's being skipped"""
    print("=== DEBUGGING SEMESTER FILTERING ===")
    
    try:
        # First, let's see what semesters are configured
        headers = {'X-User-Email': '2380223@szabist-isb.pk'}
        config_response = requests.get('http://localhost:5000/api/config', headers=headers)
        
        if config_response.status_code == 200:
            config = config_response.json()
            configured_semesters = config.get('data', {}).get('semester_filter', [])
            print(f"Configured semester filters: {configured_semesters}")
        
        # Let's try to trigger a debug scrape and see what's happening
        payload = {
            'semesters': configured_semesters,
            'force_refresh': True,
            'debug': True  # This might help get more info
        }
        
        print(f"\nTriggering scrape with payload: {json.dumps(payload, indent=2)}")
        
        scrape_response = requests.post(
            'http://localhost:5000/api/scrape',
            headers=headers,
            json=payload,
            timeout=180  # 3 minutes
        )
        
        print(f"Scrape response status: {scrape_response.status_code}")
        
        if scrape_response.status_code == 200:
            data = scrape_response.json()
            items = data.get('data', {}).get('items', [])
            print(f"Items found: {len(items)}")
            
            if len(items) == 0:
                print("❌ No items found! This confirms the semester filtering issue.")
                print("\n💡 POSSIBLE SOLUTIONS:")
                print("1. Check if Friday's schedule has different semester names")
                print("2. Update semester filters to match actual data")
                print("3. Check if the email format has changed")
            else:
                print("✅ Items found:")
                for item in items:
                    print(f"  - {item.get('semester')}: {item.get('course')} - {item.get('time')}")
        else:
            print(f"❌ Scrape failed: {scrape_response.status_code}")
            if scrape_response.text:
                print(f"Response: {scrape_response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ Request timeout - the scraper is taking too long")
        print("💡 This might be a Gmail API issue or network problem")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_semester_filtering()