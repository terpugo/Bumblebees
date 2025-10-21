#!/usr/bin/env python3
"""
daily_reports.py

Parse attacker report .txt files in a directory and write attacker_reports_YYYYMMDD.xlsx
for a specific date. By default the script processes **yesterday** (useful for daily cron).

Usage:
  python3 daily_reports.py /path/to/Attacker_Data
  python3 daily_reports.py /path/to/Attacker_Data --date 2025-10-19
"""

import sys
import re
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import argparse
import time

def extract_first(prefix, text, flags=re.MULTILINE):
    pattern = rf"^{re.escape(prefix)}\s*[:=]?\s*(.*)$"
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""

def extract_commands_block(text):
    m = re.search(r"(?mi)^list of attacker commands:\s*\n(.*?)(?:\n\s*\n|$)", text, re.S)
    return m.group(1).rstrip() if m else ""

def extract_minutes_seconds(text):
    m = re.search(r"([0-9]+)\s+minutes?\s+and\s+([0-9]+)\s+seconds", text)
    if not m:
        return 0, 0
    return int(m.group(1)), int(m.group(2))

def parse_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    config_num = extract_first("config num", text)
    attacker_ip = extract_first("attacker ip", text)
    login_time = extract_first("attacker logged in at", text)
    exit_time = extract_first("attacker left at", text)
    container_id = extract_first("container ID", text) or extract_first("Container ID", text)
    attacker_username = extract_first("Attacker username", text) or extract_first("Attacker Username", text)
    num_commands = extract_first("number of attacker commands", text)
    commands = extract_commands_block(text)
    minutes, seconds = extract_minutes_seconds(text)
    total_seconds = minutes * 60 + seconds

    # try to extract epoch from filename if present (digits)
    epoch = ""
    m = re.search(r"(\d{9,})", path.name)
    if m:
        epoch = m.group(1)
    else:
        epoch = str(int(path.stat().st_mtime))

    return {
        "filename": path.name,
        "epoch": epoch,
        "config_num": config_num,
        "attacker_ip": attacker_ip,
        "login_time": login_time,
        "exit_time": exit_time,
        "container_id": container_id,
        "attacker_username": attacker_username,
        "num_commands": num_commands,
        "commands": commands,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": total_seconds
    }

def day_range_for_date(target_date: datetime):
    start = datetime(target_date.year, target_date.month, target_date.day)
    end = start + timedelta(days=1)
    start_ts = int(time.mktime(start.timetuple()))
    end_ts = int(time.mktime(end.timetuple()))
    return start_ts, end_ts

def main():
    parser = argparse.ArgumentParser(description="Create an Excel report from daily attacker .txt files.")
    parser.add_argument("dir", help="Directory containing report .txt files (e.g. /home/student/Bumblebees/Attacker_Data)")
    parser.add_argument("--date", help="Target date YYYY-MM-DD (local). Defaults to yesterday if omitted.", default=None)
    args = parser.parse_args()

    outdir = Path(args.dir)
    if not outdir.exists() or not outdir.is_dir():
        print(f"Directory not found: {outdir}", file=sys.stderr)
        sys.exit(1)

    # Determine target date: default = yesterday
    if args.date:
        try:
            target = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
    else:
        today = datetime.now()
        y = today.date() - timedelta(days=1)
        target = datetime(y.year, y.month, y.day)

    start_ts, end_ts = day_range_for_date(target)

    rows = []
    for p in sorted(outdir.glob("*.txt")):
        try:
            mtime = int(p.stat().st_mtime)
        except Exception as e:
            print(f"Skipping {p.name}: cannot stat file ({e})", file=sys.stderr)
            continue

        # only include files modified within the target day (local time)
        if not (start_ts <= mtime < end_ts):
            continue

        try:
            row = parse_file(p)
            rows.append(row)
        except Exception as e:
            print(f"Warning: failed to parse {p.name}: {e}", file=sys.stderr)

    if not rows:
        print("No report files for the target date were found; no spreadsheet created.", file=sys.stderr)
        sys.exit(0)

    df = pd.DataFrame(rows, columns=[
        "filename","epoch","config_num","attacker_ip","login_time","exit_time",
        "container_id","attacker_username","num_commands","commands","minutes","seconds","total_seconds"
    ])

    xlsx_path = outdir / f"attacker_reports_{target.strftime('%Y%m%d')}.xlsx"
    df.to_excel(xlsx_path, index=False)
    print(f"Wrote Excel file: {xlsx_path}")

if __name__ == "__main__":
    main()
