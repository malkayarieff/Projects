# NLP-Driven Patient Risk Stratification in Long-Term Care
DS-399 Major Capstone Project · Malka Yehudis Arieff · Instructor: Sharath Kumar Jagannathan · July 2026

## Overview

This project builds an NLP-driven patient risk stratification system using one year of electronic health record (EHR) data from a long-term care facility (2,153 patients, 215,460 nursing notes). The original goal was to predict dehydration risk directly, but EDA revealed only 5 dehydrated patients out of 2,153 (0.20%), making supervised classification infeasible — any model predicting "not dehydrated" every time would hit 99.8% accuracy while being clinically useless. The project pivoted to an NLP-based risk-scoring system: scoring each patient assessment on clinical keywords found in nursing notes, tracking risk trends across visits, and validating the scoring system against a logistic regression model.

## Data

Not included in this repo — the source files (nursing notes, diagnosis records, medication records) contain real patient information from a long-term care facility and are excluded for privacy. See `Data Dictionary.pdf` for field-level documentation of what the data contained.

Scale: 2,153 patients · 215,460 nursing notes · 6,845 patient assessments

## Methodology

1. EDA and missing-value handling on notes, diagnosis, and medication records
2. Keyword-based severity scoring (29 clinical terms across 3 tiers, grounded in published clinical literature on dehydration and deterioration in elderly patients)
3. Polypharmacy flag (10+ medication classes) and visit-over-visit trend detection (WORSENING / STABLE / IMPROVING)
4. Risk tiering: STABLE (score 0) / MONITOR (1–3) / ELEVATED (4–6) / HIGH RISK (7+), calibrated to this dataset's score distribution and modeled on the tiered structure of validated clinical early-warning scores such as MEWS
5. Logistic regression and random forest models trained to validate the HIGH RISK classification against a polypharmacy-only baseline, evaluated primarily on F1 (missing a high-risk patient is more costly than a false positive, and accuracy is misleading under this class imbalance)
6. Deployed as an interactive Streamlit dashboard for population- and patient-level risk monitoring

## Key Findings

- **Nursing-note language is the dominant risk signal.** The number of clinical risk keywords in a patient's notes (`num_risk_keywords`) had the highest logistic regression coefficient (4.92) and accounted for 59.4% of random forest feature importance — well above any structured field like diagnosis codes or medication count.
- **The scoring system validates strongly against a real model.** Logistic regression reached F1 = 0.903 and AUC-ROC = 0.985, against a polypharmacy-only baseline of F1 = 0.593. Random forest performed comparably (F1 = 0.887) but didn't outperform the simpler, more interpretable logistic model.
- **Merging medication data by patient ID only, not by visit date, was necessary.** Nursing notes and medication records use different assessment schedules, so joining on (patient + date) produced near-zero matches; joining on patient ID alone captured each patient's full medication profile correctly.

| Model | F1 | AUC-ROC | Precision | Recall |
|---|---|---|---|---|
| Baseline (polypharmacy flag only) | 0.593 | 0.622 | 0.43 | 0.94 |
| Logistic Regression | 0.903 | 0.985 | 0.89 | 0.91 |
| Random Forest | 0.887 | 0.981 | 0.84 | 0.93 |

**Bottom line:** what nurses write in daily notes carries more predictive signal than any structured field in the record. A risk-scoring system built on that language, validated against a real model, outperforms one built on diagnosis or medication data alone.

## Repository Contents

- `Final_Code_EDA_Model.ipynb` — full pipeline: EDA, keyword scoring, trend detection, and model training/comparison
- `dashboard_app.py` — Streamlit dashboard for per-patient and population-level risk monitoring
- `Data Dictionary.pdf` — field-level description of the source data
- `README.md` — this file

## How to Run

1. Clone the repository, or download `Final_Code_EDA_Model.ipynb` directly
2. Install dependencies: `pip install pandas numpy scikit-learn matplotlib seaborn wordcloud plotly streamlit`
3. Open `Final_Code_EDA_Model.ipynb` in Jupyter Notebook, JupyterLab, or Google Colab
4. Run all cells in order. The notebook expects `diagnosis.csv`, `medication.csv`, and `notes.csv` (not included — see Data above) and will generate `patient_risk_scores_full.csv` on completion
5. To view the dashboard: put `dashboard_app.py` and the generated `patient_risk_scores_full.csv` in the same folder, then run `streamlit run dashboard_app.py`

## References

- Li, S., Xiao, X., & Zhang, X. (2023). Hydration status in older adults. *Nutrients*, 15, 2609.
- Ogbolu, M. O., Eniade, O. D., & Kozlovszky, M. (2025). Systematic review of risk factors for dehydration. *Healthcare*, 13, 1974.
- Santiago González, N., et al. (2023). Modified Early Warning Score. *Healthcare*, 11, 2654.

## Author

Malka Yehudis Arieff
