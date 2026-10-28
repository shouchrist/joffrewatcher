from playwright.sync_api import sync_playwright
from datetime import datetime, date, time as clock_time, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import csv
import time
import winsound

# settings
VISIT_DATES = ["2027-08-23", "2027-08-24", "2027-08-25"]
TARGET_PASSES = 3
CHECK_EVERY = 60
URL = "https://reserve.bcparks.ca/dayuse/registration"

pacific = ZoneInfo("America/Vancouver")
folder = Path("joffre_results")
folder.mkdir(exist_ok=True)
log_file = folder / "checks.csv"


# current time in vancouver
def now_pacific():
    return datetime.now(pacific)


# record the results
def log_result(visit_date, status):
    new_file = not log_file.exists()

    with log_file.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if new_file:
            writer.writerow(["Time (Pacific)", "Visit date", "Status"])
        writer.writerow([now_pacific().isoformat(timespec="seconds"), visit_date, status])


# sound an alarm
def alarm():
    for i in range(6):
        winsound.Beep(1400, 350)
        time.sleep(0.12)


# show a windows notification
def notify(message):
    try:
        from plyer import notification
        notification.notify(title="Joffre Lakes Pass Watcher", message=message, timeout=10)
    except Exception as e:
        print(f"Notification unavailable: {e}")


# check which dates can be booked
# passes open two days before a visit at 7am pacific
def booking_dates():
    now = now_pacific()
    ready = []
    next_release = None

    for text in VISIT_DATES:
        visit = date.fromisoformat(text)
        opening_day = visit - timedelta(days=2)
        release = datetime.combine(opening_day, clock_time(7), tzinfo=pacific)

        if visit < now.date():
            continue
        if release <= now:
            ready.append(text)
        elif next_release is None or release < next_release:
            next_release = release

    return ready, next_release


# wait for the next release
def countdown(target):
    print(f"Next release: {target:%Y-%m-%d %I:%M %p} Pacific")

    while now_pacific() < target:
        seconds = max(0, int((target - now_pacific()).total_seconds()))
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"\rTime remaining: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
        time.sleep(1)

    print("\nChecking passes now!")


# select the number of passes
def select_quantity(page):
    page.wait_for_timeout(800)

    for select in page.locator("select").all():
        if select.get_attribute("id") == "passType":
            continue
