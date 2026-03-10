# Dashboards

This folder is reserved for lightweight dashboard examples that sit on top of the Gold models.

Current portfolio-ready demo artifact:

- [demo_queries.sql](demo_queries.sql) contains simple reviewer-friendly SQL queries for the Gold tables
- [generate_report.py](generate_report.py) builds a lightweight HTML report from the live Gold layer
- [demo_report.html](demo_report.html) is the generated report artifact for the current dataset

The MVP intentionally stops at analytics-ready warehouse tables. A later iteration can add:

- Metabase or Superset example dashboards
- a small Streamlit exploration app
- chart specifications for hiring-manager demos
