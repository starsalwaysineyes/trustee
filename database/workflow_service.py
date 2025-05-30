"""
AI工作流服务
整合 "截图→AI分析→操作执行" 的完整流程并记录到数据库
"""

import time
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# 条件导入：支持不同的运行方式
try:
    from .models import Task, TaskStep, Screenshot, AIAnalysis, Execution
    from .dao import TaskDAO, TaskStepDAO, ScreenshotDAO, AIAnalysisDAO, ExecutionDAO
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from models import Task, TaskStep, Screenshot, AIAnalysis, Execution
    from dao import TaskDAO, TaskStepDAO, ScreenshotDAO, AIAnalysisDAO, ExecutionDAO

class WorkflowService:
    """AI工作流服务类"""
    
    def __init__(self):
        self.screenshot_dir = "screenshots"
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def create_task(self, user_id: int, task_name: str, 
                   natural_language_input: str, device_id: Optional[int] = None) -> int:
        """
        创建新任务
        
        Args:
            user_id: 用户ID
            task_name: 任务名称
            natural_language_input: 用户的自然语言指令
            device_id: 设备ID (可选)
            
        Returns:
            int: 新创建的任务ID
        """
        task = Task(
            user_id=user_id,
            device_id=device_id,
            task_name=task_name,
            task_description=f"执行指令: {natural_language_input}",
            natural_language_input=natural_language_input,
            status="pending"
        )
        
        task_id = TaskDAO.create(task)
        return task_id
    
    def start_task_execution(self, task_id: int) -> bool:
        """
        开始执行任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功开始执行
        """
        # 更新任务状态为运行中
        success = TaskDAO.update_status(task_id, "running")
        if success:
            # 创建第一个步骤：屏幕截图
            self.create_capture_step(task_id, 1, "开始任务执行，捕获当前屏幕状态")
        return success
    
    def create_capture_step(self, task_id: int, step_sequence: int, description: str) -> int:
        """
        创建截图步骤
        
        Args:
            task_id: 任务ID
            step_sequence: 步骤序号
            description: 步骤描述
            
        Returns:
            int: 步骤ID
        """
        step = TaskStep(
            task_id=task_id,
            step_sequence=step_sequence,
            step_type="capture",
            step_description=description,
            status="pending"
        )
        
        step_id = TaskStepDAO.create(step)
        return step_id
    
    def record_screenshot(self, task_id: int, step_id: int, 
                         image_path: str, screen_resolution: str,
                         purpose: str = "initial") -> int:
        """
        记录截图信息
        
        Args:
            task_id: 任务ID
            step_id: 步骤ID  
            image_path: 图片文件路径
            screen_resolution: 屏幕分辨率
            purpose: 截图用途
            
        Returns:
            int: 截图记录ID
        """
        # 计算文件大小和哈希
        file_size = os.path.getsize(image_path) if os.path.exists(image_path) else 0
        image_hash = self.calculate_file_hash(image_path) if os.path.exists(image_path) else None
        
        screenshot = Screenshot(
            task_id=task_id,
            step_id=step_id,
            image_path=image_path,
            screen_resolution=screen_resolution,
            file_size=file_size,
            image_hash=image_hash,
            purpose=purpose
        )
        
        screenshot_id = ScreenshotDAO.create(screenshot)
        
        # 更新步骤状态
        TaskStepDAO.update_step(step_id, "completed", screenshot_id=screenshot_id)
        
        return screenshot_id
    
    def create_analysis_step(self, task_id: int, step_sequence: int, 
                           screenshot_id: int, description: str) -> int:
        """
        创建AI分析步骤
        
        Args:
            task_id: 任务ID
            step_sequence: 步骤序号
            screenshot_id: 关联的截图ID
            description: 步骤描述
            
        Returns:
            int: 步骤ID
        """
        step = TaskStep(
            task_id=task_id,
            step_sequence=step_sequence,
            step_type="analyze",
            step_description=description,
            screenshot_id=screenshot_id,
            status="pending"
        )
        
        step_id = TaskStepDAO.create(step)
        return step_id
    
    def record_ai_analysis(self, task_id: int, step_id: int, screenshot_id: int,
                          prompt_text: str, ai_response: str, model_name: str,
                          extracted_data: Optional[Dict[str, Any]] = None,
                          coordinates: Optional[Tuple[int, int, int, int]] = None,
                          processing_time_ms: Optional[int] = None,
                          api_cost: Optional[float] = None,
                          conversation_context: Optional[str] = None) -> int:
        """
        记录AI分析结果
        
        Args:
            task_id: 任务ID
            step_id: 步骤ID
            screenshot_id: 截图ID
            prompt_text: 发送给AI的提示词
            ai_response: AI的回复
            model_name: 使用的模型名称
            extracted_data: 提取的JSON数据
            coordinates: 识别的坐标 (x1, y1, x2, y2)
            processing_time_ms: 处理时间
            api_cost: API成本
            conversation_context: 对话上下文
            
        Returns:
            int: 分析记录ID
        """
        analysis = AIAnalysis(
            task_id=task_id,
            step_id=step_id,
            screenshot_id=screenshot_id,
            prompt_text=prompt_text,
            model_name=model_name,
            ai_response=ai_response,
            processing_time_ms=processing_time_ms,
            api_cost=api_cost,
            conversation_context=conversation_context
        )
        
        # 设置提取的数据
        if extracted_data:
            analysis.extracted_data = extracted_data
        
        # 设置坐标
        if coordinates and len(coordinates) == 4:
            analysis.coordinates_x1, analysis.coordinates_y1, analysis.coordinates_x2, analysis.coordinates_y2 = coordinates
        
        analysis_id = AIAnalysisDAO.create(analysis)
        
        # 更新步骤状态
        TaskStepDAO.update_step(step_id, "completed", 
                               ai_analysis_id=analysis_id,
                               duration_ms=processing_time_ms)
        
        return analysis_id
    
    def create_execution_step(self, task_id: int, step_sequence: int,
                            analysis_id: int, description: str) -> int:
        """
        创建操作执行步骤
        
        Args:
            task_id: 任务ID
            step_sequence: 步骤序号
            analysis_id: 关联的AI分析ID
            description: 步骤描述
            
        Returns:
            int: 步骤ID
        """
        step = TaskStep(
            task_id=task_id,
            step_sequence=step_sequence,
            step_type="execute",
            step_description=description,
            ai_analysis_id=analysis_id,
            status="pending"
        )
        
        step_id = TaskStepDAO.create(step)
        return step_id
    
    def record_execution(self, task_id: int, step_id: int, analysis_id: int,
                        operation_type: str, target_x: int, target_y: int,
                        success: bool, execution_duration_ms: Optional[int] = None,
                        operation_params: Optional[Dict[str, Any]] = None,
                        error_message: Optional[str] = None,
                        verification_screenshot_id: Optional[int] = None) -> int:
        """
        记录操作执行结果
        
        Args:
            task_id: 任务ID
            step_id: 步骤ID
            analysis_id: AI分析ID
            operation_type: 操作类型
            target_x, target_y: 目标坐标
            success: 是否成功
            execution_duration_ms: 执行时间
            operation_params: 操作参数
            error_message: 错误信息
            verification_screenshot_id: 验证截图ID
            
        Returns:
            int: 执行记录ID
        """
        execution = Execution(
            task_id=task_id,
            step_id=step_id,
            analysis_id=analysis_id,
            operation_type=operation_type,
            target_x=target_x,
            target_y=target_y,
            execution_duration_ms=execution_duration_ms,
            success=success,
            verification_screenshot_id=verification_screenshot_id,
            error_message=error_message
        )
        
        # 设置操作参数
        if operation_params:
            execution.params = operation_params
        
        execution_id = ExecutionDAO.create(execution)
        
        # 更新步骤状态
        step_status = "completed" if success else "failed"
        TaskStepDAO.update_step(step_id, step_status,
                               execution_id=execution_id,
                               duration_ms=execution_duration_ms,
                               error_details=error_message)
        
        return execution_id
    
    def complete_task(self, task_id: int, success: bool, 
                     error_message: Optional[str] = None) -> bool:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            success: 是否成功完成
            error_message: 错误信息
            
        Returns:
            bool: 是否成功更新状态
        """
        status = "completed" if success else "failed"
        return TaskDAO.update_status(task_id, status, error_message)
    
    def update_task_progress(self, task_id: int) -> bool:
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功更新
        """
        steps = TaskStepDAO.get_by_task_id(task_id)
        total_steps = len(steps)
        completed_steps = len([s for s in steps if s.status == "completed"])
        
        return TaskDAO.update_progress(task_id, completed_steps, total_steps)
    
    def get_task_summary(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        获取任务摘要信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 任务摘要信息
        """
        task = TaskDAO.get_by_id(task_id)
        if not task:
            return None
        
        steps = TaskStepDAO.get_by_task_id(task_id)
        screenshots = ScreenshotDAO.get_by_task_id(task_id)
        analyses = AIAnalysisDAO.get_by_task_id(task_id)
        executions = ExecutionDAO.get_by_task_id(task_id)
        
        return {
            "task": task,
            "steps": steps,
            "screenshots": screenshots,
            "ai_analyses": analyses,
            "executions": executions,
            "total_steps": len(steps),
            "completed_steps": len([s for s in steps if s.status == "completed"]),
            "total_cost": sum(a.api_cost or 0 for a in analyses)
        }
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """计算文件的SHA256哈希值"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def generate_screenshot_path(self, task_id: int, step_sequence: int, purpose: str = "step") -> str:
        """
        生成截图文件路径
        
        Args:
            task_id: 任务ID
            step_sequence: 步骤序号
            purpose: 截图用途
            
        Returns:
            str: 截图文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task_{task_id}_step_{step_sequence}_{purpose}_{timestamp}.png"
        return os.path.join(self.screenshot_dir, filename) 