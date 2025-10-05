"""
SZABIST schedule parser (tolerant).
- Finds the biggest "schedule-like" table even if headers are odd.
- Maps columns by name when possible, else falls back to common positions.
- If ALLOWED_SEMESTERS is empty, returns ALL sensible rows.
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re
from .config import settings

WS = re.compile(r"\s+")
NON_ALNUM = re.compile(r"[^A-Za-z0-9]+")

def _ws(s: str) -> str:
    return WS.sub(" ", (s or "").strip())

def _tok(s: str) -> str:
    return NON_ALNUM.sub("", (s or "").upper())

def parse_schedule_text(text: str, semesters: List[str]) -> List[Dict]:
    """
    Parse plain text schedule content with enhanced data extraction.
    This handles cases where the email is not in HTML table format.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("Parsing plain text schedule content")
    
    if not text:
        logger.warning("Empty text content")
        return []
    
    # Split into lines and look for schedule-like patterns
    lines = text.split('\n')
    want = [_tok(s) for s in (semesters or [])]
    results: List[Dict] = []
    
    # Enhanced patterns for better data extraction
    time_pattern = re.compile(r'\b(\d{1,2}:\d{2}\s*(?:AM|PM)\s*[-–—→]\s*\d{1,2}:\d{2}\s*(?:AM|PM))\b', re.IGNORECASE)
    room_pattern = re.compile(r'\b(\d{3}|Lab\s*\d+|TV\s*Studio|NB-\d+|OB-\d+)\b', re.IGNORECASE)
    course_pattern = re.compile(r'\b([A-Z]{2,4}\s*\d{3,4})\b')
    
    # Create a comprehensive mapping of all schedule data in the text
    # This helps us find missing time/campus data for incomplete entries
    time_mapping = {}
    campus_mapping = {}
    
    # First pass: collect all time and campus information
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        # Look for time patterns and try to associate them with course codes or room numbers
        time_match = time_pattern.search(line)
        if time_match:
            time_str = time_match.group(1)
            # Look for course codes or room numbers in the same line
            course_match = course_pattern.search(line)
            room_match = room_pattern.search(line)
            if course_match:
                time_mapping[course_match.group(1)] = time_str
            if room_match:
                time_mapping[room_match.group(1)] = time_str
                
        # Look for campus information
        campus_match = re.search(r'(SZABIST\s+(?:University\s+Campus|HMB)[^\n]*)', line, re.IGNORECASE)
        if campus_match:
            campus_str = campus_match.group(1)
            # Look for course codes or room numbers in the same line
            course_match = course_pattern.search(line)
            room_match = room_pattern.search(line)
            if course_match:
                campus_mapping[course_match.group(1)] = campus_str
            if room_match:
                campus_mapping[room_match.group(1)] = campus_str
    
    # Pattern for SZABIST campus (appears at the end)
    campus_pattern = re.compile(r'(SZABIST\s+University\s+Campus[^\n]*)', re.IGNORECASE)
    
    # Pattern for course titles with credits - more specific for SZABIST format
    # Format: "Course Title (credits)" or "Course Title"
    title_pattern = re.compile(r'\b[A-Z]{2,4}\s*\d{3,4}\s+([A-Z][A-Za-z\s&,-]+?)(?:\s*\([0-9,\.\s]+\)|\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*$|$)')
    
    # Pattern for credit hours
    credit_pattern = re.compile(r'\((\d+[,\.]\d+)\)')
    
    processed_lines = 0
    schedule_lines = []
    
    # First pass: identify potential schedule lines
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or len(line) < 15:  # Skip very short lines
            continue
            
        processed_lines += 1
        
        # Check if line contains schedule elements
        has_time = time_pattern.search(line)
        has_room = room_pattern.search(line)
        has_course = course_pattern.search(line)
        
        # Also look for lines with semester info even without time/room
        has_semester = any(sem.upper() in line.upper() for sem in semesters) if semesters else False
        
        if has_time or has_room or has_course or has_semester:
            schedule_lines.append((line_num, line))
    
    logger.info(f"Found {len(schedule_lines)} potential schedule lines out of {processed_lines} processed")
    
    # Second pass: process and extract data from potential lines with line continuation support
    i = 0
    while i < len(schedule_lines):
        line_num, line = schedule_lines[i]
        
        # Look for semester/class section in the line
        line_upper = line.upper()
        keep = False
        match_reason = ""
        semester_found = ""
        
        if want:
            for w in want:
                # Convert back to find the original semester string in the line
                for orig_sem in semesters:
                    if _tok(orig_sem) == w and orig_sem.upper() in line_upper:
                        keep = True
                        match_reason = f"semester match: '{orig_sem}' found in line"
                        semester_found = orig_sem
                        break
                if keep:
                    break
        else:
            # No filter - keep lines that look like class schedules
            has_time = time_pattern.search(line)
            has_room = room_pattern.search(line)
            has_course = course_pattern.search(line)
            keep = bool(has_time and (has_room or has_course))
            if keep:
                match_reason = "no filter - keeping schedule-like lines"
        
        if keep:
            # For SZABIST format, check if we need to combine with next line(s)
            combined_line = line
            course_match = course_pattern.search(line)
            
            if settings.debug_parsing and line_num == 279:
                logger.debug(f"Line 279 raw content: '{line}'")
                logger.debug(f"Line 279 length: {len(line)}")
            
            # If we have a course but missing time/room info, look ahead for continuation
            if course_match:
                has_time = time_pattern.search(line)
                has_room = room_pattern.search(line)
                has_campus = re.search(r'SZABIST', line, re.IGNORECASE)
                
                # Look ahead for continuation lines if missing important info
                if not has_time or not has_campus:
                    j = i + 1
                    while j < len(schedule_lines) and j < i + 5:  # Look ahead max 5 lines
                        next_line_num, next_line = schedule_lines[j]
                        
                        if settings.debug_parsing:
                            logger.debug(f"  Checking continuation line {next_line_num}: '{next_line}'")
                        
                        # Stop if next line clearly starts a new entry (serial number at start + course pattern)
                        if (re.match(r'^\d+\s+', next_line) and 
                            (course_pattern.search(next_line) or 
                             re.search(r'\b(BS|MS|PhD|MBA|BBA)\s*\([^)]+\)', next_line))):
                            if settings.debug_parsing:
                                logger.debug(f"  Breaking: next line starts new entry")
                            break
                            
                        # If next line has time/room/campus info OR looks like a continuation
                        if (time_pattern.search(next_line) or 
                            room_pattern.search(next_line) or 
                            re.search(r'SZABIST|Campus|HMB|University', next_line, re.IGNORECASE) or
                            # Also check for partial time patterns like "PM" or numbers followed by ":"
                            re.search(r'\b(?:AM|PM)\b|\d{1,2}:\d{2}', next_line)):
                            if settings.debug_parsing:
                                logger.debug(f"  Adding continuation: '{next_line}'")
                            combined_line += " " + next_line.strip()
                            j += 1
                        else:
                            # If the line doesn't have useful info, skip it but don't stop looking
                            if len(next_line.strip()) < 5:  # Very short lines might be formatting
                                if settings.debug_parsing:
                                    logger.debug(f"  Skipping short line: '{next_line}'")
                                j += 1
                                continue
                            else:
                                if settings.debug_parsing:
                                    logger.debug(f"  Breaking: line doesn't look like continuation")
                                break
                    
                    # Set i to the last processed line
                i = j - 1
            
            if settings.debug_parsing:
                logger.info(f"Line {line_num}: KEEPING - {match_reason}")
            
            # Extract data from the combined line
            time_match = time_pattern.search(combined_line)
            room_match = room_pattern.search(combined_line)
            course_match = course_pattern.search(combined_line)
            campus_match = re.search(r'(SZABIST\s+(?:University\s+Campus|HMB)[^\n]*)', combined_line, re.IGNORECASE)
            credit_match = credit_pattern.search(combined_line)
            sr_match = re.match(r'^(\d+)\s+', combined_line)
            dept_match = re.search(r'\b(CS|SE|EE|CE|IT|BBA|MBA|Media)\b', combined_line)
            
            # Try to extract faculty name more intelligently  
            faculty_name = _extract_faculty_szabist(combined_line, course_match, credit_match)
            
            # Extract course title more accurately
            course_title = _extract_course_title_szabist(combined_line, course_match, faculty_name)
            
            # Try to fill in missing time/campus data from our mappings
            extracted_time = time_match.group(1) if time_match else None
            extracted_campus = campus_match.group(1) if campus_match else None
            extracted_room = room_match.group(1) if room_match else None
            extracted_course = course_match.group(1) if course_match else None
            
            # If time is missing, try to find it from our mapping
            if not extracted_time and extracted_course:
                extracted_time = time_mapping.get(extracted_course)
            if not extracted_time and extracted_room:
                extracted_time = time_mapping.get(extracted_room)
                
            # If campus is missing, try to find it from our mapping  
            if not extracted_campus and extracted_course:
                extracted_campus = campus_mapping.get(extracted_course)
            if not extracted_campus and extracted_room:
                extracted_campus = campus_mapping.get(extracted_room)
            
            # Special handling for SZABIST default campus
            if not extracted_campus and extracted_room and extracted_room.isdigit():
                extracted_campus = "SZABIST University Campus"
            
            # Debug output
            if settings.debug_parsing:
                logger.debug(f"Extracted - Course: {extracted_course}")
                logger.debug(f"Extracted - Faculty: {faculty_name}")
                logger.debug(f"Extracted - Title: {course_title}")
                logger.debug(f"Extracted - Time: {extracted_time}")
                logger.debug(f"Extracted - Room: {extracted_room}")
                logger.debug(f"Extracted - Campus: {extracted_campus}")
            
            rec = {
                "sr_no": sr_match.group(1) if sr_match else None,
                "dept": dept_match.group(1) if dept_match else None,
                "program": _extract_program(combined_line),
                "class_section": semester_found or _extract_class_section(combined_line),
                "course": extracted_course,
                "course_title": course_title,
                "faculty": faculty_name,
                "room": extracted_room,
                "time": extracted_time,
                "credits": credit_match.group(1) if credit_match else None,
                "campus": extracted_campus,
                "raw_cells": [combined_line],
                "semester": semester_found or None,
                "source_line": line_num,
                "full_text": combined_line,
            }
            results.append(rec)
        else:
            if settings.debug_parsing:
                logger.debug(f"Line {line_num}: Skipping - no semester match or insufficient schedule data")
        
        i += 1
    
    logger.info(f"Text parsing complete: processed {processed_lines} lines, kept {len(results)} items")
    if semesters:
        logger.info(f"Semester filters applied: {semesters}")
    else:
        logger.info("No semester filters - returned all schedule-like lines")
    
    return results

