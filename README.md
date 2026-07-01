# 🏦 European Bank Customer Churn Analytics

A segmentation-driven churn analysis of **10,000 retail banking customers** across France, Germany, and Spain — built as a research study for a (simulated) European Central Bank stakeholder briefing, delivered as an interactive Streamlit dashboard, a full academic research paper, and an executive summary.

---

## 📌 Project Overview

Retail banks lose significant revenue to customer churn, yet most retention strategies remain reactive and generic. This project investigates **who is churning, why, and where the revenue risk is concentrated**, using structured segmentation across geographic, demographic, financial, and engagement dimensions.

Core questions addressed:

- What is the bank's overall churn rate, and how does it compare to industry benchmarks?
- Which markets, age groups, and customer segments churn the most?
- Are the bank's most valuable customers also its most loyal — or its biggest flight risk?
- What early-warning signals (engagement, product count) predict churn?

---

## 🔑 Key Findings

| Finding | Detail |
|---|---|
| **Overall churn rate** | ~20.4% (≈2,037 of 10,000 customers) — above the 10–15% industry benchmark |
| **Germany** | ~32% churn — double the rate of France (~16%) and Spain (~17%) |
| **Age 46–60** | ~44% churn — the highest-risk and highest-value age cohort |
| **High-value customers** | ~26% churn vs. ~18% for low-value — the bank's best customers are its least loyal |
| **Gender gap** | Female customers churn ~9 percentage points more than male customers |
| **Engagement** | Inactive members churn roughly 2x more than active members |
| **Product count** | Customers with 3–4 products churn at 83–100%, suggesting overselling/misalignment; 2-product holders are the most loyal segment |
| **Tenure** | Churn stays flat (~20–22%) regardless of years as a customer — loyalty is not being earned over time |

Full analysis and methodology are documented in the [Research Paper](European_Bank_Churn_Research_Paper.md) and condensed in the [Executive Summary](Executive_Summary_ECB.md).

---

## 📊 Interactive Dashboard

`streamlit_dashboard.py` provides a filterable, single-page churn analytics view with a sidebar filter panel for:

- **Geography** (France / Germany / Spain)
- **Gender**
- **Age Group**
- **Customer Value** (High / Low)
- **Tenure Group** (New / Mid-term / Long-term)

The dashboard surfaces KPI cards, churn-rate breakdowns by segment, and a Balance vs. Estimated Salary scatter comparing churned and retained customers — all built on Plotly visualizations with a custom banking-themed UI.

---

## 🗂️ Repository Structure

```
European_Bank_Analysis/
│
├── streamlit_dashboard.py              # Interactive Streamlit churn dashboard
├── European_Bank_Churn_Final.csv       # Cleaned & feature-engineered dataset (10,000 records)
├── European_Bank_Churn_Research_Paper.md  # Full research paper (methodology, EDA, recommendations)
├── Executive_Summary_ECB.md            # Condensed stakeholder-facing brief
├── requirements.txt                    # Python dependencies
└── README.md
```

---

## 🧮 Dataset

**Source fields** (13 raw attributes per customer):

| Column | Description |
|---|---|
| `CustomerId` | Unique customer identifier |
| `CreditScore` | Creditworthiness score |
| `Geography` | France, Germany, or Spain |
| `Gender` | Male / Female |
| `Age` | Customer age |
| `Tenure` | Years as a customer |
| `Balance` | Account balance (EUR) |
| `NumOfProducts` | Number of bank products held |
| `HasCrCard` | Credit card ownership (0/1) |
| `IsActiveMember` | Active engagement status (0/1) |
| `EstimatedSalary` | Annual estimated salary (EUR) |
| `Exited` | Churn indicator — **target variable** (1 = churned) |

`Surname` was dropped during cleaning (no analytical value, privacy concern). No missing values were found in the analytical columns.

**Engineered features** added for segmentation:

| Feature | Logic |
|---|---|
| `Age_Group` | 18–30 \| 31–45 \| 46–60 \| 60+ |
| `Credit_Band` | Low (<580) \| Medium (580–739) \| High (>739) |
| `Tenure_Group` | New (≤2 yrs) \| Mid-term (3–7 yrs) \| Long-term (>7 yrs) |
| `Balance_Segment` | Zero-balance \| Low-balance \| High-balance (split at median of positive balances) |
| `Customer_Value` | High-Value if a customer meets ≥2 of 3 criteria: Balance, Salary, and CreditScore each in the top quartile |

---

## 🛠️ Tech Stack

- **Python** — data processing and feature engineering
- **Pandas / NumPy** — cleaning, binning, and segmentation logic
- **Plotly** — interactive charts
- **Streamlit** — dashboard front-end and deployment
- **Markdown / Word** — research paper and executive summary deliverables

---

## 🚀 Running the Dashboard Locally

```bash
# Clone the repository
git clone https://github.com/KrutikSinghYadav/European_Bank_Analysis.git
cd European_Bank_Analysis

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_dashboard.py
```

The app reads `European_Bank_Churn_Final.csv` from the repository root.

---

## 📈 Strategic Recommendations (Summary)

1. **Germany-specific retention program** — the market's ~32% churn rate is structural, not statistical noise; warrants exit surveys, competitive benchmarking, and regional relationship managers.
2. **High-Value Early Warning System** — flag high-value customers at first sign of inactivity and trigger outreach within 30–60 days.
3. **Target the 46–60 age segment** — premium service tiers and wealth-planning offers for the bank's highest-value, highest-risk cohort.
4. **Audit the female customer experience** — investigate the 9pp churn gap through segmented satisfaction surveys.
5. **Rework product cross-selling** — the 1→2 product transition drives loyalty; pushing customers to 3+ products correlates with extreme churn and should be reviewed for overselling.
6. **Introduce milestone-based loyalty rewards** — tenure alone isn't reducing churn, so loyalty needs to be actively reinforced at key account anniversaries.

---

## 👤 Author

**Krutik Singh Yadav**
Final-year Computer Engineering student, data analytics & data engineering enthusiast.

---

*This project was built as a self-directed portfolio case study to demonstrate end-to-end analytics workflow: data cleaning, feature engineering, segmentation analysis, dashboard development, and executive-level reporting.*
