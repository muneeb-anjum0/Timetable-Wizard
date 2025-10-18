#!/usr/bin/env python3
"""
Display scraped data in formatted chat-friendly output
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.advanced_table_parser import parse_html_with_advanced_pandas
import json

def display_scraped_data():
    """Display the scraped data in a formatted way"""
    
    # Load the debug HTML file
    with open('debug_email.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🎓 TIMETABLE SCRAPER - COMPLETE DATA EXTRACTION RESULTS")
    print("=" * 70)
    print(f"📧 Source: Gmail HTML ({len(html_content):,} characters)")
    print(f"📅 Schedule Date: Saturday, October 18, 2025")
    print()
    
    # Parse without filtering to get all data
    all_items = parse_html_with_advanced_pandas(html_content, None)
    
    if not all_items:
        print("❌ No data scraped")
        return
    
    print(f"📊 TOTAL CLASSES SCRAPED: {len(all_items)}")
    print()
    
    # Group by semester for better organization
    by_semester = {}
    for item in all_items:
        semester = item.get('semester', 'Unknown')
        if semester not in by_semester:
            by_semester[semester] = []
        by_semester[semester].append(item)
    
    # Display by semester
    for semester in sorted(by_semester.keys()):
        classes = by_semester[semester]
        print(f"🎯 {semester} ({len(classes)} classes)")
        print("-" * 50)
        
        for i, item in enumerate(classes, 1):
            # Format course info
            course = item.get('course', 'N/A')
            title = item.get('course_title', 'N/A')
            faculty = item.get('faculty', 'N/A')
            time = item.get('time', 'N/A')
            room = item.get('room', 'N/A')
            campus = item.get('campus', 'N/A')
            
            # Status indicators
            time_status = "✅" if time != 'N/A' and time else "❌"
            room_status = "✅" if room != 'N/A' and room else "❌"
            faculty_status = "✅" if faculty != 'N/A' and faculty else "❌"
            
            print(f"  {i}. {course} - {title}")
            print(f"     👨‍🏫 Faculty: {faculty} {faculty_status}")
            print(f"     ⏰ Time: {time} {time_status}")
            print(f"     🏛️ Room: {room} {room_status}")
            
            # Only show campus if it's reasonably short
            if campus != 'N/A' and len(campus) < 50:
                print(f"     🏫 Campus: {campus}")
            elif campus != 'N/A':
                print(f"     🏫 Campus: {campus[:47]}...")
            print()
    
    print("=" * 70)
    print("📈 DATA QUALITY SUMMARY:")
    
    # Calculate quality metrics
    total = len(all_items)
    time_complete = sum(1 for item in all_items if item.get('time'))
    room_complete = sum(1 for item in all_items if item.get('room'))
    faculty_complete = sum(1 for item in all_items if item.get('faculty'))
    
    print(f"   📚 Total Classes: {total}")
    print(f"   ⏰ Time Data: {time_complete}/{total} ({time_complete/total*100:.1f}%)")
    print(f"   🏛️ Room Data: {room_complete}/{total} ({room_complete/total*100:.1f}%)")
    print(f"   👨‍🏫 Faculty Data: {faculty_complete}/{total} ({faculty_complete/total*100:.1f}%)")
    
    # Show available semesters
    semesters = sorted(by_semester.keys())
    print(f"   🎓 Semesters Found: {len(semesters)}")
    for sem in semesters:
        print(f"      • {sem}")
    
    print()
    print("🔥 PARSER TECHNOLOGY:")
    print("   • Enhanced Pandas-based table extraction")
    print("   • Advanced regex pattern matching")
    print("   • Multi-line data reconstruction")
    print("   • Smart semester filtering")
    print("   • Complete TBD issue resolution")

if __name__ == "__main__":
    display_scraped_data()