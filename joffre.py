
from playwright.sync_api import sync_playwright
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import winsound

# settings
VISIT_DATE = "2026-08-23"
TARGET_PASSES = 3
CHECK_EVERY = 5
URL = "https://reserve.bcparks.ca/dayuse/registration"

pacific = ZoneInfo("America/Vancouver")


# play alarm when passes are available
def alarm():
    for i in range(8):
        winsound.Beep(1400, 350)
        time.sleep(0.12)


# wait until 7am pacific
def wait_until_7am():
    print("Waiting until 7:00 AM Pacific...")

    while True:
        now = datetime.now(pacific)
        target = now.replace(hour=6, minute=59, second=54, microsecond=0)

        if now >= target:
            print("STARTING")
            break

        time.sleep(0.1 if (target - now).total_seconds() < 5 else 1)


# select number of passes
def select_quantity(page):
    page.wait_for_timeout(1200)

    # check dropdowns first
    selects = page.locator("select")

    for i in range(selects.count()):
        select = selects.nth(i)

        if select.get_attribute("id") == "passType":
            continue

        options = select.locator("option")

        for j in range(options.count()):
            option = options.nth(j)
            label = option.inner_text().strip()
            value = option.get_attribute("value")

            if label == str(TARGET_PASSES):
                select.select_option(label=label)
                return True

            if value == str(TARGET_PASSES):
                select.select_option(value=value)
                return True

            if str(TARGET_PASSES) in label and "pass" in label.lower():
                select.select_option(index=j)
                return True

    # check number inputs if no dropdown works
    boxes = page.locator('input[type="number"]')

    for i in range(boxes.count()):
        box = boxes.nth(i)

        if box.is_visible() and box.is_enabled():
            box.fill(str(TARGET_PASSES))
            box.press("Tab")
            return True

    return False


# start the watcher
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("JOFFRE LAKES PASS WATCHER")
    print(f"Visit date: {VISIT_DATE}")
    print(f"Passes: {TARGET_PASSES}")

    try:
        wait_until_7am()
        page.goto(URL, wait_until="domcontentloaded")

        # keep checking for passes
        while True:
            try:
                page.reload(wait_until="domcontentloaded")

                # enter visit date
                date_box = page.locator("#visitDate")
                date_box.fill(VISIT_DATE)
                date_box.press("Tab")

                page.wait_for_timeout(1000)

                # select joffre lakes
                page.locator("#passType").select_option(
                    label="Joffre Lakes - Trail"
                )

                page.wait_for_timeout(2000)

                # check availability
                availability = page.locator(
                    '[data-testid="day-availability-text"]'
                ).inner_text().strip()

                day_pass = page.locator("#visitTimeDAY")
                now = datetime.now(pacific).strftime("%H:%M:%S")

                if day_pass.is_disabled():
                    print(f"[{now}] {availability}")
                    time.sleep(CHECK_EVERY)
                    continue

                # passes are available
                print(f"[{now}] PASS AVAILABLE!")
                alarm()

                # select all day
                day_pass.check()
                page.wait_for_timeout(1200)

                # select number of passes
                if not select_quantity(page):
                    print("Could not select quantity. Check browser.")
                    alarm()
                    break

                print(f"Selected {TARGET_PASSES} passes")

                # go to next page
                next_button = page.get_by_role(
                    "button", name="Next", exact=True
                )

                if next_button.is_enabled():
                    next_button.click()
                    page.wait_for_timeout(2500)
                    print("Reached next booking step!")
                else:
                    print("Next button disabled. Check browser.")

                alarm()
                break

            except Exception as e:
                print(f"Check failed: {e}")
                time.sleep(CHECK_EVERY)

    except KeyboardInterrupt:
        print("Watcher stopped.")

    # leave browser open for manual booking
    input("Check browser and finish booking. Press ENTER when done.")
    browser.close()
