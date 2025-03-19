from datetime import datetime
import re
from typing import List, Optional


def extract_dates(date_text: Optional[str]) -> List[str]:
    """ Extract dates from text in format dd.mm.yyyy .

    Args:
        Text containing dates

    Returns:
        List containing [from_date, to_date]
    
    """
    if not date_text:
        return ["", ""]
    
    # Get dates from the text
    dates = re.findall(r'\d{2}\.\d{2}\.\d{4}', date_text)
    
    # In some cases there is written only single date
    # "von Montag 23.03.2025"
    # Here we check for "von" (translated "from") and if found, assign as starting date
    if len(dates) == 1:
        return [dates[0], ""] if "von" in date_text else ["", dates[0]]
    elif len(dates) == 2:
        return dates

    return ["", ""]

def reformat_dates(dates: List[str], input_format: str, output_format: str) -> List[str]:
    """ Reformats dates to desired format.

    Args:
        dates: List of dates in dd.mm.yyyy format of str type
        input_format: Format of date which is being formatted
        output_format: Format that we are formatting to
    
    Returns:
        Reformated list of dates of str type
    """
    reformatted_dates = []

    for date in dates:
        # If empty date, keep empty
        if date == "":
            reformatted_dates.append("")

        else:
            # Turn str into datetime obj
            date_obj = datetime.strptime(date, input_format)

            # Turn datetime obj into reformatted str
            reformatted_date = date_obj.strftime(output_format)

            reformatted_dates.append(reformatted_date)            
    
    return reformatted_dates

def is_valid_now(from_date: Optional[str], to_date: Optional[str], date_format: str) -> bool:
    """ Checks if current date falls between start and end date.

    Args:
        from_date: Starting date as dd.mm.yyyy
        to_date: Ending date as dd.mm.yyyy
        date_format: Format of date for turning str to datetime obj

    Returns:
        Boolean indicating if within the range
    
    """
    date_format = date_format
    date_now = datetime.now()
    
    # Put 0 hours, minutes, seconds
    # otherwise same-day comparisons won't work, 
    # Date from website is always 00:00:00 clock time
    date_now = date_now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Transform date strings into datetime for comparison
    try:
        date_start = datetime.strptime(from_date, date_format) if from_date else None
        date_end = datetime.strptime(to_date, date_format) if to_date else None
    except ValueError:
        return False
    
    # If both dates
    if date_start and date_end:
        return date_start <= date_now <= date_end
    
    # If only start date
    if date_start and not date_end:
        return date_start <= date_now
    
    # If only end date
    if not date_start and date_end:
        return date_now <= date_end

    # If no dates
    return False
