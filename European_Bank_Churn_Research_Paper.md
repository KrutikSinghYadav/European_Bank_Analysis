# Customer Segmentation & Churn Pattern Analytics in European Banking
### A Research Paper Submitted to the European Central Bank Internship Program

---

## Abstract

This research investigates customer churn behavior in European retail banking using a dataset of 10,000 customers across France, Germany, and Spain. Through systematic segmentation across geographic, demographic, and financial dimensions, the study identifies high-risk customer groups, quantifies revenue exposure, and proposes actionable retention strategies. Key findings reveal an overall churn rate of ~20%, with the 46–60 age group, German customers, and high-balance segments posing the greatest retention risk.

---

## 1. Introduction

Customer churn is one of the most consequential challenges in retail banking. Acquiring a new customer costs five to seven times more than retaining an existing one, making churn prevention a high-priority strategic objective. Despite banks having access to rich transactional and behavioral data, most churn management strategies remain reactive and generic — targeting customers only after they have already signaled exit intent.

This project moves beyond reactive approaches. By applying structured segmentation analytics to customer-level data from three European markets — France, Germany, and Spain — this research uncovers *which* customers are churning, *why* they may be leaving, and *what* targeted interventions can reduce attrition.

### 1.1 Objectives

**Primary:**
- Measure the overall churn rate across the customer base
- Identify churn distribution across key customer segments
- Compare churn behavior across geographic regions and demographics

**Secondary:**
- Understand churn risk among high-value customers
- Evaluate the relationship between engagement/tenure and churn
- Support strategic planning and marketing decisions with quantified insights

---

## 2. Dataset Description

The dataset contains **10,000 customer records** from a European retail bank, with 13 features covering identity, financial profile, engagement behavior, and a binary churn outcome.

| Column | Type | Description |
|---|---|---|
| CustomerId | ID | Unique customer identifier |
| Surname | Text | Customer surname (removed before analysis) |
| CreditScore | Numeric | Creditworthiness score |
| Geography | Categorical | France, Spain, Germany |
| Gender | Categorical | Male / Female |
| Age | Numeric | Customer age in years |
| Tenure | Numeric | Years as a customer |
| Balance | Numeric | Account balance (EUR) |
| NumOfProducts | Numeric | Number of bank products held |
| HasCrCard | Binary | Credit card ownership (0/1) |
| IsActiveMember | Binary | Active member status (0/1) |
| EstimatedSalary | Numeric | Annual estimated salary (EUR) |
| Exited | Binary | Churn indicator — **target variable** (1 = churned) |

**Target distribution:** Approximately 20% of customers have churned (Exited = 1), indicating a class imbalance that should be accounted for in any predictive modeling extension of this work.

---

## 3. Data Preprocessing & Feature Engineering

### 3.1 Data Cleaning

- **Surname removed:** The `Surname` column was dropped as it provides no analytical value and raises privacy concerns (`df.drop('Surname', axis=1)`).
- **No missing values** were detected in the primary analytical columns.
- **Binary variable consistency** was validated for `HasCrCard`, `IsActiveMember`, and `Exited`.

### 3.2 Derived Segmentation Features

To enable multi-dimensional analysis, four new columns were engineered:

**Age Group** (`Age_Group`):
```
18–30 | 31–45 | 46–60 | 60+
```
Binning used `pd.cut()` with `include_lowest=True` to ensure 18-year-olds are captured.

**Credit Band** (`Credit_Band`):
```
Low: CreditScore < 580
Medium: 580 ≤ CreditScore ≤ 739
High: CreditScore > 739
```

**Tenure Group** (`Tenure_Group`):
```
New: Tenure ≤ 2 years
Mid-term: 3–7 years
Long-term: > 7 years
```

**Balance Segment** (`Balance_Segment`):
```
Zero-balance: Balance = 0
Low-balance: 0 < Balance ≤ median of positive balances
High-balance: Balance > median of positive balances
```

