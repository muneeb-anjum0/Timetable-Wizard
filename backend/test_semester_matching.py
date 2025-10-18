#!/usr/bin/env python3
"""
Test semester filtering logic
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.advanced_table_parser import AdvancedTableParser

def test_semester_matching():
    """Test semester normalization and matching"""
    
    parser = AdvancedTableParser()
    
    # Test cases - config format vs parsed format
    test_cases = [
        # (config_semester, parsed_semester, should_match)
        ("BS (SE) - 5C", "BS(SE) - 5C", True),
        ("BS (CS) - 5B", "BS(CS) - 5B", True),  
        ("BS (AI) - 3A", "BS(AI) - 3A", True),
        ("BS(CS) - 5B", "BS(CS) - 5B", True),
        ("BS(CS) - 5B", "BS (CS) - 5B", True),
        ("BS(AI) - 5B", "BS(CS) - 5B", True),  # Data error case
        ("BS(CS) - 5B", "BS(AI) - 5B", True),  # Data error case
    ]
    
    print("🔍 Testing semester matching logic:")
    for config_sem, parsed_sem, expected in test_cases:
        normalized_config = parser._normalize_semester(config_sem)
        normalized_parsed = parser._normalize_semester(parsed_sem)
        matches = parser._semester_matches(parsed_sem, config_sem)
        
        status = "✅" if matches == expected else "❌"
        print(f"{status} '{config_sem}' vs '{parsed_sem}'")
        print(f"    Normalized: '{normalized_config}' vs '{normalized_parsed}'")
        print(f"    Matches: {matches} (expected: {expected})")
        print()

if __name__ == "__main__":
    test_semester_matching()