"""
数据模型定义
包含所有数据库表对应的模型类
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import json

@dataclass
class User:
    """用户模型"""
    user_id: Optional[int] = None
    username: str = ""
    email: Optional[str] = None
    password_hash: str = ""
    permission_level: int = 1
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    preferences_json: Optional[str] = None
    
    @property
    def preferences(self) -> Dict[str, Any]:
        """获取用户偏好设置"""
        if self.preferences_json:
            return json.loads(self.preferences_json)
        return {}
    
    @preferences.setter
    def preferences(self, value: Dict[str, Any]):
        """设置用户偏好"""
        self.preferences_json = json.dumps(value, ensure_ascii=False)

@dataclass
class Device:
    """设备模型"""
    device_id: Optional[int] = None
    device_name: str = ""
    device_ip: Optional[str] = None
    device_type: str = "local"  # 'local', 'remote'
    os_info: Optional[str] = None
    screen_resolution: Optional[str] = None
    last_online: Optional[datetime] = None
    status: str = "offline"  # 'online', 'offline', 'busy'
    owner_user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

@dataclass
class Task:
    """任务模型"""
    task_id: Optional[int] = None
    user_id: int = 0
    device_id: Optional[int] = None
    task_name: str = ""
    task_description: Optional[str] = None
    task_type: str = "manual"  # 'manual', 'scheduled', 'triggered'
    natural_language_input: Optional[str] = None
    status: str = "pending"  # 'pending', 'running', 'paused', 'completed', 'failed'
    priority: int = 0
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    total_steps: int = 0
    completed_steps: int = 0
    error_message: Optional[str] = None
    config_json: Optional[str] = None
    estimated_duration: Optional[str] = None
    actual_duration: Optional[str] = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """获取任务配置"""
        if self.config_json:
            return json.loads(self.config_json)
        return {}
    
    @config.setter
    def config(self, value: Dict[str, Any]):
        """设置任务配置"""
        self.config_json = json.dumps(value, ensure_ascii=False)
    
    @property
    def progress_percentage(self) -> float:
        """获取任务进度百分比"""
        if self.total_steps == 0:
            return 0.0
        return (self.completed_steps / self.total_steps) * 100

@dataclass
class TaskStep:
    """任务执行步骤模型"""
    step_id: Optional[int] = None
    task_id: int = 0
    step_sequence: int = 0
    step_type: str = "capture"  # 'capture', 'analyze', 'execute', 'verify'
    step_description: Optional[str] = None
    screenshot_id: Optional[int] = None
    ai_analysis_id: Optional[int] = None
    execution_id: Optional[int] = None
    status: str = "pending"  # 'pending', 'running', 'completed', 'failed'
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    retry_count: int = 0
    error_details: Optional[str] = None

@dataclass
class Screenshot:
    """屏幕截图模型"""
    screenshot_id: Optional[int] = None
    task_id: int = 0
    step_id: Optional[int] = None
    image_path: str = ""
    image_base64: Optional[str] = None
    screen_resolution: Optional[str] = None
    capture_timestamp: Optional[datetime] = None
    file_size: Optional[int] = None
    image_hash: Optional[str] = None
    purpose: str = "initial"  # 'initial', 'verification', 'error'

@dataclass
class AIAnalysis:
    """AI分析记录模型"""
    analysis_id: Optional[int] = None
    task_id: int = 0
    step_id: Optional[int] = None
    screenshot_id: int = 0
    prompt_text: str = ""
    model_name: Optional[str] = None
    ai_response: str = ""
    extracted_json: Optional[str] = None
    coordinates_x1: Optional[int] = None
    coordinates_y1: Optional[int] = None
    coordinates_x2: Optional[int] = None
    coordinates_y2: Optional[int] = None
    confidence_score: Optional[float] = None
    analysis_timestamp: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    api_cost: Optional[float] = None
    conversation_context: Optional[str] = None
    
    @property
    def extracted_data(self) -> Dict[str, Any]:
        """获取提取的JSON数据"""
        if self.extracted_json:
            return json.loads(self.extracted_json)
        return {}
    
    @extracted_data.setter
    def extracted_data(self, value: Dict[str, Any]):
        """设置提取的JSON数据"""
        self.extracted_json = json.dumps(value, ensure_ascii=False)
    
    @property
    def center_coordinates(self) -> tuple[int, int]:
        """获取识别区域的中心坐标"""
        if all([self.coordinates_x1, self.coordinates_y1, self.coordinates_x2, self.coordinates_y2]):
            center_x = (self.coordinates_x1 + self.coordinates_x2) // 2
            center_y = (self.coordinates_y1 + self.coordinates_y2) // 2
            return (center_x, center_y)
        return (0, 0)

@dataclass
class Execution:
    """操作执行记录模型"""
    execution_id: Optional[int] = None
    task_id: int = 0
    step_id: Optional[int] = None
    analysis_id: Optional[int] = None
    operation_type: str = "click"  # 'click', 'type', 'key_press', 'drag', 'scroll'
    target_x: Optional[int] = None
    target_y: Optional[int] = None
    operation_params: Optional[str] = None
    execution_timestamp: Optional[datetime] = None
    execution_duration_ms: Optional[int] = None
    success: bool = False
    verification_screenshot_id: Optional[int] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    @property
    def params(self) -> Dict[str, Any]:
        """获取操作参数"""
        if self.operation_params:
            return json.loads(self.operation_params)
        return {}
    
    @params.setter
    def params(self, value: Dict[str, Any]):
        """设置操作参数"""
        self.operation_params = json.dumps(value, ensure_ascii=False) 