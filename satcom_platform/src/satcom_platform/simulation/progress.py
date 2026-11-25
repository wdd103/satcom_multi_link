"""Shared, throttled progress reporting for the worker, web UI and STK."""
from __future__ import annotations

import time
from collections.abc import Callable


STAGES = {
    "PREPARING": (0, 2, "准备输入"),
    "CONNECTING": (2, 5, "连接 STK"),
    "RF_ENVIRONMENT": (5, 8, "配置大气传播模型"),
    "BUILDING": (8, 25, "创建场景对象"),
    "COMPUTING": (25, 45, "计算航空器几何"),
    "GATEWAY_GEOMETRY": (45, 52, "计算网关几何"),
    "BODY_MASK": (52, 55, "计算机体遮挡"),
    "COMMUNICATIONS": (55, 85, "计算链路预算"),
    "INTERFERENCE": (85, 95, "计算下行同频干扰"),
    "EXPORTING": (95, 99, "导出并保存结果"),
    "COMPLETE": (100, 100, "运行完成"),
}


class RunProgress:
    """Percentages weight stages; counts within each stage track actual work.

    These are work estimates, not elapsed-time estimates. A failed STK display
    must not interrupt simulation or prevent progress from reaching the web UI.
    """

    def __init__(self, status: dict, persist: Callable[[], None], *, clock=time.monotonic):
        self.status, self.persist, self.clock = status, persist, clock
        self.root = None
        self.last_emit = float("-inf")
        self.previous_percent = 0.0

    def attach_stk(self, root) -> None:
        self.root = root
        try:
            root.ExecuteCommand("MessageWindow / Raise")
        except Exception as exc:
            self.status["stk_progress_error"] = str(exc)
        self.emit(force=True)

    def stage(self, name: str, total: int = 1, detail: str = "") -> None:
        self.status["phase"] = name
        self.status["progress"] = {"stage": name, "label": STAGES[name][2],
                                   "completed": 0, "total": max(1, total), "detail": detail}
        self.update(0, detail, force=True)

    def update(self, completed: int, detail: str = "", *, force: bool = False) -> None:
        progress = self.status["progress"]
        progress["completed"] = max(0, min(completed, progress["total"]))
        progress["detail"] = detail
        low, high, _ = STAGES[progress["stage"]]
        percent = low + (high - low) * progress["completed"] / progress["total"]
        self.previous_percent = max(self.previous_percent, percent)
        progress["percent"] = round(self.previous_percent, 1)
        self.emit(force=force or completed == progress["total"])

    def emit(self, *, force: bool = False) -> None:
        now = self.clock()
        if not force and now - self.last_emit < 1:
            return
        self.last_emit = now
        progress = self.status.get("progress", {})
        text = (f"[SATCOM {self.status.get('run_id', '')}] {progress.get('percent', 0):.1f}% | "
                f"{progress.get('label', '')} | {progress.get('completed', 0)}/{progress.get('total', 1)} | "
                f"{progress.get('detail', '')}")
        if self.root is not None:
            try:
                # Connect strings cannot contain embedded quotes or newlines.
                safe = text.replace('"', "'").replace("\r", " ").replace("\n", " ")
                self.root.ExecuteCommand(f'Message / {4 if self.status["state"] == "FAILED" else 1} "{safe}"')
            except Exception as exc:
                self.status["stk_progress_error"] = str(exc)
                self.root = None
        self.persist()

    def fail(self, message: str) -> None:
        self.status.update(state="FAILED", error=message)
        if "progress" in self.status:
            self.status["progress"].update(label="运行失败", detail=message)
        self.emit(force=True)

    def complete(self) -> None:
        self.status.update(state="COMPLETE", phase="COMPLETE")
        self.status["progress"] = {"stage": "COMPLETE", "label": STAGES["COMPLETE"][2],
                                   "completed": 1, "total": 1, "detail": "场景及结果文件已保存"}
        self.update(1, "场景及结果文件已保存", force=True)
