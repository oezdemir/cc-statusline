#!/usr/bin/env python3
"""Test parsing against saved sample outputs."""
import os
import re
import sys
from datetime import datetime, timedelta

def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    text = re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', text)
    text = re.sub(r'[^\S\n]+', ' ', text)
    return text

def calc_hours_until_time(reset_line: str, assume_am_for_small_hours: bool = False) -> str:
    """Calculate hours until reset time."""
    match = re.search(r'Rese[ts]*\s*(\d{1,2})(?::(\d{2}))?([ap])?m', reset_line, re.IGNORECASE)
    if not match:
        return "?"
    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    if match.group(3):
        ampm = match.group(3).lower()
    elif assume_am_for_small_hours and hour <= 6:
        ampm = 'a'
    else:
        ampm = 'p'
    if ampm == "p" and hour != 12:
        hour += 12
    elif ampm == "a" and hour == 12:
        hour = 0
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    hours_until = int((target - now).total_seconds() / 3600)
    return f"{hours_until}h"

def calc_days_until_date(reset_line: str) -> str:
    """Calculate days until reset date."""
    match = re.search(r'Resets\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})', reset_line, re.IGNORECASE)
    if not match:
        return "?"
    month_str = match.group(1)
    day = int(match.group(2))
    months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
              "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    month = months.get(month_str.lower(), 1)
    now = datetime.now()
    year = now.year
    try:
        target = datetime(year, month, day)
        if target.date() < now.date():
            target = datetime(year + 1, month, day)
        days_until = (target.date() - now.date()).days
        if days_until == 0:
            return "<1d"
        return f"{days_until}d"
    except ValueError:
        return "?"

def parse_usage(usage_data: str) -> dict:
    """Parse usage data and return structured info."""
    clean = strip_ansi(usage_data)
    result = {
        "session_percent": None,
        "session_reset": "?",
        "week_percent": None,
        "week_reset": "?",
    }

    session_section_match = re.search(r'Current session(.*?)Current week', clean, re.DOTALL | re.IGNORECASE)
    if session_section_match:
        session_section = session_section_match.group(1)
        pct_match = re.search(r'(\d+)%\s*used', session_section)
        if pct_match:
            result["session_percent"] = int(pct_match.group(1))
        reset_match = re.search(r'Rese[ts]*\s*(\d{1,2})(?::\d{2})?[ap]?m', session_section, re.IGNORECASE)
        if reset_match:
            result["session_reset"] = calc_hours_until_time(reset_match.group(0), assume_am_for_small_hours=True)

    week_section_match = re.search(r'Current week \(all models\)(.*?)(?:Current week \(Sonnet|escape|$)', clean, re.DOTALL | re.IGNORECASE)
    if week_section_match:
        week_section = week_section_match.group(1)
        pct_match = re.search(r'(\d+)%\s*used', week_section)
        if pct_match:
            result["week_percent"] = int(pct_match.group(1))
        date_match = re.search(r'Resets\s+((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2})', week_section, re.IGNORECASE)
        if date_match:
            result["week_reset"] = calc_days_until_date(date_match.group(0))
        else:
            time_match = re.search(r'Rese[ts]*\s*(\d{1,2})(?::\d{2})?[ap]?m', week_section, re.IGNORECASE)
            if time_match:
                result["week_reset"] = calc_hours_until_time(time_match.group(0))

    return result

def test_sample(filename):
    """Test parsing a sample file."""
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.exists(filepath):
        print(f"SKIP: {filename} not found")
        return None

    with open(filepath) as f:
        usage_data = f.read()

    result = parse_usage(usage_data)

    print(f"\n{filename}:")
    print(f"  Session: {result['session_percent']}% (reset: {result['session_reset']})")
    print(f"  Week: {result['week_percent']}% (reset: {result['week_reset']})")

    errors = []
    if result['session_percent'] is None:
        errors.append("session_percent is None")
    if result['session_reset'] == '?':
        errors.append("session_reset is '?'")
    if result['week_percent'] is None:
        errors.append("week_percent is None")
    if result['week_reset'] == '?':
        errors.append("week_reset is '?'")

    if errors:
        print(f"  FAIL: {', '.join(errors)}")
        return False
    print("  PASS")
    return True

if __name__ == "__main__":
    test_dir = os.path.dirname(os.path.abspath(__file__))
    samples = [f for f in os.listdir(test_dir)
               if f.startswith("sample_output") and f.endswith(".txt")]

    if not samples:
        print("No sample files found")
        sys.exit(1)

    passed = failed = 0
    for sample in sorted(samples):
        result = test_sample(sample)
        if result is True:
            passed += 1
        elif result is False:
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
