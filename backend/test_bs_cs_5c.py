#!/usr/bin/env python3
"""
Test scraper specifically for BS(CS) - 5C semester
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.advanced_table_parser import parse_html_with_advanced_pandas

def test_bs_cs_5c():
    """Test scraper for BS(CS) - 5C specifically"""
    
    # Load the debug HTML file
    with open('debug_email.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🎓 TIMETABLE SCRAPER - BS(CS) - 5C SPECIFIC TEST")
    print("=" * 60)
    print(f"📧 Source: Gmail HTML ({len(html_content):,} characters)")
    print(f"📅 Schedule Date: Saturday, October 18, 2025")
    print(f"🎯 Target Semester: BS(CS) - 5C")
    print()
    
    # Parse with BS(CS) - 5C filter
    target_semesters = ["BS(CS) - 5C"]
    filtered_items = parse_html_with_advanced_pandas(html_content, target_semesters)
    
    print(f"📊 FILTERED RESULTS FOR BS(CS) - 5C:")
    print(f"   Classes found: {len(filtered_items)}")
    print()
    
    if filtered_items:
        print("📋 DETAILED CLASS INFORMATION:")
        print("-" * 50)
        
        for i, item in enumerate(filtered_items, 1):
            # Extract all fields
            course = item.get('course', 'N/A')
            title = item.get('course_title', 'N/A')
            faculty = item.get('faculty', 'N/A')
            time = item.get('time', 'N/A')
            room = item.get('room', 'N/A')
            campus = item.get('campus', 'N/A')
            sr_no = item.get('sr_no', 'N/A')
            dept = item.get('dept', 'N/A')
            
            # Status indicators
            time_status = "✅" if time and time != 'N/A' else "❌ TBD"
            room_status = "✅" if room and room != 'N/A' else "❌ TBD"
            faculty_status = "✅" if faculty and faculty != 'N/A' else "❌ TBD"
            
            print(f"📝 CLASS {i}:")
            print(f"   🆔 Serial No: {sr_no}")
            print(f"   📚 Course: {course}")
            print(f"   📖 Title: {title}")
            print(f"   🏢 Department: {dept}")
            print(f"   🎓 Semester: {item.get('semester', 'N/A')}")
            print(f"   👨‍🏫 Faculty: {faculty} {faculty_status}")
            print(f"   ⏰ Time: {time} {time_status}")
            print(f"   🏛️ Room: {room} {room_status}")
            
            if campus and campus != 'N/A':
                if len(campus) < 60:
                    print(f"   🏫 Campus: {campus}")
                else:
                    print(f"   🏫 Campus: {campus[:57]}...")
            print()
        
        # Quality analysis
        total = len(filtered_items)
        time_complete = sum(1 for item in filtered_items if item.get('time'))
        room_complete = sum(1 for item in filtered_items if item.get('room'))
        faculty_complete = sum(1 for item in filtered_items if item.get('faculty'))
        
        print("📈 BS(CS) - 5C DATA QUALITY:")
        print(f"   ⏰ Time Completeness: {time_complete}/{total} ({time_complete/total*100:.1f}%)")
        print(f"   🏛️ Room Completeness: {room_complete}/{total} ({room_complete/total*100:.1f}%)")
        print(f"   👨‍🏫 Faculty Completeness: {faculty_complete}/{total} ({faculty_complete/total*100:.1f}%)")
        
        # Schedule analysis
        if time_complete > 0:
            print(f"\n📅 SCHEDULE PATTERN FOR BS(CS) - 5C:")
            times = [item.get('time') for item in filtered_items if item.get('time')]
            for i, time_slot in enumerate(times, 1):
                course_name = filtered_items[i-1].get('course', 'N/A')
                print(f"   {i}. {time_slot} - {course_name}")
    else:
        print("❌ No classes found for BS(CS) - 5C")
        print("   This could mean:")
        print("   • No Saturday classes for this semester")
        print("   • Different semester format in email")
        print("   • Parsing issue with semester detection")
    
    print("\n" + "=" * 60)
    print("🔍 SEMESTER FILTERING TEST COMPLETE")

if __name__ == "__main__":
    test_bs_cs_5c()