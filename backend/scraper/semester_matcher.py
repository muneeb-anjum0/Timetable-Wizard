"""
Enhanced semester matching utilities for handling various formatting variations.
Handles cases like: BS(SE)-4A, BS (SE) - 4A, BS( SE)-  4A, etc.
"""

import re
from typing import List, Set

def normalize_semester(semester: str) -> str:
    """
    Normalize semester string by removing extra spaces and standardizing format.
    Examples:
    - 'BS (SE) - 4A' -> 'BS(SE)-4A'
    - 'BS( SE)-  4A' -> 'BS(SE)-4A'
    - 'BS(SE) - 4A' -> 'BS(SE)-4A'
    """
    if not semester:
        return ""
    
    # Remove extra spaces around parentheses and dashes
    normalized = re.sub(r'\s*\(\s*', '(', semester)
    normalized = re.sub(r'\s*\)\s*', ')', normalized)
    normalized = re.sub(r'\s*-\s*', '-', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)  # Multiple spaces to single space
    
    return normalized.strip()

def tokenize_semester(semester: str) -> str:
    """
    Create a tokenized version for matching (removes all non-alphanumeric).
    Examples:
    - 'BS(SE)-4A' -> 'BSSE4A'
    - 'BS (SE) - 4A' -> 'BSSE4A'
    """
    return re.sub(r'[^A-Za-z0-9]', '', semester.upper())

def generate_semester_variations(semester: str) -> List[str]:
    """
    Generate common variations of a semester string for flexible matching.
    
    Args:
        semester: Base semester string like 'BS(SE)-4A'
    
    Returns:
        List of variations including different spacing patterns
    """
    if not semester:
        return []
    
    # First normalize the input
    base = normalize_semester(semester)
    
    # Extract components using regex
    match = re.match(r'([A-Z]+)\(([A-Z]+)\)-?(\d+[A-Z])', base.upper())
    if not match:
        # If it doesn't match expected pattern, return normalized version
        return [base]
    
    degree, specialization, section = match.groups()
    
    # Generate variations
    variations = [
        f"{degree}({specialization})-{section}",           # BS(SE)-4A
        f"{degree}({specialization}) - {section}",         # BS(SE) - 4A  
        f"{degree} ({specialization})-{section}",          # BS (SE)-4A
        f"{degree} ({specialization}) - {section}",       # BS (SE) - 4A
        f"{degree}( {specialization})-  {section}",       # BS( SE)-  4A
        f"{degree}( {specialization}) -  {section}",      # BS( SE) -  4A
        f"{degree}({specialization})- {section}",         # BS(SE)- 4A
        f"{degree} ({specialization})- {section}",        # BS (SE)- 4A
    ]
    
    # Add the original and normalized versions
    variations.append(semester)
    variations.append(base)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for var in variations:
        if var not in seen:
            seen.add(var)
            unique_variations.append(var)
    
    return unique_variations

def flexible_semester_match(target_semester: str, email_text: str, allowed_semesters: List[str]) -> bool:
    """
    Check if a target semester matches any allowed semester with flexible formatting.
    
    Args:
        target_semester: Semester string found in email (potentially with varied formatting)
        email_text: Full email text for context
        allowed_semesters: List of allowed semester patterns
    
    Returns:
        True if target_semester matches any allowed semester
    """
    if not target_semester or not allowed_semesters:
        return False
    
    target_token = tokenize_semester(target_semester)
    
    # Check against all allowed semesters and their variations
    for allowed in allowed_semesters:
        allowed_token = tokenize_semester(allowed)
        
        # Direct token match
        if target_token == allowed_token:
            return True
        
        # Check if any variation of the allowed semester matches
        for variation in generate_semester_variations(allowed):
            if tokenize_semester(variation) == target_token:
                return True
        
        # Check if target semester appears in any variation of allowed semester
        for variation in generate_semester_variations(allowed):
            if variation.upper() in email_text.upper():
                return True
    
    return False

def find_best_semester_match(email_text: str, allowed_semesters: List[str]) -> str:
    """
    Find the best matching semester from email text based on allowed semesters.
    
    Args:
        email_text: Full email text to search
        allowed_semesters: List of allowed semester patterns
    
    Returns:
        Best matching semester string or empty string if none found
    """
    if not allowed_semesters:
        return ""
    
    # Look for semester patterns in the email
    semester_patterns = [
        r'\b([A-Z]+\s*\(\s*[A-Z]+\s*\)\s*-?\s*\d+[A-Z])\b',  # BS(SE)-4A variations
        r'\b([A-Z]+\s+[A-Z]+\s*-?\s*\d+[A-Z])\b',            # Alternative formats
    ]
    
    found_semesters = []
    for pattern in semester_patterns:
        matches = re.findall(pattern, email_text, re.IGNORECASE)
        found_semesters.extend(matches)
    
    # Check each found semester against allowed semesters
    for found in found_semesters:
        if flexible_semester_match(found, email_text, allowed_semesters):
            return normalize_semester(found)
    
    # If no direct match, try partial matching
    for allowed in allowed_semesters:
        for variation in generate_semester_variations(allowed):
            if variation.upper() in email_text.upper():
                return normalize_semester(allowed)
    
    return ""

# Test function to verify the system works
def test_semester_matching():
    """Test function to verify semester matching works correctly"""
    test_cases = [
        ("BS(SE)-4A", ["BS(SE)-4A"]),
        ("BS (SE) - 4A", ["BS(SE)-4A"]),
        ("BS( SE)-  4A", ["BS(SE)-4A"]),
        ("BS(SE) - 4A", ["BS(SE)-4A"]),
        ("BS (SE)- 4A", ["BS(SE)-4A"]),
    ]
    
    print("Testing semester matching...")
    for target, allowed in test_cases:
        result = flexible_semester_match(target, f"Test email with {target}", allowed)
        print(f"'{target}' matches {allowed}: {result}")
        
        variations = generate_semester_variations(allowed[0])
        print(f"  Variations for '{allowed[0]}': {variations[:3]}...")  # Show first 3
    
    print("All tests completed!")

if __name__ == "__main__":
    test_semester_matching()