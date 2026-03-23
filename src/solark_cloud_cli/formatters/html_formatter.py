import html
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from solark_cloud_cli import __version__
from solark_cloud_cli.models.energy import EnergyReport


class HtmlFormatter:
    def __init__(self, plant_url: str, username: str | None = None) -> None:
        self._plant_url = plant_url
        self._username = username

    def format(self, report: EnergyReport) -> str:
        has_values = report.valuations is not None and len(report.valuations) > 0
        labels = report.labels

        # Build pivoted data
        by_time: dict[str, dict[str, float]] = {}
        for record in report.records:
            if record.timestamp not in by_time:
                by_time[record.timestamp] = {}
            by_time[record.timestamp][record.label] = record.value

        val_by_time: dict[str, object] = {}
        if has_values:
            for v in report.valuations:
                val_by_time[v.timestamp] = v

        # Totals
        energy_totals: dict[str, float] = {label: 0.0 for label in labels}
        val_totals = {"self_consumed": 0.0, "avoided": 0.0, "export_credit": 0.0, "total": 0.0}

        rows_html = []
        for timestamp in sorted(by_time.keys()):
            row_data = by_time[timestamp]
            cells = [f'<td class="ts">{html.escape(timestamp)}</td>']
            for label in labels:
                val = row_data.get(label)
                if val is not None:
                    energy_totals[label] += val
                cells.append(f'<td class="num">{val:,.1f}</td>' if val is not None else '<td class="num">—</td>')

            if has_values:
                v = val_by_time.get(timestamp)
                if v is not None:
                    val_totals["self_consumed"] += v.self_consumed_kwh
                    val_totals["avoided"] += v.avoided_cost
                    val_totals["export_credit"] += v.export_credit
                    val_totals["total"] += v.total_value
                    cells.append(f'<td class="num">{v.self_consumed_kwh:,.1f}</td>')
                    cells.append(f'<td class="money">${v.avoided_cost:,.2f}</td>')
                    cells.append(f'<td class="money">${v.export_credit:,.2f}</td>')
                    cells.append(f'<td class="money total-val">${v.total_value:,.2f}</td>')
                else:
                    cells.extend(['<td class="num">—</td>'] * 4)

            rows_html.append(f"<tr>{''.join(cells)}</tr>")

        # Totals row
        if has_values:
            total_cells = ['<td class="ts total-row">TOTAL</td>']
            for label in labels:
                total_cells.append(f'<td class="num total-row">{energy_totals[label]:,.1f}</td>')
            total_cells.append(f'<td class="num total-row">{val_totals["self_consumed"]:,.1f}</td>')
            total_cells.append(f'<td class="money total-row">${val_totals["avoided"]:,.2f}</td>')
            total_cells.append(f'<td class="money total-row">${val_totals["export_credit"]:,.2f}</td>')
            total_cells.append(f'<td class="money total-row total-val">${val_totals["total"]:,.2f}</td>')
            rows_html.append(f'<tr class="totals">{"".join(total_cells)}</tr>')

        # Header
        header_cells = ["<th>Time</th>"]
        for label in labels:
            header_cells.append(f"<th>{html.escape(label)}</th>")
        if has_values:
            header_cells.extend(["<th>Self-Used</th>", "<th>Avoided $</th>", "<th>Export $</th>", "<th>Value $</th>"])

        period_display = report.period.replace("_", " ").title()
        tz_name = os.environ.get("SOLARK_TIMEZONE")
        tz = ZoneInfo(tz_name) if tz_name else datetime.now(tz=timezone.utc).astimezone().tzinfo
        now = datetime.now(tz=tz)
        generated = now.strftime("%Y-%m-%d %H:%M %Z")
        plant_link = f'<a href="{html.escape(self._plant_url)}" target="_blank">{html.escape(self._plant_url)}</a>'
        account_display = html.escape(self._username) if self._username else "—"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Solar Energy Report — {html.escape(report.date)} — Plant {html.escape(report.plant_id)}</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-dim: #8b949e;
    --accent: #58a6ff;
    --green: #3fb950;
    --purple: #bc8cff;
    --yellow: #d29922;
    --money: #3fb950;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
    line-height: 1.6;
    padding: 2rem;
  }}
  .container {{ max-width: 1400px; margin: 0 auto; }}
  header {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
  }}
  header h1 {{
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 0.5rem;
  }}
  .meta {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.75rem;
    font-size: 0.875rem;
  }}
  .meta-item {{ color: var(--text-dim); }}
  .meta-item strong {{ color: var(--text); }}
  .meta-item a {{ color: var(--accent); text-decoration: none; }}
  .meta-item a:hover {{ text-decoration: underline; }}
  .meta-item.full-width {{ grid-column: 1 / -1; word-break: break-all; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    font-size: 0.875rem;
  }}
  thead {{ background: rgba(88, 166, 255, 0.08); }}
  th {{
    padding: 0.75rem 1rem;
    text-align: right;
    font-weight: 600;
    color: var(--accent);
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
  }}
  th:first-child {{ text-align: left; }}
  td {{
    padding: 0.5rem 1rem;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }}
  .ts {{ text-align: left; color: var(--text-dim); font-family: 'SF Mono', Consolas, monospace; }}
  .num {{ text-align: right; font-family: 'SF Mono', Consolas, monospace; }}
  .money {{ text-align: right; color: var(--money); font-family: 'SF Mono', Consolas, monospace; }}
  .total-val {{ color: var(--purple); font-weight: 600; }}
  .total-row {{ font-weight: 700; background: rgba(88, 166, 255, 0.06); }}
  tr:hover td {{ background: rgba(88, 166, 255, 0.04); }}
  tr.totals td {{ border-top: 2px solid var(--accent); border-bottom: none; }}
  footer {{
    margin-top: 1.5rem;
    padding: 1rem 2rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    font-size: 0.75rem;
    color: var(--text-dim);
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
  }}
  footer a {{ color: var(--accent); text-decoration: none; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Solar Energy Report</h1>
    <div class="meta">
      <div class="meta-item"><strong>Plant ID:</strong> {html.escape(report.plant_id)}</div>
      <div class="meta-item"><strong>Period:</strong> {html.escape(period_display)}</div>
      <div class="meta-item"><strong>Date:</strong> {html.escape(report.date)}</div>
      <div class="meta-item"><strong>Account:</strong> {account_display}</div>
      <div class="meta-item"><strong>Generated:</strong> {generated}</div>
      <div class="meta-item full-width"><strong>SolarkCloud:</strong> {plant_link}</div>
    </div>
  </header>
  <table>
    <thead><tr>{"".join(header_cells)}</tr></thead>
    <tbody>
{"".join(rows_html)}
    </tbody>
  </table>
  <footer>
    <span>Generated by solark-cloud-cli v{html.escape(__version__)}</span>
    <span>Data source: <a href="{html.escape(self._plant_url)}" target="_blank">SolarkCloud</a></span>
  </footer>
</div>
</body>
</html>"""
