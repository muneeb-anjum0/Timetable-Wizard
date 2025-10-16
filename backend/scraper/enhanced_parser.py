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
        },
        'CSC 1206': {
            'time': '12:00 PM – 01:30 PM'  # Correct time for Asim Shabir's Probability and Statistics
        },
        'PSY 8139': {
            'course_title': 'Psychotherapy and Counseling-I',
            'faculty': 'Dr. Abdur Rashid',
            'room': 'Psychology Lab',
            'time': '09:00 AM – 12:00 PM',
            'campus': 'SZABIST University Campus'
        },
        'MD 3523': {
            'course_title': 'Production Practices-II',
            'faculty': 'Azfar Hussain Jaffari',
            'room': 'TV Studio',
            'time': '02:20 PM – 05:20 PM'
        },
        'MD 2424': {
            'course_title': 'Media Psychology',
            'faculty': 'Muhammad Arslan Saeed',
            'room': 'Media Lab',
            'time': '08:00 AM – 11:00 AM'
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
        'MBA': 'Master of Business Administration',
        'PSY': 'Psychology',
        'MD': 'Media Studies'
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
        course = item.get('course', '') or ''
        course_title = item.get('course_title', '') or ''
        
        # Lab courses typically have longer durations
        if ('L' in course or 'lab' in (course_title or '').lower()):
            return 'TBD (Lab Session - 3 hours)'
        
        # Regular courses
        return 'TBD'
    
    @classmethod
    def _generate_room_fallback(cls, item: Dict[str, Any]) -> str:
        """Generate room fallback based on course patterns"""
        course = item.get('course', '') or ''
        course_title = item.get('course_title', '') or ''
        
        # Check if room data exists in raw_cells or full_text
        raw_text = item.get('full_text', '') or ' '.join(item.get('raw_cells', []))
        
        # Try to extract room from raw text if not already found
        if raw_text:
            # Look for room patterns: numbers, "Lab XX", "Digital Lab", "Psychology Lab", etc.
            room_patterns = [
                r'\b(Psychology\s+Lab)\b',             # Psychology Lab
                r'\b(Lab\s+\d+)\b',                    # Lab 02, Lab 05
                r'\b(Digital\s+Lab)\b',                # Digital Lab
                r'\b(Computer\s+Lab)\b',               # Computer Lab
                r'\b(\d{3})\b',                        # Room numbers like 302
                r'\b(NB-\d+|OB-\d+)\b',               # Building codes
                r'\b(TBD)\b',                          # TBD rooms (treat as online)
                r'\b(Online|Virtual)\b',               # Online classes
                r'\b(Lab\s+\w+)\b'                     # Other lab variations
            ]
            
            for pattern in room_patterns:
                match = re.search(pattern, raw_text, re.IGNORECASE)
                if match:
                    room = match.group(1)
                    # Convert TBD to Online for consistency
                    return 'Online' if room.upper() == 'TBD' else room
        
        # Fallback based on course type
        course_title_safe = (course_title or '').lower()
        if ('L' in course or 'lab' in course_title_safe):
            if 'computer' in course_title_safe or 'CS' in course:
                return 'Computer Lab (TBD)'
            elif 'digital' in course_title_safe:
                return 'Digital Lab'
            elif 'psychology' in course_title_safe or 'PSY' in course:
                return 'Psychology Lab'
            else:
                return 'Lab (TBD)'
        
        # Psychology courses default to Psychology Lab
        if 'PSY' in course or 'psychology' in course_title_safe:
            return 'Psychology Lab'
        
        # Online courses
        if ('online' in course_title_safe or 
            'virtual' in course_title_safe or
            'distance' in course_title_safe):
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
        
        course = item.get('course', '')
        logger.info(f"🔥 ENHANCE_ITEM CALLED for {course}")
        
        # Debug what we received from the original parser
        logger.info(f"DEBUG _enhance_item received: course_title='{item.get('course_title')}', faculty='{item.get('faculty')}', room='{item.get('room')}', raw_cells={item.get('raw_cells')}")
        
        # Fix missing course_title when raw_cells contain the data
        # This happens when the original parser's pick() function returns None
        raw_cells = item.get('raw_cells', [])
        if (not item.get('course_title') or item.get('course_title') == 'None') and len(raw_cells) > 1:
            # For 9-column format: [Sr, Dept, Program, Class/Section, Course, Faculty, Room, Time, Campus]
            # For 6-column format: [SEMESTER, COURSE_TITLE, FACULTY, ROOM, TIME, CAMPUS]
            
            if len(raw_cells) >= 9:
                # 9-column format - course is at index 4
                enhanced['course_title'] = raw_cells[4]
                logger.info(f"Fixed missing course_title from raw_cells[4]: '{raw_cells[4]}'")
            else:
                # 6-column format - course title is at index 1
                enhanced['course_title'] = raw_cells[1]
                logger.info(f"Fixed missing course_title from raw_cells[1]: '{raw_cells[1]}'")
        
        # First, fix cases where faculty field contains room data (like "Room 01")
        enhanced = self._fix_misassigned_faculty_room(enhanced)
        
        # Handle case where course field contains mixed data (happens when table structure is wrong)
        # This needs to happen first to extract the correct room before data alignment fixes
        enhanced = self._split_mixed_course_field(enhanced)
        
        # Check for data alignment issues in the raw cells
        # Only run this if the mixed course field split didn't already fix the data
        if not enhanced.get('_course_split_applied'):
            enhanced = self._fix_data_alignment(enhanced)
        
        # Check if course_title contains mixed data (title + faculty + room)
        enhanced = self._split_mixed_course_title(enhanced)
        
        # Handle case where course_title contains course code + title + faculty + room
        # This happens in the 6-column format: SEMESTER | COURSE TITLE | FACULTY | ROOM | TIME | CAMPUS
        enhanced = self._split_course_title_with_course_code(enhanced)
        
        # Clean up internal flags
        enhanced.pop('_course_split_applied', None)
        
        # Final cleanup for course titles ending with titles
        enhanced = self._clean_course_title_endings(enhanced)
        
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
        
        # Assign course codes if missing
        enhanced = self._assign_course_code(enhanced)
        
        return enhanced
    
    def _clean_course_title_endings(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Clean course titles that end with title fragments like ' Dr' or ' Prof'"""
        course_title = item.get('course_title', '')
        
        if course_title:
            # Remove common title endings that shouldn't be part of course title
            title_endings = [' Dr', ' Prof', ' Dr.', ' Prof.']
            
            for ending in title_endings:
                if course_title.endswith(ending):
                    cleaned_title = course_title[:-len(ending)].strip()
                    if cleaned_title:  # Make sure we don't end up with empty string
                        item['course_title'] = cleaned_title
                        logger.info(f"DEBUG: Cleaned course title ending '{ending}': '{course_title}' -> '{cleaned_title}'")
                        break
        
        return item
    
    def _fix_misassigned_faculty_room(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Fix cases where faculty field contains room data and extract real faculty from course_title"""
        faculty = item.get('faculty', '')
        course_title = item.get('course_title', '')
        room = item.get('room', '')
        
        # Check if faculty looks like room data
        if faculty and (faculty.startswith('Room') or faculty.startswith('Lab') or faculty.isdigit()):
            logger.info(f"DEBUG: Faculty field contains room data: '{faculty}' - extracting real faculty from title")
            
            # Move faculty data to room if room is TBD
            if not room or room.upper() in ['TBD', 'NONE']:
                item['room'] = faculty
                logger.info(f"DEBUG: Moved '{faculty}' from faculty to room")
            
            # Try to extract real faculty from course_title
            # Pattern like "Inter Law & Human Rights Dr. Taraq" -> extract "Dr. Taraq"
            faculty_patterns = [
                r'\b(Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b(Prof\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            ]
            
            extracted_faculty = None
            for pattern in faculty_patterns:
                match = re.search(pattern, course_title)
                if match:
                    extracted_faculty = match.group(1).strip()
                    # Remove the faculty from course_title
                    item['course_title'] = course_title.replace(match.group(0), '').strip()
                    logger.info(f"DEBUG: Extracted faculty '{extracted_faculty}' from course title")
                    break
            
            if extracted_faculty:
                item['faculty'] = extracted_faculty
            else:
                item['faculty'] = 'TBD'
                logger.info(f"DEBUG: Could not extract faculty from title, setting to TBD")
        
        return item

    def _assign_course_code(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Assign course codes based on course title patterns when missing"""
        
        # Skip if course code already exists
        if item.get('course'):
            return item
            
        course_title = item.get('course_title', '').strip()
        if not course_title:
            return item
        
        # Create reverse mapping from course title to course code
        title_to_code = {}
        for course_code, corrections in self.corrector.COURSE_CORRECTIONS.items():
            if 'course_title' in corrections:
                title_to_code[corrections['course_title']] = course_code
        
        # Check for exact match
        if course_title in title_to_code:
            item['course'] = title_to_code[course_title]
            logger.info(f"Assigned course code '{title_to_code[course_title]}' to course title '{course_title}'")
        else:
            # Check for partial matches (case insensitive)
            course_title_lower = course_title.lower()
            for title, code in title_to_code.items():
                if title.lower() == course_title_lower:
                    item['course'] = code
                    logger.info(f"Assigned course code '{code}' to course title '{course_title}' (case insensitive match)")
                    break
        
        return item
    
    def _split_course_title_with_course_code(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case where course_title field contains course code + title + faculty + room"""
        course_title = item.get('course_title', '')
        
        # Debug logging
        logger.info(f"DEBUG _split_course_title_with_course_code: received course_title='{course_title}'")
        
        # Skip if we already have a separate course field or if course_title looks clean
        if item.get('course') or not course_title or len(course_title) < 10:
            logger.info(f"DEBUG: Skipping split - course='{item.get('course')}', title_len={len(course_title) if course_title else 0}")
            return item
        
        # Check if course_title contains course code + mixed data
        # Pattern: "MD 2424 Media Psychology Muhammad Arslan Saeed"
        # Pattern: "Media Psychology Muhammad Arslan Lab" (no course code)
        
        # First, try to extract course code from the beginning
        course_match = re.match(r'^([A-Z]{2,4}\s*\d{3,4})\s+(.+)', course_title)
        if course_match:
            course_code = course_match.group(1).strip()
            remaining_text = course_match.group(2).strip()
            
            # Extract title and faculty using MD course logic
            if course_code.startswith('MD'):
                faculty_match = re.search(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*$', remaining_text)
                if faculty_match:
                    faculty_name = faculty_match.group(1).strip()
                    title = remaining_text[:faculty_match.start()].strip()
                    
                    item['course'] = course_code
                    item['course_title'] = title
                    if not item.get('faculty') or item.get('faculty') in ['TBD', '']:
                        item['faculty'] = faculty_name
                    
                    logger.info(f"Split course_title with course code: course='{course_code}', title='{title}', faculty='{faculty_name}'")
                else:
                    # No faculty found, just set course and title
                    item['course'] = course_code
                    item['course_title'] = remaining_text
            else:
                # For other course codes, use general logic
                item['course'] = course_code
                item['course_title'] = remaining_text
                logger.info(f"Split course_title with course code: course='{course_code}', title='{remaining_text}'")
        else:
            # No course code found, try to extract from title without course code
            # Pattern: "Media Psychology Muhammad Arslan Lab"
            # Look for faculty names in the middle and room at the end
            
            logger.info(f"DEBUG: No course code found, trying to split '{course_title}' without course code")
            
            # Try to match: Title + Faculty + Room pattern
            # Look for room patterns at the end first
            room_patterns = [
                r'\s+(Lab|Digital\s+Lab|Media\s+Lab|Psychology\s+Lab|TV\s+Studio|Computer\s+Lab|\d{3})\s*$',
                r'\s+([A-Z][a-z]+\s+Lab)\s*$'
            ]
            
            room_match = None
            for pattern in room_patterns:
                room_match = re.search(pattern, course_title, re.IGNORECASE)
                if room_match:
                    break
            
            if room_match:
                room_name = room_match.group(1).strip()
                text_before_room = course_title[:room_match.start()].strip()
                
                logger.info(f"DEBUG: Found room '{room_name}', text before room: '{text_before_room}'")
                
                # Now look for faculty in the remaining text
                faculty_match = re.search(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*$', text_before_room)
                if faculty_match:
                    faculty_name = faculty_match.group(1).strip()
                    title = text_before_room[:faculty_match.start()].strip()
                    
                    item['course_title'] = title
                    if not item.get('faculty') or item.get('faculty') in ['TBD', '']:
                        item['faculty'] = faculty_name
                    if not item.get('room') or item.get('room') in ['TBD', '']:
                        item['room'] = room_name
                    
                    logger.info(f"Split course_title without course code: title='{title}', faculty='{faculty_name}', room='{room_name}'")
                else:
                    logger.info(f"DEBUG: No faculty found in '{text_before_room}'")
            else:
                logger.info(f"DEBUG: No room pattern found in '{course_title}'")
        
        return item
    
    def _fix_data_alignment(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Fix data alignment issues where table columns are shifted"""
        raw_cells = item.get('raw_cells', [])
        
        # Handle 6-column format: [SEMESTER, COURSE_TITLE, FACULTY, ROOM, TIME, CAMPUS]
        if len(raw_cells) == 6:
            semester = raw_cells[0] if len(raw_cells) > 0 else ''
            
            if 'BS (MS)' in semester:
                # Extract from raw_cells directly to ensure correct alignment
                course_title_raw = raw_cells[1] if len(raw_cells) > 1 else ''
                faculty_raw = raw_cells[2] if len(raw_cells) > 2 else ''
                room_raw = raw_cells[3] if len(raw_cells) > 3 else ''
                time_raw = raw_cells[4] if len(raw_cells) > 4 else ''
                campus_raw = raw_cells[5] if len(raw_cells) > 5 else ''
                
                logger.info(f"BS (MS) 6-column format detected - raw data:")
                logger.info(f"  course_title_raw: '{course_title_raw}'")
                logger.info(f"  faculty_raw: '{faculty_raw}'")
                logger.info(f"  room_raw: '{room_raw}'")
                
                # Check if course title contains mixed data (title + faculty + room)
                if course_title_raw:
                    # Pattern: "Media Psychology Muhammad Arslan Lab"
                    # Split if we find faculty name patterns in the course title
                    
                    # Try to split by common faculty name patterns
                    faculty_patterns = ['Muhammad', 'Ali', 'Ahmad', 'Hassan', 'Dr\.', 'Prof\.', 'Mr\.', 'Ms\.', 'Mrs\.']
                    
                    for pattern in faculty_patterns:
                        if pattern in course_title_raw:
                            # Split on the faculty name
                            parts = course_title_raw.split(pattern, 1)
                            if len(parts) == 2:
                                # parts[0] = "Media Psychology ", parts[1] = " Arslan Lab"
                                course_only = parts[0].strip()
                                faculty_room_part = pattern + parts[1]  # "Muhammad Arslan Lab"
                                
                                # Try to separate faculty from room in the second part
                                # Look for room patterns like "Lab", "Room", etc.
                                room_patterns = [r'\b(Media\s+Lab|Psychology\s+Lab|TV\s+Studio|Computer\s+Lab|Lab\s+\d+|Lab|Room|Hall|Auditorium|Theatre)\b']
                                
                                faculty_name = ''
                                room_name = ''
                                
                                for room_pattern in room_patterns:
                                    match = re.search(room_pattern, faculty_room_part, re.IGNORECASE)
                                    if match:
                                        # Split at the room pattern
                                        room_start = match.start()
                                        faculty_name = faculty_room_part[:room_start].strip()
                                        room_name = faculty_room_part[room_start:].strip()
                                        
                                        # Special case: if room name is just "Lab" and course is about Media Psychology
                                        if room_name.lower() == 'lab' and 'media' in course_only.lower():
                                            room_name = 'Media Lab'
                                        
                                        break
                                
                                if not faculty_name:
                                    # If no room pattern found, assume entire remaining part is faculty
                                    faculty_name = faculty_room_part.strip()
                                    room_name = ''
                                
                                # Update the fields
                                item['course_title'] = course_only
                                item['faculty'] = faculty_name
                                if room_name:
                                    item['room'] = room_name
                                
                                logger.info(f"Split mixed course_title:")
                                logger.info(f"  course_title: '{course_only}'")
                                logger.info(f"  faculty: '{faculty_name}'")
                                logger.info(f"  room: '{room_name}'")
                                
                                break
                
                return item
        
        # Handle 9-column format: [Sr, Dept, Program, Class/Section, Course, Faculty, Room, Time, Campus]
        if not raw_cells or len(raw_cells) < 7:
            return item
        
        # Look for time patterns in wrong positions
        time_pattern = re.compile(r'\b\d{1,2}:\d{2}\s*(?:AM|PM)\s*[-–—]\s*\d{1,2}:\d{2}\s*(?:AM|PM)\b', re.IGNORECASE)
        campus_pattern = re.compile(r'SZABIST\s+University\s+Campus', re.IGNORECASE)
        
        # If faculty field contains what looks like a room, and room contains time, fix it
        faculty = item.get('faculty', '')
        room = item.get('room', '')
        time_val = item.get('time', '')
        campus = item.get('campus', '')
        
        logger.info(f"DEBUG data alignment check: faculty='{faculty}', room='{room}', time='{time_val}', campus='{campus}'")
        
        # Detect misalignment pattern: faculty=room, room=time, time=campus
        # Only apply this if the room field doesn't already contain a valid room name
        valid_room_patterns = [r'psychology\s+lab', r'media\s+lab', r'tv\s+studio', r'computer\s+lab', r'lab\s+\d+']
        room_is_already_valid = any(re.search(pattern, room, re.IGNORECASE) for pattern in valid_room_patterns)
        
        logger.info(f"DEBUG room_is_already_valid: {room_is_already_valid}")
        
        if (faculty and re.match(r'^(Media\s+Lab|TV\s+Studio|Lab\s+\d+|\d{3})$', faculty, re.IGNORECASE) and
            room and time_pattern.match(room) and
            time_val and campus_pattern.search(time_val) and
            not room_is_already_valid):  # Only fix if room is not already correct
            
            # Shift data to correct positions
            item['room'] = faculty  # Faculty field actually contains room
            item['time'] = room     # Room field actually contains time
            item['campus'] = time_val  # Time field actually contains campus
            item['faculty'] = 'TBD'    # Faculty was shifted, set to TBD for correction
            
            logger.info(f"Fixed data alignment for course {item.get('course', 'unknown')}: room='{faculty}', time='{room}', campus='{time_val}'")
        
        return item
    
    def _split_mixed_course_field(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Split course field if it contains mixed data (course + title + faculty + room)"""
        course_raw = item.get('course', '')
        
        if not course_raw or len(course_raw) < 20:  # If too short, probably not mixed
            return item
        
        # Pattern examples:
        # "PSY 8139 Psychotherapy and Counseling-I Dr. Abdur Rashid Psychology Lab"
        # "MD 2424 Media Psychology Muhammad Arslan Saeed"
        # "MD 3523 Production Practices-II"
        
        # Extract course code from the beginning
        course_match = re.match(r'^([A-Z]{2,4}\s*\d{3,4})\s+(.+)', course_raw)
        if course_match:
            course_code = course_match.group(1).strip()
            remaining_text = course_match.group(2).strip()
            
            # Special handling for MD courses
            if course_code.startswith('MD'):
                # For MD courses, try to find faculty name at the end
                # Pattern: "Media Psychology Muhammad Arslan Saeed"
                # Faculty names are typically 2-3 proper nouns at the end
                faculty_match = re.search(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*$', remaining_text)
                if faculty_match:
                    faculty_name = faculty_match.group(1).strip()
                    course_title = remaining_text[:faculty_match.start()].strip()
                    
                    # Validate that faculty name doesn't contain course title words
                    course_title_words = course_title.lower().split() if course_title else []
                    faculty_words = faculty_name.lower().split()
                    
                    # If faculty name contains course title words, it's probably incorrectly extracted
                    if any(word in faculty_words for word in course_title_words):
                        # Try a more restrictive pattern - look for typical name patterns
                        name_match = re.search(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s*$', remaining_text)
                        if name_match and name_match.group(1) != faculty_name:
                            faculty_name = name_match.group(1).strip()
                            course_title = remaining_text[:name_match.start()].strip()
                    
                    # Update the item
                    item['course'] = course_code
                    if course_title and len(course_title) > 2:
                        item['course_title'] = course_title
                    if faculty_name and (not item.get('faculty') or item.get('faculty') == 'TBD'):
                        item['faculty'] = faculty_name
                    
                    logger.info(f"Split MD course field: course='{course_code}', title='{course_title}', faculty='{faculty_name}'")
                    return item
                else:
                    # No faculty found, just set course and title
                    item['course'] = course_code
                    item['course_title'] = remaining_text
                    logger.info(f"Split MD course field (no faculty): course='{course_code}', title='{remaining_text}'")
                    return item
            
            # For other courses, use the original pattern matching
            faculty_patterns = [
                r'\b(Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?=\w+\s+Lab\b|\w+\s*\d+\b|Lab\s+\d+\b|TBD\b)',
                r'\b(Prof\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?=\w+\s+Lab\b|\w+\s*\d+\b|Lab\s+\d+\b|TBD\b)',
                r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?=\w+\s+Lab\b|\w+\s*\d+\b|Lab\s+\d+\b|TBD\b)',
            ]
            
            faculty_match = None
            for pattern in faculty_patterns:
                faculty_match = re.search(pattern, remaining_text, re.IGNORECASE)
                if faculty_match:
                    break
            
            if faculty_match:
                faculty_name = faculty_match.group(1).strip()
                faculty_start = faculty_match.start(1)
                
                # Extract course title (everything before faculty)
                course_title = remaining_text[:faculty_start].strip()
                
                # Extract room (everything after faculty)
                after_faculty = remaining_text[faculty_match.end():].strip()
                room_patterns = [
                    r'\b(Psychology\s+Lab)\b',
                    r'\b(Digital\s+Lab)\b',
                    r'\b(Computer\s+Lab)\b',
                    r'\b(Media\s+Lab)\b',
                    r'\b(TV\s+Studio)\b',
                    r'\b(Lab\s+\d+)\b',
                    r'\b(\w+\s+Lab)\b',
                    r'\b(\d{3})\b',
                    r'\b(TBD|Online)\b'
                ]
                
                room_name = None
                for room_pattern in room_patterns:
                    room_match = re.search(room_pattern, after_faculty, re.IGNORECASE)
                    if room_match:
                        room_name = room_match.group(1)
                        break
                
                # Update the item with extracted data
                item['course'] = course_code
                
                if course_title and len(course_title) > 2:
                    item['course_title'] = course_title
                
                # For PhD Psychology and MD courses, always override faculty and room
                # since the original parsing is misaligned for these courses
                
                # Save original misaligned values before overriding
                original_room = item.get('room')  # Contains time due to misalignment
                original_time = item.get('time')  # Contains campus due to misalignment
                
                if faculty_name:
                    item['faculty'] = faculty_name
                
                if room_name:
                    item['room'] = room_name
                
                # Fix time and campus based on original misalignment pattern
                # Original misalignment: faculty=room, room=time, time=campus
                time_pattern = re.compile(r'\b\d{1,2}:\d{2}\s*(?:AM|PM)\s*[-–—]\s*\d{1,2}:\d{2}\s*(?:AM|PM)\b', re.IGNORECASE)
                if time_pattern.search(str(original_room)):
                    item['time'] = original_room
                if 'SZABIST' in str(original_time):
                    item['campus'] = original_time
                
                # Set flag to indicate that course field was successfully split
                item['_course_split_applied'] = True
                
                logger.info(f"Split mixed course field: course='{course_code}', title='{course_title}', faculty='{faculty_name}', room='{room_name}'")
        
        return item
    
    def _split_mixed_course_title(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Split course_title field if it contains mixed data (title + faculty + room)"""
        course_title = item.get('course_title', '')
        course = item.get('course', '')
        faculty = item.get('faculty', '')
        
        if not course_title:
            return item
        
        # Skip processing if faculty is already properly set (not None, empty, or TBD)
        # BUT still process if course_title contains mixed data (like "Dr." or faculty names)
        faculty_properly_set = (faculty and faculty.strip() and 
                              faculty.strip().upper() not in ['TBD', 'NONE', 'NULL', 'ROOM', 'LAB'] and
                              not faculty.strip().startswith('Room') and
                              not faculty.strip().startswith('Lab') and
                              len(faculty.split()) >= 2)  # Real names have at least 2 words
        
        course_title_has_mixed_data = (course_title and 
                                     ('Dr.' in course_title or 'Prof.' in course_title or
                                      'Room' in course_title or 'Lab' in course_title))
        
        # For cases like "Media Research Dr" where faculty is already correct "Muhammad Riaz Raza"
        # Just clean the course title and skip complex processing
        if faculty_properly_set and course_title and course_title.endswith((' Dr', ' Prof', ' Dr.', ' Prof.')):
            logger.info(f"DEBUG: Faculty properly set, just cleaning course title ending for {course}")
            item = self._clean_course_title_endings(item)
            return item
        
        if faculty_properly_set and not course_title_has_mixed_data:
            logger.info(f"DEBUG: Skipping mixed title processing for {course} - faculty already set: '{faculty}' and no mixed data in title")
            return item
        
        logger.info(f"DEBUG _split_mixed_course_title: processing '{course_title}' for course '{course}'")
        
        # Check if course_title contains faculty names and room info
        # Pattern: "[Course Code] Course Title Dr. Faculty Name Room"
        # Example: "PSY 8139 Psychotherapy and Counseling-I Dr. Abdur Rashid Psychology Lab"
        
        # First, remove the course code from the beginning if present
        cleaned_title = course_title
        if course and course in course_title:
            cleaned_title = course_title.replace(course, '', 1).strip()
            logger.info(f"DEBUG: After removing course code '{course}': '{cleaned_title}'")
        
        # Improved faculty detection patterns - dynamic and comprehensive
        # Remove course code from title first
        cleaned_title = course_title
        if course and course in course_title:
            cleaned_title = course_title.replace(course, '', 1).strip()
            logger.info(f"DEBUG: After removing course code '{course}': '{cleaned_title}'")
        
        # Dynamic pattern matching for course_title + faculty_name + room structure
        # Pattern: "Course Title [Faculty Name] [Room/Lab]"
        
        # Step 1: Look for room patterns at the end (ordered from most specific to least)
        room_patterns = [
            r'\b(Psychology\s+Lab)\b$',
            r'\b(Media\s+Lab)\b$', 
            r'\b(Digital\s+Lab)\b$',
            r'\b(Computer\s+Lab)\b$',
            r'\b(TV\s+Studio)\b$',
            r'\b(Lab\s+\d+)\b$',
            r'\b(Chemistry\s+Lab|Physics\s+Lab|Biology\s+Lab)\b$',  # Science labs
            r'\b(\d{3})\b$',      # Room numbers like 302
            r'\b(TBD|Online)\b$',
            r'\s+(Lab)\b$'        # Just "Lab" at the end (with space before)
        ]
        
        detected_room = None
        room_end_pos = len(cleaned_title)
        
        for pattern in room_patterns:
            room_match = re.search(pattern, cleaned_title, re.IGNORECASE)
            if room_match:
                detected_room = room_match.group(1).strip()
                room_end_pos = room_match.start()
                logger.info(f"DEBUG: Detected room '{detected_room}' at position {room_end_pos}")
                break
        
        # If no specific room found but ends with "Lab", treat as generic lab
        if not detected_room and cleaned_title.strip().endswith('Lab'):
            detected_room = 'Lab'
            room_end_pos = cleaned_title.rfind('Lab')
            logger.info(f"DEBUG: Detected generic 'Lab' at position {room_end_pos}")
        
        # Step 2: Extract text before room (should contain course title + faculty)
        text_before_room = cleaned_title[:room_end_pos].strip()
        logger.info(f"DEBUG: Text before room: '{text_before_room}'")
        
        if not text_before_room:
            return item
        
        # Step 3: Smart faculty detection from the end
        # For text like "Media Psychology Muhammad Arslan", we want:
        # course_title = "Media Psychology", faculty = "Muhammad Arslan"
        
        detected_faculty = None
        faculty_start_pos = 0
        
        # Split into words for analysis
        words = text_before_room.split()
        
        if len(words) >= 2:
            # Strategy 1: Look for Dr./Prof. patterns first
            dr_prof_pattern = r'\b(Dr\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*$'
            dr_match = re.search(dr_prof_pattern, text_before_room)
            if dr_match:
                detected_faculty = dr_match.group(1).strip()
                faculty_start_pos = dr_match.start()
                logger.info(f"DEBUG: Found Dr./Prof. pattern: '{detected_faculty}' at position {faculty_start_pos}")
            else:
                # Strategy 2: Smart detection of faculty names
                # Check for 3-word faculty names first, but exclude common course title words
                course_title_words = {'psychology', 'programming', 'management', 'practices', 'counseling', 
                                     'therapy', 'media', 'digital', 'computer', 'science', 'engineering',
                                     'introduction', 'advanced', 'basic', 'fundamentals'}
                
                if (len(words) >= 3):
                    last_three_words = words[-3:]
                    # Check if all three words are proper names (not course title words)
                    if (len(last_three_words) == 3 and 
                        all(len(word) > 1 and word[0].isupper() and word[1:].islower() for word in last_three_words) and
                        not any(word.lower() in course_title_words for word in last_three_words)):
                        detected_faculty = ' '.join(last_three_words)
                        faculty_start_pos = text_before_room.rfind(detected_faculty)
                        logger.info(f"DEBUG: Found 3-word faculty name: '{detected_faculty}' at position {faculty_start_pos}")
                    else:
                        # Try 2-word faculty names
                        last_two_words = words[-2:]
                        if (len(last_two_words) == 2 and 
                            all(len(word) > 1 and word[0].isupper() and word[1:].islower() for word in last_two_words) and
                            not any(word.lower() in course_title_words for word in last_two_words)):
                            detected_faculty = ' '.join(last_two_words)
                            faculty_start_pos = text_before_room.rfind(detected_faculty)
                            logger.info(f"DEBUG: Found 2-word faculty name: '{detected_faculty}' at position {faculty_start_pos}")
                        else:
                            # Fallback: assume last 2 words are faculty (even if they might be course title words)
                            detected_faculty = ' '.join(words[-2:])
                            faculty_start_pos = text_before_room.rfind(detected_faculty)
                            logger.info(f"DEBUG: Fallback 2-word faculty: '{detected_faculty}' at position {faculty_start_pos}")
                else:
                    # For cases with only 2 words total
                    last_two_words = words[-2:]
                    if (len(last_two_words) == 2 and 
                        all(len(word) > 1 and word[0].isupper() and word[1:].islower() for word in last_two_words)):
                        detected_faculty = ' '.join(last_two_words)
                        faculty_start_pos = text_before_room.rfind(detected_faculty)
                        logger.info(f"DEBUG: Found 2-word faculty name: '{detected_faculty}' at position {faculty_start_pos}")
        
        # Step 4: Extract course title (everything before faculty)
        if detected_faculty and faculty_start_pos > 0:
            detected_title = text_before_room[:faculty_start_pos].strip()
        else:
            detected_title = text_before_room
                
        logger.info(f"DEBUG: Final parsing - title: '{detected_title}', faculty: '{detected_faculty}', room: '{detected_room}'")
        
        # Update item with detected values
        if detected_title and len(detected_title.strip()) > 0:
            item['course_title'] = detected_title.strip()
        
        if detected_faculty and len(detected_faculty.strip()) > 0:
            item['faculty'] = detected_faculty.strip()
        
        if detected_room and len(detected_room.strip()) > 0:
            item['room'] = detected_room.strip()
        
        logger.info(f"Split mixed course_title for {course}: title='{item.get('course_title')}', faculty='{item.get('faculty')}', room='{item.get('room')}'")
        
        return item
    
    def _add_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Add helpful metadata to the item"""
        item['data_quality'] = self._assess_data_quality(item)
        item['enhanced'] = True
        
        # Mark fields that were corrected
        corrected_fields = []
        course = item.get('course') or ''
        if course in self.corrector.COURSE_CORRECTIONS:
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
    logger.info("🔥 ENHANCED PARSER CALLED! 🔥")
    logger.info(f"HTML length: {len(html) if html else 0}")
    logger.info(f"Semesters: {semesters}")
    
    parser = EnhancedParser()
    result = parser.parse_and_enhance(html, semesters)
    
    logger.info(f"🔥 ENHANCED PARSER RESULT: {len(result)} items")
    for i, item in enumerate(result[:2]):
        logger.info(f"  Item {i+1}: course='{item.get('course')}', title='{item.get('course_title')}', faculty='{item.get('faculty')}', room='{item.get('room')}'")
    
    return result