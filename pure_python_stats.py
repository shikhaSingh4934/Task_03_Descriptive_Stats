import csv
import os
from collections import defaultdict, Counter
from statistics import mean, stdev
from typing import List
import ast
from datetime import datetime
import time

import pandas as pd

def unpack_nested_rows(data, key, prefix):
    unpacked_rows = []

    for row in data:
        raw_value = row.get(key, '').strip()
        try:
            nested_dict = ast.literal_eval(raw_value)
        except:
            continue  # skip rows with bad format

        for subkey, subvals in nested_dict.items():
            new_row = row.copy()
            # Use generic keys based on prefix:
            new_row[f'{prefix}_key'] = subkey
            new_row[f'{prefix}_spend'] = subvals.get('spend', 0)
            new_row[f'{prefix}_impressions'] = subvals.get('impressions', 0)
            unpacked_rows.append(new_row)

    return unpacked_rows

def detect_unpackable_columns(data, sample_size=5):
    """
    Detect columns where values parse to dict of dicts (nested JSON-like).
    Returns list of such column names.
    """
    if not data:
        return []
    columns = data[0].keys()
    unpackable = []

    for col in columns:
        samples = [row.get(col, '') for row in data if col in row][:sample_size]
        for val in samples:
            try:
                val_str = str(val).strip()  # Convert to string before strip
                parsed = ast.literal_eval(val_str)
                if isinstance(parsed, dict) and all(isinstance(v, dict) for v in parsed.values()):
                    unpackable.append(col)
                    break
            except:
                continue
    return unpackable

def summarize_columns(data):
    if not data:
        return []

    columns = data[0].keys()
    summary_rows = []

    for col in columns:
        values = [row[col] for row in data if col in row and row[col] != 'NA']
        count = len(values)
        unique = len(set(values))
        numeric_vals = []

        for val in values:
            try:
                numeric_vals.append(float(val))
            except:
                continue

        row_summary = {
            "column": col,
            "count": count,
            "unique": unique,
            "mean": round(sum(numeric_vals)/len(numeric_vals), 4) if numeric_vals else 'NA',
            "min": min(numeric_vals) if numeric_vals else 'NA',
            "max": max(numeric_vals) if numeric_vals else 'NA',
            "std_dev": round((sum((x - sum(numeric_vals)/len(numeric_vals))**2 for x in numeric_vals) / len(numeric_vals))**0.5, 4) if numeric_vals else 'NA',
        }

        if not numeric_vals:
            freq = {}
            for v in values:
                freq[v] = freq.get(v, 0) + 1
            if freq:
                most_common = max(freq.items(), key=lambda x: x[1])
                row_summary["most_freq"] = f"{most_common[0]} ({most_common[1]})"
            else:
                row_summary["most_freq"] = "NA"
        else:
            row_summary["most_freq"] = "NA"

        summary_rows.append(row_summary)

    return summary_rows

def is_number(s):
    try:
        float(s.replace(',', '').strip())
        return True
    except:
        return False

def to_number(s):
    return float(s.replace(',', '').strip())


DATASETS = [
    "./period_03/2024_fb_ads_president_scored_anon.csv",
    "./period_03/2024_fb_posts_president_scored_anon.csv",
    "./period_03/2024_tw_posts_president_scored_anon.csv"
]

def clean_row(row):
    cleaned = {}
    for key, value in row.items():
        value = value.strip()
        if value == '':
            cleaned[key] = 'NA'
        elif is_number(value):
            cleaned[key] = to_number(value)
        else:
            cleaned[key] = value
    return cleaned

def load_csv(filepath: str) -> List[dict]:
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = [clean_row(row) for row in reader]
    return data

def preview_data(data):
    print(f"Loaded {len(data)} rows")
    print("Sample row:")
    print(data[0])


all_summaries = []

if __name__ == "__main__":
    for file in DATASETS:
        platform_name = file.split("/")[-1].split("_")[1]  # e.g. "fb", "tw"
        print(f"\n--- Analyzing: {file} ---")
        start = time.perf_counter()
        data = load_csv(file)
        data = [row for row in data if any(v != 'NA' for v in row.values())]

        unpack_cols = detect_unpackable_columns(data)
        for col in unpack_cols:
            prefix = col.split('_')[0]
            data = unpack_nested_rows(data, col, prefix)

        # Full dataset summary
        summary = summarize_columns(data)
        for row in summary:
            row["platform"] = platform_name
            row["group"] = "full_dataset"
        all_summaries.extend(summary)

        # Grouped by page_id
        grouped_by_page = defaultdict(list)
        for row in data:
            page_id = row.get('page_id', 'NA')
            grouped_by_page[page_id].append(row)

        for page_id, rows in grouped_by_page.items():
            summary = summarize_columns(rows)
            for row in summary:
                row["platform"] = platform_name
                row["group"] = f"page_id={page_id}"
            all_summaries.extend(summary)

        # Grouped by (page_id, ad_id)
        grouped_by_page_ad = defaultdict(list)
        for row in data:
            key = (row.get("page_id", "NA"), row.get("ad_id", "NA"))
            grouped_by_page_ad[key].append(row)

        for (page_id, ad_id), rows in grouped_by_page_ad.items():
            summary = summarize_columns(rows)
            for row in summary:
                row["platform"] = platform_name
                row["group"] = f"page_id={page_id}, ad_id={ad_id}"
            all_summaries.extend(summary)

    # Write to Excel
    df_summary = pd.DataFrame(all_summaries)
    df_summary.to_csv("full_summary_output_python.csv", index=False)
    print("\n📄 Summary written to 'full_summary_output_python.csv'")
