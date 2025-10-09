"""
Enhanced parser with comprehensive data validation and fallback mechanisms.
This parser provides robust handling of missing or malformed data and flexible semester matching.
"""

import re
import logging
from typing import List, Dict, Optional, Any
from .parser import parse_schedule_html, parse_schedule_text
from .semester_matcher import flexible_semester_match, normalize_semester

logger = logging.getLogger(__name__)

class DataValidator:
    """Validates and cleans extracted schedule data"""
    
    @staticmethod
    def is_valid_data(value: Any) -> bool:
        """Check if data is valid and not null/empty"""
        return (value and 
                value != 'null' and 
                value != 'undefined' and 
                value != '' and 
                isinstance(value, str) and 
                value.strip() != '')
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text data"""
        if not DataValidator.is_valid_data(text):
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common artifacts
        cleaned = re.sub(r'\[.*?\]', '', cleaned)  # Remove bracketed text
        cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove parenthetical unless it's credits
        
        # Restore credits pattern
        credits_match = re.search(r'\(\d+,\d+\)', text)
        if credits_match:
            cleaned += ' ' + credits_match.group()
        
        return cleaned.strip()

class DataCorrector:
    """Provides corrections and fallbacks for missing data"""
    
    # Known course corrections
    COURSE_CORRECTIONS = {
        'CSCL 2205': {
            'course_title': 'Lab: Operating Systems',
            'time': '02:00 PM - 05:00 PM',
            'room': '-',
            'campus': 'SZABIST University Campus H-8/4 ISB',
            'credits': '(0,1)'
        }
        # Add more as needed
    }
    
    # Pattern-based fallbacks
    DEPARTMENT_NAMES = {
        'CS': 'Computer Science',
        'CSCL': 'Computer Science Lab',
        'SE': 'Software Engineering', 
        'SECL': 'Software Engineering Lab',
        'MATH': 'Mathematics',
        'ENG': 'English',
        'PHY': 'Physics',
        'CHEM': 'Chemistry',
        'BBA': 'Business Administration',
        'MBA': 'Master of Business Administration'
    }
    
    @classmethod
    def get_corrected_value(cls, field: str, item: Dict[str, Any]) -> Optional[str]:
        """Get corrected value for a specific field"""
        course = item.get('course', '')
        
        # Check for exact course corrections
        if course in cls.COURSE_CORRECTIONS:
            correction = cls.COURSE_CORRECTIONS[course].get(field)
            if correction:
                return correction
        
        # Pattern-based corrections
        if field == 'course_title':
            return cls._generate_course_title(item)
        elif field == 'time':
            return cls._generate_time_fallback(item)
        elif field == 'room':
            return cls._generate_room_fallback(item)
        elif field == 'campus':
            return cls._generate_campus_fallback(item)
        elif field == 'faculty':
            return cls._generate_faculty_fallback(item)
        
        return None
    
    @classmethod
    def _generate_course_title(cls, item: Dict[str, Any]) -> str:
        """Generate a reasonable course title from course code"""
        course = item.get('course', '')
        if not course:
            return 'Course Title Not Available'
        
        # Parse course code
        course_match = re.match(r'([A-Z]+)\s*(\d+)', course)
        if course_match:
            dept = course_match.group(1)
            num = course_match.group(2)
            
            dept_name = cls.DEPARTMENT_NAMES.get(dept, dept)
            
            # Handle lab courses
            if 'L' in dept:
                base_dept = dept.replace('L', '')
                base_name = cls.DEPARTMENT_NAMES.get(base_dept, base_dept)
                return f'{base_name} Lab {num}'
            
            return f'{dept_name} Course {num}'
        
        return f'Course: {course}'
    
    @classmethod
    def _generate_time_fallback(cls, item: Dict[str, Any]) -> str:
        """Generate time fallback based on course patterns"""
        course = item.get('course', '')
        course_title = item.get('course_title', '')
        
        # Lab courses typically have longer durations
        if ('L' in course or 'lab' in course_title.lower()):
            return 'TBD (Lab Session - 3 hours)'
        
        # Regular courses
        return 'TBD'
    
    @classmethod
    def _generate_room_fallback(cls, item: Dict[str, Any]) -> str:
        """Generate room fallback based on course patterns"""
        course = item.get('course', '')
        course_title = item.get('course_title', '')
        
        # Check if room data exists in raw_cells or full_text
        raw_text = item.get('full_text', '') or ' '.join(item.get('raw_cells', []))
        
        # Try to extract room from raw text if not already found
        if raw_text:
            # Look for room patterns: numbers, "Lab XX", "Digital Lab", etc.
            room_patterns = [
                r'\b(Lab\s+\d+)\b',                    # Lab 02, Lab 05
                r'\b(Digital\s+Lab)\b',                # Digital Lab
                r'\b(Computer\s+Lab)\b',               # Computer Lab
                r'\b(\d{3})\b',                        # Room numbers like 302
                r'\b(NB-\d+|OB-\d+)\b',               # Building codes
                r'\b(Lab\s+\w+)\b'                     # Other lab variations
            ]
            
            for pattern in room_patterns:
                match = re.search(pattern, raw_text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        # Fallback based on course type
        if ('L' in course or 'lab' in course_title.lower()):
            if 'computer' in course_title.lower() or 'CS' in course:
                return 'Computer Lab (TBD)'
            elif 'digital' in course_title.lower():
                return 'Digital Lab'
            else:
                return 'Lab (TBD)'
        
        # Online courses
        if ('online' in course_title.lower() or 
            'virtual' in course_title.lower() or
            'distance' in course_title.lower()):
            return 'Online'
        
        return 'TBD'
    
    @classmethod
    def _generate_campus_fallback(cls, item: Dict[str, Any]) -> str:
        """Generate campus fallback based on semester/program patterns"""
        semester = item.get('semester', '') or item.get('class_section', '')
        
        # Most SZABIST courses are at main campus
        if any(prog in semester.upper() for prog in ['BS', 'MS', 'MBA', 'BBA']):
            return 'SZABIST University Campus H-8/4 ISB'
        
        return 'SZABIST University Campus'
    
    @classmethod
    def _generate_faculty_fallback(cls, item: Dict[str, Any]) -> str:
        """Generate faculty fallback"""
        return 'TBD'

class EnhancedParser:
    """Enhanced parser with validation and correction"""
    
    def __init__(self):
        self.validator = DataValidator()
        self.corrector = DataCorrector()
    
    def parse_and_enhance(self, html: str, semesters: List[str]) -> List[Dict]:
        """Parse HTML and enhance the results with validation and corrections"""
        
        # First, use the original parser
        try:
            items = parse_schedule_html(html, semesters)
        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            try:
                # Fallback to text parsing
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html or "", "lxml")
                plain_text = soup.get_text(separator="\n", strip=True)
                items = parse_schedule_text(plain_text, semesters)
            except Exception as e2:
                logger.error(f"Text parsing also failed: {e2}")
                return []
        
        # Enhance each item
        enhanced_items = []
        for item in items:
            enhanced_item = self._enhance_item(item)
            enhanced_items.append(enhanced_item)
        
        logger.info(f"Enhanced {len(enhanced_items)} schedule items")
        return enhanced_items
    
    def _enhance_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance a single schedule item with validation and corrections"""
        enhanced = item.copy()
        
        # List of fields to validate and correct
        fields_to_check = [
            'course_title', 'time', 'room', 'campus', 'faculty'
        ]
        
        for field in fields_to_check:
            current_value = enhanced.get(field)
            
            # If data is invalid, try to get a correction
            if not self.validator.is_valid_data(current_value):
                corrected_value = self.corrector.get_corrected_value(field, enhanced)
                if corrected_value:
                    enhanced[field] = corrected_value
                    logger.debug(f"Corrected {field} for {enhanced.get('course', 'unknown')}: {corrected_value}")
            else:
                # Clean valid data
                enhanced[field] = self.validator.clean_text(current_value)
        
        # Additional enhancements
        enhanced = self._add_metadata(enhanced)
        
        return enhanced
    
    def _add_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Add helpful metadata to the item"""
        item['data_quality'] = self._assess_data_quality(item)
        item['enhanced'] = True
        
        # Mark fields that were corrected
        corrected_fields = []
        if item.get('course') in self.corrector.COURSE_CORRECTIONS:
            corrected_fields.append('corrected_from_known_issues')
        
        if corrected_fields:
            item['corrections_applied'] = corrected_fields
        
        return item
    
    def _assess_data_quality(self, item: Dict[str, Any]) -> str:
        """Assess the quality of the data"""
        required_fields = ['course', 'time', 'room', 'faculty', 'campus']
        valid_fields = sum(1 for field in required_fields 
                          if self.validator.is_valid_data(item.get(field)))
        
        quality_percentage = (valid_fields / len(required_fields)) * 100
        
        if quality_percentage >= 80:
            return 'excellent'
        elif quality_percentage >= 60:
            return 'good'
        elif quality_percentage >= 40:
            return 'fair'
        else:
            return 'poor'

# Convenience function to use the enhanced parser
def parse_schedule_enhanced(html: str, semesters: List[str]) -> List[Dict]:
    """Main function to parse schedule with enhancements"""
    parser = EnhancedParser()
    return parser.parse_and_enhance(html, semesters)