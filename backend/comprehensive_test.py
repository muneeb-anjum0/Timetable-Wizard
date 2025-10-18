#!/usr/bin/env python3
"""
Comprehensive test for all semester patterns
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.advanced_table_parser import parse_html_with_advanced_pandas

def comprehensive_semester_test():
    """Test all semester patterns comprehensively"""
    
    # Load the debug HTML file
    with open('debug_email.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"📧 Loaded Gmail HTML: {len(html_content)} characters")
    
    # All target semesters from your list
    target_semesters = [
        # Computer Science & Software Engineering
        "BS(CS) - 5C", "BS(SE) - 2C", "BS(SE) - 3A", "BS(SE) - 3B",
        
        # AI Programs
        "BS(AI) - 3A", "BS(AI) - 3B", "BS(AI) - 3C", "BS(AI) - 4A", "BS(AI) - 4B",
        "BS(AI) - 7A", "BS(AI) - 5B", "BS(AI) - 5C",
        
        # Multiple sections (joint classes)
        "BS(CS) / BS (SE) / BSAI Open B", "BS(CS) / BS (SE) / BSAI",
        "BS(CS) / BS (SE) / BSAI Open A",
        
        # Social Sciences & Psychology
        "BS (SS) - 1", "BS (Psy) - 2", "BS (Psy) - 1", "BS (Psy) - 12",
        "BS (SS) - 2", "BS (SS) - 4", "BS (SS) - 6", "BS (SS) - 3", "BS (Psy) - 3",
        
        # Masters Programs
        "MS (SS) - Open", "MSS - Open", "MS (SS) - 1", "MSS - 1", "MS (SS) - 1 / MSS - 1",
        
        # Business Administration
        "BBA - 1 A & B", "BS (AF) - 3", "BS (AF) - 4", "BS (AF) - 5", "BS (AF) - 6",
        "BS (AF) - 7", "BS (AF) - 8",
        
        # Business & Management
        "BS (BA) - 1", "BS (BA) - 2", "BS (BA) - 3",
        
        # Masters Business/Management
        "MS (MS) / MS (BA) Deficiency Course", "MBA (36) Eve - 1", "MS (BA) - 1", "MS (BA) - 2",
        "MS (PM) - 1 B", "MS (PM) Open Elective", "MS (PM) - 1 A Core", "MS (PM) - 1 B Core",
        "MS (PM) - 2 A Core", "MS (PM) - 2 B Core",
        
        # Data Science
        "MS (DS) - 2", "MS (DS) - 1", "MS (DS) - 3", "MS Data Sc - 1",
        
        # PhD Programs
        "PhD Psychology - 1",
        
        # MMS Programs
        "MMS - 1", "MMS Open A", "MMS Zero", "MMS Open",
        
        # Cyber Security
        "MS-CPY - 1 A", "MS-CPY - 1 B", "MS-CPY - Open", "MS Cyber Sc - 3",
        
        # MBA Programs
        "EMBA - 1", "PMBA - 1", "EMBA - 2", "PMBA - 2", "MBA (72) Day & Eve - 1",
        "EMBA - 3", "EMBA - 4",
        
        # HR Management
        "MHRM - 1", "MHRM - 2",
        
        # Masters in other fields
        "MS (MS) - 1", "MPM - 1", "MPM - 2",
        
        # Combined/Joint sections
        "EMBA1/MBA1/MHRM1", "EMBA - 1 / PMBA - 1 / MBA (72) Day & Eve - 1",
        "EMBA - 2 / PMBA - 2", "MHRM - 1 / MHRM - 2 / MS (BA) / MS (MS) Elective",
        "MBA Elective / MS (MS) - 2", "MBA Elective / MS (BA) - 2",
        "MBA / MSBA / MBA Elective / MS (BA) – 3", "MBA Elective",
        
        # Additional CS
        "BS(CS) - 5A", "BS(CS) - 5B"
    ]
    
    print(f"🎯 Testing {len(target_semesters)} different semester patterns")
    print()
    
    # Parse without filtering first to see what's available
    all_items = parse_html_with_advanced_pandas(html_content, None)
    
    if not all_items:
        print("❌ Parser failed - no items found")
        return
    
    # Get all available semesters from the parsed data
    available_semesters = set(item.get('semester') for item in all_items if item.get('semester'))
    
    print(f"📊 AVAILABLE SEMESTERS IN EMAIL ({len(available_semesters)}):")
    for sem in sorted(available_semesters):
        print(f"  • {sem}")
    print()
    
    # Test each target semester
    print("🔍 SEMESTER TESTING RESULTS:")
    print("=" * 80)
    
    found_count = 0
    missing_count = 0
    
    for target in target_semesters:
        # Check for exact match
        exact_match = target in available_semesters
        
        # Check for partial/flexible matches
        partial_matches = [sem for sem in available_semesters if target.replace(" ", "") in sem.replace(" ", "") or sem.replace(" ", "") in target.replace(" ", "")]
        
        if exact_match:
            found_count += 1
            print(f"✅ {target:<50} EXACT MATCH")
        elif partial_matches:
            found_count += 1
            print(f"🔶 {target:<50} PARTIAL MATCH: {partial_matches[0]}")
        else:
            missing_count += 1
            print(f"❌ {target:<50} NOT FOUND")
    
    print("=" * 80)
    print(f"📈 SUMMARY:")
    print(f"   Target semesters tested: {len(target_semesters)}")
    print(f"   Found (exact + partial): {found_count}")
    print(f"   Missing: {missing_count}")
    print(f"   Success rate: {(found_count / len(target_semesters) * 100):.1f}%")
    print()
    
    # Show some examples of parsed data quality
    print("📋 DATA QUALITY SAMPLE (first 5 items):")
    for i, item in enumerate(all_items[:5]):
        time_status = "✅" if item.get('time') else "❌ TBD"
        room_status = "✅" if item.get('room') else "❌ TBD"
        faculty_status = "✅" if item.get('faculty') else "❌ TBD"
        
        print(f"  {i+1}. {item.get('course', 'N/A')} - {item.get('semester', 'N/A')}")
        print(f"     Time: {time_status}, Room: {room_status}, Faculty: {faculty_status}")
    
    print(f"\n🎯 Total classes parsed with complete data: {len(all_items)}")

if __name__ == "__main__":
    comprehensive_semester_test()