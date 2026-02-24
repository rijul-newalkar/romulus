"""Tests for built-in agent tools (get_time, get_system_info, calculate)."""

import platform
import re
from datetime import datetime

import pytest

from romulus.agent.tools import calculate, get_system_info, get_time


# ---------------------------------------------------------------------------
# get_time
# ---------------------------------------------------------------------------

class TestGetTime:
    async def test_returns_valid_time(self):
        result = await get_time()
        assert isinstance(result, str)
        # Should match YYYY-MM-DD HH:MM:SS format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed.year >= 2024

    async def test_returns_current_time(self):
        before = datetime.now().replace(microsecond=0)
        result = await get_time()
        after = datetime.now().replace(microsecond=0)

        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert before <= parsed <= after

    async def test_format_consistency(self):
        result = await get_time()
        # Pattern: 4-digit year, 2-digit month, 2-digit day, space, HH:MM:SS
        assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", result)


# ---------------------------------------------------------------------------
# get_system_info
# ---------------------------------------------------------------------------

class TestGetSystemInfo:
    async def test_returns_string(self):
        result = await get_system_info()
        assert isinstance(result, str)
        assert len(result) > 0

    async def test_contains_os(self):
        result = await get_system_info()
        assert "OS:" in result
        assert platform.system() in result

    async def test_contains_python_version(self):
        result = await get_system_info()
        assert "Python:" in result
        assert platform.python_version() in result

    async def test_contains_host(self):
        result = await get_system_info()
        assert "Host:" in result

    async def test_contains_arch(self):
        result = await get_system_info()
        assert "Arch:" in result
        assert platform.machine() in result


# ---------------------------------------------------------------------------
# calculate — valid expressions
# ---------------------------------------------------------------------------

class TestCalculateValid:
    async def test_addition(self):
        assert await calculate("2 + 3") == "5"

    async def test_subtraction(self):
        assert await calculate("10 - 4") == "6"

    async def test_multiplication(self):
        assert await calculate("6 * 7") == "42"

    async def test_division(self):
        assert await calculate("10 / 4") == "2.5"

    async def test_modulo(self):
        assert await calculate("17 % 5") == "2"

    async def test_power(self):
        assert await calculate("2 ** 10") == "1024"

    async def test_negative(self):
        assert await calculate("-5 + 3") == "-2"

    async def test_float(self):
        assert await calculate("3.14 * 2") == "6.28"

    async def test_complex_expression(self):
        result = await calculate("(2 + 3) * 4 - 1")
        assert result == "19"

    async def test_nested_parens(self):
        result = await calculate("((2 + 3) * (4 - 1))")
        assert result == "15"

    async def test_integer_result(self):
        result = await calculate("10 / 2")
        assert result == "5.0"  # Python truediv returns float

    async def test_whitespace_handling(self):
        result = await calculate("  2 + 2  ")
        assert result == "4"

    async def test_zero(self):
        assert await calculate("0") == "0"

    async def test_large_number(self):
        result = await calculate("999999 * 999999")
        assert result == "999998000001"


# ---------------------------------------------------------------------------
# calculate — dangerous expressions rejected
# ---------------------------------------------------------------------------

class TestCalculateDangerous:
    async def test_import_os(self):
        result = await calculate("import os")
        assert "Error" in result

    async def test_dunder_import(self):
        result = await calculate("__import__('os')")
        assert "Error" in result

    async def test_exec(self):
        result = await calculate("exec('print(1)')")
        assert "Error" in result

    async def test_eval(self):
        result = await calculate("eval('2+2')")
        assert "Error" in result

    async def test_open_file(self):
        result = await calculate("open('/etc/passwd')")
        assert "Error" in result

    async def test_system_command(self):
        result = await calculate("os.system('ls')")
        assert "Error" in result

    async def test_string_literal(self):
        result = await calculate("'hello'")
        assert "Error" in result

    async def test_list_comprehension(self):
        result = await calculate("[x for x in range(10)]")
        assert "Error" in result

    async def test_variable_name(self):
        result = await calculate("x + 1")
        assert "Error" in result

    async def test_function_call(self):
        result = await calculate("print(42)")
        assert "Error" in result

    async def test_division_by_zero(self):
        result = await calculate("1 / 0")
        assert "Error" in result

    async def test_empty_expression(self):
        result = await calculate("")
        assert "Error" in result
