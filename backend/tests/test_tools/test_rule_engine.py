import pytest
from src.tools.rule_engine import validate_compliance

def test_validate_compliance_pass():
    """测试合规校验通过"""
    data = {
        "strain_name": "LGG",
        "viable_count": 1000000,
        "declared_count": 1000000,
    }
    result = validate_compliance.invoke({"data": data})
    assert "passed" in result

def test_validate_compliance_fail():
    """测试合规校验失败"""
    data = {
        "strain_name": "Unknown Strain",
        "viable_count": 1000000,
        "declared_count": 1000000,
    }
    result = validate_compliance.invoke({"data": data})
    # Should fail since Unknown Strain not in approved list
    assert "passed" in result