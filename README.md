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

## ⚙️ How to Run the Scripts

1. **Clone the repo**:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
