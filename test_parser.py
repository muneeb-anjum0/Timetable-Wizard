# Quick test to verify parser functionality
import sys
sys.path.append('src')

from scraper.parser import parse_schedule_text

# Test the exact same data format that would come from Gmail
test_data = """
20 CS BS (SE) BS (SE) - 4A SEC 2404 Software Design and Architecture (2,0) Tehreem Saboor 301 12:30 PM – 02:30 PM SZABIST University Campus H-8/4 ISB
"""

# Parse with semester filter
result = parse_schedule_text(test_data, ['BS (SE) - 4A'])

print("Parser Test Results:")
print("="*50)
if result:
    for item in result:
        print(f"Course: {item.get('course')}")
        print(f"Course Title: '{item.get('course_title')}'")
        print(f"Faculty: '{item.get('faculty')}'")
        print(f"Room: '{item.get('room')}'")
        print(f"Time: '{item.get('time')}'")
        print(f"Semester: '{item.get('semester')}'")
        print("-" * 30)
else:
    print("No results found!")