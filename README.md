# 📊 Election Dataset Analysis

This repository contains multiple approaches to summarize and analyze Facebook and Twitter political content datasets from the 2024 U.S. presidential election period.

---

## 📁 Files in This Repo

| File                  | Description                                                             |
|-----------------------|-------------------------------------------------------------------------|
| `pure_python_stats.py` | Summarizes CSVs using pure Python (dicts, loops, no libraries).         |
| `pandas_stats.py`      | Uses **Pandas** to unpack, clean, and summarize datasets.               |
| `polars_stats.py`      | Uses **Polars** for high-performance summary and nested field unpacking.|
| `shared_analysis.ipynb`| Jupyter notebook comparing shared illuminating columns across platforms.|
| `.gitignore`           | Prevents uploading large data files and temp files to GitHub.           |

---
## 📈 Insights & Results

Scripts unpack nested JSON fields like `delivery_by_region` and `demographic_distribution` to normalize ad-level data.

Shared variables (e.g., `scam_illuminating`, `advocacy_msg_type_illuminating`) were compared across **Facebook Ads**, **Facebook Posts**, and **Twitter Posts**.

---

### 📊 Key Insights

- **Facebook Ads** had the highest proportion of potential scam-like and election-integrity messaging.

- **Twitter Posts** showed similar levels of advocacy and incivility as Facebook Ads, despite being organic content.

- **Facebook Posts** revealed slightly more fraud-oriented narratives compared to Twitter.

- Topics like **women’s issues**, **race and ethnicity**, and **technology/privacy** were flagged across all platforms — suggesting **cross-platform narrative targeting**.


## ⚙️ How to Run the Scripts

1. **Clone the repo**:
   ```bash
   git clone https://github.com/shikhaSingh4934/Task_03_Descriptive_Stats.git
   cd Task_03_Descriptive_Stats
   
