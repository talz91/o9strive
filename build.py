#!/usr/bin/env python3
"""
BBU UAT Dashboard — Build Script
Usage: python3 build.py <path_to_smartsheet_export.xlsx>
Output: BBU_UAT_Dashboard.html (commit this to GitHub to deploy)
"""

import sys, re, json, math
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas not installed. Run: pip install pandas openpyxl")
    sys.exit(1)

# ── CONFIG ────────────────────────────────────────────────────────────────────
TEMPLATE_FILE = Path(__file__).parent / "BBU_UAT_Dashboard.html"
OUTPUT_FILE = Path(__file__).parent / "index.html"

# ── NAME MAP ──────────────────────────────────────────────────────────────────
NAME_MAP = {
    'Dadabo, John F': 'John Dadabo','John Dadabo': 'John Dadabo',
    'Marzo, Brian A': 'Brian Marzo','Brian A Marzo': 'Brian Marzo','Brian Marzo': 'Brian Marzo',
    'Bernabe, Teresa': 'Teresa Bernabe','Davis, Caleb M': 'Caleb Davis',
    'Evers, Kyle J': 'Kyle Evers','Hignight, Greg': 'Greg Hignight',
    'Hughes, Chrissy': 'Chrissy Hughes','Jepsen, Jodie M': 'Jodie Jepsen',
    'McDonald, Hayden O': 'Hayden McDonald','Morrow, Heather R': 'Heather Morrow',
    'Padgett, Justin S': 'Justin Padgett','Sears, Kristin M': 'Kristin Sears',
    'Smith, Liv': 'Liv Smith','Socci, Lenet Marie': 'Lenet Socci',
    'Varma, Apeksha': 'Apeksha Varma','kelly.dolan@grupobimbo.com': 'Kelly Dolan',
    'Dolan, Kelly': 'Kelly Dolan','Alberto Garcia': 'Alberto Garcia',
    'Garcia, Alberto A': 'Alberto Garcia','Eisenberg, Christopher T (Todd)': 'Todd Eisenberg',
    'Worrell, Whitney R': 'Whitney Worrell','Park, James M': 'James Park',
    'Zernhel, Jessica A': 'Jessica Zernhel','McCullagh, Carol': 'Carol McCullagh',
    'Smith, Kristin R': 'Kristin Smith','Archambault, Elizabeth': 'Elizabeth Archambault',
    'Nordman, Rodney': 'Rodney Nordman','Campos, Alejandro': 'Alejandro Campos',
    'Rosson, Rob': 'Rob Rosson','Robert Rosson': 'Rob Rosson',
    'Deepa Yadav': 'Deepa Yadav','Manthan Wadibhasme': 'Manthan Wadibhasme',
    'Nikilesh Narayan': 'Nikilesh Narayan','Ravi Chauhan': 'Ravi Chauhan',
}

def std_name(raw):
    if not raw or str(raw).strip() == '' or str(raw).lower() == 'nan': return ''
    raw = str(raw).strip()
    if raw in NAME_MAP: return NAME_MAP[raw]
    if ',' in raw:
        parts = raw.split(',')
        first = parts[1].strip().split()[0]
        return first + ' ' + parts[0].strip()
    return raw

