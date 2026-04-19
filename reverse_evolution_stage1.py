#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path
from statistics import mean

WORKSPACE = Path(r"C:\Users\kevin\.openclaw\workspace")
OUTDIR = WORKSPACE / "mx_data" / "output"
ARCHIVE = WORKSPACE / "stock_archive"
ARCHIVE.mkdir(parents=True, exist_ok=True)

DATES = [
    "2026-04-17", "2026-04-16", "2026-04-15", "2026-04-14", "2026-04-13",
    "2026-04-10", "2026-04-09", "2026-04-08", "2026-04-07", "2026-04-06"
]


def parse_num(text):
    if text is None:
        return None
    s = str(text).strip().replace(',', '')
    if not s:
        return None
    mult = 1.0
    if '亿' in s:
        mult = 1e8
        s = s.replace('亿', '')
    elif '万' in s:
        mult = 1e4
        s = s.replace('万', '')
    s = re.sub(r'[^0-9+\-.]', '', s)
    if s in {'', '-', '.', '+', '+.', '-.'}:
        return None
    try:
        return float(s) * mult
    except Exception:
        return None


def is_main_board(code):
    code = str(code).strip()
    return re.fullmatch(r'(60\d{4}|00\d{4})', code) is not None


def load_csv(path):
    with open(path, 'r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def pick_col(row, hints):
    for key in row.keys():
        if all(h in key for h in hints):
            return key
    return None


def score_row(row):
    code_col = pick_col(row, ['代码']) or '代码'
    name_col = pick_col(row, ['名称']) or '名称'
    pct_col = pick_col(row, ['涨跌'])
    inflow_col = pick_col(row, ['主力净流入'])
    ddx_col = pick_col(row, ['DDX'])
    ddy_col = pick_col(row, ['DDY'])
    ddz_col = pick_col(row, ['DDZ'])
    turnover_col = pick_col(row, ['换手'])
    ratio_col = pick_col(row, ['量比'])

    code = str(row.get(code_col, '')).strip()
    name = str(row.get(name_col, '')).strip()
    if not is_main_board(code) or 'ST' in name.upper():
        return None

    pct = parse_num(row.get(pct_col)) if pct_col else None
    inflow = parse_num(row.get(inflow_col)) if inflow_col else None
    ddx = parse_num(row.get(ddx_col)) if ddx_col else None
    ddy = parse_num(row.get(ddy_col)) if ddy_col else None
    ddz = parse_num(row.get(ddz_col)) if ddz_col else None
    turnover = parse_num(row.get(turnover_col)) if turnover_col else None
    ratio = parse_num(row.get(ratio_col)) if ratio_col else None

    score = 0.0
    tags = []
    if inflow and inflow > 3e7:
        score += min(inflow / 1e8, 18)
        tags.append('主力净流入')
    if ddx and ddx > 0:
        score += min(ddx * 3, 14)
        tags.append('DDX+')
    if ddy and ddy > 0:
        score += min(ddy * 2, 14)
        tags.append('DDY+')
    if ddz and ddz > 2:
        score += min(ddz, 10)
        tags.append('DDZ+')
    if turnover and 3 <= turnover <= 20:
        score += min(turnover / 2, 10)
        tags.append('换手适中')
    if ratio and ratio >= 1.0:
        score += min(ratio * 2, 10)
        tags.append('量比+')
    if pct is not None and -2 <= pct <= 10:
        score += 8
        tags.append('涨跌幅窗口')

    return {
        'code': code,
        'name': name,
        'pct': pct,
        'inflow': inflow,
        'ddx': ddx,
        'ddy': ddy,
        'ddz': ddz,
        'turnover': turnover,
        'ratio': ratio,
        'score': round(score, 2),
        'tags': tags,
    }


def audit_date(dt):
    files = sorted(OUTDIR.glob(f'*{dt}*.csv'))
    reports = []
    for f in files[:12]:
        rows = load_csv(f)
        scored = []
        for row in rows:
            item = score_row(row)
            if item:
                scored.append(item)
        scored.sort(key=lambda x: x['score'], reverse=True)
        if scored:
            reports.append({
                'date': dt,
                'file': f.name,
                'count': len(scored),
                'avg_score': round(mean([x['score'] for x in scored]), 2),
                'top3': scored[:3],
            })
    return reports


def main():
    final = []
    for dt in DATES:
        final.extend(audit_date(dt))
    out_json = ARCHIVE / 'reverse_evolution_stage1_20260419.json'
    out_txt = ARCHIVE / 'reverse_evolution_stage1_20260419.txt'
    out_json.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = []
    for rep in final:
        lines.append(f"DATE | {rep['date']} | FILE | {rep['file']} | count={rep['count']} avg={rep['avg_score']}")
        for i, s in enumerate(rep['top3'], 1):
            lines.append(f"TOP{i} | {s['code']} {s['name']} | score={s['score']} | tags={','.join(s['tags'])}")
        lines.append('')
    out_txt.write_text('\n'.join(lines), encoding='utf-8')
    print(out_txt)
    print(out_json)


if __name__ == '__main__':
    main()
