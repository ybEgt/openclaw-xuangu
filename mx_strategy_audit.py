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


def find_col(row, keywords):
    for k in row.keys():
        if all(word in k for word in keywords):
            return k
    return None


def analyze_csv(path):
    rows = load_csv(path)
    if not rows:
        return None
    sample = rows[0]
    code_col = find_col(sample, ['代码']) or '代码'
    name_col = find_col(sample, ['名称']) or '名称'
    pct_col = find_col(sample, ['涨跌'])
    inflow_col = find_col(sample, ['主力净流入'])
    ddx_col = find_col(sample, ['DDX'])
    ddy_col = find_col(sample, ['DDY'])
    ddz_col = find_col(sample, ['DDZ'])
    turnover_col = find_col(sample, ['换手'])
    ratio_col = find_col(sample, ['量比'])
    cap_col = find_col(sample, ['流通市值'])

    clean = []
    for r in rows:
        code = str(r.get(code_col, '')).strip()
        name = str(r.get(name_col, '')).strip()
        if not is_main_board(code):
            continue
        if 'ST' in name.upper():
            continue
        item = {
            'code': code,
            'name': name,
            'pct': parse_num(r.get(pct_col)) if pct_col else None,
            'inflow': parse_num(r.get(inflow_col)) if inflow_col else None,
            'ddx': parse_num(r.get(ddx_col)) if ddx_col else None,
            'ddy': parse_num(r.get(ddy_col)) if ddy_col else None,
            'ddz': parse_num(r.get(ddz_col)) if ddz_col else None,
            'turnover': parse_num(r.get(turnover_col)) if turnover_col else None,
            'ratio': parse_num(r.get(ratio_col)) if ratio_col else None,
            'cap': parse_num(r.get(cap_col)) if cap_col else None,
        }
        score = 0.0
        if item['inflow'] and item['inflow'] > 0:
            score += min(item['inflow'] / 1e8, 20)
        if item['ddx'] and item['ddx'] > 0:
            score += min(item['ddx'] * 3, 15)
        if item['ddy'] and item['ddy'] > 0:
            score += min(item['ddy'] * 2, 15)
        if item['ddz'] and item['ddz'] > 0:
            score += min(item['ddz'], 10)
        if item['turnover'] and 3 <= item['turnover'] <= 20:
            score += min(item['turnover'] / 2, 10)
        if item['ratio'] and item['ratio'] >= 0.8:
            score += min(item['ratio'] * 2, 10)
        if item['pct'] is not None and -2 <= item['pct'] <= 10:
            score += 10
        item['score'] = round(score, 2)
        clean.append(item)

    clean.sort(key=lambda x: x['score'], reverse=True)
    top3 = clean[:3]
    return {
        'file': str(path),
        'rows': len(rows),
        'main_board_rows': len(clean),
        'avg_score': round(mean([x['score'] for x in clean]), 2) if clean else 0,
        'top3': top3,
    }


def main():
    patterns = [
        '*2026-04-17*.csv',
        '*2026-04-16*.csv',
        '*2026-04-15*.csv',
        '*2026-04-14*.csv',
        '*2026-04-13*.csv',
        '*2026-04-10*.csv',
    ]
    files = []
    for p in patterns:
        files.extend(sorted(OUTDIR.glob(p)))
    files = [f for f in files if f.is_file()]

    reports = []
    for f in files[:20]:
        try:
            rep = analyze_csv(f)
            if rep:
                reports.append(rep)
        except Exception as e:
            reports.append({'file': str(f), 'error': str(e)})

    out_json = ARCHIVE / 'mx_strategy_audit_20260419.json'
    out_txt = ARCHIVE / 'mx_strategy_audit_20260419.txt'
    out_json.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = []
    for rep in reports:
        if 'error' in rep:
            lines.append(f"ERR | {rep['file']} | {rep['error']}")
            continue
        lines.append(f"FILE | {rep['file']}")
        lines.append(f"ROWS | total={rep['rows']} main_board={rep['main_board_rows']} avg_score={rep['avg_score']}")
        for i, s in enumerate(rep['top3'], 1):
            lines.append(f"TOP{i} | {s['code']} {s['name']} | score={s['score']} pct={s['pct']} inflow={s['inflow']} ddx={s['ddx']} ddy={s['ddy']} ddz={s['ddz']} turnover={s['turnover']} ratio={s['ratio']}")
        lines.append('')
    out_txt.write_text('\n'.join(lines), encoding='utf-8')
    print(out_txt)
    print(out_json)


if __name__ == '__main__':
    main()
