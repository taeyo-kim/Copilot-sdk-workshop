"""
extras_usage.py — Optional terminal logger for token / cost usage.

Not part of the main tutorial. Enable it for a livestream demo with:

    export SHOW_USAGE=1

When unset, importing this module is a no-op — nothing is patched,
nothing is printed, and learners can ignore the file entirely.

When set, it transparently wraps CopilotClient.create_session so every
session prints per-call usage data to the terminal as the agent runs.
"""

import functools
import os

if os.environ.get("SHOW_USAGE"):
    from copilot import CopilotClient

    _totals = {"input": 0, "output": 0, "calls": 0, "cost": 0.0}

    def _on_event(event):
        name = event.type.value if hasattr(event.type, "value") else str(event.type)
        if name != "assistant.usage":
            return
        d = event.data
        inp = int(getattr(d, "input_tokens", 0) or 0)
        out = int(getattr(d, "output_tokens", 0) or 0)
        _totals["input"] += inp
        _totals["output"] += out
        _totals["calls"] += 1
        _totals["cost"] += float(getattr(d, "cost", 0) or 0)
        print(
            f"\n[usage] call #{_totals['calls']} "
            f"model={getattr(d, 'model', '?')} in={inp} out={out} "
            f"| totals in={_totals['input']} out={_totals['output']} "
            f"cost=${_totals['cost']:.4f}",
            flush=True,
        )

    _original = CopilotClient.create_session

    @functools.wraps(_original)
    async def _patched(self, *args, **kwargs):
        session = await _original(self, *args, **kwargs)
        session.on(_on_event)
        return session

    CopilotClient.create_session = _patched
    print("[extras_usage] enabled — token usage will be printed to the terminal", flush=True)
