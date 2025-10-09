"""
Test script for semester matching functionality.
Run this to verify that semester matching works correctly.
"""

import sys
import os

# Add the parent directory to the path so we can import the scraper modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.scraper.semester_matcher import (
    normalize_semester,
    tokenize_semester, 
    generate_semester_variations,
    flexible_semester_match,
    find_best_semester_match
)

def test_semester_matching():
    """Test the flexible semester matching system"""
    
    print("🔍 Testing Semester Matching System")
    print("=" * 50)
    
    # Test case: User sets "BS(SE)-4A" as allowed semester
    allowed_semesters = ["BS(SE)-4A"]
    
    # Test variations that should all match
    test_variations = [
        "BS(SE)-4A",          # Exact match
        "BS(SE) - 4A",        # Spaces around dash
        "BS (SE)-4A",         # Space before parentheses
        "BS (SE) - 4A",       # Spaces everywhere
        "BS( SE)-  4A",       # Irregular spacing
        "BS( SE) -  4A",      # More irregular spacing
        "BS(SE)- 4A",         # Space after dash
        "BS (SE)- 4A",        # Mixed spacing
    ]
    
    print(f"✅ Allowed semester: {allowed_semesters[0]}")
    print(f"🎯 Testing {len(test_variations)} variations...")
    print()
    
    all_passed = True
    
    for i, variation in enumerate(test_variations, 1):
        # Create a mock email text
        email_text = f"Sample email content with semester {variation} and other text"
        
        # Test the matching
        matches = flexible_semester_match(variation, email_text, allowed_semesters)
        
        # Show results
        status = "✅ PASS" if matches else "❌ FAIL"
        print(f"{i:2}. {status} | '{variation}' -> {matches}")
        
        if not matches:
            all_passed = False
    
    print()
    print("🔧 Technical Details:")
    print("-" * 30)
    
    base_semester = allowed_semesters[0]
    print(f"Base semester: '{base_semester}'")
    print(f"Normalized: '{normalize_semester(base_semester)}'")
    print(f"Tokenized: '{tokenize_semester(base_semester)}'")
    print()
    
    variations = generate_semester_variations(base_semester)
    print(f"Generated {len(variations)} variations:")
    for var in variations:
        print(f"  - '{var}' -> token: '{tokenize_semester(var)}'")
    
    print()
    print("🎯 Overall Result:")
    if all_passed:
        print("✅ ALL TESTS PASSED! Semester matching is working correctly.")
        print("💪 Your system will now handle ALL spacing variations!")
    else:
        print("❌ Some tests failed. Check the implementation.")
    
    print()
    print("🚀 Real-world test:")
    sample_emails = [
        "Class schedule for BS (SE) - 4A students on Monday",
        "Schedule update for BS( SE)-  4A section",
        "Timetable for BS(SE) - 4A - Computer Lab session"
    ]
    
    for email in sample_emails:
        found = find_best_semester_match(email, allowed_semesters)
        print(f"📧 '{email[:40]}...' -> Found: '{found}'")

if __name__ == "__main__":
    test_semester_matching()