def _get_text(el) -> str:
    return _ws(el.get_text(" ", strip=True)) if el else ""

def _guess_schedule_table(tables) -> Optional[object]:
    """
    Pick the most 'schedule-like' table:
    - contains many rows
    - has cells mentioning known headers or patterns across any row
    """
    best = None
    best_score = -1
    header_words = {"sr", "dept", "program", "class", "section", "course", "faculty", "room", "time", "campus"}
    for tbl in tables:
        trs = tbl.find_all("tr")
        if not trs:
            continue
        score = len(trs)
        # small bonus if any header-like word appears in th/tds
        head_text = " ".join(_get_text(x).lower() for x in tbl.find_all(["th", "td"])[:40])
        score += sum(1 for w in header_words if w in head_text)
        if score > best_score:
            best_score = score
            best = tbl
    return best

def _header_map(tr) -> Dict[str, int]:
    headers = [_get_text(th).lower() for th in tr.find_all(["th", "td"])]
    mapping = {}
    for i, h in enumerate(headers):
        if "sr" in h:                mapping.setdefault("sr_no", i)
        if "dept" in h:              mapping.setdefault("dept", i)
        if "program" in h:           mapping.setdefault("program", i)
        if "class" in h or "section" in h: mapping.setdefault("class_section", i)
        if "course" in h:            mapping.setdefault("course", i)
        if "faculty" in h or "teacher" in h: mapping.setdefault("faculty", i)
        if "room" in h:              mapping.setdefault("room", i)
        if "time" in h:              mapping.setdefault("time", i)
        if "campus" in h:            mapping.setdefault("campus", i)
    return mapping

