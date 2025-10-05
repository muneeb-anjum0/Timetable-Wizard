"""
Beautiful table formatting for schedule data using Rich library.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.columns import Columns
from rich.align import Align
from datetime import datetime


def format_schedule_json(json_file_path: str | Path) -> None:
    """
    Read a JSON schedule file and display it in a beautiful table format with comprehensive error handling.
    
    Args:
        json_file_path: Path to the JSON file containing schedule data
    """
    try:
        # Validate file path
        file_path = Path(json_file_path)
        if not file_path.exists():
            console = Console()
            console.print(f"[red]❌ Error: File '{json_file_path}' not found.[/red]")
            return
            
        if file_path.stat().st_size == 0:
            console = Console()
            console.print(f"[red]❌ Error: File '{json_file_path}' is empty.[/red]")
            return
            
        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
            console = Console()
            console.print(f"[yellow]⚠️  Warning: File '{json_file_path}' is very large ({file_path.stat().st_size / 1024 / 1024:.1f}MB).[/yellow]")
        
        # Load JSON data with enhanced error handling
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['utf-8-sig', 'latin1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        data = json.load(f)
                    break
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            else:
                raise ValueError("Could not decode file with any supported encoding")
        
        # Validate JSON structure
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object/dictionary")
            
        # Create Rich console with error handling
        try:
            console = Console()
        except Exception as e:
            print(f"❌ Error: Could not create console: {e}")
            return
        
        # Validate required data
        items = data.get('items', [])
        if not isinstance(items, list):
            console.print("[yellow]⚠️  Warning: 'items' field is not a list or is missing.[/yellow]")
            items = []
        
        # Display with enhanced error recovery
        try:
            _display_header(console, data)
        except Exception as e:
            console.print(f"[red]❌ Error displaying header: {e}[/red]")
            
        try:
            _display_schedule_table(console, items)
        except Exception as e:
            console.print(f"[red]❌ Error displaying table: {e}[/red]")
            # Fallback to simple display
            console.print(f"\n[dim]Raw data: {len(items)} items found[/dim]")
            for i, item in enumerate(items[:5]):  # Show first 5 items
                course = item.get('course', 'N/A')
                title = item.get('course_title', 'N/A')
                console.print(f"  {i+1}. {course}: {title}")
            if len(items) > 5:
                console.print(f"  ... and {len(items) - 5} more items")
            
        try:
            _display_summary(console, data)
        except Exception as e:
            console.print(f"[red]❌ Error displaying summary: {e}[/red]")
            
        # Display data quality metrics if available
        if 'data_quality' in data:
            try:
                _display_data_quality(console, data['data_quality'])
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not display data quality metrics: {e}[/yellow]")
                
    except FileNotFoundError:
        print(f"❌ Error: File '{json_file_path}' not found.")
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{json_file_path}': {e}")
    except PermissionError:
        print(f"❌ Error: Permission denied accessing '{json_file_path}'.")
    except Exception as e:
        print(f"❌ Error: {e}")


def _display_header(console: Console, data: Dict[str, Any]) -> None:
    """Display header information with schedule details."""
    
    # Extract basic info
    for_day = data.get('for_day', 'Unknown')
    for_date = data.get('for_date', 'Unknown')
    message_id = data.get('message_id', 'Unknown')
    filtered_semesters = data.get('filtered_semesters', [])
    
    # Create title panel
    title = Panel(
        Align.center("[bold blue]📅 Class Schedule[/bold blue]"),
        style="bold",
        border_style="blue"
    )
    console.print(title)
    
    # Format date
    if for_date != 'Unknown':
        try:
            date_obj = datetime.strptime(for_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')
        except:
            formatted_date = for_date
    else:
        formatted_date = for_date
    
    info_text = f"[bold]{for_day}[/bold] - {formatted_date}"
    
    # Create info panels
    panels = []
    
    # Day and Date panel
    panels.append(Panel(
        Align.center(info_text),
        title="📆 Schedule Date",
        border_style="blue",
        width=35
    ))
    
    # Message ID panel
    panels.append(Panel(
        Align.center(str(message_id)[:16] if message_id != 'Unknown' else message_id),
        title="📧 Message ID",
        border_style="green",
        width=25
    ))
    
    # Filtered Semesters panel
    # Get semesters from the actual data items if not in metadata
    if not filtered_semesters:
        # Extract unique semesters from the actual schedule items
        items = data.get('items', [])
        semester_set = set()
        for item in items:
            semester = item.get('semester') or item.get('class_section')
            if semester:
                semester_set.add(semester)
        filtered_semesters = sorted(list(semester_set))
    
    if filtered_semesters:
        semester_text = "\n".join([f"• {semester}" for semester in filtered_semesters])
    else:
        semester_text = "None specified"
    
    panels.append(Panel(
        semester_text,
        title="🎓 Filtered Semesters",
        border_style="magenta",
        width=35
    ))
    
    # Display panels side by side
    if panels:
        console.print(Columns(panels, equal=False, expand=False))
    
    console.print()


def _display_schedule_table(console: Console, items: List[Dict[str, Any]]) -> None:
    """Display schedule items in a beautiful table."""
    
    # Create the main table
    table = Table(
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        row_styles=["none", "dim"],
        expand=True
    )
    
    # Add columns with specific widths and styles
    table.add_column("Sr", style="dim", width=9, justify="center")
    table.add_column("Course", style="bold cyan", width=17)
    table.add_column("Course Title", style="green", min_width=20, max_width=42)
    table.add_column("Faculty", style="yellow", width=24)
    table.add_column("Time", style="bright_blue", width=27)
    table.add_column("Room", style="bright_cyan", width=14, justify="center")
    table.add_column("Campus", style="bright_green", width=37)
    
    if not items:
        console.print("[red]No schedule items found.[/red]")
        return
    
    # Group by semester
    semester_groups = {}
    for item in items:
        semester = item.get('semester', 'Unknown')
        if semester not in semester_groups:
            semester_groups[semester] = []
        semester_groups[semester].append(item)
    
    # Display each semester group
    for semester, semester_items in semester_groups.items():
        # Add semester header row
        if len(semester_groups) > 1:
            table.add_row(
                "",
                "",
                "",
                f"[bold white on blue] {semester} [/bold white on blue]",
                "",
                "",
                "",
                style="bold"
            )
        
        # Sort items by time for better readability
        semester_items.sort(key=lambda x: x.get('time', '') or '')
        
        for item in semester_items:
            # Format each field with fallbacks
            sr_no = str(item.get('sr_no', '') or '')
            course = str(item.get('course', 'N/A') or 'N/A')
            title = str(item.get('course_title', 'N/A') or 'N/A')
            faculty = str(item.get('faculty', 'N/A') or 'N/A')
            time = str(item.get('time', 'N/A') or 'N/A')
            room = str(item.get('room', 'N/A') or 'N/A')
            campus = str(item.get('campus', 'N/A') or 'N/A')
            
            # Truncate long course titles for better display
            if len(title) > 30:
                title = title[:27] + "..."
            
            # Add row to table
            table.add_row(
                sr_no,
                course,
                title,
                faculty,
                time,
                room,
                campus
            )
    
    console.print(table)


def _display_summary(console: Console, data: Dict[str, Any]) -> None:
    """Display summary information."""
    
    summary = data.get('summary', {})
    
    if summary:
        # Get total classes
        total_classes = summary.get('total_items', 0)
        
        # Create summary panel
        summary_panel = Panel(
            Align.center(f"[bold bright_blue]{total_classes}[/bold bright_blue]"),
            title="📊 Total Classes",
            border_style="bright_blue",
            width=20
        )
        
        console.print(summary_panel)
    
    # Display generation timestamp
    generated_at = data.get('generated_at', '')
    if generated_at:
        try:
            # Try to parse and format the timestamp
            dt = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_time = generated_at
        
        console.print(f"\n[dim]Generated at: {formatted_time}[/dim]", justify="right")


def _display_data_quality(console: Console, quality_data: Dict[str, Any]) -> None:
    """
    Display data quality metrics in a visually appealing format.
    """
    if not quality_data:
        return
        
    # Create quality panel
    completeness = quality_data.get('completeness_score', 0)
    color = "green" if completeness > 0.8 else "yellow" if completeness > 0.5 else "red"
    
    quality_text = f"[{color}]{completeness:.1%}[/{color}] complete"
    
    # Add detailed metrics if available
    metrics = []
    if 'items_with_time' in quality_data and 'items_with_campus' in quality_data:
        total = quality_data.get('items_with_time', 0) + quality_data.get('items_missing_time', 0)
        if total > 0:
            time_pct = quality_data['items_with_time'] / total
            campus_pct = quality_data['items_with_campus'] / total
            metrics.append(f"Time: {time_pct:.0%}")
            metrics.append(f"Campus: {campus_pct:.0%}")
    
    if metrics:
        quality_text += f"\n{' | '.join(metrics)}"
    
    quality_panel = Panel(
        Align.center(quality_text),
        title="📊 Data Quality",
        border_style=color,
        width=20
    )
    
    console.print(quality_panel)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        format_schedule_json(sys.argv[1])
    else:
        print("Usage: python table_formatter.py <json_file_path>")