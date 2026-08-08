# Business Stage Map — Streamlit prototype

A Streamlit + Plotly results page for the 7-question Business Stage Map assessment.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## URL parameters

The app reads:

- `type` — Product, Service, Content, Local, Hybrid
- `stage` — Starting, Growing, Established, Fixing
- `concern` — Money, Getting customers, Keeping customers, Working smarter
- `x` — Market Reach score (0–10; 0–100 also accepted and normalized)
- `y` — Operational Maturity score (0–10; 0–100 also accepted and normalized)

Example:

`/?type=Product&stage=Growing&concern=Getting%20customers&x=7.2&y=4.5`

## Deploy

Upload the folder to a GitHub repository and deploy it with Streamlit Community Cloud.

The benchmark ranges and interpretation logic are currently embedded in `app.py` for the first prototype and can be refined from the benchmark workbook.