**Customer Value** (`Customer_Value`):
A composite scoring model was used. Customers meeting **at least 2 of 3** criteria are classified as High-Value:
- Balance ≥ 75th percentile
- EstimatedSalary ≥ 75th percentile
- CreditScore ≥ 75th percentile

This multi-criteria approach is more robust than using any single dimension alone.

---

## 4. Exploratory Data Analysis (EDA)

### 4.1 Overall Churn Rate

The dataset's overall churn rate is approximately **20.4%** — meaning 1 in 5 customers has exited. This is significantly above the typical European retail bank benchmark of 10–15%, indicating a systemic retention problem warranting strategic intervention.

| Metric | Value |
|---|---|
| Total customers | 10,000 |
| Churned customers (~) | ~2,037 |
| Retained customers (~) | ~7,963 |
| Overall churn rate | ~20.4% |

### 4.2 Geographic Churn Analysis

Germany exhibits dramatically higher churn compared to France and Spain.

| Country | Approx. Churn Rate |
|---|---|
| Germany | ~32% |
| France | ~16% |
| Spain | ~17% |

**Key Insight:** German customers churn at twice the rate of French and Spanish customers. This cannot be explained by dataset composition alone — it points to structural issues such as competitive market dynamics, customer service quality, or product-market fit in Germany specifically.

### 4.3 Age Group Churn Analysis

Age is one of the strongest predictors of churn in this dataset.

| Age Group | Approx. Churn Rate |
|---|---|
| 18–30 | ~7% |
| 31–45 | ~12% |
| 46–60 | ~44% |
| 60+ | ~35% |

**Key Insight:** Middle-aged customers (46–60) churn at the highest rate — over 4× the rate of the youngest group. This cohort typically has the highest financial sophistication, more options to compare, and higher switching propensity. Retaining this group is critical as they also tend to be high-balance holders.

### 4.4 Gender-Based Churn Analysis

| Gender | Approx. Churn Rate |
|---|---|
| Female | ~25% |
| Male | ~16% |

**Key Insight:** Female customers churn at a rate roughly 9 percentage points higher than male customers. This disparity warrants qualitative investigation — it may reflect product design, communication style, or service experience gaps.

### 4.5 Tenure Group Churn Analysis

| Tenure Group | Approx. Churn Rate |
|---|---|
| New (≤2 yrs) | ~22% |
| Mid-term (3–7 yrs) | ~20% |
| Long-term (>7 yrs) | ~21% |

**Key Insight:** Notably, tenure shows a relatively flat churn curve — customers do not significantly increase loyalty over time. This is an important finding: the bank is not building loyalty through longevity. Long-term customers should be churning far less; the fact that they don't suggests unmet engagement or value delivery.

### 4.6 Credit Band Churn Analysis

| Credit Band | Approx. Churn Rate |
|---|---|
| Low (<580) | ~24% |
| Medium (580–739) | ~20% |
| High (>739) | ~19% |

**Key Insight:** While higher credit scores correlate with marginally lower churn, the difference is not dramatic. Credit score alone is a weak predictor of retention. Financial profile must be evaluated in combination with balance and salary.

### 4.7 Balance Segment Churn Analysis

| Balance Segment | Approx. Churn Rate |
|---|---|
| Zero-balance | ~14% |
| Low-balance | ~16% |
| High-balance | ~28% |

**Key Insight:** Counter-intuitively, high-balance customers churn *more* than low-balance ones. This is a critical finding — it suggests the bank may be failing to meet the expectations of its most financially engaged customers. High-balance churners represent significant revenue risk.

### 4.8 Customer Value Segment Churn

| Segment | Approx. Churn Rate |
|---|---|
| High-Value | ~26% |
| Low-Value | ~18% |

**Key Insight:** High-value customers (meeting 2 of 3 criteria: high balance, salary, and credit score) churn at a higher rate than low-value ones. This inverted relationship — where more valuable customers are *less* loyal — is the single most actionable finding of this study.

### 4.9 Product Count & Churn

| Products Held | Approx. Churn Rate |
|---|---|
| 1 product | ~28% |
| 2 products | ~8% |
| 3 products | ~83% |
| 4 products | ~100% |

