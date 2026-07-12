"""
Computes an intern's card validity period from their start date + duration.

Assumption: "duration_weeks" is calendar weeks (e.g. 8 weeks = start_date + 56
days), since internships naturally only involve weekday attendance -- weekends
aren't "used up" time, they just aren't worked. If you actually want the
validity period stretched so that duration_weeks worth of WEEKDAYS are
included (i.e. skip weekends when counting), use
`calculate_valid_until_business_days` instead and swap the call in
routers/interns.py.
"""

from datetime import date, timedelta


def calculate_valid_until(start_date: date, duration_weeks: int) -> date:
    """Simple calendar-week calculation: 8 weeks = start_date + 56 days."""
    return start_date + timedelta(weeks=duration_weeks)


def calculate_valid_until_business_days(start_date: date, duration_weeks: int) -> date:
    """
    Alternative: counts only Mon-Fri as 'internship days' and stretches the
    calendar end date so exactly duration_weeks * 5 weekdays are covered,
    skipping Sat/Sun. Use this if the internship period should extend past
    weekends rather than absorb them.
    """
    total_weekdays_needed = duration_weeks * 5
    current = start_date
    weekdays_counted = 0
    while weekdays_counted < total_weekdays_needed:
        current += timedelta(days=1)
        if current.weekday() < 5:  # Mon-Fri
            weekdays_counted += 1
    return current