from random import randint
from datetime import datetime
from zoneinfo import ZoneInfo
import webbrowser

def open_url_in_browser(url: str) -> str:
    """Open a URL directly in the default web browser (like Chrome, Google, etc.) 
    instead of extracting its content.
    
    Args:
        url: The web URL to open.
        
    Returns:
        A success or error message.
    """
    try:
        # Ensure URL has a scheme
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
            
        # Opens the URL in the default system browser
        success = webbrowser.open(url)
        
        if success:
            return f"Successfully opened {url} in your web browser."
        else:
            return f"Failed to launch browser for URL: {url}"
            
    except Exception as e:
        return f"Error opening URL in browser: {str(e)}"
    

def get_random_number(
    min_val: int = 0,
    max_val: int = 10
) -> int:
    """Returns a random integer between min_val and max_val (inclusive).
    
    Args:
        min_val: Starting number
        max_val: Last number
    
    Returns:
        Random number between min_val and max_val.
    """
    return randint(min_val, max_val)

def get_current_datetime():
    """Get current date, time and timezone in India.
    
    Returns:
        A dict of time and date.
    """
    
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    return {
        "date": now.strftime("%d %B %Y"),
        "day": now.strftime("%A"),
        "time": now.strftime("%I:%M:%S %p"),
        "timezone": "Asia/Kolkata",
        "iso_format": now.isoformat()
    }


def get_current_date():
    """Get today's date.
    
    Returns:
        Date as a string.
    """
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return now.strftime("%d %B %Y")


def get_current_time():
    """Get current time.
    
    Returns:
        Time as a string.
    """
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return now.strftime("%I:%M:%S %p")