def _find_header_row(trs) -> Optional[int]:
    for i, tr in enumerate(trs[:10]):
        ths = tr.find_all("th")
        if ths:
            return i
        # also accept a row whose cells look like header text
        line = " ".join(_get_text(td).lower() for td in tr.find_all("td"))
        if any(k in line for k in ["class", "course", "faculty", "room", "time", "campus"]):
            return i
    return None

def parse_schedule_html(html: str, semesters: List[str]) -> List[Dict]:
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting parse with {len(semesters)} semester filters: {semesters}")
    
    # Check if debug parsing is enabled
    from .config import settings
    if hasattr(settings, 'debug_parsing') and settings.debug_parsing:
        logger.setLevel(10)  # DEBUG level
    
    soup = BeautifulSoup(html or "", "lxml")
    tables = soup.find_all("table")
    
    # If no tables found, try to parse as plain text
    if not tables:
        logger.warning("No tables found in HTML, attempting plain text parsing")
        # Convert HTML to plain text properly
        plain_text = soup.get_text(separator="\n", strip=True)
        return parse_schedule_text(plain_text, semesters)

    table = _guess_schedule_table(tables)
    if not table:
        logger.warning("No schedule-like table found, attempting plain text parsing")
        # Convert HTML to plain text properly
        plain_text = soup.get_text(separator="\n", strip=True)
        return parse_schedule_text(plain_text, semesters)

    trs = table.find_all("tr")
    if not trs:
        logger.warning("No rows found in table, attempting plain text parsing")
        # Convert HTML to plain text properly
        plain_text = soup.get_text(separator="\n", strip=True)
        return parse_schedule_text(plain_text, semesters)

    logger.info(f"Found table with {len(trs)} rows")

    header_idx = _find_header_row(trs)
    if header_idx is None:
        header_idx = 0
    colmap = _header_map(trs[header_idx])

    # If no headers detected, fall back to common indices (seen in your screenshot)
    # Sr, Dept, Program, Class/Section, Course, Faculty, Room, Time, Campus
    fallback = {
        "sr_no": 0, "dept": 1, "program": 2, "class_section": 3,
        "course": 4, "faculty": 5, "room": 6, "time": 7, "campus": 8
    }
    for k, v in fallback.items():
        colmap.setdefault(k, v)

    logger.info(f"Column mapping: {colmap}")

    want = [_tok(s) for s in (semesters or [])]
    logger.info(f"Tokenized semester filters: {want}")
    results: List[Dict] = []

    processed_rows = 0
    for tr in trs[header_idx + 1:]:
        tds = tr.find_all("td")
        if not tds:
            continue
        cells = [_get_text(td) for td in tds]
        if len([c for c in cells if c]) < 3:
            continue  # skip decorative rows
        
        processed_rows += 1
        
        def pick(key: str) -> Optional[str]:
            i = colmap.get(key)
            return cells[i] if i is not None and i < len(cells) else None

        class_section = pick("class_section") or ""
        class_tok = _tok(class_section)
        
        logger.debug(f"Row {processed_rows}: class_section='{class_section}', tokenized='{class_tok}'")
        logger.debug(f"Row {processed_rows}: cells={cells[:9]}")

        keep = False
        match_reason = ""
        
        if want:
            # exact or contains either way to survive spacing/formatting differences
            for w in want:
                if class_tok == w:
                    keep = True
                    match_reason = f"exact match: '{class_tok}' == '{w}'"
                    break
                elif class_tok and w in class_tok:
                    keep = True
                    match_reason = f"contains match: '{w}' in '{class_tok}'"
                    break
                elif class_tok and class_tok in w:
                    keep = True
                    match_reason = f"reverse contains: '{class_tok}' in '{w}'"
                    break
            
            if not keep:
                logger.debug(f"Row {processed_rows}: No semester match - wanted {want}, got '{class_tok}'")
        else:
            # no filter provided -> keep sensible rows
            keep = any(pick(k) for k in ("course", "time", "room", "faculty", "campus"))
            if keep:
                match_reason = "no filter - keeping all valid rows"
            else:
                logger.debug(f"Row {processed_rows}: Skipping - not enough valid data")

        if keep:
            logger.info(f"Row {processed_rows}: KEEPING - {match_reason}")
        
        if not keep:
            continue

        rec = {
            "sr_no": pick("sr_no"),
            "dept": pick("dept"),
            "program": pick("program"),
            "class_section": class_section,
            "course": pick("course"),
            "faculty": pick("faculty"),
            "room": pick("room"),
            "time": pick("time"),
            "campus": pick("campus"),
            "raw_cells": cells,
            "semester": class_section if want else None,
        }
        results.append(rec)

    logger.info(f"Parsing complete: processed {processed_rows} rows, kept {len(results)} items")
    if semesters:
        logger.info(f"Semester filters applied: {semesters}")
    else:
        logger.info("No semester filters - returned all valid rows")
    
    return results

