📊 Election Dataset Analysis
This repository contains multiple approaches to summarize and analyze Facebook and Twitter political content datasets from the 2024 U.S. presidential election period.

📁 Files in This Repo
File	Description
pure_python_stats.py	Summarizes CSVs using pure Python (dicts, loops, no libraries).
pandas_stats.py	Uses Pandas to unpack, clean, and summarize datasets.
polars_stats.py	Uses Polars for high-performance summary and nested field unpacking.
shared_analysis.ipynb	Jupyter notebook comparing shared illuminating columns across platforms.
.gitignore	Prevents uploading large data files and temp files to GitHub.

⚙️ How to Run the Scripts
Clone the repo:

bash
Copy
Edit
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Install dependencies:

bash
Copy
Edit
pip install pandas polars
Place datasets (e.g., 2024_fb_ads_president_scored_anon.csv, etc.) inside a ./period_03/ folder as expected by the scripts.
⚠️ Datasets are not included in this repository.

Run any script:

bash
Copy
Edit
python pandas_stats.py
or

bash
Copy
Edit
python polars_stats.py
📈 Insights & Results
Scripts unpack nested JSON fields like delivery_by_region and demographic_distribution to normalize ad-level data.

Shared variables (e.g., scam_illuminating, advocacy_msg_type_illuminating) were compared across Facebook ads, Facebook posts, and Twitter posts.

📊 Key Insights
Facebook Ads had the highest proportion of potential scam-like and election-integrity messaging.

Twitter Posts showed similar levels of advocacy and incivility as Facebook Ads, despite being organic content.

Facebook Posts revealed slightly more fraud-oriented narratives compared to Twitter.

Topics like women’s issues, race and ethnicity, and technology/privacy were flagged across all platforms, suggesting cross-platform narrative targeting.

🚫 Note on Data Files
This repo does not include any raw dataset files. Please do not upload .csv datasets here.
The .gitignore file actively blocks uploading:

markdown
Copy
Edit
*.csv
*.xlsx
*.json
__pycache__/
.ipynb_checkpoints/
