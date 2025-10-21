#!/usr/bin/env python3
"""
daily_reports.py

Process daily attacker report .txt files written in the new positional format and
write attacker_reports_YYYYMMDD.xlsx.

New positional format (expected lines):
  0: con_name
  1: config_num
  2: attacker_ip
  3: login_time
  4: exit_time
  5: num_commands
  6..N-1: commands (one per line)
  optionally final line: "X minutes and Y seconds"

Usage:
  python3 daily_reports.py /path/to/Attacker_Data
  python3 daily_reports.py /path/to/Attacker_Data --date 2025-10-20
"""
import sys
import re
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import argparse
import time

def day_range_for_date(target_date: datetime):
    start = datetime(target_date.year, target_date.month, target_date.day)
    end = start + timedelta(days=1)
    start_ts = int(time.mktime(start.timetuple()))
    end_ts = int(time.mktime(end.timetuple()))
    return start_ts, end_ts

def parse_positional_file(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [ln.rstrip("\n") for ln in text.splitlines()]
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    con_name = lines[0] if len(lines) > 0 else ""
    config_num = lines[1] if len(lines) > 1 else ""
    attacker_ip = lines[2] if len(lines) > 2 else ""
    login_time = lines[3] if len(lines) > 3 else ""
    exit_time = lines[4] if len(lines) > 4 else ""
    num_commands = ""
    commands = ""
    minutes = 0
    seconds = 0

    if len(lines) > 5:
        if lines[5].strip().isdigit():
            num_commands = lines[5].strip()
            cmd_lines = lines[6:]
        else:
            cmd_lines = lines[5:]
        if cmd_lines:
            last = cmd_lines[-1].strip()
            m = re.search(r"([0-9]+)\s+minutes?\s+and\s+([0-9]+)\s+seconds", last)
            if m:
                minutes = int(m.group(1))
                seconds = int(m.group(2))
                cmd_lines = cmd_lines[:-1]
        commands = "\n".join(cmd_lines).strip()
        if not num_commands:
            num_commands = str(len([c for c in cmd_lines if c.strip()]))
    else:
        commands = ""
        num_commands = lines[5].strip() if len(lines) > 5 else ""

    total_seconds = minutes * 60 + seconds

    return {
        "filename": path.name,
        "config_num": config_num,
        "attacker_ip": attacker_ip,
        "login_time": login_time,
        "exit_time": exit_time,
        "container_id": con_name,
        "attacker_username": "",
        "num_commands": num_commands,
        "commands": commands,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": total_seconds
    }

def main():
    parser = argparse.ArgumentParser(description="Create Excel report from positional attacker .txt files.")
    parser.add_argument("dir", help="Directory containing report .txt files")
    parser.add_argument("--date", help="Target date YYYY-MM-DD (local). Defaults to yesterday if omitted.", default=None)
    args = parser.parse_args()

    outdir = Path(args.dir)
    if not outdir.exists() or not outdir.is_dir():
        print(f"Directory not found: {outdir}", file=sys.stderr)
        sys.exit(1)

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

        if not (start_ts <= mtime < end_ts):
            continue

        try:
            row = parse_positional_file(p)
            rows.append(row)
        except Exception as e:
            print(f"Warning: failed to parse {p.name}: {e}", file=sys.stderr)

    if not rows:
        print("No report files for the target date were found; no spreadsheet created.", file=sys.stderr)
        sys.exit(0)

    df = pd.DataFrame(rows, columns=[
        "filename","config_num","attacker_ip","login_time","exit_time",
        "container_id","attacker_username","num_commands","commands","minutes","seconds","total_seconds"
    ])

    xlsx_path = outdir / f"attacker_reports_{target.strftime('%Y%m%d')}.xlsx"
    try:
        df.to_excel(xlsx_path, index=False)
        print(f"Wrote Excel file: {xlsx_path}")
    except Exception as e:
        print(f"Failed to write Excel file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

