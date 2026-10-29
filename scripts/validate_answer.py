#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""答卷自检：结构、题号完整性、空值检查。

用法：
    python validate_answer.py 答案.json [题目.json]
"""
import json
import sys

CANNOT = "该需求不能直接转换为FOFA搜索语句"


try:  # Windows 控制台默认 GBK，避免中文/emoji 输出报错
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def load(path: str):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    answer = load(sys.argv[1])
    problems = []

    for key in ("选手名称", "参赛包编号", "答案"):
        if key not in answer:
            problems.append(f"缺少顶层字段: {key}")
    items = answer.get("答案", [])
    ids = [it.get("题号") for it in items]

    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        problems.append(f"题号重复: {dup}")

    for it in items:
        q = it.get("查询语句")
        if q is None or not str(q).strip():
            problems.append(f"查询语句为空: {it.get('题号')}")
        elif q != CANNOT and ("\n" in q or "```" in q):
            problems.append(f"查询语句含换行/Markdown: {it.get('题号')}")

    if len(sys.argv) > 2:
        questions = [q["题号"] for q in load(sys.argv[2])]
        missing = [i for i in questions if i not in set(ids)]
        extra = [i for i in ids if i not in set(questions)]
        if missing:
            problems.append(f"缺题: {missing}")
        if extra:
            problems.append(f"未知题号: {extra}")
        if len(questions) != len(ids):
            problems.append(f"数量不一致: 题目 {len(questions)} / 答案 {len(ids)}")
        if ids != questions:
            problems.append("题号顺序与题目集不一致（多数平台可接受，但建议对齐）")

    if problems:
        print("❌ 校验未通过：")
        for p in problems:
            print(" -", p)
        return 1

    print(f"✅ 校验通过：{len(ids)} 题，选手={answer['选手名称']}，参赛包={answer['参赛包编号']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
