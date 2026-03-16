# Bambuk Data Analyst Take-Home Task

Solution to the Bambuk data analyst take-home task — four questions covering log parsing,
synthetic data generation, external enrichment, and time-series decomposition.

---

## Questions

| # | Question | One-line summary |
|---|----------|-----------------|
| [Q1](bambuk_interview.ipynb#q1) | Log Line Regex | Single regex that validates and parses all 7 fields |
| [Q2](bambuk_interview.ipynb#q2) | Control Dataset Generator | Generates N random rows, all passing the Q1 regex |
| [Q3](bambuk_interview.ipynb#q3) | External Data Enrichment | 9 open data sources joinable to the log |
| [Q4](bambuk_interview.ipynb#q4) | Time-Series Decomposition | STL decomposition with synthetic demo + Prophet skeleton |

The notebook is pre-executed — open `bambuk_interview.ipynb` directly on GitHub to read
code and output in the browser without installing anything.

---

## Repository structure

```
bambuk-analytics-task/
├── README.md                  ← this file
├── bambuk_interview.ipynb     ← main deliverable (all 4 answers, pre-executed)
├── q1_regex.py                ← regex module imported by the notebook
├── q2_generator.py            ← generator module imported by the notebook
└── requirements.txt           ← dependencies
```

---

## How to run locally

```bash
pip install -r requirements.txt
jupyter notebook bambuk_interview.ipynb
```

Run all cells with **Kernel → Restart & Run All**.
