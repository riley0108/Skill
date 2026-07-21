"""verified_run — 給自己的自動化加上「驗證迴圈 + budget」的最小工具。

核心一句話：讓「完成」變成「被檢查過的宣稱」，而不是 worker 自己說了算。
worker 產出候選 → checker 依固定 rubric 打分 → 沒過帶 feedback 重試 → budget
花完就 escalate（回 ok=False 交給人/告警），不會無限重試燒錢。

改編自 hardness1020/awesome-agent-architecture §21（MIT）＋ Claude Code Workflow
的 verify stage 概念。純標準庫、零相依，可直接塞進 ~/kuba 的任何腳本。

用法：
    from verified_run import verified_run, needs_all, human_escalate

    def worker(prompt: str) -> str:
        # 你的產出邏輯：呼叫 LLM、跑 stock.py、組行銷文案…
        return generate(prompt)

    def checker(task: str, out: str) -> dict:
        # 回 {"passed": bool, "reason": str}
        return needs_all(out, must_contain=["資料時間", "約延遲15分"])

    r = verified_run("查 2330 股價", worker, checker, budget=2)
    if r["ok"]:
        deliver(r["output"])          # 通過才發出去
    else:
        human_escalate(r)             # budget 花完：告警給人，附完整嘗試紀錄
"""
from __future__ import annotations
import time
from typing import Callable


def verified_run(task: str,
                 worker: Callable[[str], str],
                 checker: Callable[[str, str], dict],
                 budget: int = 2,
                 max_seconds: float | None = None) -> dict:
    """跑 worker 直到 checker 通過，或 budget（次數 / 時間）用完。

    - worker(prompt) -> 候選輸出文字
    - checker(task, output) -> {"passed": bool, "reason": str}  ← 要是「另一個」判斷，別讓 worker 自己評自己
    - budget: 硬上限（嘗試次數）。range() 就是天花板，第 budget+1 次不會發生
    - max_seconds: 選用的 wall-clock 上限
    回 {"ok", "output", "attempts"}；ok=False = 該 escalate 給人。
    """
    feedback = ""
    attempts = []
    t0 = time.monotonic()
    for n in range(1, budget + 1):
        if max_seconds is not None and time.monotonic() - t0 > max_seconds:
            attempts.append({"attempt": n, "passed": False, "reason": f"wall-clock budget {max_seconds}s 花完"})
            break
        out = worker(task + feedback)                       # 內層 agent loop
        verdict = checker(task, out)                        # 獨立 checker（固定 rubric）
        attempts.append({"attempt": n, "passed": verdict["passed"], "reason": verdict["reason"]})
        if verdict["passed"]:
            return {"ok": True, "output": out, "attempts": attempts}
        # 失敗的評語是「資料」——帶進下一次重試，讓第二次知道第一次錯在哪
        feedback = (f"\n\n[上一次被退回]\n產出：\n{out}\n"
                    f"退回原因：{verdict['reason']}\n請修正後重新產出。")
    return {"ok": False, "output": None, "attempts": attempts}   # budget 花完：escalate


# ---------- 現成 checker 積木（rule-based，零相依） ----------

def needs_all(out: str, must_contain: list[str]) -> dict:
    """輸出必須包含所有指定字串（例如股價回覆必含「資料時間」「約延遲15分」）。"""
    missing = [s for s in must_contain if s not in (out or "")]
    if missing:
        return {"passed": False, "reason": f"缺少必要內容：{missing}"}
    return {"passed": True, "reason": "含全部必要內容"}


def forbids_any(out: str, must_not_contain: list[str]) -> dict:
    """輸出不得包含任何禁字（例如翻譯不該殘留原文標記、回覆不該出現佔位符）。"""
    hit = [s for s in must_not_contain if s in (out or "")]
    if hit:
        return {"passed": False, "reason": f"出現禁止內容：{hit}"}
    return {"passed": True, "reason": "無禁止內容"}


def combine(*checks: dict) -> dict:
    """把多個 checker 結果 AND 起來（全過才過）。"""
    for c in checks:
        if not c["passed"]:
            return c
    return {"passed": True, "reason": "全部檢查通過"}


def llm_checker(rubric: str, ask: Callable[[str], str]) -> Callable[[str, str], dict]:
    """用 LLM 當 grader：ask(prompt)->文字，回 PASS/FAIL 開頭 + 一句理由。
    ⚠️ 要用「乾淨 context」的另一個呼叫，別跟 worker 共用對話，否則等於自己評自己。
    對抗式：rubric 裡叫它「盡量挑錯，拿不準就 FAIL」，避免橡皮圖章。"""
    def check(task: str, output: str) -> dict:
        prompt = ("你是嚴格審查員。依 rubric 給下面產出打分，不要幫它修。\n"
                  "盡量挑毛病；拿不準就給 FAIL。\n"
                  f"Rubric：{rubric}\n任務：{task}\n產出：\n{output}\n"
                  "第一個字回 PASS 或 FAIL，接著一句話理由。")
        text = (ask(prompt) or "").strip()
        word, _, reason = text.partition(" ")
        return {"passed": word.upper().startswith("PASS"), "reason": reason.strip() or text}
    return check


def human_escalate(result: dict, notify: Callable[[str], None] | None = None) -> None:
    """budget 花完時的預設升級：把完整嘗試紀錄丟給人（預設 print，可換成 Telegram 告警）。"""
    lines = ["⚠️ verified_run budget 花完，未通過驗證，需人工介入："]
    for a in result.get("attempts", []):
        lines.append(f"  第{a['attempt']}次 passed={a['passed']} — {a['reason']}")
    msg = "\n".join(lines)
    (notify or print)(msg)


if __name__ == "__main__":
    # 示範：模擬一個「第一次忘了加延遲註記、第二次補上」的股價回覆
    calls = {"n": 0}
    def demo_worker(prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            return "台積電 2330 收盤 1085 元"                       # 缺時間與延遲註記 → 會被退
        return "台積電 2330 收盤 1085 元（資料時間 13:30，約延遲15分）"
    def demo_checker(task, out):
        return needs_all(out, must_contain=["資料時間", "約延遲15分"])
    r = verified_run("查 2330", demo_worker, demo_checker, budget=2)
    print("ok =", r["ok"])
    print("output =", r["output"])
    for a in r["attempts"]:
        print(" ", a)
