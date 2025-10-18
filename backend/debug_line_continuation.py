#!/usr/bin/env python3
"""
Debug the line continuation logic specifically
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.advanced_table_parser import AdvancedTableParser
from bs4 import BeautifulSoup
import re

def debug_line_continuation():
    """Debug how line continuation is working"""
    
    # Load the debug HTML file
    with open('debug_email.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text('\n')
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    
    print("🔍 Looking for line 11 (AIC 4802 problematic entry):")
    print()
    
    # Find the problematic entry
    for i, line in enumerate(lines):
        if line.startswith('11 AI BSAI BS(AI) - 4B AIC 4802'):
            print(f"Found line 11 at index {i}:")
            print(f"  Main line: '{line}'")
            
            # Show the next few lines 
            print("  Next lines:")
            for j in range(1, 8):
                if i + j < len(lines):
                    next_line = lines[i + j]
                    print(f"    +{j}: '{next_line}'")
                    
                    # Check if it starts with a number (would be next entry)
                    if re.match(r'^\d+\s+[A-Z]', next_line):
                        print(f"    --> Next entry starts at +{j}")
                        break
            
            # Now test what the continuation logic would collect
            print(f"\n🔧 Testing continuation logic:")
            full_line = line
            j = i + 1
            collected_lines = [line]
            
            while j < len(lines) and j < i + 8:
                next_line = lines[j].strip()
                # If next line starts with number, it's a new entry
                if re.match(r'^\d+\s+[A-Z]', next_line):
                    print(f"  Stop: Next entry found at line {j}")
                    break
                # If it looks like a continuation
                if next_line and not re.match(r'^[🕗🔸]', next_line):
                    # Special handling for time/room/campus continuations
                    if (re.search(r'\d{1,2}:\d{2}\s*[AP]M|Hall|Lab|NB-|\d{3}|SZABIST|Campus|H-8/4', next_line) or
                        len(next_line.split()) <= 4):
                        full_line += " " + next_line
                        collected_lines.append(next_line)
                        print(f"  Collected: '{next_line}'")
                    else:
                        print(f"  Skipped: '{next_line}' (doesn't match continuation criteria)")
                j += 1
            
            print(f"\n📝 Final reconstructed line:")
            print(f"'{full_line}'")
            
            # Test parsing this reconstructed line
            print(f"\n🧪 Testing parse result:")
            parser = AdvancedTableParser()
            result = parser._parse_schedule_line(full_line)
            
            if result:
                for key in ['course', 'faculty', 'time', 'room', 'campus']:
                    value = result.get(key)
                    status = "✅" if value else "❌ TBD"
                    print(f"  {key}: {value} {status}")
            else:
                print("  ❌ Parse failed")
            
            break

if __name__ == "__main__":
    debug_line_continuation()