"""
tools.py — Tool functions for PhysicsBuddy Agent
Tools handle what the KB cannot: current date/time and arithmetic calculations.
RULE: Tools NEVER raise exceptions — they always return error strings on failure.
"""

import math
from datetime import datetime


def get_datetime_tool() -> str:
    """Returns current date, time, and day of week. Useful for study schedule queries."""
    try:
        now = datetime.now()
        return (
            f"Current date: {now.strftime('%A, %d %B %Y')}. "
            f"Current time: {now.strftime('%I:%M %p')}."
        )
    except Exception as e:
        return f"[datetime tool error: {str(e)}]"


def calculator_tool(expression: str) -> str:
    """
    Safely evaluates a physics arithmetic expression.
    Supports: +, -, *, /, **, sqrt, sin, cos, tan, log, pi, e
    Returns a string result or an error message.
    """
    try:
        # Safe math environment — no builtins, only math functions
        safe_env = {
            "__builtins__": {},
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "pi": math.pi,
            "e": math.e,
            "abs": abs,
            "pow": pow,
        }
        result = eval(expression, safe_env)  # noqa: S307
        return f"Calculator result for '{expression}' = {result:.6g}"
    except ZeroDivisionError:
        return "[calculator error: division by zero]"
    except Exception as e:
        return f"[calculator error: {str(e)}]"


def run_tool(tool_name: str, tool_input: str) -> str:
    """
    Dispatcher for all tools. Called by tool_node.
    Always returns a string — never raises an exception.
    """
    try:
        if tool_name == "datetime":
            return get_datetime_tool()
        elif tool_name == "calculator":
            return calculator_tool(tool_input)
        else:
            return f"[tool error: unknown tool '{tool_name}']"
    except Exception as e:
        return f"[tool dispatcher error: {str(e)}]"
