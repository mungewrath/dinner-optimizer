import datetime


def most_recent_saturday():
    return nth_most_recent_saturday(1)


def nth_most_recent_saturday(n: int):
    if n < 1:
        raise Exception("n must be >= 1")

    # Get the current date
    today = datetime.date.today()

    # Calculate the number of days to subtract to reach the most recent Saturday
    days_until_saturday = (today.weekday() - 5) % 7  # Saturday is weekday 5

    # Subtract the days to get the most recent Saturday
    recent_saturday = today - datetime.timedelta(
        days=(days_until_saturday) + 7 * (n - 1)
    )

    # Format the date as "MM-DD-YYYY"
    formatted_date = recent_saturday.strftime("%m-%d-%Y")

    return formatted_date


def current_time():
    # Get the current time
    current_time = datetime.datetime.now().time()

    # Format the time as "HH:MM:SS"
    formatted_time = current_time.strftime("%H:%M:%S")

    return formatted_time