# ── TEST ID MAPS ──────────────────────────────────────────────────────────────
UAT_TEST_ID_MAP = {
    '01_Master Data_UAT': '01_Master Data',
    '02_Transactional Data_UAT': '02_Transactional Data',
    '03_Review & Update Authorization List_UAT': '03_Review & Update Authorization List',
    '04_NPI Like Item_UAT': '04_NPI Like Item',
    '05_COGS & Commissions_UAT': '05_COGS and Commissions',
    '05_COGS and Commissions_UAT': '05_COGS and Commissions',
    '06_EDLP & SRP_UAT': '06_EDLP & SRP',
    '07_Sell-out to Sell-in Offsets_UAT': '07_Sell-out to Sell-in Offsets',
    '08_Guidelines & Guardrails_UAT ADMIN': '08_Guardrails & Guidelines',
    '08_Guardrails & Guidelines_UAT ADMIN': '08_Guardrails & Guidelines',
    '08.2_Guidelines & Guardrails_UAT PLANNER': '08.2_Guardrails & Guidelines',
    '08.2_Guardrails & Guidelines_UAT PLANNER': '08.2_Guardrails & Guidelines',
    '09_AOP Targets_UAT ADMIN': '09_AOP Targets',
    '09_AOP Target_UAT ADMIN': '09_AOP Targets',
    '09.2_AOP Targets_UAT PLANNER': '09.2_AOP Targets',
    '10_Baseline Forecast_UAT': '10_Baseline Forecast',
    '11_Promo Event Planning_UAT': '11_Promo Event Planning',
    '12_Promo Recommendation_UAT': '12_Promo Recommmendation',
    '12_Promo Recommmendation_UAT': '12_Promo Recommmendation',
    '13_Promo Initiative Approval_UAT ADMIN': '13_Promo Initiative Approval',
    '13_Promo Approval_UAT': '13_Promo Initiative Approval',
    '14_Promo Exceptions_UAT': '14_Promo Exceptions',
    '15_Promo Actualization_UAT': '15_Promo Actualization',
    '16_Promo Ranking - Net Sales vs VCM-AVD_UAT': '16_Promo Ranking - Net Sales vs VCM-AVD',
    '17_Shipments vs Consumption_UAT': '17_Shipments Vs Consumption',
    '17_Shipments Vs Consumption_UAT': '17_Shipments Vs Consumption',
    '18_Cross Competitor Consumption_UAT': '18_Cross Competitor Consumption',
    '19_Manual Initiative_UAT': '19_Manual Initiative',
    '20_Non Promo Trade_UAT': '20_Non Promo Trade',
    '21_Gap Closure_UAT': '21_Gap Closure',
    '22_Commercial P&L_UAT': '22_Commercial P&L',
    # E2E passthroughs
    '01_Master Data': '01_Master Data',
    '02_Transactional Data': '02_Transactional Data',
    '03_Authorization': '03_Review & Update Authorization List',
    '03_Review & Update Authorization List': '03_Review & Update Authorization List',
    '04_NPI Like Item': '04_NPI Like Item',
    '05_COGS and Commissions': '05_COGS and Commissions',
    '06_EDLP & SRP': '06_EDLP & SRP',
    '07_Sell-out to Sell-in Offsets': '07_Sell-out to Sell-in Offsets',
    '08_Guardrails & Guidelines': '08_Guardrails & Guidelines',
    '09_AOP Target': '09_AOP Targets',
    '09_AOP Targets': '09_AOP Targets',
    '10_Baseline Forecast': '10_Baseline Forecast',
    '11_Promo Event Planning': '11_Promo Event Planning',
    '12_Promo Recommmendation': '12_Promo Recommmendation',
    '13_Promo Approval': '13_Promo Initiative Approval',
    '14_Promo Exceptions': '14_Promo Exceptions',
    '15_Promo Actualization': '15_Promo Actualization',
    '17_Shipments Vs Consumption': '17_Shipments Vs Consumption',
    '19_Manual Initiative': '19_Manual Initiative',
    '21_Gap Closure': '21_Gap Closure',
    '22_Commercial P&L': '22_Commercial P&L',
}

COMP_NORM = {
    '01_Master Data_UAT': '01_Master Data',
    '02_Transactional Data_UAT': '02_Transactional Data',
    '03_Review & Update Authorization List_UAT': '03_Review & Update Authorization List',
    '04_NPI Like Item_UAT': '04_NPI Like Item',
    '05_COGS & Commissions_UAT': '05_COGS & Commissions',
    '05_COGS and Commissions_UAT': '05_COGS & Commissions',
    '06_EDLP & SRP_UAT': '06_EDLP & SRP',
    '07_Sell-out to Sell-in Offsets_UAT': '07_Sell-out to Sell-in Offsets',
    '08_Guidelines & Guardrails_UAT ADMIN': '08_Guidelines & Guardrails',
    '08_Guardrails & Guidelines_UAT ADMIN': '08_Guidelines & Guardrails',
    '08.2_Guidelines & Guardrails_UAT PLANNER': '08.2_Guidelines & Guardrails',
    '08.2_Guardrails & Guidelines_UAT PLANNER': '08.2_Guidelines & Guardrails',
    '09_AOP Targets_UAT ADMIN': '09_AOP Targets',
    '09_AOP Target_UAT ADMIN': '09_AOP Targets',
    '09.2_AOP Targets_UAT PLANNER': '09.2_AOP Targets',
    '10_Baseline Forecast_UAT': '10_Baseline Forecast',
    '11_Promo Event Planning_UAT': '11_Promo Event Planning',
    '12_Promo Recommendation_UAT': '12_Promo Recommendation',
    '12_Promo Recommmendation_UAT': '12_Promo Recommendation',
    '13_Promo Initiative Approval_UAT ADMIN': '13_Promo Initiative Approval',
    '13_Promo Approval_UAT': '13_Promo Initiative Approval',
    '14_Promo Exceptions_UAT': '14_Promo Exceptions',
    '15_Promo Actualization_UAT': '15_Promo Actualization',
    '16_Promo Ranking - Net Sales vs VCM-AVD_UAT': '16_Promo Ranking - Net Sales vs VCM-AVD',
    '17_Shipments vs Consumption_UAT': '17_Shipments vs Consumption',
    '17_Shipments Vs Consumption_UAT': '17_Shipments vs Consumption',
    '18_Cross Competitor Consumption_UAT': '18_Cross Competitor Consumption',
    '19_Manual Initiative_UAT': '19_Manual Initiative',
    '20_Non Promo Trade_UAT': '20_Non Promo Trade',
    '21_Gap Closure_UAT': '21_Gap Closure',
    '22_Commercial P&L_UAT': '22_Commercial P&L',
    '23_YoY Drivers vs Plan Consolidated_UAT': '23_YoY Drivers vs Plan Consolidated',
    '24_Latest Estimate vs Target Consolidated_UAT': '24_Latest Estimate vs Target Consolidated',
    '25_Scenarios_UAT': '25_Scenarios',
}

