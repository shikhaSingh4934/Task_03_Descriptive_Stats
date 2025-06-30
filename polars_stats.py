import polars as pl
import ast
import time

DATASETS = [
    "./period_03/2024_fb_ads_president_scored_anon.csv",
    "./period_03/2024_fb_posts_president_scored_anon.csv",
    "./period_03/2024_tw_posts_president_scored_anon.csv"
]

all_summary_rows = []  # ← to store final summary rows

NUMERIC_DTYPES = {
    pl.Int8, pl.Int16, pl.Int32, pl.Int64,
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    pl.Float32, pl.Float64
}

def is_numeric_dtype(dtype):
    return dtype in NUMERIC_DTYPES

def detect_unpackable_columns(df, sample_size=5):
    unpackable_cols = []
    for col in df.columns:
        col_vals = df[col].limit(sample_size).to_list()
        for val in col_vals:
            try:
                if isinstance(val, str):
                    parsed = ast.literal_eval(val)
                    if isinstance(parsed, dict) and all(isinstance(v, dict) for v in parsed.values()):
                        unpackable_cols.append(col)
                        break
            except:
                continue
    return unpackable_cols

def unpack_nested_column(df, column_name, prefix):
    unpacked = []
    for row in df.iter_rows(named=True):
        try:
            if row[column_name] is not None and row[column_name] != "":
                nested = ast.literal_eval(row[column_name])
            else:
                nested = {}
            for key, val in nested.items():
                new_row = dict(row)
                new_row[f"{prefix}_key"] = key
                new_row[f"{prefix}_spend"] = val.get("spend", 0)
                new_row[f"{prefix}_impressions"] = val.get("impressions", 0)
                unpacked.append(new_row)
        except:
            continue
    return pl.DataFrame(unpacked)

def summarize_polars_df(df: pl.DataFrame, name="", platform=""):
    summary = []

    for col in df.columns:
        series = df[col]
        dtype = series.dtype
        count = series.len() - series.null_count()
        unique = series.n_unique()
        mean_val = min_val = max_val = std_dev = most_freq = "NA"

        if is_numeric_dtype(dtype):
            mean_raw = series.mean()
            if mean_raw is not None:
                mean_val = round(mean_raw, 4)
            min_val = series.min()
            max_val = series.max()
            std_raw = series.std()
            if std_raw is not None:
                std_dev = round(std_raw, 4)
        else:
            try:
                vc_df = (df
                         .select(pl.col(col).value_counts().alias("vc"))
                         .unnest("vc")
                         .sort("count", descending=True))
                if vc_df.height > 0:
                    top_val = vc_df[col][0]
                    top_count = vc_df["count"][0]
                    most_freq = f"{top_val} ({top_count})"
            except Exception as e:
                most_freq = f"Err: {e}"

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


if __name__ == "__main__":
    for file in DATASETS:
        platform = file.split("/")[-1].split("_")[1]  # "fb" or "tw"
        print(f"\n--- Analyzing: {file} ---")
        start = time.perf_counter()
        df = pl.read_csv(file)
        df = df.filter(~pl.all_horizontal(pl.all().is_null()))  # drop null-only rows
        # df = df.slice(0, 10)
        print(df)
        print(f"Load time: {time.perf_counter() - start:.2f} sec")

        # Detect nested columns
        unpack_cols = detect_unpackable_columns(df)
        print(f"\nDetected unpackable columns: {unpack_cols}")

        # Unpack each
        for col in unpack_cols:
            prefix = col.split('_')[-1]
            print(f"\nUnpacking {col} with prefix '{prefix}' ...")
            start = time.perf_counter()
            df = unpack_nested_column(df, col, prefix)
            print(f" Unpack time: {time.perf_counter() - start:.2f} sec")

        # Full summary
        start = time.perf_counter()
        summary = summarize_polars_df(df, name="Full Dataset", platform=platform)
        all_summary_rows.extend(summary)
        print(f"Full dataset summary time: {time.perf_counter() - start:.2f} sec")

        # By page_id
        if "page_id" in df.columns:
            print("\n--- Summary after aggregation by page_id ---")
            start = time.perf_counter()
            for pid in df.select("page_id").unique().iter_rows():
                pid_val = pid[0]
                group = df.filter(pl.col("page_id") == pid_val)
                summary = summarize_polars_df(group, name=f"page_id={pid_val}", platform=platform)
                all_summary_rows.extend(summary)
            print(f"Summary by page_id time: {time.perf_counter() - start:.2f} sec")

        # By page_id + ad_id
        if "page_id" in df.columns and "ad_id" in df.columns:
            print("\n--- Summary after aggregation by (page_id, ad_id) ---")
            start = time.perf_counter()
            group_keys = df.select(["page_id", "ad_id"]).unique().iter_rows()
            for pid, aid in group_keys:
                group = df.filter((pl.col("page_id") == pid) & (pl.col("ad_id") == aid))
                summary = summarize_polars_df(group, name=f"page_id={pid}, ad_id={aid}", platform=platform)
                all_summary_rows.extend(summary)
            print(f"Summary by (page_id, ad_id) time: {time.perf_counter() - start:.2f} sec")

    # Export all summary rows to CSV
    output_df = pl.DataFrame(all_summary_rows)
    output_df.write_csv("polars_summary_output.csv")
    print("Summary saved to 'polars_summary_output.csv'")
