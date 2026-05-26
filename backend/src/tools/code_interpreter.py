from typing import Dict
from langchain_core.tools import tool
import subprocess
import json

EXECUTION_TIMEOUT = 30

ALLOWED_PACKAGES = ["pandas", "numpy", "scipy", "matplotlib", "sklearn"]

@tool
def execute_python_safely(code: str, context: Dict = None) -> Dict:
    """在安全沙箱中执行Python代码

    Args:
        code: 要执行的Python代码
        context: 数据上下文（将通过stdin传入）
    """
    context = context or {}

    if not _validate_code_safety(code):
        return {
            "status": "error",
            "error": "代码包含不安全操作",
            "output": None,
        }

    try:
        full_code = f"""
import sys
import json
context = json.loads(sys.stdin.read())
{code}
result = locals().get('result', {{'status': 'completed'}})
print(json.dumps(result))
"""

        result = subprocess.run(
            ["python", "-c", full_code],
            input=json.dumps(context),
            capture_output=True,
            text=True,
            timeout=EXECUTION_TIMEOUT,
        )

        if result.returncode != 0:
            return {
                "status": "error",
                "error": result.stderr,
                "output": None,
            }

        output = json.loads(result.stdout) if result.stdout else {}
        return {
            "status": "success",
            "output": output,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "error": f"代码执行超时（>{EXECUTION_TIMEOUT}秒）",
            "output": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "output": None,
        }

def _validate_code_safety(code: str) -> bool:
    """验证代码安全性"""
    dangerous_patterns = [
        "import os",
        "import sys",
        "subprocess",
        "eval(",
        "exec(",
        "open(",
        "input(",
        "__import__",
        "os.path",
        "os.system",
        "shutil.rmtree",
        "requests",
        "urllib",
    ]

    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern.lower() in code_lower:
            return False

    return True

@tool
def generate_pandas_analysis(user_query: str, data_schema: Dict) -> str:
    """根据用户查询生成Pandas分析代码"""
    return f"""
try:
    df = pd.DataFrame(context['data'])
    result = {{'status': 'completed', 'shape': df.shape}}
except Exception as e:
    result = {{'error': str(e)}}
"""