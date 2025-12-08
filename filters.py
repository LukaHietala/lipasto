from datetime import datetime


# Filter to format datetime objects or timestamps as strings (2025-12-08 12:18:21 )
def datetime_filter(value, format="%Y-%m-%d %H:%M:%S"):
    if isinstance(value, datetime):
        return value.strftime(format)
    if isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value)
        return dt.strftime(format)
    return value


# Filter to display age in human-readable format (like "2 days ago", "3 hours ago")
def age_filter(value):
    if isinstance(value, (int, float)):
        dt = datetime.fromtimestamp(value)
    elif isinstance(value, datetime):
        dt = value
    else:
        return value
    now = datetime.now()
    diff = now - dt
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    if diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    if diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    if diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    return "just now"


# Filter to display file sizes in human-readable format (bytes to KB, MB, GB)
def size_filter(value):
    if value is None:
        return ""
    if value < 1024:
        return f"{value} B"
    if value < 1024 * 1024:
        return f"{value / 1024:.1f} KB"
    if value < 1024 * 1024 * 1024:
        return f"{value / (1024 * 1024):.1f} MB"
    return f"{value / (1024 * 1024 * 1024):.1f} GB"


# Register filters with Flask app
def register_filters(app):
    app.jinja_env.filters["datetime"] = datetime_filter
    app.jinja_env.filters["age"] = age_filter
    app.jinja_env.filters["size"] = size_filter
