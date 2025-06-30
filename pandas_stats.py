import pandas as pd
import ast
import time

DATASETS = [
    "./period_03/2024_fb_ads_president_scored_anon.csv",
    "./period_03/2024_fb_posts_president_scored_anon.csv",
    "./period_03/2024_tw_posts_president_scored_anon.csv"
]

def detect_unpackable_columns(df, sample_size=5):
    """
    Detect columns that contain nested JSON-like dict-of-dicts strings.
    """
    unpackable_cols = []
    for col in df.columns:
        samples = df[col].dropna().head(sample_size).astype(str).str.strip()
        for val in samples:
            try:
                parsed = ast.literal_eval(val)
                if isinstance(parsed, dict) and all(isinstance(v, dict) for v in parsed.values()):
                    unpackable_cols.append(col)
                    break
            except:
                continue
    return unpackable_cols

def unpack_nested_column(df, column, prefix):
    unpacked_rows = []
    for _, row in df.iterrows():
        try:
            nested = ast.literal_eval(row[column]) if pd.notna(row[column]) else {}
            for key, val in nested.items():
                new_row = row.to_dict()
                new_row[f"{prefix}_key"] = key
                new_row[f"{prefix}_spend"] = val.get("spend", 0)
                new_row[f"{prefix}_impressions"] = val.get("impressions", 0)
                unpacked_rows.append(new_row)
        except:
            continue
    return pd.DataFrame(unpacked_rows)

def summarize_dataframe(df, name="", platform=""):
    summary = []
    for col in df.columns:
        series = df[col]
        count = series.count()
        unique = series.nunique(dropna=True)
        mean_val = min_val = max_val = std_dev = most_freq = "NA"

        if pd.api.types.is_numeric_dtype(series):
            mean_val = round(series.mean(), 4)
            min_val = series.min()
            max_val = series.max()
            std_dev = round(series.std(), 4)
        else:
            most_common = series.mode()
            if not most_common.empty:
                most_freq = f"{most_common[0]} ({series.value_counts().iloc[0]})"

        summary.append({
            "platform": platform,
            "group": name,
            "column": col,
            "count": count,
            "unique": unique,
            "mean": mean_val,
            "min": min_val,
            "max": max_val,
            "std_dev": std_dev,
            "most_freq": most_freq
        })
    return summary
all_summary_rows = []  

if __name__ == "__main__":
    for file in DATASETS:
        platform = file.split("_")[1]  # e.g., 'fb' or 'tw'
        print(f"\n--- Analyzing: {file} ---")
        start = time.perf_counter()
        df = pd.read_csv(file).dropna(how="all")
        end = time.perf_counter()
        print(f"Load time: {end - start:.2f} sec")

        unpack_cols = detect_unpackable_columns(df)
        print(f"\nDetected unpackable columns: {unpack_cols}")

        for col in unpack_cols:
            prefix = col.split('_')[-1]
            print(f"\nUnpacking {col} with prefix '{prefix}' ...")
            start = time.perf_counter()
            df = unpack_nested_column(df, col, prefix)
            print(f" Unpack time: {time.perf_counter() - start:.2f} sec")

        # Full dataset summary
        start = time.perf_counter()
        summary = summarize_dataframe(df, name="Full Dataset", platform=platform)
        all_summary_rows.extend(summary)
        print(f"Full dataset summary time: {time.perf_counter() - start:.2f} sec")

        # Grouped by page_id
        if 'page_id' in df.columns:
            print("\n--- Summary after aggregation by page_id ---")
            start = time.perf_counter()
            for page_id, group in df.groupby('page_id'):
                summary = summarize_dataframe(group, name=f"page_id={page_id}", platform=platform)
                all_summary_rows.extend(summary)
            print(f"Summary by page_id time: {time.perf_counter() - start:.2f} sec")

        # Grouped by (page_id, ad_id)
        if 'page_id' in df.columns and 'ad_id' in df.columns:
            print("\n--- Summary after aggregation by (page_id, ad_id) ---")
            start = time.perf_counter()
            for keys, group in df.groupby(['page_id', 'ad_id']):
                summary = summarize_dataframe(group, name=f"page_id={keys[0]}, ad_id={keys[1]}", platform=platform)
                all_summary_rows.extend(summary)
            print(f"Summary by (page_id, ad_id) time: {time.perf_counter() - start:.2f} sec")

# At end of script
df_all_summary = pd.DataFrame(all_summary_rows)
df_all_summary.to_csv("summary_output_pandas.csv", index=False)
print("Summary saved to 'summary_output_pandas.csv'")