**Key Insight:** Customers with 2 products have the lowest churn — they appear to be optimally engaged. Customers with 3 or 4 products have extremely high churn, possibly indicating overselling or product misalignment.

---

## 5. High-Value Customer Churn Analysis

### 5.1 Revenue Risk Quantification

Customers classified as High-Value represent roughly the top 25th percentile on balance, salary, and credit score. Their average balance substantially exceeds that of low-value customers.

If approximately 26% of high-value customers churn, and average high-value balance is ~€150,000 (estimated from top-quartile balance), the implied **balance outflow risk** is substantial — on the order of hundreds of millions of euros across a portfolio of this size.

### 5.2 Geography × Value Interaction

German high-value customers face a compounding risk: Germany already has the highest overall churn rate, and within Germany, the high-value segment churns at an even greater relative rate. This makes **Germany + High-Value** the single most urgent customer segment to address.

### 5.3 Engagement of High-Value Churners

A significant portion of high-value churners are classified as **inactive members** (`IsActiveMember = 0`). Inactivity appears to be a leading indicator of churn — customers who stop engaging with the bank are far more likely to exit, regardless of their financial profile.

---

## 6. Key Performance Indicators Summary

| KPI | Value |
|---|---|
| Overall Churn Rate | ~20.4% |
| Highest Geographic Churn | Germany (~32%) |
| Highest Age Group Churn | 46–60 (~44%) |
| High-Value Customer Churn Rate | ~26% |
| Gender Churn Gap | Female 9pp higher than Male |
| Engagement Drop Risk | Inactive members churn ~2× more |
| Highest Product Churn | 3–4 products (~83–100%) |

---

## 7. Recommendations

### 7.1 Geographic Strategy — Germany Priority Intervention
Deploy a dedicated retention task force for the German market. Conduct exit interviews or surveys to understand the primary drivers of dissatisfaction. Consider reviewing product pricing, fee structures, and customer service quality specific to Germany. A regional loyalty program may help.

### 7.2 Age-Targeted Retention — 46–60 Segment
This segment has the highest churn rate and likely holds significant assets. Assign relationship managers or premium service tiers to customers in this cohort. Offer personalized financial planning, estate planning, or wealth management services aligned with their life stage.

### 7.3 High-Value Customer Proactive Outreach
Implement an early warning system (EWS) flagging high-value customers who become inactive. Trigger automated, personalized outreach within 30–60 days of inactivity detection. Offer exclusive benefits, dedicated support lines, or fee waivers.

### 7.4 Female Customer Experience Audit
The 9 percentage point gender churn gap demands investigation. Conduct a structured NPS and satisfaction survey segmented by gender to identify specific pain points. Review marketing communications, product design, and branch/app experience for gender-related friction.

### 7.5 Product Portfolio Optimization
The 3–4 product churn spike suggests aggressive cross-selling may backfire. Audit customers with 3+ products to determine if they were sold appropriate products. Focus cross-selling on the 1→2 product transition, which shows the greatest loyalty gain.

### 7.6 Tenure-Based Loyalty Program
Since long-tenure customers don't show meaningfully lower churn, introduce milestone-based loyalty rewards at years 3, 5, and 10. Reinforce the relationship at key anniversaries to rebuild emotional loyalty and switching costs.

---

## 8. Conclusion

This research provides a structured, segmentation-driven understanding of customer churn across three European markets. The most critical finding is the **concentration of churn among high-value, middle-aged customers in Germany** — a combination that represents significant revenue risk. Standard churn metrics mask this pattern; only through segmentation does the true risk profile become visible.

The recommendations outlined above move from generic churn management to targeted, data-driven retention strategies that align interventions with the specific segments and behaviors that drive attrition. Implementation of even a subset of these recommendations — particularly the high-value EWS and Germany-specific outreach — could meaningfully reduce revenue leakage and improve customer lifetime value across the portfolio.

---

*Prepared by: [Your Name] | European Central Bank Internship Program | 2025*
