from pathlib import Path
import json
from datetime import datetime

ROOT = Path(r"C:\Users\kevin\Desktop\OpenClaw")
FILES = {
    "角色协议": {"file": "角色协议.md", "keywords": ["Kevin", "旺财的主人", "旺财"]},
    "运行机制": {"file": "运行机制.md", "keywords": ["默认发言顺序", "任务分发机制", "证据链"]},
    "任务分发机制": {"file": "任务分发机制.md", "keywords": ["不清楚归主人", "升级给", "旺财"]},
    "证据链模板": {"file": "证据链模板.md", "keywords": ["任务目标", "执行动作", "证据位置"]},
    "验收模板": {"file": "验收模板.md", "keywords": ["任务名称", "验收结论", "下一步处理"]},
    "运行检查清单": {"file": "运行检查清单.md", "keywords": ["角色串位", "证据链", "验收结论"]},
    "真实任务试运行机制": {"file": "真实任务试运行机制.md", "keywords": ["试运行流程", "验收模板", "运行检查清单"]},
    "双角色协议": {"file": "双角色协议.md", "keywords": ["审问官", "参谋长", "发言格式"]},
    "问题清单": {"file": "问题清单.txt", "keywords": ["第一组", "第二组", "第五组"]},
    "治理进度": {"file": "治理进度.md", "keywords": ["当前状态", "下一关注点"]},
    "治理完成标准": {"file": "治理完成标准.md", "keywords": ["够用", "真实任务闭环", "成熟度判断"]},
    "治理阶段验收": {"file": "治理阶段验收.md", "keywords": ["基本通过", "剩余关键项"]},
}


def inspect_file(path: Path, keywords):
    if not path.exists():
        return {"exists": False, "empty": None, "missing_keywords": keywords, "level": "missing"}
    text = path.read_text(encoding="utf-8", errors="ignore")
    empty = len(text.strip()) == 0
    missing_keywords = [k for k in keywords if k not in text]
    if empty:
        level = "empty"
    elif missing_keywords:
        level = "warning"
    else:
        level = "ok"
    return {"exists": True, "empty": empty, "missing_keywords": missing_keywords, "level": level}


def maturity(summary):
    if summary["missing"] or summary["empty"]:
        return "未就绪"
    if summary["warning"]:
        return "可运行但未稳定"
    return "基本成熟"


def main():
    status = {
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root": str(ROOT),
        "files": [],
        "summary": {"ok": 0, "warning": 0, "empty": 0, "missing": 0},
    }
    lines = [f"检查时间: {status['checked_at']}", f"根目录: {ROOT}", ""]
    for label, meta in FILES.items():
        path = ROOT / meta["file"]
        result = inspect_file(path, meta["keywords"])
        item = {"label": label, "file": meta["file"], "path": str(path), **result}
        status["files"].append(item)
        status["summary"][result["level"]] += 1
        lines.append(f"[{result['level'].upper()}] {label} -> {meta['file']}")
        if result["exists"] and result["missing_keywords"]:
            lines.append(f"  缺少关键字段: {', '.join(result['missing_keywords'])}")
        if result["exists"] and result["empty"]:
            lines.append("  文件为空")
    status["maturity"] = maturity(status["summary"])
    lines.append("")
    lines.append("汇总:")
    for k, v in status["summary"].items():
        lines.append(f"- {k}: {v}")
    lines.append(f"- maturity: {status['maturity']}")

    json_path = ROOT / "governance_status.json"
    md_path = ROOT / "治理文件索引.md"
    json_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(md_path)
    print(json_path)
    print(json.dumps({"summary": status["summary"], "maturity": status["maturity"]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
