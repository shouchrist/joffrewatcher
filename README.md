# Joffre Lakes Pass Watcher

A Python script that watches the BC Parks day-use site for Joffre Lakes passes. working & updated 2026-09

## How it works

- BC Parks releases day-use passes **2 days before the visit date, at 7:00 am Pacific**.
- Before release, the script shows a live countdown to the next release time.
- Once passes are out, it checks the BC Parks site every 60 seconds.
- When passes are available, it plays an alarm and shows a Windows notification.
- It leaves the browser open so I can finish the booking myself. **It does not book automatically.**
- Every check is saved to `joffre_results/checks.csv`, with the time (Pacific), visit date and status.

## Requirements

- Windows (the alarm uses `winsound`,  only works on Windows)
- Python 3.11 or newer
- [Playwright](https://playwright.dev/python/), to control the browser
- [Plyer](https://pypi.org/project/plyer/), for notifications (optional: the script still runs without it)
- [tzdata](https://pypi.org/project/tzdata/), for Pacific time on Windows

## Setup

```
pip install -r requirements.txt
playwright install chromium
```

The second line downloads the browser that Playwright controls

## How to run

```
python joffre.py
```

Press **Ctrl + C** to stop it.

## Settings

you can change these on top of `joffre.py`:

| Setting | What it does | Default |
| --- | --- | --- |
| `VISIT_DATES` | The dates you want to visit, as `YYYY-MM-DD` | three dates in August 2027 |
| `TARGET_PASSES` | How many passes to look for | `3` |
| `CHECK_EVERY` | Seconds between checks | `60` |

## Notes
- Dates that have already passed are skipped automatically
- [check out joffre lakes](https://www.instagram.com/reels/DcEZKAYhRO5/)

