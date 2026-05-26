from typing import List, Dict, Optional
from langgraph import StateGraph, END
from src.agents.base import BaseAgent
from src.schemas.agents import QCState
from src.config import get_settings

settings = get_settings()

QC_AGENT_PROMPT = """你是一个质量控制智能助手，专注于产品质量控制报告生成和合规性校验。

你的职责：
1. 质量控制报告生成 - 根据原始数据生成QC报告
2. 合规性校验 - 严格按照规则引擎验证产品指标
3. 版本对比分析 - 比较不同版本间的质量差异
4. 人工审核判断 - 根据规则判断是否需要人工审核

输出要求：
- 所有输出必须包含版本溯源（version_required=True）
- 涉及菌株名称、指标范围的数据必须通过规则引擎校验
- 不符合标准时标注为违规项（violation）
- 审核状态必须明确标注（pending_approval/approved/rejected）
"""


class QCAgent(BaseAgent):
    """质量控制Agent"""

    def __init__(self):
        super().__init__(
            name="qc_agent",
            state_schema=QCState,
            system_prompt=QC_AGENT_PROMPT,
        )

    def define_nodes(self, workflow: StateGraph) -> None:
        workflow.add_node("load_raw_data", self._load_raw_data)
        workflow.add_node("generate_draft_report", self._generate_draft_report)
        workflow.add_node("validate_compliance", self._validate_compliance)
        workflow.add_node("check_human_review_required", self._check_human_review_required)
        workflow.add_node("assign_reviewers", self._assign_reviewers)
        workflow.add_node("generate_pdf", self._generate_pdf)
        workflow.add_node("create_audit_log", self._create_audit_log)
        workflow.add_node("format_output", self._format_output)

    def define_edges(self, workflow: StateGraph) -> None:
        workflow.add_edge("load_raw_data", "generate_draft_report")
        workflow.add_edge("generate_draft_report", "validate_compliance")
        workflow.add_edge("validate_compliance", "check_human_review_required")

        workflow.add_conditional_edges(
            "check_human_review_required",
            lambda s: "assign_reviewers" if s.get("human_review_required") else "generate_pdf",
        )

        workflow.add_edge("assign_reviewers", "format_output")
        workflow.add_edge("generate_pdf", "create_audit_log")
        workflow.add_edge("create_audit_log", "format_output")
        workflow.add_edge("format_output", END)

    def get_entry_point(self) -> str:
        return "load_raw_data"

    async def _load_raw_data(self, state: QCState) -> QCState:
        """加载原始质量控制数据"""
        # Placeholder - actual implementation would load from database or file
        raw_data = state.get("raw_data", {})
        return {"raw_data": raw_data, **state}

    async def _generate_draft_report(self, state: QCState) -> QCState:
        """生成草稿QC报告"""
        raw_data = state.get("raw_data", {})
        user_input = state.get("user_input", "")

        # Generate draft report based on raw data
        draft_report = f"QC Report Draft - Based on data: {raw_data.get('sample_id', 'Unknown')}"
        return {"draft_report": draft_report, **state}

    async def _validate_compliance(self, state: QCState) -> QCState:
        """校验合规性"""
        # Placeholder - actual implementation would validate against rules
        compliance_issues = []
        draft_report = state.get("draft_report", "")

        # Basic compliance check
        if not draft_report:
            compliance_issues.append({
                "type": "missing_report",
                "severity": "high",
                "message": "Draft report is empty"
            })

        return {"compliance_issues": compliance_issues, **state}

    async def _check_human_review_required(self, state: QCState) -> QCState:
        """检查是否需要人工审核"""
        compliance_issues = state.get("compliance_issues", [])

        # Determine if human review is required based on compliance issues
        high_severity_issues = [
            issue for issue in compliance_issues
            if issue.get("severity") == "high"
        ]

        human_review_required = len(high_severity_issues) > 0
        return {"human_review_required": human_review_required, **state}

    async def _assign_reviewers(self, state: QCState) -> QCState:
        """分配审核人员"""
        # Placeholder - actual implementation would assign reviewers based on rules
        # TODO: Replace with actual reviewer assignment logic
        reviewers = ["qc_reviewer_1", "qc_reviewer_2"]
        return {"reviewers": reviewers, **state}

    async def _generate_pdf(self, state: QCState) -> QCState:
        """生成PDF报告"""
        # Placeholder - actual implementation would generate PDF
        final_pdf = b"PDF placeholder - actual PDF content would be generated here"
        return {"final_pdf": final_pdf, **state}

    async def _create_audit_log(self, state: QCState) -> QCState:
        """创建审计日志"""
        from datetime import datetime

        audit_log = {
            "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
            "action": "qc_report_generated",
            "user_id": state.get("user_id", "system"),
            "session_id": state.get("session_id", ""),
            "compliance_issues_count": len(state.get("compliance_issues", [])),
            "status": "completed"
        }
        return {"audit_log": audit_log, **state}

    async def _format_output(self, state: QCState) -> QCState:
        """格式化最终输出"""
        output = {
            "user_input": state.get("user_input", ""),
            "draft_report": state.get("draft_report", ""),
            "compliance_issues": state.get("compliance_issues", []),
            "human_review_required": state.get("human_review_required", False),
            "reviewers": state.get("reviewers", []),
            "final_pdf": state.get("final_pdf"),
            "audit_log": state.get("audit_log", {}),
            "status": "approved" if not state.get("human_review_required") else "pending_approval"
        }
        return {"final_output": output, **state}
