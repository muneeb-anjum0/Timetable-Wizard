#!/usr/bin/env python3
"""
Analyze BS(AI) - 4B data for TBD issues
"""
import json

def analyze_4b_data():
    """Analyze BS(AI) - 4B classes for TBD issues"""
    
    with open('current_scrape_result.json', 'r') as f:
        data = json.load(f)
    
    print('🔍 BS(AI) - 4B Classes Analysis:')
    print('=' * 50)
    
    count = 0
    tbd_issues = 0
    
    for item in data['data']['items']:
        if item['semester'] == 'BS(AI) - 4B':
            count += 1
            has_tbd = False
            
            print(f'{count}. {item["course"]} - {item["course_title"]}')
            
            # Check for TBD/null values
            faculty = item["faculty"] or "TBD"
            time = item["time"] or "TBD"
            room = item["room"] or "TBD"
            campus = item["campus"] or "TBD"
            
            if "TBD" in [faculty, time, room]:
                has_tbd = True
                tbd_issues += 1
            
            print(f'   Faculty: {faculty}{"  ❌ TBD" if faculty == "TBD" else "  ✅"}')
            print(f'   Time: {time}{"  ❌ TBD" if time == "TBD" else "  ✅"}')
            print(f'   Room: {room}{"  ❌ TBD" if room == "TBD" else "  ✅"}')
            print(f'   Campus: {campus}{"  ❌ TBD" if campus == "TBD" else "  ✅"}')
            print()
    
    print(f'📊 Summary:')
    print(f'   Total BS(AI) - 4B classes: {count}')
    print(f'   Classes with TBD issues: {tbd_issues}')
    print(f'   Complete data rate: {((count - tbd_issues) / count * 100):.1f}%' if count > 0 else '   No classes found')

if __name__ == "__main__":
    analyze_4b_data()