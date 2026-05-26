from typing import List, Dict, Optional
from langgraph import StateGraph, END
from src.agents.base import BaseAgent
from src.schemas.agents import MaintState
from src.config import get_settings

settings = get_settings()

MAINT_AGENT_PROMPT = """你是一个设备维护智能助手，专注于设备预测性维护。

你的职责：
1. 传感器数据分析 - 分析设备传感器时序数据，检测异常模式
2. 异常检测 - 使用规则引擎识别设备异常和故障信号
3. 故障预测 - 基于历史数据和模式识别预测潜在故障
4. 维护建议 - 生成预防性维护建议和推荐行动
5. 工单生成 - 创建维护工单并发送告警通知

输出要求：
- 异常评分低于0.7时标注不确定性
- 所有推荐行动必须包含优先级和预计工时
- 告警通知需包含设备ID、位置、严重程度
"""

class MaintAgent(BaseAgent):
    """设备维护Agent"""

    def __init__(self):
        super().__init__(
            name="maint_agent",
            state_schema=MaintState,
            system_prompt=MAINT_AGENT_PROMPT,
        )

    def define_nodes(self, workflow: StateGraph) -> None:
        workflow.add_node("load_sensor_data", self._load_sensor_data)
        workflow.add_node("detect_anomaly", self._detect_anomaly)
        workflow.add_node("predict_failure", self._predict_failure)
        workflow.add_node("generate_actions", self._generate_actions)
        workflow.add_node("create_work_order", self._create_work_order)
        workflow.add_node("send_alert", self._send_alert)
        workflow.add_node("format_output", self._format_output)

    def define_edges(self, workflow: StateGraph) -> None:
        workflow.add_edge("load_sensor_data", "detect_anomaly")
        workflow.add_edge("detect_anomaly", "predict_failure")
        workflow.add_edge("predict_failure", "generate_actions")
        workflow.add_edge("generate_actions", "create_work_order")
        workflow.add_edge("create_work_order", "send_alert")
        workflow.add_edge("send_alert", "format_output")
        workflow.add_edge("format_output", END)

    def get_entry_point(self) -> str:
        return "load_sensor_data"

    async def _load_sensor_data(self, state: MaintState) -> MaintState:
        """加载设备传感器数据"""
        # Placeholder - actual implementation uses sensor data API
        device_id = state.get("device_id", "")
        return {"sensor_data": {"device_id": device_id, "readings": []}, **state}

    async def _detect_anomaly(self, state: MaintState) -> MaintState:
        """使用规则引擎检测异常"""
        sensor_data = state.get("sensor_data", {})
        anomaly_score = 0.5  # Placeholder - actual implementation analyzes sensor patterns
        anomaly_pattern = None

        # Simple rule-based anomaly detection placeholder
        if sensor_data.get("readings"):
            anomaly_pattern = "normal"
            anomaly_score = 0.3

        return {"anomaly_score": anomaly_score, "anomaly_pattern": anomaly_pattern, **state}

    async def _predict_failure(self, state: MaintState) -> MaintState:
        """预测潜在故障"""
        anomaly_score = state.get("anomaly_score", 0.0)
        anomaly_pattern = state.get("anomaly_pattern")

        failure_prediction = None
        if anomaly_score > 0.6:
            failure_prediction = {
                "likelihood": "high",
                "predicted_failure": "bearing_wear",
                "time_to_failure": "72h",
                "confidence": anomaly_score,
            }
        elif anomaly_score > 0.3:
            failure_prediction = {
                "likelihood": "medium",
                "predicted_failure": "vibration_increase",
                "time_to_failure": "168h",
                "confidence": anomaly_score,
            }

        return {"failure_prediction": failure_prediction, **state}

    async def _generate_actions(self, state: MaintState) -> MaintState:
        """生成推荐的维护行动"""
        failure_prediction = state.get("failure_prediction")
        recommended_actions = []

        if failure_prediction:
            likelihood = failure_prediction.get("likelihood", "low")
            if likelihood == "high":
                recommended_actions = [
                    {"action": "schedule_immediate_inspection", "priority": "critical", "estimated_hours": 2},
                    {"action": "order_replacement_parts", "priority": "high", "estimated_hours": 1},
                    {"action": "notify_ops_manager", "priority": "high", "estimated_hours": 0.5},
                ]
            elif likelihood == "medium":
                recommended_actions = [
                    {"action": "schedule_planned_maintenance", "priority": "medium", "estimated_hours": 4},
                    {"action": "perform_vibration_analysis", "priority": "medium", "estimated_hours": 2},
                ]

        return {"recommended_actions": recommended_actions, **state}

    async def _create_work_order(self, state: MaintState) -> MaintState:
        """创建维护工单"""
        # Placeholder - actual implementation creates work order in CMMS
        device_id = state.get("device_id", "")
        recommended_actions = state.get("recommended_actions", [])
        failure_prediction = state.get("failure_prediction")

        work_order = {
            "work_order_id": f"WO-{device_id}-001",
            "device_id": device_id,
            "actions": recommended_actions,
            "predicted_failure": failure_prediction.get("predicted_failure") if failure_prediction else None,
            "status": "created",
        }

        return {"work_order": work_order, **state}

    async def _send_alert(self, state: MaintState) -> MaintState:
        """发送告警通知"""
        # Placeholder - actual implementation sends notification via email/SMS
        work_order = state.get("work_order")
        failure_prediction = state.get("failure_prediction")

        alert_sent = False
        if work_order and failure_prediction:
            alert_sent = True  # Notification sent successfully

        return {"alert_sent": alert_sent, **state}

    async def _format_output(self, state: MaintState) -> MaintState:
        """格式化最终输出"""
        output = {
            "device_id": state.get("device_id"),
            "sensor_data": state.get("sensor_data"),
            "anomaly_score": state.get("anomaly_score"),
            "anomaly_pattern": state.get("anomaly_pattern"),
            "failure_prediction": state.get("failure_prediction"),
            "recommended_actions": state.get("recommended_actions"),
            "work_order": state.get("work_order"),
            "alert_sent": state.get("alert_sent"),
        }
        return {"final_output": output, **state}