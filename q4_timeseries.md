# Question 4 — Functional components of booking frequency vs. time

## Decomposition model

```
Y(t) = T(t) + S_year(t) + S_week(t) + H(t) + ε(t)
```

where Y(t) is the daily count of bookings (payment timestamps aggregated to calendar day).

---

## Component breakdown

### T(t) — Trend

**Definition:** The long-term, slow-moving direction of booking volume after all
cyclic and calendar effects are removed.

**Expected shape for Bambuk:** Piecewise log-linear growth.
- 2023 data likely shows post-pandemic recovery (step-up at the start of the series).
- Gradual platform growth thereafter (user base expansion, new property listings).
- Possible inflection points around major product launches or marketing campaigns.

**How to detect and estimate:**
- Fit OLS on the 28-day rolling mean to get a first visual impression.
- Use STL (Seasonal-Trend decomposition using LOESS) from statsmodels for a robust estimate.
- Test for structural breaks with the Chow test or CUSUM plot — these mark regime changes
  (e.g., a marketing spike that permanently shifted the baseline).

---

### S_year(t) — Annual seasonality  (period = 365.25 days)

**Definition:** Intra-year demand rhythm that repeats every calendar year.

**Expected pattern for country-house bookings:**
- **Peak 1 — summer (July–August):** strongest signal; families book countryside houses
  during school summer holidays.
- **Peak 2 — winter holidays (late December – early January):** New Year retreats,
  ski-adjacent properties.
- **Trough — February–March:** lowest demand in the absence of holidays.

**How to detect:**
- ACF spike at lag ≈ 365 days (requires at least 2 years of data — covered by 2023–2025 range).
- Fourier harmonics k = 1, 2, 3 fitted to the de-trended series capture the main shape
  without overfitting; k = 1 gives the broad summer/winter wave, k = 2–3 adds the
  spring shoulder season and the winter peak asymmetry.

---

### S_week(t) — Weekly seasonality  (period = 7 days)

**Definition:** Day-of-week pattern in booking behaviour.

**Expected pattern:**
- **High:** Friday and Saturday (leisure mindset, browsing after work).
- **Moderate:** Sunday.
- **Low:** Monday–Thursday (work week suppresses discretionary spending).

**How to detect:**
- ACF spike at lag 7 (and 14, 21…).
- Fourier harmonics k = 1, 2 on a 7-day period are sufficient.
- Alternatively: day-of-week dummy variables in a regression framework.

---

### H(t) — Holiday and calendar effects

**Definition:** Irregular but predictable demand bumps tied to specific calendar dates
rather than a fixed seasonal rhythm.

**Main drivers:**
- Public holidays (national and regional) in the booker's country of origin — join from
  the Nager.Date data obtained in Q3.
- School vacation windows (especially spring break and October half-term).
- "Bridge days" — working days between a public holiday and a weekend that workers take
  as leave, creating 4–5 day mini-breaks with high property demand.
- Long-weekend effect: if a holiday falls on Thursday, Friday bookings spike.

**How to model:**
- Binary indicator variables: `is_holiday`, `is_school_break`, `days_to_nearest_holiday`.
- "Window" indicators: +3 days before and after a major holiday.
- In Prophet these are supplied as the `holidays` dataframe; in a regression model
  they enter as additional regressors.

---

### ε(t) — Residual / noise

**Definition:** Unexplained variance remaining after T, S_year, S_week, and H are removed.

**Sources:**
- Random day-to-day fluctuations (weather surprises, viral social-media posts).
- Measurement noise (server outages causing missed bookings).
- One-off local events not captured in H(t) (large festival → spike; regional disaster → drop).

**How to analyse:**
- Check ACF/PACF of residuals: if autocorrelation remains, an AR/MA component may help.
- Inspect outliers (|ε| > 3 σ) — these often mark data quality issues or genuine shocks
  worth investigating.

---

### Additional structural feature — Lead-time distribution

Not a seasonal component per se, but critical for operational forecasting.

**Definition:** Distribution of (check-in date − payment date) across all bookings.

**Expected shape:** Bimodal.
- **Mode 1 — Planned bookings:** peak at 30–60 days ahead; driven by families securing
  summer and holiday slots early.
- **Mode 2 — Last-minute bookings:** peak at 0–7 days; impulsive weekend getaways,
  weather-triggered decisions.

**How to use:**
- Separate the two modes with a mixture model (Gaussian mixture or log-normal mixture).
- "Planned" vs. "last-minute" segments have different price sensitivity: planned bookers
  compare options, last-minute bookers prioritise availability.
- Enables demand backfilling: given bookings today, estimate how many more will arrive
  for check-in dates 7 / 30 / 60 days out.

---

## Practical implementation

```python
# Option A — Facebook Prophet (recommended for quick, interpretable results)
from prophet import Prophet
import pandas as pd

df = (
    bookings
    .assign(ds=lambda x: x["paid_at"].dt.date, y=1)
    .groupby("ds", as_index=False)["y"].sum()
)

m = Prophet(
    yearly_seasonality=True,   # Fourier k=10 by default; reduce to 5 for smoother fit
    weekly_seasonality=True,
    daily_seasonality=False,
    holidays=national_holidays_df,   # from Nager.Date (Q3)
    changepoint_prior_scale=0.05,    # regularise trend flexibility
)
m.fit(df)
forecast = m.predict(m.make_future_dataframe(periods=90))
m.plot_components(forecast)   # visualises T, S_year, S_week, H separately


# Option B — statsmodels STL (more explicit, no black-box changepoints)
from statsmodels.tsa.seasonal import STL

result = STL(daily_counts, period=365, robust=True).fit()
trend     = result.trend
seasonal  = result.seasonal   # captures annual cycle only; add weekly separately
residual  = result.resid
```

**Scalability note:** With 6 M rows, aggregate to daily counts first (< 1 100 rows for
3 years), then fit the decomposition. Fitting on raw event-level data is unnecessary
and orders of magnitude slower.

---

## Summary table

| Component | Period | Detection method | Implementation |
|---|---|---|---|
| T(t) Trend | Aperiodic | Rolling mean, STL, Chow test | Prophet changepoints / STL trend |
| S_year Annual | 365.25 d | ACF lag 365, Fourier k=1–3 | Prophet yearly / STL period=365 |
| S_week Weekly | 7 d | ACF lag 7, Fourier k=1–2 | Prophet weekly / day-of-week dummies |
| H(t) Holidays | Calendar | Domain knowledge + holiday API | Prophet holidays df / indicator vars |
| Lead-time | — | Histogram of check-in − paid_at | GMM / log-normal mixture |
| Breaks | Irregular | CUSUM, Chow test, PACF of residuals | Prophet changepoint_prior_scale |