def _extract_program(line: str) -> Optional[str]:
    """Extract program information like BS, MS, PhD"""
    program_match = re.search(r'\b(BS|MS|PhD|MBA|BBA)\s*\([^)]+\)', line)
    return program_match.group(0) if program_match else None

def _extract_class_section(line: str) -> Optional[str]:
    """Extract class section when semester filter doesn't match"""
    # Look for patterns like "5C", "7A", "1B" etc.
    section_match = re.search(r'\b\d+[A-Z]\b', line)
    return section_match.group(0) if section_match else None

def _extract_faculty(line: str) -> Optional[str]:
    """Extract faculty name with multiple strategies"""
    # Strategy 1: Name at the end of line
    words = line.split()
    if len(words) >= 2:
        # Check if last 1-3 words look like a name
        potential_name = ' '.join(words[-3:]).strip()
        if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]*)*(?:\s+[A-Z]\.?)?$', potential_name):
            return potential_name
    
    # Strategy 2: Look for name patterns anywhere in the line
    name_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]*){0,2})\b', line)
    if name_matches:
        # Return the longest reasonable name
        names = [name for name in name_matches if len(name) > 3 and len(name) < 30]
        if names:
            return max(names, key=len)
    
    return None

def _extract_faculty_szabist(line: str, course_match, credit_match) -> Optional[str]:
    """Extract faculty name specifically for SZABIST format"""
    # In SZABIST format, faculty typically comes after course title and credits
    # Examples: 
    # "29 CS BS (SE) BS (SE) - 5C SEC 4714 Business Process Engineering (3,0) Arfa"
    # "Asaf  302 02:00 PM – 03:30 PM SZABIST University Campus..."
    
    if not course_match:
        return None
    
    # Start after the course code
    after_course = line[course_match.end():].strip()
    
    # If there are credits, faculty comes after them
    if credit_match:
        # Faculty should be after credits
        after_credits = line[credit_match.end():].strip()
        
        # Look for faculty name pattern: one or more capitalized words
        # Remove time, room, and campus info
        cleaned = re.sub(r'\d{1,2}:\d{2}\s*(?:AM|PM)', '', after_credits)
        cleaned = re.sub(r'\b(?:NB-\d+|Lab\s*\d+|\d{3}|Hall\s*\d+[A-Z]?|TV\s*Studio|Media\s*Lab)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'SZABIST\s+(?:University\s+Campus|HMB).*', '', cleaned, flags=re.IGNORECASE)
        
        # Extract faculty name from what remains
        faculty_words = []
        words = cleaned.split()
        
        for word in words:
            # Stop at room numbers, times, or other non-name tokens
            if re.match(r'^\d+$|^\d{1,2}:\d{2}|^(?:AM|PM)$|^-$|^–$', word):
                break
            # Keep capitalized words that look like names
            if word and word[0].isupper() and len(word) > 1 and word.isalpha():
                faculty_words.append(word)
            elif word and len(faculty_words) > 0:  # Stop at non-name words after we started collecting
                break
        
        if faculty_words:
            return ' '.join(faculty_words)
    else:
        # No credits found, look for faculty pattern at the end
        # Remove known patterns like time, room, campus first
        cleaned = re.sub(r'\d{1,2}:\d{2}\s*(?:AM|PM)', '', after_course)
        cleaned = re.sub(r'\b(?:NB-\d+|Lab\s*\d+|\d{3}|Hall\s*\d+[A-Z]?|TV\s*Studio|Media\s*Lab)\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'SZABIST\s+(?:University\s+Campus|HMB).*', '', cleaned, flags=re.IGNORECASE)
        
        # Look for names at the end
        words = cleaned.split()
        if len(words) >= 1:
            # Take last 2-3 capitalized words as faculty name
            potential_names = []
            
            for i in range(max(0, len(words) - 3), len(words)):
                if i < len(words) and words[i] and words[i][0].isupper() and words[i].isalpha():
                    potential_names.append(words[i])
            
            if potential_names:
                return ' '.join(potential_names)
    
    return None

def _extract_course_title_szabist(line: str, course_match, faculty_name: str) -> Optional[str]:
    """Extract course title specifically for SZABIST format"""
    if not course_match:
        return None
    
    # Start after the course code
    after_course = line[course_match.end():].strip()
    
    # Course title is between course code and credits/(faculty)
    title_part = after_course
    
    # Remove credits pattern if present
    credits_match = re.search(r'\s*\([0-9,\.\s]+\)', title_part)
    if credits_match:
        title_part = title_part[:credits_match.start()]
    
    # Remove time patterns
    title_part = re.sub(r'\d{1,2}:\d{2}\s*(?:AM|PM)', '', title_part)
    
    # Remove room patterns
    title_part = re.sub(r'\b(?:NB-\d+|Lab\s*\d+|\d{3}|Hall\s*\d+[A-Z]?|TV\s*Studio|Media\s*Lab)\b', '', title_part, flags=re.IGNORECASE)
    
    # Remove campus patterns
    title_part = re.sub(r'SZABIST\s+(?:University\s+Campus|HMB).*', '', title_part, flags=re.IGNORECASE)
    
    # Remove faculty name if we found it (from the end)
    if faculty_name:
        # Try to remove faculty from the end
        faculty_words = faculty_name.split()
        for word in reversed(faculty_words):
            if title_part.endswith(word):
                title_part = title_part[:-len(word)].rstrip()
    
    # Clean up the title
    title_part = title_part.strip()
    
    # Remove trailing non-alphabetic characters
    title_part = re.sub(r'[^\w\s]+$', '', title_part).strip()
    
    # The title should be what remains - typically course title words
    if title_part and len(title_part) > 3:
        # Clean up extra spaces and ensure proper capitalization
        title_part = re.sub(r'\s+', ' ', title_part)
        
        # Additional cleanup for common SZABIST patterns
        # Remove things like "and Development" if it appears to be split
        words = title_part.split()
        clean_words = []
        
        for word in words:
            # Skip if it looks like a continuation artifact
            if word.lower() in ['and', 'development', 'engineering', 'of', 'the'] and len(clean_words) == 0:
                continue
            clean_words.append(word)
        
        if clean_words:
            return ' '.join(clean_words)
    
    return None
    
    return None

def _extract_campus_szabist(line: str) -> Optional[str]:
    """Extract campus information specifically for SZABIST format"""
    # Look for SZABIST University Campus pattern
    campus_match = re.search(r'(SZABIST\s+University\s+Campus[^\n]*)', line, re.IGNORECASE)
    if campus_match:
        campus_info = campus_match.group(1).strip()
        # Clean up extra text
        campus_info = re.sub(r'\s+', ' ', campus_info)
        return campus_info
    
    # Look for campus codes like "H-8/4 ISB"
    campus_code = re.search(r'\b(H-\d+/\d+\s+ISB|H-\d+\s+ISB)\b', line)
    if campus_code:
        return f"SZABIST University Campus {campus_code.group(1)}"
    
    return None

def _extract_campus(line: str) -> Optional[str]:
    """Extract campus information"""
    # First try SZABIST specific extraction
    szabist_campus = _extract_campus_szabist(line)
    if szabist_campus:
        return szabist_campus
    
    # Fallback to general patterns
    campus_patterns = [
        r'\b(Main Campus|New Building|NB|Old Building|OB)\b',
        r'\b(Islamabad|Karachi|Lahore)\b',
        r'\bCampus\s*[:-]?\s*([A-Z][a-z]+)\b'
    ]
    
    for pattern in campus_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return match.group(1) if match.lastindex else match.group(0)
    
    return None
