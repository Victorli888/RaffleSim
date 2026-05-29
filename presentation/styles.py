CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&family=Spline+Sans+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg:#111111; --panel:#1b1b1b; --panel-bd:#2c2c2c;
  --card:#242424; --card-bd:#333333; --inset:#161616;
  --derived:#2c2c2c; --input-bg:#141414; --input-bd:#3a3a3a;
  --tx:#ededed; --tx-2:#aeaeae; --tx-3:#7d7d7d; --tx-4:#5e5e5e;
  --m-bg:#E1F5EE; --m-tx:#085041; --m-ac:#1D9E75;
  --t-bg:#E6F1FB; --t-tx:#0C447C; --t-ac:#378ADD;
  --w-bg:#FAECE7; --w-tx:#712B13; --w-ac:#D85A30;
  --curve:#7E76E6; --curve-deep:#534AB7;
}
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: "Figtree", system-ui, sans-serif !important;
  font-variant-numeric: tabular-nums;
  color: var(--tx);
}
[data-testid="stAppViewContainer"] > .main { background: var(--bg) !important; }
[data-testid="stHeader"] { background: var(--bg) !important; }
[data-testid="block-container"] {
  max-width: 1480px;
  padding: 24px 34px 80px;
}
.sim-panel {
  background: var(--panel);
  border: 1px solid var(--panel-bd);
  border-radius: 20px;
  padding: 26px;
}
.kicker {
  font-size: 12px; font-weight: 700; letter-spacing: 0.09em;
  color: var(--tx-3); text-transform: uppercase; margin-bottom: 14px;
}
.bucket {
  border: 1px solid var(--card-bd);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 12px;
}
.bk-head {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px;
}
.bk-ring {
  width: 18px; height: 18px; border-radius: 50%; flex-shrink: 0;
  border: 2.5px solid currentColor; position: relative;
  display: flex; align-items: center; justify-content: center;
}
.bk-ring::after {
  content: ""; width: 7px; height: 7px;
  border-radius: 50%; background: currentColor;
}
.bk-name { font-size: 16px; font-weight: 700; }
.bk-range { margin-left: auto; font-size: 12px; opacity: 0.8; }
.bk-body {
  display: grid; grid-template-columns: 1fr 1fr 1fr 1.05fr;
}
.cell {
  padding: 10px 14px; border-right: 1px solid var(--card-bd);
  background: var(--card);
}
.cell:last-child { border-right: none; }
.cell.derived { background: var(--derived); }
.clbl { font-size: 13px; color: var(--tx-2); display: block; margin-bottom: 6px; text-align: center; }
.dval {
  display: block; font-size: 26px; font-weight: 700;
  letter-spacing: -0.02em; line-height: 1.1;
}
.dtag {
  display: block; font-size: 10.5px; font-weight: 600;
  text-transform: uppercase; color: var(--tx-4); margin-top: 2px;
}
.deq {
  display: block; font-size: 11px; color: var(--tx-4);
  font-family: "Spline Sans Mono", monospace; margin-top: 2px;
}
.pool-bar {
  height: 12px; border-radius: 7px; background: var(--inset);
  display: flex; gap: 3px; overflow: hidden; margin: 8px 0;
}
.pool-seg { height: 100%; border-radius: 3px; transition: flex-grow .35s ease; }
.pool-legend { display: flex; gap: 16px; flex-wrap: wrap; margin-top: 6px; }
.pl { font-size: 13px; color: var(--tx-2); display: flex; align-items: center; gap: 5px; }
.dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.prize-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.prize-chip {
  background: var(--card); border: 1px solid var(--card-bd);
  border-radius: 9px; padding: 9px 12px;
  display: flex; justify-content: space-between; align-items: center;
  min-width: 140px; border-left-width: 3px;
}
.prize-n { font-size: 12px; font-weight: 600; color: var(--tx-3); }
.prize-win { font-size: 13px; font-weight: 700; }
.sum-chips { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
.sum-chip {
  background: var(--card); border: 1px solid var(--card-bd);
  border-radius: 10px; padding: 10px 14px;
  display: flex; align-items: center; gap: 8px;
}
.sv { font-size: 20px; font-weight: 700; }
.se { font-size: 11px; color: var(--tx-3); }
.run-btn {
  background: #378ADD; color: #fff; border: none;
  border-radius: 10px; padding: 0 18px; height: 40px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  display: inline-flex; align-items: center; gap: 7px;
}
.run-btn:hover { background: #4A9AEF; }
.st-key-run_draw_btn [data-testid="stBaseButton-secondary"],
.st-key-run_draw_btn [data-testid="stBaseButton-primary"] {
  background-color: #378ADD !important;
  border-color: #378ADD !important;
  color: #fff !important;
  font-weight: 600 !important;
}
.st-key-run_draw_btn [data-testid="stBaseButton-secondary"]:hover,
.st-key-run_draw_btn [data-testid="stBaseButton-primary"]:hover {
  background-color: #4A9AEF !important;
  border-color: #4A9AEF !important;
  color: #fff !important;
}
.st-key-run_draw_btn [data-testid="stBaseButton-secondary"]:focus,
.st-key-run_draw_btn [data-testid="stBaseButton-primary"]:focus {
  box-shadow: 0 0 0 3px rgba(55, 138, 221, 0.35) !important;
}
.gamma-pill {
  background: #534AB7; color: #fff; border-radius: 9px;
  padding: 5px 14px; font-family: "Spline Sans Mono", monospace;
  font-size: 15px; font-weight: 600;
}
.global-card {
  background: var(--card); border: 1px solid var(--card-bd);
  border-radius: 14px; padding: 16px;
}
[data-testid="stNumberInput"] button { display: none !important; }
[data-testid="stNumberInput"] input { text-align: center !important; }
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
  background: var(--input-bg) !important;
  border: 1px solid var(--input-bd) !important;
  border-radius: 10px !important;
  color: var(--tx) !important;
  font-size: 17px !important;
  font-weight: 600 !important;
}
[data-testid="stNumberInput"] {
  max-width: 140px !important;
  margin: 0 auto !important;
}
[data-testid="stNumberInput"] input:focus {
  border-color: #555 !important;
  box-shadow: 0 0 0 3px rgba(255,255,255,.06) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
  background: #fff !important;
  border: 4px solid #534AB7 !important;
}
/* bucket counter buttons — :not() prevents common-ancestor bleed */
[data-testid="stVerticalBlock"]:has(.counter-btn-minus):not(:has(.counter-btn-plus)) [data-testid="stBaseButton-secondary"],
[data-testid="stVerticalBlock"]:has(.counter-btn-plus):not(:has(.counter-btn-minus)) [data-testid="stBaseButton-secondary"] {
  padding: 0 !important;
  width: 26px !important;
  min-width: 26px !important;
  height: 26px !important;
  min-height: 26px !important;
  font-size: 15px !important;
  line-height: 1 !important;
  border-radius: 6px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
[data-testid="stVerticalBlock"]:has(.counter-btn-minus):not(:has(.counter-btn-plus)) [data-testid="stBaseButton-secondary"] {
  background-color: #8B1A1A !important;
  border-color: #8B1A1A !important;
  color: #fff !important;
}
[data-testid="stVerticalBlock"]:has(.counter-btn-minus):not(:has(.counter-btn-plus)) [data-testid="stBaseButton-secondary"]:hover {
  background-color: #A52020 !important;
  border-color: #A52020 !important;
}
[data-testid="stVerticalBlock"]:has(.counter-btn-plus):not(:has(.counter-btn-minus)) [data-testid="stBaseButton-secondary"] {
  background-color: #145A32 !important;
  border-color: #145A32 !important;
  color: #fff !important;
}
[data-testid="stVerticalBlock"]:has(.counter-btn-plus):not(:has(.counter-btn-minus)) [data-testid="stBaseButton-secondary"]:hover {
  background-color: #1D7A43 !important;
  border-color: #1D7A43 !important;
}
/* tight gap + centered buttons in the counter row */
[data-testid="stHorizontalBlock"]:has(.counter-btn-minus):has(.counter-btn-plus) {
  gap: 3px !important;
  align-items: center !important;
}
[data-testid="stHorizontalBlock"]:has(.counter-btn-minus):has(.counter-btn-plus) > [data-testid="stColumn"] {
  padding-left: 0 !important;
  padding-right: 0 !important;
}
[data-testid="stVerticalBlock"]:has(.counter-btn-minus):not(:has(.counter-btn-plus)),
[data-testid="stVerticalBlock"]:has(.counter-btn-plus):not(:has(.counter-btn-minus)) {
  align-items: center !important;
}
/* level/EXP threshold table */
.level-table {
  width: 100%;
  border-collapse: collapse;
}
.level-table th {
  font-size: 10.5px; font-weight: 700; letter-spacing: 0.07em;
  text-transform: uppercase; color: var(--tx-3);
  padding: 4px 8px; border-bottom: 1px solid #2c2c2c; text-align: left;
}
.level-table th:last-child,
.level-table td:last-child { text-align: right; }
.level-table td {
  padding: 3px 8px;
  font-family: "Spline Sans Mono", monospace;
  font-size: 12px; color: var(--tx-2);
  border-bottom: 1px solid #1e1e1e;
}
.level-table td:first-child { color: var(--tx-4); }
.level-table tr:last-child td { border-bottom: none; }
#MainMenu, footer, [data-testid="stDeployButton"] { visibility: hidden; }
label[data-testid="stWidgetLabel"] { color: var(--tx-2) !important; }
.currency-sym {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 38px;
  font-size: 17px;
  font-weight: 600;
  color: var(--tx-2);
  padding-right: 2px;
}
.st-key-gamma_inp [data-testid="stNumberInput"] {
  max-width: 120px !important;
  margin: 0 0 0 auto !important;
}
.st-key-gamma_inp label[data-testid="stWidgetLabel"] {
  justify-content: flex-end !important;
}
.st-key-gamma_inp label[data-testid="stWidgetLabel"] p {
  text-align: right !important;
  font-size: 11.5px !important;
}
</style>
"""