def display_status(progress, ado_status):
    if ado_status == 'Closed': return 'Closed'
    if progress in [75, 90]: return 'Pending Validation'
    return ado_status or 'Active'

def classify_defect(title, desc):
    t = (str(title) + ' ' + str(desc)).lower()
    if re.search(r'past week|historical|override.*past|past.*override|lly|baseline.*ly|ly.*baseline|carry.forward|actuali[sz]|historical.*lock', t): return 4
    if re.search(r'erp|base cost.*incorrect|not aligned|sync|upstream|master data inconsist|not authorized.*costco|cost is not correct|no values|future projected.*no', t): return 5
    if re.search(r'not carry|carry forward|end.to.end|downstream|approval.*not visible|initiative.*not visible|gap closure.*fail|send.*cwv|lump sum.*not carried|offset.*not respected', t): return 3
    if re.search(r'override.*logic|logic.*incorrect|incorrect.*calc|formula|precedence|should not allow|commission sign|trade rate|margin.*impacted|historical.*allowed|allowed.*cancel|allowed.*delete|guardrail.*violation|not highlight|allowed mechanics', t): return 2
    return 1

def build(xlsx_path):
    print(f"Reading {xlsx_path}...")
    df = pd.read_excel(xlsx_path, sheet_name=0)
    print(f"  {len(df)} rows loaded")

    # ── Load template ─────────────────────────────────────────────────────────
    if not TEMPLATE_FILE.exists():
        print(f"ERROR: Template not found at {TEMPLATE_FILE}")
        sys.exit(1)
    with open(TEMPLATE_FILE) as f:
        content = f.read()

    # ── Build DEFECTS ─────────────────────────────────────────────────────────
    defect_rows = df[
        (df['o9 Feedback'].astype(str).str.strip().str.lower() == 'defect') &
        (df['ADO ID'].notna())
    ]
    defects = []
    for _, r in defect_rows.iterrows():
        try:
            ado_id = str(int(float(r['ADO ID'])))
        except:
            continue
        raw_test_id = str(r.get('Test ID') or '').strip()
        test_id  = UAT_TEST_ID_MAP.get(raw_test_id, raw_test_id)
        step_id  = str(r.get('Step ID') or '').strip()
        ado_status = str(r.get('ADO Status') or 'Active').strip()
        try: progress = float(r['Progress']) if r['Progress'] else 0
        except: progress = 0
        ds       = display_status(progress, ado_status)
        phase    = str(r.get('Phase') or 'E2E').strip()
        title    = str(r.get('Title') or r.get('Defect Description') or '')[:80]
        tester   = std_name(r.get('Tester Name'))
        desc     = str(r.get('Defect Description') or '').strip()
        expected = str(r.get('Expected Behavior') or '').strip()
        severity = str(r.get('Severity') or 'Medium').strip()
        ado_url  = str(r.get('ADO Url') or '').strip()
        cat      = classify_defect(title, desc)
        defects.append({
            'ADO ID': ado_id, 'ADO Url': ado_url, 'Test ID': test_id,
            'Raw Test ID': raw_test_id, 'Step ID': step_id,
            'ADO Status': ado_status, 'Display Status': ds, 'Phase': phase,
            'Title': title, 'Tester Name': tester, 'Defect Description': desc,
            'Expected Behavior': expected, 'Severity': severity, 'Category': cat
        })
    print(f"  {len(defects)} defects built")

    # ── Build completion data ─────────────────────────────────────────────────
    # Extract assignment matrix from current template
    m = re.search(r'const PLAN_DATA\s*=\s*(\[.*?\]);\nconst TESTER_DATA', content, re.DOTALL)
    old_plan = json.loads(m.group(1))
    plan_assignment = {p['label']: p['assigned'] for p in old_plan}
    plan_seqs       = {p['label']: p['seq']      for p in old_plan}

    uatrows = df[df['Phase'].astype(str).str.strip().str.upper() == 'UAT']
    completed_pairs = set()
    for _, r in uatrows.iterrows():
        cs = str(r.get('Completed Script') or '').lower()
        if 'completed' not in cs: continue
        raw_tid = str(r.get('Test ID') or '').strip()
        label = COMP_NORM.get(raw_tid)
        if not label: continue
        tester = std_name(r.get('Tester Name'))
        if not tester: continue
        completed_pairs.add(tester + '|||' + label)

    plan_data = []
    for label, assigned in plan_assignment.items():
        done     = [t for t in assigned if t + '|||' + label in completed_pairs]
        not_done = [t for t in assigned if t + '|||' + label not in completed_pairs]
        n_done = len(done); n_assigned = len(assigned)
        pct = round(1000 * n_done / n_assigned) / 10 if n_assigned else 0
        plan_data.append({
            'seq': plan_seqs.get(label, ''), 'label': label,
            'assigned': assigned, 'done_list': done, 'not_done_list': not_done,
            'n_done': n_done, 'n_assigned': n_assigned, 'pct': pct
        })

    all_testers = sorted(set(t for v in plan_assignment.values() for t in v))
    plan_labels = list(plan_assignment.keys())
    tester_data = []
    for tester in all_testers:
        tests = {}; n_done = n_assigned = 0
        for label in plan_labels:
            if tester not in plan_assignment[label]: tests[label] = 'na'; continue
            n_assigned += 1
            done = (tester + '|||' + label) in completed_pairs
            tests[label] = 'done' if done else 'not_done'
            if done: n_done += 1
        pct = round(1000 * n_done / n_assigned) / 10 if n_assigned else 0
        tester_data.append({'name': tester, 'n_done': n_done, 'n_assigned': n_assigned, 'pct': pct, 'tests': tests})

    total_assigned  = sum(p['n_assigned'] for p in plan_data)
    total_completed = sum(p['n_done']     for p in plan_data)
    tests_started   = sum(1 for p in plan_data if p['n_done'] > 0)
    testers_active  = sum(1 for t in tester_data if t['n_done'] > 0)
    avg_tester_pct  = round(10 * sum(t['pct'] for t in tester_data) / len(tester_data)) / 10 if tester_data else 0
    overall_pct     = round(1000 * total_completed / total_assigned) / 10 if total_assigned else 0
    summary = {
        'overall_pct': overall_pct, 'total_completed': total_completed,
        'total_assigned': total_assigned, 'tests_started': tests_started,
        'total_tests': len(plan_data), 'testers_active': testers_active,
        'avg_tester_pct': avg_tester_pct, 'total_testers': len(tester_data)
    }
    print(f"  {overall_pct}% overall completion, {total_completed}/{total_assigned} tester-tests")

    # ── Inject data into HTML ─────────────────────────────────────────────────
    content = re.sub(r'const DEFECTS = \[.*?\];\nconst TOTAL',
        'const DEFECTS = ' + json.dumps(defects) + ';\nconst TOTAL', content, flags=re.DOTALL)

    content = re.sub(r'const PLAN_DATA\s*=\s*\[.*?\];\nconst TESTER_DATA',
        'const PLAN_DATA    = ' + json.dumps(plan_data) + ';\nconst TESTER_DATA', content, flags=re.DOTALL)

    content = re.sub(r'const TESTER_DATA\s*=\s*\[.*?\];\nconst SUMMARY',
        'const TESTER_DATA  = ' + json.dumps(tester_data) + ';\nconst SUMMARY', content, flags=re.DOTALL)

    content = re.sub(r'const SUMMARY\s*=\s*\{.*?\};',
        'const SUMMARY      = ' + json.dumps(summary) + ';', content, flags=re.DOTALL)

    # ── Timestamp ─────────────────────────────────────────────────────────────
    edt = datetime.now(timezone(timedelta(hours=-4)))
    stamp = edt.strftime('%-B %-d, %Y · %-I:%M %p EDT')
    content = re.sub(r'<span id="refresh-stamp">.*?</span>',
        f'<span id="refresh-stamp">As of {stamp}</span>', content)
    content = re.sub(r'Generated \w+ \d+, \d+ · \d+:\d+ [AP]M EDT',
        f'Generated {stamp}', content)
    print(f"  Timestamp: {stamp}")

    # ── Write output ──────────────────────────────────────────────────────────
    with open(OUTPUT_FILE, 'w') as f:
        f.write(content)

    print(f"\n✓ Built: {OUTPUT_FILE}")
    print(f"  Commit and push to GitHub — Netlify will deploy automatically.\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 build.py <path_to_export.xlsx>")
        print("Example: python3 build.py ~/Downloads/o9_UAT_15.xlsx")
        sys.exit(1)
    build(sys.argv[1])
