#!/usr/bin/env python3
"""
Test the enhanced advanced parser with real Gmail HTML data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.advanced_table_parser import parse_html_with_advanced_pandas

def test_gmail_parser():
    """Test the advanced parser with actual Gmail HTML"""
    
    # Load the debug HTML file
    with open('debug_email.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"📧 Loaded Gmail HTML: {len(html_content)} characters")
    
    # Test without filtering to check AIC 4802 specifically
    test_semesters = None
    
    print(f"🎯 Testing with no filtering to check AIC 4802 fix")
    
    # Parse the HTML
    items = parse_html_with_advanced_pandas(html_content, test_semesters)
    
    print(f"\n🔥 ADVANCED PARSER RESULTS: {len(items)} items found")
    
    if items:
        # Check specifically for AIC 4802 courses
        aic_courses = [item for item in items if item.get('course') == 'AIC 4802']
        print(f"\n� Found {len(aic_courses)} AIC 4802 courses:")
        
        for i, course in enumerate(aic_courses):
            print(f"  {i+1}. AIC 4802 - {course.get('course_title', 'N/A')}")
            print(f"     Semester: {course.get('semester', 'N/A')}")
            print(f"     Faculty: {course.get('faculty', 'N/A')}")
            print(f"     Time: {course.get('time', 'N/A')} {'❌ TBD' if not course.get('time') else '✅'}")
            print(f"     Room: {course.get('room', 'N/A')} {'❌ TBD' if not course.get('room') else '✅'}")
            print(f"     Campus: {course.get('campus', 'N/A')} {'❌ TBD' if not course.get('campus') else '✅'}")
            print()
        
        # Check BS(AI) - 4B specifically
        bs_4b_courses = [item for item in items if item.get('semester') == 'BS(AI) - 4B']
        print(f"🎯 Found {len(bs_4b_courses)} BS(AI) - 4B courses:")
        for i, course in enumerate(bs_4b_courses):
            has_tbd = not course.get('time') or not course.get('room') or not course.get('campus')
            status = "❌ HAS TBD" if has_tbd else "✅ COMPLETE"
            print(f"  {i+1}. {course.get('course')} - {status}")
            if has_tbd:
                print(f"     Missing: {', '.join([k for k in ['time', 'room', 'campus'] if not course.get(k)])}")
    else:
        print("❌ No items found - parser failed")

if __name__ == "__main__":
    test_gmail_parser()