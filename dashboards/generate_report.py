from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

from ingestion.common.db import get_connection

OUTPUT_PATH = Path("dashboards/demo_report.html")

METRIC_QUERIES = {
    "Daily Active Wallets": (
        "select count(*) as value from analytics_analytics.gold_daily_active_wallets"
    ),
    "Transactions Per Day": (
        "select count(*) as value from analytics_analytics.gold_transactions_per_day"
    ),
    "Gas Metrics Daily": (
        "select count(*) as value from analytics_analytics.gold_gas_metrics_daily"
    ),
    "Token Price Daily": (
        "select count(*) as value from analytics_analytics.gold_token_price_daily"
    ),
}

TABLE_QUERY = """
select
    asset_id,
    price_date,
    close_price,
    market_cap,
    total_volume
from analytics_analytics.gold_token_price_daily
order by price_date desc, asset_id
limit 10
"""


def fetch_metrics() -> dict[str, int]:
    metrics: dict[str, int] = {}
    with get_connection() as connection:
        with connection.cursor() as cursor:
            for label, query in METRIC_QUERIES.items():
                cursor.execute(query)
                metrics[label] = int(cursor.fetchone()["value"])
    return metrics


def fetch_price_rows() -> list[dict]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(TABLE_QUERY)
            return list(cursor.fetchall())


def build_html(metrics: dict[str, int], rows: list[dict]) -> str:
    metric_cards = "\n".join(
        f"""
        <article class="card">
          <p class="eyebrow">{escape(label)}</p>
          <p class="value">{value}</p>
        </article>
        """
        for label, value in metrics.items()
    )

    table_rows = "\n".join(
        f"""
        <tr>
          <td>{escape(str(row["asset_id"]))}</td>
          <td>{escape(str(row["price_date"]))}</td>
          <td>{escape(str(row["close_price"]))}</td>
          <td>{escape(str(row["market_cap"]))}</td>
          <td>{escape(str(row["total_volume"]))}</td>
        </tr>
        """
        for row in rows
    )

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>digital-assets-warehouse Demo Report</title>
    <style>
      :root {{
        --bg: #f3f0e8;
        --surface: rgba(255, 255, 255, 0.78);
        --ink: #13202c;
        --muted: #5d6874;
        --line: #d8d7cd;
        --accent: #0f766e;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: "Avenir Next", "Segoe UI", sans-serif;
        background:
          radial-gradient(circle at top left, rgba(15, 118, 110, 0.12), transparent 28%),
          linear-gradient(180deg, #f8f6f0 0%, var(--bg) 100%);
        color: var(--ink);
      }}
      main {{
        max-width: 1120px;
        margin: 0 auto;
        padding: 56px 24px 72px;
      }}
      h1 {{
        margin: 0;
        font-size: 48px;
        line-height: 1.05;
      }}
      .lede {{
        max-width: 760px;
        color: var(--muted);
        font-size: 19px;
        line-height: 1.6;
        margin-top: 18px;
      }}
      .stamp {{
        color: var(--muted);
        font-size: 14px;
        margin-top: 14px;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 18px;
        margin-top: 36px;
      }}
      .card, .panel {{
        backdrop-filter: blur(8px);
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: 0 16px 30px rgba(19, 32, 44, 0.07);
      }}
      .card {{
        padding: 22px 22px 26px;
      }}
      .eyebrow {{
        margin: 0;
        color: var(--muted);
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }}
      .value {{
        margin: 18px 0 0;
        font-size: 54px;
        font-weight: 700;
      }}
      .panel {{
        margin-top: 26px;
        padding: 24px;
      }}
      h2 {{
        margin: 0 0 14px;
        font-size: 24px;
      }}
      table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
      }}
      th, td {{
        padding: 12px 10px;
        border-bottom: 1px solid var(--line);
        text-align: left;
      }}
      th {{
        color: var(--muted);
        font-weight: 600;
      }}
      .note {{
        margin-top: 18px;
        color: var(--muted);
        line-height: 1.5;
      }}
      .pill {{
        display: inline-block;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(15, 118, 110, 0.12);
        color: var(--accent);
        font-size: 13px;
        font-weight: 600;
        margin-top: 18px;
      }}
      @media (max-width: 900px) {{
        .grid {{
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
      }}
      @media (max-width: 620px) {{
        h1 {{
          font-size: 38px;
        }}
        .grid {{
          grid-template-columns: 1fr;
        }}
        table {{
          font-size: 13px;
          display: block;
          overflow-x: auto;
        }}
      }}
    </style>
  </head>
  <body>
    <main>
      <p class="pill">Local portfolio demo</p>
      <h1>digital-assets-warehouse</h1>
      <p class="lede">
        Lightweight analytics report generated from the Gold layer of the local warehouse.
        This artifact is meant for hiring managers, founders, and technical reviewers who
        want to see concrete outputs without navigating the full stack first.
      </p>
      <p class="stamp">Generated from live Postgres data at {escape(generated_at)}</p>
      <section class="grid">
        {metric_cards}
      </section>
      <section class="panel">
        <h2>Token Price Sample</h2>
        <table>
          <thead>
            <tr>
              <th>Asset</th>
              <th>Date</th>
              <th>Close Price</th>
              <th>Market Cap</th>
              <th>Total Volume</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>
        <p class="note">
          These rows come from <code>analytics_analytics.gold_token_price_daily</code>.
          The current dataset is intentionally small, but the same delivery pattern works for
          broader backfills and richer Gold marts.
        </p>
      </section>
    </main>
  </body>
</html>
"""


def main() -> None:
    metrics = fetch_metrics()
    rows = fetch_price_rows()
    OUTPUT_PATH.write_text(build_html(metrics, rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
