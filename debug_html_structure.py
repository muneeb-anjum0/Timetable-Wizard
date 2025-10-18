#!/usr/bin/env python3
"""
Debug the HTML structure to understand why advanced parser fails
"""
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

def debug_html_structure():
    print("🔍 Debugging HTML structure...")
    
    # Make API call to trigger parsing and check logs
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
        print(f"✅ API Response: {len(data['data']['items'])} items")
        
        # The HTML isn't in the response, but let's create a test to see what HTML looks like
        test_html = """
        <p>Classes Schedule – Saturday, October 18th, 2025 (Fall 2025)</p>
        <p>Sr. No Dept Program Class / Section Course Faculty Room Time Campus</p>
        <p>🕗 Slot 01 (08:00 AM – 11:00 AM)</p>
        <p>1 CS BS(CS) BS(CS) - 5C CSC 3109 Software Engineering (3,0) Awais Nawaz Hall 01 A 09:30 AM - 11:00 AM SZABIST University Campus</p>
        <p>6 AI BSAI BS(AI) - 3A CSCL 3105 Lab: Computer Organization and Assembly Language (0,1) Sarwat Nadeem - Lab 05 08:00 AM - 11:00 AM SZABIST</p>
        """
        
        print("\n🔍 Testing pandas table extraction on sample HTML:")
        try:
            tables = pd.read_html(test_html)
            print(f"✅ Pandas found {len(tables)} tables")
            for i, table in enumerate(tables):
                print(f"Table {i+1} shape: {table.shape}")
                print(table.head())
        except Exception as e:
            print(f"❌ Pandas failed: {e}")
            
        print("\n🔍 Testing BeautifulSoup structure:")
        soup = BeautifulSoup(test_html, 'html.parser')
        table_elements = soup.find_all('table')
        print(f"Found {len(table_elements)} <table> elements")
        
        p_elements = soup.find_all('p')
        print(f"Found {len(p_elements)} <p> elements")
        for i, p in enumerate(p_elements):
            print(f"P{i+1}: {p.get_text()[:100]}...")
            
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    debug_html_structure()