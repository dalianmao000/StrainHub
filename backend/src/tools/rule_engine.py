from typing import List, Dict
from langchain_core.tools import tool
import os

@tool
def validate_compliance(data: Dict, rules: List[Dict] = None) -> Dict:
    """使用规则引擎校验数据合规性

    Args:
        data: 待校验数据
        rules: 规则列表，如果为None则使用默认规则
    """
    if rules is None:
        rules = _load_default_rules()

    violations = []
    for rule in rules:
        result = _evaluate_rule(data, rule)
        if not result["passed"]:
            violations.append({
                "rule_id": rule.get("id", "unknown"),
                "rule_name": rule.get("name", "Unnamed Rule"),
                "message": result["message"],
                "severity": rule.get("severity", "warning"),
            })

    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "total_rules_checked": len(rules),
    }

def _load_default_rules() -> List[Dict]:
    """加载默认合规规则"""
    return [
        {
            "id": "BR-001",
            "name": "菌株名称校验",
            "description": "菌株名称必须在批准名单内",
            "severity": "error",
            "condition": "strain_name in approved_strains",
        },
        {
            "id": "BR-002",
            "name": "活菌数下限",
            "description": "活菌数必须>=标称值的95%",
            "severity": "error",
            "condition": "viable_count >= declared_count * 0.95",
        },
    ]

def _evaluate_rule(data: Dict, rule: Dict) -> Dict:
    """评估单条规则"""
    condition = rule.get("condition", "")

    try:
        if "strain_name" in condition and "approved_strains" in condition:
            strain_name = data.get("strain_name", "")
            approved_strains = data.get("approved_strains", [])
            if approved_strains and strain_name not in approved_strains:
                return {
                    "passed": False,
                    "message": f"菌株'{strain_name}'不在批准名单内"
                }

        if "viable_count" in condition and "declared_count" in condition:
            viable = data.get("viable_count", 0)
            declared = data.get("declared_count", 0)
            if viable < declared * 0.95:
                return {
                    "passed": False,
                    "message": f"活菌数{viable}低于要求（标称值{declared}的95%）"
                }

        return {"passed": True, "message": "规则通过"}

    except Exception as e:
        return {"passed": False, "message": f"规则评估错误: {str(e)}"}

@tool
def load_compliance_rules(category: str = "iso22000") -> List[Dict]:
    """加载指定类别的合规规则

    Args:
        category: 规则类别（iso22000, cgmp, kosher, hala等）
    """
    # 简化实现：返回默认规则
    return _load_default_rules()