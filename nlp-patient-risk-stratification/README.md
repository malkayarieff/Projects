# NLP-Driven Patient Risk Stratification in Long-Term Care
**DS-399 Major Capstone Project**
**Student:** Malka Yehudis Arieff
**Instructor:** Sharath Kumar Jagannathan
**July 2026**

---

## Project Overview

This project builds an NLP-driven patient risk stratification system using one year of electronic health record (EHR) data from a long-term care facility (2,153 patients, 215,460 nursing notes). The original goal was to predict dehydration risk, but EDA revealed only 5 dehydrated patients (0.20%), making supervised classification infeasible. The project pivoted to an unsupervised NLP approach: scoring each patient assessment based on clinical keywords in nursing notes, detecting risk trends over time, and validating the scoring system with a logistic regression model.

**Three main deliverables:**
1. NLP keyword-based risk scoring system (STABLE / MONITOR / ELEVATED / HIGH RISK)
2. Logistic regression model identifying the drivers of HIGH RISK classifications (F1 = 0.903, AUC-ROC = 0.985)
3. Interactive Streamlit dashboard for per-patient risk lookup and monitoring

---

## Files

| File | Description |
|------|--------------|
| `Final_Code_EDA_Model.ipynb` | Main notebook — all EDA, risk scoring, modelling, and exports |
| `dashboard_app.py` | Streamlit dashboard application |
| `Data_Dictionary.pdf` | Field-level description of the source data |
| `Research_Paper.pdf` | Full write-up: literature review, methods, results, limitations |
| `diagnosis.csv`, `medication.csv`, `notes.csv` | Source data (anonymized; resident IDs replace patient names) |
| `patient_risk_scores_full.csv` | Model output — risk scores and categories per patient assessment |
| `README.md` | This file |

**Note on data:** The dataset is anonymized at source, with resident IDs replacing patient names, and was shared with permission from the data provider for use in this project.

---

## How to Run

### 1. Run the Notebook (Google Colab)

1. Open [Google Colab](https://colab.research.google.com)
2. Upload `Final_Code_EDA_Model.ipynb`
3. Upload `diagnosis.csv`, `medication.csv`, and `notes.csv` from this folder
4. Run all cells in order (Runtime → Run all)
5. The notebook will generate `patient_risk_scores_full.csv` and all chart files

### 2. Run the Dashboard (Local)

1. Install dependencies:

```bash
pip install streamlit pandas plotly
```

2. Put `dashboard_app.py` and `patient_risk_scores_full.csv` in the same folder

3. Run:

```bash
cd /path/to/folder
streamlit run dashboard_app.py
```

4. The dashboard opens automatically in your browser at `localhost:8501`

---

## Dependencies

```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
matplotlib>=3.7
seaborn>=0.12
wordcloud>=1.9
plotly>=5.0
streamlit>=1.37
```

Install all at once:

```bash
pip install pandas numpy scikit-learn matplotlib seaborn wordcloud plotly streamlit
```

---

## Key Technical Decisions

### Why NLP keyword scoring instead of supervised ML?
The dehydration target variable had only 5 positive cases out of 2,153 patients (0.20%), making supervised binary classification meaningless — any model predicting "not dehydrated" every time would achieve 99.8% accuracy while being clinically useless.

### Why logistic regression as the primary model?
The target (HIGH RISK flag) is binary, the feature set is small (8 features), and the primary goal is interpretability — understanding *which factors drive high risk* rather than just maximizing predictive accuracy. Logistic regression coefficients directly answer this question.

### Why merge medications by patient ID only?
The nursing notes and medication files use different assessment date schedules for the same patient, so merging by (resident_id + date_of_target) produces near-zero matches. The correct approach is to merge medication summaries by patient ID only, capturing each patient's full medication profile.

### How are risk thresholds defined?
The keyword severity tiers (high/medium/low weight) are grounded in published clinical indicators of dehydration and deterioration in elderly patients (Ogbolu et al., 2025; Li et al., 2023). The risk score cutoffs (STABLE=0, MONITOR=1-3, ELEVATED=4-6, HIGH RISK=7+) follow the tiered scoring structure used in validated clinical early warning scores such as MEWS (Santiago González et al., 2023), calibrated to this dataset's score distribution.

---

## Model Performance

| Model | F1 Score | AUC-ROC | Precision | Recall |
|-------|----------|---------|-----------|--------|
| Baseline (Polypharmacy flag) | 0.593 | 0.622 | 0.43 | 0.94 |
| Logistic Regression | 0.903 | 0.985 | 0.89 | 0.91 |
| Random Forest | 0.887 | 0.981 | 0.84 | 0.93 |

**Primary evaluation metric:** F1 score — chosen because missing a high-risk patient (false negative) is more costly than a false positive in a clinical setting, and accuracy is misleading under class imbalance.

---

## Key Finding

Nursing note content is the dominant predictor of patient risk classification. The number of clinical risk keywords in nursing notes (num_risk_keywords) had the highest logistic regression coefficient (4.92) and accounted for 59.4% of random forest feature importance. This means the language nurses use in their daily documentation is the most informative signal available in this dataset for identifying at-risk patients.

**Limitation:** the HIGH RISK label used to train and evaluate the model is derived from the same keyword scoring system, so these results reflect internal consistency rather than external clinical validity. See `Research_Paper.pdf` for the full discussion, including proposed next steps for validating against independent clinical outcomes.

---

## References

- Li, S., Xiao, X., & Zhang, X. (2023). Hydration status in older adults. *Nutrients*, 15, 2609.
- Ogbolu, M. O., Eniade, O. D., & Kozlovszky, M. (2025). Systematic review of risk factors for dehydration. *Healthcare*, 13, 1974.
- Santiago González, N., et al. (2023). Modified Early Warning Score. *Healthcare*, 11, 2654.
