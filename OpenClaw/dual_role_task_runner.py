from pathlib import Path
from datetime import datetime
import sys

ROOT = Path(r"C:\Users\kevin\Desktop\OpenClaw")
OUT = ROOT / "双角色任务样板.md"
PROGRESS = ROOT / "治理进度.md"


def main():
    task = " ".join(sys.argv[1:]).strip() or "待定义任务"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"# 双角色任务样板\n\n时间：{now}\n任务：{task}\n\n## 【旺财的主人】\n- 任务定义：\n- 验收标准：\n- 风险边界：\n\n## 【旺财】\n- 执行动作：\n- 交付物：\n- 证据链：\n\n## 【旺财的主人】验收\n- 是否通过：\n- 验收结论：\n- 下一步：\n"
    OUT.write_text(content, encoding="utf-8")

    progress = f"时间：{now}\n阶段：双角色治理\n当前状态：已具备协议、机制、模板、检查器、任务样板脚本\n下一关注点：防止治理空转，开始用真实任务检验\n\n"
    if PROGRESS.exists():
        old = PROGRESS.read_text(encoding="utf-8", errors="ignore")
        PROGRESS.write_text(progress + old, encoding="utf-8")
    else:
        PROGRESS.write_text(progress, encoding="utf-8")

    print(OUT)
    print(PROGRESS)
    print("ok")

if __name__ == "__main__":
    main()
