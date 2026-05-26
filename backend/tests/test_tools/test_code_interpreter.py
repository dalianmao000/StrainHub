import pytest
from src.tools.code_interpreter import execute_python_safely

def test_code_interpreter_safety():
    """测试代码解释器安全检查"""
    result = execute_python_safely.invoke({
        "code": "import os",
        "context": {},
    })
    assert result["status"] == "error"

def test_code_interpreter_valid():
    """测试代码解释器有效执行"""
    result = execute_python_safely.invoke({
        "code": "result = {'value': 42}",
        "context": {},
    })
    assert result["status"] == "success"
    assert result["output"]["value"] == 42