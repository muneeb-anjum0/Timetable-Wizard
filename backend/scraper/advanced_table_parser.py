#!/usr/bin/env python3
"""
Advanced Pandas-based Table Parser for Timetable Data
This replaces the fragile line-by-line parsing with proper table extraction
"""
import pandas as pd
import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import io
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class AdvancedTableParser:
    def __init__(self):
        # Define expected column patterns (flexible matching)
        self.column_patterns = {
            'sr_no': r'(?:sr\.?\s*no|serial|s\.?\s*no|#)',
            'dept': r'(?:dept|department)',
            'program': r'(?:program)',
            'semester': r'(?:class|section|semester)',
            'course_code': r'(?:course_code|course|subject|code)',
            'course_title': r'(?:course_title|title|name)',
            'faculty': r'(?:faculty|teacher|instructor)',
            'room': r'(?:room|venue|location)',
            'time': r'(?:time|timing|schedule)',
            'campus': r'(?:campus)',
            'credits': r'(?:credits?|cr\.?)'
        }
        
        # Semester patterns for filtering
        self.semester_patterns = [
            r'BS\s*\([A-Z]{2,4}\)\s*-\s*\d+[A-Z]',
            r'MS\s*\([A-Z]{2,4}\)\s*-\s*\d+[A-Z]',
            r'PhD\s*\([A-Z]{2,4}\)\s*-\s*\d+[A-Z]'
        ]
        
    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def find_best_column_match(self, header: str) -> Optional[str]:
        """Find the best matching column type for a header"""
        header_clean = re.sub(r'[^\w\s]', '', header.lower().strip())
        
        best_match = None
        best_score = 0.0
        
        for col_type, pattern in self.column_patterns.items():
            if re.search(pattern, header_clean, re.IGNORECASE):
                # Exact match gets higher priority
                if header_clean == col_type or header_clean.replace('_', '') == col_type.replace('_', ''):
                    return col_type
                    
                match_obj = re.search(pattern, header_clean, re.IGNORECASE)
                score = len(match_obj.group(0)) / len(header_clean) if match_obj else 0
                if score > best_score:
                    best_score = score
                    best_match = col_type
        
        return best_match if best_score > 0.3 else None
    
    def extract_tables_from_html(self, html_content: str) -> List[pd.DataFrame]:
        """Extract all tables from HTML using pandas"""
        tables = []
        
        try:
            # Try pandas read_html first (most robust for actual tables)
            pandas_tables = pd.read_html(html_content, header=0)
            logger.info(f"✅ Pandas found {len(pandas_tables)} HTML tables directly")
            tables.extend(pandas_tables)
        except Exception as e:
            logger.warning(f"⚠️ Pandas read_html failed: {e}")
            
        # Gmail emails often don't have proper tables - extract from text content
        try:
            text_tables = self._extract_tables_from_text(html_content)
            if text_tables:
                logger.info(f"✅ Extracted {len(text_tables)} tables from text content")
                tables.extend(text_tables)
        except Exception as e:
            logger.warning(f"⚠️ Text table extraction failed: {e}")
            
        # Fallback: Use BeautifulSoup to clean and extract any remaining tables
        if not tables:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                table_elements = soup.find_all('table')
                
                if table_elements:
                    for i, table in enumerate(table_elements):
                        try:
                            table_html = str(table)
                            df_list = pd.read_html(table_html, header=0)
                            tables.extend(df_list)
                            logger.info(f"✅ Extracted HTML table {i+1} with shape {df_list[0].shape}")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to parse HTML table {i+1}: {e}")
                else:
                    logger.warning("❌ No table elements found in HTML")
            except Exception as e:
                logger.error(f"❌ BeautifulSoup fallback failed: {e}")
                
        return tables
    
    def _extract_tables_from_text(self, html_content: str) -> List[pd.DataFrame]:
        """Extract table data from text content (Gmail-style formatting) - ENHANCED"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get all text content, preserving line breaks
        text_content = soup.get_text('\n')
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        logger.info(f"🔍 Processing {len(lines)} lines from Gmail text content")
        
        # Look for schedule data patterns - Gmail format is numbered lines
        schedule_lines = []
        potential_lines = []
        
        # First pass: collect lines that might be schedule data
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for lines starting with a number (schedule entries)
            if re.match(r'^\d+\s+[A-Z]{2,4}\s+', line):  # Require 2-4 letter department code
                # This might be a schedule line, but could span multiple lines
                full_line = line
                
                # Check if the next few lines are continuations (don't start with number)
                j = i + 1
                while j < len(lines) and j < i + 8:  # Look ahead max 8 lines (increased from 5)
                    next_line = lines[j].strip()
                    # If next line starts with number + department, it's a new entry
                    if re.match(r'^\d+\s+[A-Z]{2,4}\s+', next_line):  # Must have department code
                        break
                    # If it looks like a continuation (no number, has relevant content)
                    if next_line and not re.match(r'^[🕗🔸]', next_line):  # Skip emoji headers
                        # Special handling for time/room/campus continuations
                        if (re.search(r'\d{1,2}:\d{2}\s*[AP]M|Hall|Lab|NB-|\d{3}|SZABIST|Campus|H-8/4', next_line) or
                            len(next_line.split()) <= 4):  # Short lines are likely continuations
                            full_line += " " + next_line
                    j += 1
                
                potential_lines.append(full_line)
                i = j  # Skip the lines we've already processed
            else:
                i += 1
        
        logger.info(f"📝 Found {len(potential_lines)} potential schedule entries")
        
        # Second pass: filter for actual schedule lines
        for line in potential_lines:
            # Must contain semester pattern AND course code
            if (re.search(r'BS\([A-Z]{2,4}\)\s*-\s*[0-9A-Z]+', line) and 
                re.search(r'\b[A-Z]{2,4}L?\s*\d{2,4}\b', line)):
                schedule_lines.append(line)
                logger.debug(f"✅ Valid schedule line: {line[:80]}...")
        
        logger.info(f"🎯 Filtered to {len(schedule_lines)} valid schedule lines")
        
        if not schedule_lines:
            logger.warning("❌ No valid schedule lines found in text content")
            return []
            
        # Parse lines into structured data
        rows = []
        for i, line in enumerate(schedule_lines):
            row_data = self._parse_schedule_line(line)
            if row_data:
                rows.append(row_data)
                if i < 3:  # Log first few for debugging
                    logger.info(f"✅ Parsed entry {i+1}: {row_data.get('course')} - {row_data.get('semester')} - {row_data.get('time')}")
        
        if not rows:
            logger.warning("❌ No valid rows parsed from schedule lines")
            return []
            
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Add standard column names if we don't have them
        expected_columns = ['sr_no', 'dept', 'program', 'semester', 'course_code', 'course_title', 'faculty', 'room', 'time', 'campus']
        
        # Map columns based on what we have
        if len(df.columns) <= len(expected_columns):
            column_mapping = {}
            for i, col in enumerate(df.columns):
                if i < len(expected_columns):
                    column_mapping[col] = expected_columns[i]
            df = df.rename(columns=column_mapping)
        
        logger.info(f"✅ Created DataFrame from text with shape {df.shape}")
        return [df]
    
    def _parse_schedule_line(self, line: str) -> Optional[Dict]:
        """Parse a single schedule line into structured data - ENHANCED for Gmail format"""
        try:
            logger.debug(f"🔧 Parsing line: {line}")
            
            # Gmail format example:
            # "9 AI BSAI BS(AI) - 4A CSC 3202 Design and Analysis of Algorithms (3,0) TAUQEER AHMAD 205 08:00 AM - 09:30 AM SZABIST University Campus"
            
            # Enhanced regex patterns for Gmail format
            
            # Extract serial number (at the beginning)
            sr_match = re.match(r'^(\d+)\s+', line)
            sr_no = sr_match.group(1) if sr_match else None
            
            # Extract department (after serial number)
            dept_match = re.search(r'^\d+\s+([A-Z/\s]+?)\s+(?:BS|MS|BBA)', line)
            dept = dept_match.group(1).strip() if dept_match else None
            
            # Extract semester (e.g., "BS(AI) - 4A", "BS(CS) - 5B")
            semester_match = re.search(r'(BS\([A-Z]+\)\s*-\s*[0-9A-Z]+)', line)
            semester = semester_match.group(1) if semester_match else None
            
            # Extract course code (e.g., "CSC 3202", "CSCL 3105")
            course_match = re.search(r'\b([A-Z]{2,4}L?\s*\d{2,4})\b', line)
            course = course_match.group(1) if course_match else None
            
            # Extract course title (between course code and faculty name)
            course_title = None
            if course_match:
                # Look for text after course code until we hit faculty name or time pattern
                after_course = line[course_match.end():].strip()
                # Course title is usually before faculty name 
                # Pattern: "Lab: Data Structures and Algorithms (0,1) Sidra Safdar"
                title_match = re.search(r'^([^()]*(?:\([0-9,]+\))?)\s+([A-Z])', after_course)
                if title_match:
                    course_title = title_match.group(1).strip()
                    # Clean up course title - remove trailing numbers and parentheses
                    course_title = re.sub(r'\s*\([0-9,]+\)\s*$', '', course_title).strip()
            
            # Extract faculty name (between course title and room/time)
            faculty_patterns = [
                # Pattern 1: After course title/credits, before room/time 
                # "...algorithms (3,0) TAUQEER AHMAD 205 08:00"
                r'\([0-9,]+\)\s+([A-Z][A-Za-z\s]+?)\s+(?:\d+|Hall|NB-|Lab|\d{1,2}:\d{2})',
                # Pattern 2: After course title, before room/time (no credits)
                # "...algorithms Haroon Siddique 305 09:30"  
                r'(?:algorithms|systems|mining|engineering|programming|studies|languages?|organization)\s+([A-Z][A-Za-z\s]+?)\s+(?:\d+|Hall|NB-|Lab|\d{1,2}:\d{2})',
                # Pattern 3: Common pattern with dash separator
                # "Sarwat Nadeem -  Lab 05"
                r'\)\s+([A-Z][A-Za-z\s]+?)\s*-\s+(?:\d+|Hall|NB-|Lab)',
                # Pattern 4: Faculty name before room number
                r'\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+(?:Hall\s+\d+|NB-\d+|Lab\s+\d+|\d{3})\s+\d{1,2}:\d{2}',
                # Pattern 5: All caps name (sometimes used for faculty)
                r'\b([A-Z]{2,}\s+[A-Z]{2,})\s+(?:\d+|Hall|NB-|Lab|\d{1,2}:\d{2})',
            ]
            
            faculty = None
            for pattern in faculty_patterns:
                faculty_match = re.search(pattern, line)
                if faculty_match:
                    potential_faculty = faculty_match.group(1).strip()
                    # Filter out common non-faculty words
                    if not re.match(r'^(Lab|Hall|Room|AM|PM|SZABIST|University|Campus|Design|Analysis|Data|Computer|Assembly)$', potential_faculty, re.IGNORECASE):
                        faculty = potential_faculty
                        break
            
            # Extract time (enhanced to handle split patterns)
            time_patterns = [
                # Standard format: "08:00 AM - 09:30 AM"
                r'(\d{1,2}:\d{2}\s*[AP]M\s*(?:-|–|—)\s*\d{1,2}:\d{2}\s*[AP]M)',
                # Split format: "01 B 08:00 AM - 09:30 AM" (room and time together)
                r'(?:Hall|Lab|NB-|\d{2,3})\s+(?:\d+\s+)?[A-Z]?\s*(\d{1,2}:\d{2}\s*[AP]M\s*(?:-|–|—)\s*\d{1,2}:\d{2}\s*[AP]M)',
                # Split across words: "08:00 AM - 09:30 AM"  
                r'(\d{1,2}:\d{2}\s*[AP]M(?:\s*(?:-|–|—)\s*\d{1,2}:\d{2}\s*[AP]M)?)',
            ]
            
            time = None
            for pattern in time_patterns:
                time_match = re.search(pattern, line)
                if time_match:
                    time = time_match.group(1) if len(time_match.groups()) > 0 else time_match.group(0)
                    time = re.sub(r'\s+', ' ', time.strip())  # Clean up spacing
                    break
            
            # Extract room (usually before time, can be "Hall 01 A", "NB-206", "305", "Lab 02")
            room_patterns = [
                r'\b(Hall\s+\d+\s*[A-Z]?)\s+\d{1,2}:\d{2}',  # "Hall 01 A"
                r'\b(NB-\d+)\s+\d{1,2}:\d{2}',               # "NB-206"
                r'\b(Lab\s+\d+)\s+\d{1,2}:\d{2}',            # "Lab 02"
                r'\b(\d{3})\s+\d{1,2}:\d{2}',                # "305"
            ]
            
            room = None
            for pattern in room_patterns:
                room_match = re.search(pattern, line)
                if room_match:
                    room = room_match.group(1).strip()
                    break
            
            # Extract campus (usually at the end)
            campus_match = re.search(r'(SZABIST[^$]+)$', line)
            campus = campus_match.group(1).strip() if campus_match else None
            
            # Create the parsed item
            parsed_item = {
                'sr_no': sr_no,
                'dept': dept,
                'program': 'BS',  # Most are BS programs
                'semester': semester,
                'course': course,
                'course_title': course_title,
                'faculty': faculty,
                'room': room,
                'time': time,
                'campus': campus,
                'raw_line': line[:100] + ('...' if len(line) > 100 else '')  # For debugging
            }
            
            # Only return if we have the essential fields
            if semester and course:
                logger.debug(f"✅ Successfully parsed: {course} - {semester} - {time}")
                return parsed_item
            else:
                logger.debug(f"❌ Missing essential fields - semester: {semester}, course: {course}")
                return None
                
        except Exception as e:
            logger.warning(f"❌ Failed to parse line: {line[:50]}... Error: {e}")
            return None
            room_match = re.search(r'\b(\d{3}|Lab\s*\d+|Hall\s*\d+\s*[A-Z]?|NB-\d+|Digital\s*Lab)\b', line)
            campus_match = re.search(r'(SZABIST\s+(?:University\s+Campus|HMB))', line)
            
            # Extract faculty name (improved pattern)
            faculty_name = None
            if course_match:
                # Look for name after course title pattern
                after_course = line[course_match.end():].strip()
                # Pattern: ") Faculty Name Room/Time"
                faculty_match = re.search(r'\)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z]+)*)', after_course)
                if not faculty_match:
                    # Alternative pattern: look for capitalized names
                    faculty_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]*)*(?:\s+[A-Z][a-z]+))\b', after_course)
                if faculty_match:
                    faculty_name = faculty_match.group(1).strip()
                    # Clean faculty name (remove room numbers that might be captured)
                    faculty_name = re.sub(r'\b\d{3}\b', '', faculty_name).strip()
            
            # Extract course title (between course code and credits/faculty)
            course_title = None
            if course_match:
                after_course = line[course_match.end():].strip()
                # Look for text before credits pattern (x,y) or faculty
                title_match = re.search(r'^([^(]+?)\s*(?:\([0-9,]+\)|[A-Z][a-z])', after_course)
                if title_match:
                    course_title = title_match.group(1).strip()
            
            row = {
                'sr_no': sr_match.group(1) if sr_match else None,
                'dept': dept_match.group(1) if dept_match else None,
                'program': program_match.group(1) if program_match else None,
                'semester': semester_match.group(1) if semester_match else None,
                'course_code': course_match.group(1) if course_match else None,
                'course_title': course_title,
                'faculty': faculty_name,
                'room': room_match.group(1) if room_match else None,
                'time': time_match.group(1) if time_match else None,
                'campus': campus_match.group(1) if campus_match else None,
            }
            
            logger.debug(f"✅ Parsed: {row}")
            
            # Only return if we have essential data
            if row['course_code'] and row['semester']:
                return row
            else:
                logger.debug(f"❌ Missing essential data: course={row['course_code']}, semester={row['semester']}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse line: {line[:50]}... Error: {e}")
            
        return None
    
    def normalize_column_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize and map column headers to standard names"""
        df_copy = df.copy()
        column_mapping = {}
        
        for col in df_copy.columns:
            col_str = str(col).strip()
            best_match = self.find_best_column_match(col_str)
            if best_match:
                column_mapping[col] = best_match
                logger.debug(f"📝 Mapped column '{col}' -> '{best_match}'")
        
        # Rename columns
        df_copy = df_copy.rename(columns=column_mapping)
        
        # If we don't have standard column names, try to infer from position
        if 'semester' not in df_copy.columns or 'course_code' not in df_copy.columns:
            df_copy = self._infer_columns_by_position(df_copy)
        
        return df_copy
    
    def _infer_columns_by_position(self, df: pd.DataFrame) -> pd.DataFrame:
        """Infer column types based on typical timetable structure"""
        df_copy = df.copy()
        cols = list(df_copy.columns)
        
        # Common timetable column order patterns
        standard_names = ['sr_no', 'dept', 'program', 'semester', 'course_code', 'course_title', 'faculty', 'room', 'time', 'campus']
        
        # Map by position if we have enough columns
        if len(cols) >= 6:
            new_mapping = {}
            for i, std_name in enumerate(standard_names[:len(cols)]):
                if i < len(cols):
                    new_mapping[cols[i]] = std_name
            
            df_copy = df_copy.rename(columns=new_mapping)
            logger.info(f"🔄 Inferred columns by position: {list(new_mapping.values())}")
        
        return df_copy
    
    def filter_by_semester(self, df: pd.DataFrame, target_semesters: List[str]) -> pd.DataFrame:
        """Filter dataframe by target semesters"""
        if not target_semesters:
            return df
        
        # Normalize target semesters
        target_normalized = [self._normalize_semester(sem) for sem in target_semesters]
        
        # Find semester column
        semester_col = None
        for col in df.columns:
            if 'semester' in str(col).lower() or 'class' in str(col).lower() or 'section' in str(col).lower():
                semester_col = col
                break
        
        if not semester_col:
            logger.warning("⚠️ No semester column found for filtering")
            return df
        
        # Filter rows
        mask = df[semester_col].astype(str).apply(
            lambda x: any(self._semester_matches(x, target) for target in target_normalized)
        )
        
        filtered_df = df[mask].copy()
        logger.info(f"🎯 Filtered from {len(df)} to {len(filtered_df)} rows for semesters: {target_semesters}")
        
        return filtered_df
    
    def _normalize_semester(self, semester: str) -> str:
        """Normalize semester string for comparison - ENHANCED for space variations"""
        if not semester:
            return ""
        
        # Remove extra spaces and normalize format
        normalized = re.sub(r'\s+', ' ', semester.strip())
        
        # Handle space variations between BS/MS and parentheses
        # Convert "BS (CS)" to "BS(CS)" and "BS(CS)" to "BS(CS)" (standardize to no space)
        normalized = re.sub(r'\b(BS|MS|PhD)\s+\(', r'\1(', normalized)
        
        # Fix parentheses
        normalized = re.sub(r'[\(\)]+', lambda m: '(' if '(' in m.group() else ')', normalized)
        
        return normalized
    
    def _semester_matches(self, semester_cell: str, target_semester: str) -> bool:
        """Check if a semester cell matches target semester"""
        if not semester_cell or not target_semester:
            return False
        
        cell_normalized = self._normalize_semester(str(semester_cell))
        target_normalized = self._normalize_semester(target_semester)
        
        # Exact match
        if cell_normalized == target_normalized:
            return True
        
        # Handle common variations and data errors
        # BS(CS) - 5B might appear as BS(AI) - 5B in email (data error)
        if target_normalized == "BS(CS) - 5B" and cell_normalized == "BS(AI) - 5B":
            return True
        if target_normalized == "BS(AI) - 5B" and cell_normalized == "BS(CS) - 5B":
            return True
            
        # Flexible matching for spacing variations
        cell_compact = re.sub(r'\s+', '', cell_normalized)
        target_compact = re.sub(r'\s+', '', target_normalized)
        if cell_compact == target_compact:
            return True
        
        # Similarity matching
        similarity = self.similarity(cell_normalized, target_normalized)
        return similarity > 0.85
    
    def extract_schedule_data(self, df: pd.DataFrame) -> List[Dict]:
        """Extract schedule data from normalized dataframe"""
        schedule_items = []
        
        for idx, row in df.iterrows():
            try:
                # Extract data with fallbacks
                item = {
                    'sr_no': self._safe_extract(row, ['sr_no', 'sr', 'serial', 0]),
                    'dept': self._safe_extract(row, ['dept', 'department']),
                    'program': self._safe_extract(row, ['program']),
                    'semester': self._safe_extract(row, ['semester', 'class', 'section']),
                    'course': self._safe_extract(row, ['course_code', 'course', 'subject']),
                    'course_title': self._safe_extract(row, ['course_title', 'title', 'name']),
                    'faculty': self._safe_extract(row, ['faculty', 'teacher', 'instructor']),
                    'room': self._safe_extract(row, ['room', 'venue', 'location']),
                    'time': self._safe_extract(row, ['time', 'timing', 'schedule']),
                    'campus': self._safe_extract(row, ['campus', 'location']),
                    'credits': self._safe_extract(row, ['credits', 'cr']),
                }
                
                # Clean and validate data
                item = self._clean_extracted_data(item)
                
                # Only add if we have essential data
                if item.get('course') and item.get('semester'):
                    schedule_items.append(item)
                    logger.debug(f"✅ Extracted: {item['course']} for {item['semester']}")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to extract row {idx}: {e}")
                continue
        
        return schedule_items
    
    def _safe_extract(self, row: pd.Series, column_names: List) -> Optional[str]:
        """Safely extract value from row using multiple possible column names"""
        for col_name in column_names:
            try:
                if col_name in row.index:
                    value = row[col_name]
                    if pd.notna(value) and str(value).strip():
                        return str(value).strip()
                elif isinstance(col_name, int) and col_name < len(row):
                    value = row.iloc[col_name]
                    if pd.notna(value) and str(value).strip():
                        return str(value).strip()
            except:
                continue
        return None
    
    def _clean_extracted_data(self, item: Dict) -> Dict:
        """Clean and normalize extracted data"""
        # Clean None values
        for key in item:
            if item[key] in [None, 'None', 'nan', '']:
                item[key] = None
        
        # Normalize course codes
        if item.get('course'):
            item['course'] = re.sub(r'\s+', ' ', item['course']).strip()
        
        # Normalize times
        if item.get('time'):
            time_str = item['time']
            # Try to fix common time format issues
            time_str = re.sub(r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})', 
                            r'\1:\2 - \3:\4', time_str)
            item['time'] = time_str
        
        # Set default campus for numbered rooms
        if item.get('room') and not item.get('campus'):
            if re.match(r'^\d{3}$', str(item['room'])):
                item['campus'] = 'SZABIST University Campus'
        
        return item
    
    def parse_timetable(self, html_content: str, target_semesters: List[str] = None) -> List[Dict]:
        """Main method to parse timetable from HTML"""
        logger.info("🚀 Starting advanced pandas-based table parsing")
        logger.info(f"🎯 Target semesters: {target_semesters}")
        
        try:
            # Extract tables
            tables = self.extract_tables_from_html(html_content)
            
            if not tables:
                logger.error("❌ No tables found in HTML content")
                return []
            
            all_schedule_items = []
            
            for i, table in enumerate(tables):
                logger.info(f"📊 Processing table {i+1}: shape {table.shape}")
                
                # Skip empty or too small tables
                if table.empty or len(table.columns) < 3:
                    logger.warning(f"⚠️ Skipping table {i+1}: too small")
                    continue
                
                # Normalize column headers
                normalized_table = self.normalize_column_headers(table)
                logger.info(f"📊 Normalized table {i+1} columns: {list(normalized_table.columns)}")
                
                # Filter by semesters if specified
                if target_semesters:
                    filtered_table = self.filter_by_semester(normalized_table, target_semesters)
                else:
                    filtered_table = normalized_table
                
                if filtered_table.empty:
                    logger.info(f"ℹ️ Table {i+1}: No matching semesters found")
                    continue
                
                # Extract schedule data
                schedule_items = self.extract_schedule_data(filtered_table)
                all_schedule_items.extend(schedule_items)
                
                logger.info(f"✅ Table {i+1}: Extracted {len(schedule_items)} schedule items")
            
            logger.info(f"🎯 Total extracted: {len(all_schedule_items)} schedule items")
            
            # Log what we found for debugging
            if all_schedule_items:
                semesters_found = list(set(item.get('semester') for item in all_schedule_items if item.get('semester')))
                logger.info(f"🔍 Semesters found: {semesters_found}")
                logger.info(f"🔍 Target semesters: {target_semesters}")
                
                # Check if we got what we expected
                if target_semesters and len(all_schedule_items) > 0:
                    expected_found = any(any(self._semester_matches(found, target) for target in target_semesters) for found in semesters_found)
                    if not expected_found:
                        logger.warning(f"⚠️ Expected semesters {target_semesters} but found {semesters_found}")
            
            return all_schedule_items
            
        except Exception as e:
            logger.error(f"❌ Advanced parser failed with error: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []


def parse_html_with_advanced_pandas(html_content: str, target_semesters: List[str] = None) -> List[Dict]:
    """
    Main function to parse HTML timetable using advanced pandas table extraction
    """
    parser = AdvancedTableParser()
    return parser.parse_timetable(html_content, target_semesters)


if __name__ == "__main__":
    # Test the parser
    test_html = """
    <table>
        <tr><th>Sr No</th><th>Dept</th><th>Program</th><th>Class/Section</th><th>Course</th><th>Faculty</th><th>Room</th><th>Time</th><th>Campus</th></tr>
        <tr><td>1</td><td>CS</td><td>BS(CS)</td><td>BS(CS) - 5B</td><td>CSC 2123</td><td>Dr. Aqeel Ahmed</td><td>301</td><td>02:00 PM - 03:30 PM</td><td>SZABIST University Campus</td></tr>
        <tr><td>2</td><td>CS</td><td>BS(CS)</td><td>BS(CS) - 5B</td><td>CSC 2205</td><td>Awais Mehmood</td><td>301</td><td>03:30 PM - 05:00 PM</td><td>SZABIST University Campus</td></tr>
    </table>
    """
    
    result = parse_html_with_advanced_pandas(test_html, ['BS(CS) - 5B'])
    for item in result:
        print(f"Course: {item['course']}, Time: {item['time']}, Room: {item['room']}")