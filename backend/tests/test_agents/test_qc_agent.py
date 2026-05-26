import pytest
from src.agents.qc_agent import QCAgent
from src.schemas.agents import QCState

@pytest.fixture
def qc_agent():
    return QCAgent()

@pytest.mark.asyncio
async def test_qc_agent_initialization(qc_agent):
    """测试QC Agent初始化"""
    assert qc_agent.name == "qc_agent"
    assert qc_agent.state_schema == QCState

@pytest.mark.asyncio
async def test_load_raw_data(qc_agent):
    """测试加载原始数据"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        raw_data={"sample_id": "SAMPLE-001", "batch": "BATCH-2024-001"},
    )
    result = await qc_agent._load_raw_data(state)
    assert result["raw_data"]["sample_id"] == "SAMPLE-001"
    assert result["raw_data"]["batch"] == "BATCH-2024-001"

@pytest.mark.asyncio
async def test_generate_draft_report(qc_agent):
    """测试生成草稿报告"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        raw_data={"sample_id": "SAMPLE-001"},
    )
    result = await qc_agent._generate_draft_report(state)
    assert "draft_report" in result
    assert "SAMPLE-001" in result["draft_report"]

@pytest.mark.asyncio
async def test_validate_compliance(qc_agent):
    """测试合规性校验"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        draft_report="QC Report Draft - Based on data: SAMPLE-001",
    )
    result = await qc_agent._validate_compliance(state)
    assert "compliance_issues" in result
    assert isinstance(result["compliance_issues"], list)

@pytest.mark.asyncio
async def test_validate_compliance_with_empty_report(qc_agent):
    """测试空报告的合规性校验"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        draft_report="",
    )
    result = await qc_agent._validate_compliance(state)
    assert len(result["compliance_issues"]) > 0
    assert result["compliance_issues"][0]["severity"] == "high"

@pytest.mark.asyncio
async def test_check_human_review_required_with_high_severity(qc_agent):
    """测试需要人工审核的情况"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        compliance_issues=[
            {"type": "missing_report", "severity": "high", "message": "Draft report is empty"}
        ],
    )
    result = await qc_agent._check_human_review_required(state)
    assert result["human_review_required"] == True

@pytest.mark.asyncio
async def test_check_human_review_required_without_high_severity(qc_agent):
    """测试不需要人工审核的情况"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        compliance_issues=[
            {"type": "minor_issue", "severity": "low", "message": "Minor issue"}
        ],
    )
    result = await qc_agent._check_human_review_required(state)
    assert result["human_review_required"] == False

@pytest.mark.asyncio
async def test_assign_reviewers(qc_agent):
    """测试分配审核人员"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
    )
    result = await qc_agent._assign_reviewers(state)
    assert "reviewers" in result
    assert len(result["reviewers"]) == 2
    assert "qc_reviewer_1" in result["reviewers"]

@pytest.mark.asyncio
async def test_generate_pdf(qc_agent):
    """测试生成PDF"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
    )
    result = await qc_agent._generate_pdf(state)
    assert "final_pdf" in result
    assert result["final_pdf"] == b"PDF placeholder - actual PDF content would be generated here"

@pytest.mark.asyncio
async def test_create_audit_log(qc_agent):
    """测试创建审计日志"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        user_id="test-user",
        compliance_issues=[],
    )
    result = await qc_agent._create_audit_log(state)
    assert "audit_log" in result
    assert result["audit_log"]["action"] == "qc_report_generated"
    assert result["audit_log"]["user_id"] == "test-user"
    assert result["audit_log"]["session_id"] == "test-session"

@pytest.mark.asyncio
async def test_format_output_without_human_review(qc_agent):
    """测试格式化输出（不需要人工审核）"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        draft_report="QC Report Draft",
        compliance_issues=[],
        human_review_required=False,
        reviewers=[],
    )
    result = await qc_agent._format_output(state)
    assert "final_output" in result
    assert result["final_output"]["status"] == "approved"

@pytest.mark.asyncio
async def test_format_output_with_human_review(qc_agent):
    """测试格式化输出（需要人工审核）"""
    state = QCState(
        user_input="生成QC报告",
        session_id="test-session",
        draft_report="QC Report Draft",
        compliance_issues=[{"type": "test", "severity": "high"}],
        human_review_required=True,
        reviewers=["qc_reviewer_1"],
    )
    result = await qc_agent._format_output(state)
    assert "final_output" in result
    assert result["final_output"]["status"] == "pending_approval"

def test_workflow_builds(qc_agent):
    """测试工作流可以构建"""
    workflow = qc_agent.build_workflow()
    assert workflow is not None