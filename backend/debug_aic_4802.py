#!/usr/bin/env python3
"""
Debug the specific AIC 4802 parsing issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.advanced_table_parser import AdvancedTableParser
import re

def test_specific_line():
    """Test parsing of the problematic AIC 4802 line"""
    
    # Reconstruct the exact line from the Gmail HTML
    problematic_line = "11 AI BSAI BS(AI) - 4B AIC 4802 Data Mining (3,0) Hasaan Mujtaba Hall 01 B 08:00 AM - 09:30 AM SZABIST University Campus H-8/4 ISB"
    
    print("🔍 Testing specific problematic line:")
    print(f"Line: {problematic_line}")
    print()
    
    parser = AdvancedTableParser()
    result = parser._parse_schedule_line(problematic_line)
    
    if result:
        print("✅ Parse Result:")
        for key, value in result.items():
            status = "✅" if value else "❌ TBD"
            print(f"  {key}: {value} {status}")
    else:
        print("❌ Failed to parse line")
        
    # Test regex patterns individually
    print("\n🔧 Testing individual regex patterns:")
    
    # Time pattern
    time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M\s*(?:-|–|—)\s*\d{1,2}:\d{2}\s*[AP]M)', problematic_line)
    print(f"Time match: {time_match.group(1) if time_match else 'None'}")
    
    # Room patterns
    room_patterns = [
        r'\b(Hall\s+\d+\s*[A-Z]?)\s+\d{1,2}:\d{2}',
        r'\b(NB-\d+)\s+\d{1,2}:\d{2}',
        r'\b(Lab\s+\d+)\s+\d{1,2}:\d{2}',
        r'\b(\d{3})\s+\d{1,2}:\d{2}',
    ]
    
    for i, pattern in enumerate(room_patterns):
        room_match = re.search(pattern, problematic_line)
        print(f"Room pattern {i+1}: {room_match.group(1) if room_match else 'None'}")
    
    # Campus pattern
    campus_match = re.search(r'(SZABIST[^$]+)$', problematic_line)
    print(f"Campus match: {campus_match.group(1) if campus_match else 'None'}")

if __name__ == "__main__":
    test_specific_line()