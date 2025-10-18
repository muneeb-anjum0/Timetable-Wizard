#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.scraper.advanced_table_parser import parse_html_with_advanced_pandas

test_html = '''
<p>1 CS BS(CS) BS(CS) - 5B CSC 2123 Graph Theory (3,0) Dr. Aqeel Ahmed 301 02:00 PM - 03:30 PM SZABIST</p>
<p>2 CS BS(CS) BS(CS) - 5B CSC 2205 Operating Systems (3,0) Awais Mehmood 301 03:30 PM - 05:00 PM SZABIST</p>
'''

result = parse_html_with_advanced_pandas(test_html, ['BS(CS) - 5B'])
print(f'Advanced parser result: {len(result)} items')
for i in result:
    print(f"  {i['course']}: {i['semester']} - {i['time']} in {i['room']}")