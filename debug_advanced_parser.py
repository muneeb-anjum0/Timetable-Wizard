#!/usr/bin/env python3
"""
Debug the advanced parser to see why it's not finding BS(CS)-5B
"""
import requests
import json

def debug_advanced_parser():
    print("🔍 Debugging Advanced Parser...")
    
    # Check user settings first
    response = requests.get(
        "http://localhost:5000/api/status",
        headers={"X-User-Email": "2380223@szabist-isb.pk"}
    )
    
    if response.status_code == 200:
        status = response.json()
        print(f"✅ User Settings:")
        print(f"  Target Semesters: {status.get('settings', {}).get('allowed_semesters', 'N/A')}")
        print(f"  Status: {status.get('message', 'N/A')}")
    else:
        print(f"❌ Status check failed: {response.status_code}")
    
    # Test scrape and check what semesters are actually found
    response = requests.post(
        "http://localhost:5000/api/scrape", 
        headers={
            "Content-Type": "application/json", 
            "X-User-Email": "2380223@szabist-isb.pk"
        }, 
        json={}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📊 Scrape Results:")
        print(f"  Total Items: {len(data['data']['items'])}")
        print(f"  Semesters Found: {data['data'].get('semesters', [])}")
        
        # Check what courses we're getting
        bs_cs_items = [item for item in data['data']['items'] if 'CS' in item.get('semester', '') and '5' in item.get('semester', '')]
        bs_ai_items = [item for item in data['data']['items'] if 'AI' in item.get('semester', '') and '3A' in item.get('semester', '')]
        
        print(f"\n🎯 BS(CS) related items: {len(bs_cs_items)}")
        for item in bs_cs_items:
            print(f"  - {item['course']}: {item['semester']}")
            
        print(f"\n🎯 BS(AI)-3A items: {len(bs_ai_items)}")
        for item in bs_ai_items:
            print(f"  - {item['course']}: {item['semester']}")
            
        # Check if we're getting the wrong parser
        print(f"\n🔍 Summary:")
        print(f"  Expected: BS(AI)-3A (2 classes) + BS(CS)-5B (2 classes) = 4 total")
        print(f"  Actual: {len(data['data']['items'])} classes from semesters: {data['data'].get('semesters', [])}")
        
        if len(data['data']['items']) != 4 or 'BS(CS)-5B' not in str(data['data'].get('semesters', [])):
            print("❌ Advanced parser likely failed, falling back to old parser")
        else:
            print("✅ Advanced parser working correctly")
    else:
        print(f"❌ Scrape failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    debug_advanced_parser()