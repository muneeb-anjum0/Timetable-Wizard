#!/usr/bin/env python3
"""
Test the advanced parser with real email content from the API
"""
import requests

# Make API call to get fresh scrape results
response = requests.post(
    "http://localhost:5000/api/scrape", 
    headers={
        "Content-Type": "application/json", 
        "X-User-Email": "2380223@szabist-isb.pk"
    }, 
    json={"debug": True}
)

if response.status_code == 200:
    data = response.json()
    print(f"📊 Current Results:")
    print(f"  Total Items: {len(data['data']['items'])}")
    print(f"  Semesters: {data['data'].get('semesters', [])}")
    
    # Check what semesters we're actually supposed to target
    target_semesters = ['BS(AI) - 3A', 'BS(CS) - 5B']
    print(f"  Expected Semesters: {target_semesters}")
    
    # Count by semester
    semester_counts = {}
    for item in data['data']['items']:
        sem = item.get('semester', 'Unknown')
        semester_counts[sem] = semester_counts.get(sem, 0) + 1
    
    print(f"\n📈 Semester Breakdown:")
    for sem, count in semester_counts.items():
        expected = "✅" if sem in target_semesters or any(t.replace(' ', '') in sem.replace(' ', '') for t in target_semesters) else "❌"
        print(f"  {expected} {sem}: {count} classes")
    
    # The issue: we should only get target semesters
    wrong_semesters = [sem for sem in semester_counts.keys() if not any(t.replace(' ', '') in sem.replace(' ', '') for t in target_semesters)]
    if wrong_semesters:
        print(f"\n❌ PROBLEM: Getting unexpected semesters: {wrong_semesters}")
        print("This means the advanced parser failed and fallback parser is not respecting user semester filters")
    
    # Check for missing target semesters
    missing_semesters = [sem for sem in target_semesters if not any(sem.replace(' ', '') in actual.replace(' ', '') for actual in semester_counts.keys())]
    if missing_semesters:
        print(f"\n❌ MISSING: Target semesters not found: {missing_semesters}")
        
else:
    print(f"❌ API Error: {response.status_code}")
    print(response.text)