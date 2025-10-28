#!/usr/bin/env python3
import pandas as pd
from datetime import datetime

# Read the Excel file
input_file = 'honeypot_data_sheets/attacker_reports_20251026.xlsx'  # Change this to your input file name
output_file = 'honeypot_data_sheets/attacker_reports_20251026.xlsx'  # Change this to your desired output file name

# Read the Excel file
df = pd.read_excel(input_file)

# Convert login_time and exit_time to datetime objects if they aren't already
df['login_time'] = pd.to_datetime(df['login_time'])
df['exit_time'] = pd.to_datetime(df['exit_time'])

# Calculate duration in milliseconds
df['duration_ms'] = (df['exit_time'] - df['login_time']).dt.total_seconds() * 1000

# Save to new Excel file
df.to_excel(output_file, index=False)

print(f"Processing complete! New file saved as: {output_file}")
print(f"Total rows processed: {len(df)}")
print("\nFirst few rows with duration:")
print(df.head())
