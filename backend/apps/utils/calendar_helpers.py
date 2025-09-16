import calendar

def generate_month(year, month):
    WEEK_MAX_LENGTH = 7

    days_with_weekdays = {}

    num_days = calendar.monthrange(year, month)[1]

    for day in range(1, num_days + 1):
        weekday = calendar.weekday(year, month, day)
        weekday_name = calendar.day_name[weekday]
        
        days_with_weekdays[day] = weekday_name
    
    month = []    
    new_week = {}

    for day, weekday in days_with_weekdays.items():
        new_week[weekday] = day

        if (len(new_week) == WEEK_MAX_LENGTH) or (day == len(days_with_weekdays)):
            month.append(new_week)
            new_week = {}

    return month

def get_month_days(year, month):
    return calendar.monthrange(year, month)[1]