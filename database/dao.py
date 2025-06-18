"""
数据访问对象 (DAO)
提供各个模型的增删改查操作
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import sqlite3
import logging

# 条件导入：支持不同的运行方式
try:
    from .database import db_manager
    from .models import Task, TaskStep, Screenshot, AIAnalysis, Execution, User, Device, AnalysisLog
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from database import db_manager
    from models import Task, TaskStep, Screenshot, AIAnalysis, Execution, User, Device, AnalysisLog

logger = logging.getLogger(__name__)

class BaseDAO:
    """基础DAO类，提供通用的数据库操作方法"""
    
    @staticmethod
    def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典"""
        return dict(row) if row else {}

class TaskDAO(BaseDAO):
    """任务数据访问对象"""
    
    @staticmethod
    def create(task: Task) -> int:
        """创建新任务"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (user_id, device_id, task_name, task_description, 
                                 task_type, natural_language_input, status, priority, config_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.user_id, task.device_id, task.task_name, task.task_description,
                task.task_type, task.natural_language_input, task.status, 
                task.priority, task.config_json
            ))
            task_id = cursor.lastrowid
            conn.commit()
            logger.info(f"创建任务成功，任务ID: {task_id}")
            return task_id
    
    @staticmethod
    def get_by_id(task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return Task(**BaseDAO.row_to_dict(row))
            return None
    
    @staticmethod
    def get_by_user_id(user_id: int, status: Optional[str] = None) -> List[Task]:
        """获取用户的任务列表"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
                    (user_id, status)
                )
            else:
                cursor.execute(
                    "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
                    (user_id,)
                )
            rows = cursor.fetchall()
            return [Task(**BaseDAO.row_to_dict(row)) for row in rows]
    
    @staticmethod
    def update_status(task_id: int, status: str, error_message: Optional[str] = None) -> bool:
        """更新任务状态"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            if status == "running":
                cursor.execute("""
                    UPDATE tasks SET status = ?, started_at = ?, last_updated = ?
                    WHERE task_id = ?
                """, (status, current_time, current_time, task_id))
            elif status in ["completed", "failed"]:
                cursor.execute("""
                    UPDATE tasks SET status = ?, completed_at = ?, last_updated = ?, error_message = ?
                    WHERE task_id = ?
                """, (status, current_time, current_time, error_message, task_id))
            else:
                cursor.execute("""
                    UPDATE tasks SET status = ?, last_updated = ?
                    WHERE task_id = ?
                """, (status, current_time, task_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def update_progress(task_id: int, completed_steps: int, total_steps: int) -> bool:
        """更新任务进度"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks SET completed_steps = ?, total_steps = ?, last_updated = ?
                WHERE task_id = ?
            """, (completed_steps, total_steps, datetime.now().isoformat(), task_id))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def update(task: Task) -> bool:
        """更新任务信息"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks SET task_name = ?, task_description = ?, task_type = ?,
                               natural_language_input = ?, status = ?, priority = ?,
                               config_json = ?, last_updated = ?
                WHERE task_id = ?
            """, (
                task.task_name, task.task_description, task.task_type,
                task.natural_language_input, task.status, task.priority,
                task.config_json, datetime.now().isoformat(), task.task_id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(task_id: int) -> bool:
        """删除任务"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            # 先删除相关的步骤
            cursor.execute("DELETE FROM task_steps WHERE task_id = ?", (task_id,))
            # 删除相关的截图
            cursor.execute("DELETE FROM screenshots WHERE task_id = ?", (task_id,))
            # 删除相关的AI分析
            cursor.execute("DELETE FROM ai_analysis WHERE task_id = ?", (task_id,))
            # 删除相关的执行记录
            cursor.execute("DELETE FROM executions WHERE task_id = ?", (task_id,))
            # 最后删除任务本身
            cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

class AnalysisLogDAO(BaseDAO):
    """分析日志数据访问对象"""

    @staticmethod
    def add_analysis_log(log: "AnalysisLog") -> Optional[int]:
        """
        将一条新的AI分析记录添加到数据库。
        :param log: 包含分析数据的AnalysisLog对象。
        :return: 新记录的ID，如果失败则返回None。
        """
        sql = """
        INSERT INTO analysis_log (
            user_id, timestamp, user_instruction, original_screenshot_base64,
            annotated_screenshot_base64, analysis_result_json, target_resolution
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            log.user_id,
            log.timestamp or datetime.utcnow(),
            log.user_instruction,
            log.original_screenshot_base64,
            log.annotated_screenshot_base64,
            log.analysis_result_json,
            log.target_resolution
        )
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                log_id = cursor.lastrowid
                conn.commit()
                logger.info(f"成功添加分析日志，ID: {log_id}")
                return log_id
        except Exception as e:
            logger.error(f"DAO: 添加分析日志失败: {e}")
            return None

    @staticmethod
    def get_analysis_logs_paginated(page: int, per_page: int) -> Dict[str, Any]:
        """
        分页查询AI分析日志。
        :param page: 当前页码 (从1开始)。
        :param per_page: 每页记录数。
        :return: 包含日志列表和总数的字典。
        """
        offset = (page - 1) * per_page
        
        try:
            with db_manager.get_connection() as conn:
                # 查询总数
                total_count = conn.execute("SELECT COUNT(*) FROM analysis_log").fetchone()[0]
                
                # 查询分页数据
                query_sql = """
                SELECT * FROM analysis_log
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """
                
                rows = conn.execute(query_sql, (per_page, offset)).fetchall()
                
                logs = [AnalysisLog(**BaseDAO.row_to_dict(row)) for row in rows]
                
                return {
                    "logs": logs,
                    "total": total_count,
                }
        except Exception as e:
            logger.error(f"DAO: 分页查询分析日志失败: {e}")
            return {"logs": [], "total": 0}

class TaskStepDAO(BaseDAO):
    """任务步骤数据访问对象"""
    
    @staticmethod
    def create(step: TaskStep) -> int:
        """创建新的任务步骤"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO task_steps (task_id, step_sequence, step_type, step_description, status)
                VALUES (?, ?, ?, ?, ?)
            """, (step.task_id, step.step_sequence, step.step_type, step.step_description, step.status))
            step_id = cursor.lastrowid
            conn.commit()
            return step_id
    
    @staticmethod
    def get_by_task_id(task_id: int) -> List[TaskStep]:
        """获取任务的所有步骤"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM task_steps WHERE task_id = ? ORDER BY step_sequence",
                (task_id,)
            )
            rows = cursor.fetchall()
            return [TaskStep(**BaseDAO.row_to_dict(row)) for row in rows]
    
    @staticmethod
    def update_step(step_id: int, status: str, **kwargs) -> bool:
        """更新步骤信息"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            update_fields = ["status = ?"]
            params = [status]
            
            if status == "running":
                update_fields.append("started_at = ?")
                params.append(datetime.now().isoformat())
            elif status in ["completed", "failed"]:
                update_fields.append("completed_at = ?")
                params.append(datetime.now().isoformat())
                if "duration_ms" in kwargs:
                    update_fields.append("duration_ms = ?")
                    params.append(kwargs["duration_ms"])
            
            for key, value in kwargs.items():
                if key not in ["duration_ms"]:  # 避免重复添加
                    update_fields.append(f"{key} = ?")
                    params.append(value)
            
            params.append(step_id)  # WHERE条件
            
            sql = f"UPDATE task_steps SET {', '.join(update_fields)} WHERE step_id = ?"
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0

class ScreenshotDAO(BaseDAO):
    """截图数据访问对象"""
    
    @staticmethod
    def create(screenshot: Screenshot) -> int:
        """保存截图记录"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO screenshots (task_id, step_id, image_path, screen_resolution, 
                                       file_size, image_hash, purpose)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                screenshot.task_id, screenshot.step_id, screenshot.image_path,
                screenshot.screen_resolution, screenshot.file_size, 
                screenshot.image_hash, screenshot.purpose
            ))
            screenshot_id = cursor.lastrowid
            conn.commit()
            return screenshot_id
    
    @staticmethod
    def get_by_task_id(task_id: int) -> List[Screenshot]:
        """获取任务的所有截图"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM screenshots WHERE task_id = ? ORDER BY capture_timestamp",
                (task_id,)
            )
            rows = cursor.fetchall()
            return [Screenshot(**BaseDAO.row_to_dict(row)) for row in rows]

class AIAnalysisDAO(BaseDAO):
    """AI分析数据访问对象"""
    
    @staticmethod
    def create(analysis: AIAnalysis) -> int:
        """保存AI分析记录"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ai_analysis (task_id, step_id, screenshot_id, prompt_text, 
                                       model_name, ai_response, extracted_json, 
                                       coordinates_x1, coordinates_y1, coordinates_x2, coordinates_y2,
                                       confidence_score, processing_time_ms, api_cost, conversation_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.task_id, analysis.step_id, analysis.screenshot_id,
                analysis.prompt_text, analysis.model_name, analysis.ai_response,
                analysis.extracted_json, analysis.coordinates_x1, analysis.coordinates_y1,
                analysis.coordinates_x2, analysis.coordinates_y2, analysis.confidence_score,
                analysis.processing_time_ms, analysis.api_cost, analysis.conversation_context
            ))
            analysis_id = cursor.lastrowid
            conn.commit()
            return analysis_id
    
    @staticmethod
    def get_by_task_id(task_id: int) -> List[AIAnalysis]:
        """获取任务的所有AI分析记录"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM ai_analysis WHERE task_id = ? ORDER BY analysis_timestamp",
                (task_id,)
            )
            rows = cursor.fetchall()
            return [AIAnalysis(**BaseDAO.row_to_dict(row)) for row in rows]

class ExecutionDAO(BaseDAO):
    """操作执行数据访问对象"""
    
    @staticmethod
    def create(execution: Execution) -> int:
        """保存操作执行记录"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO executions (task_id, step_id, analysis_id, operation_type,
                                      target_x, target_y, operation_params, 
                                      execution_duration_ms, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.task_id, execution.step_id, execution.analysis_id,
                execution.operation_type, execution.target_x, execution.target_y,
                execution.operation_params, execution.execution_duration_ms,
                execution.success, execution.error_message
            ))
            execution_id = cursor.lastrowid
            conn.commit()
            return execution_id
    
    @staticmethod
    def get_by_task_id(task_id: int) -> List[Execution]:
        """获取任务的所有执行记录"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM executions WHERE task_id = ? ORDER BY execution_timestamp",
                (task_id,)
            )
            rows = cursor.fetchall()
            return [Execution(**BaseDAO.row_to_dict(row)) for row in rows]

class UserDAO(BaseDAO):
    """用户数据访问对象"""
    
    @staticmethod
    def create(user: User) -> int:
        """创建新用户"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, permission_level, preferences_json)
                VALUES (?, ?, ?, ?, ?)
            """, (user.username, user.email, user.password_hash, user.permission_level, user.preferences_json))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
    
    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """根据用户名获取用户"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return User(**BaseDAO.row_to_dict(row))
            return None

class DeviceDAO(BaseDAO):
    """设备数据访问对象"""
    
    @staticmethod
    def create(device: Device) -> int:
        """创建新设备"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO devices (device_name, device_ip, device_type, os_info, 
                                   screen_resolution, status, owner_user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                device.device_name, device.device_ip, device.device_type,
                device.os_info, device.screen_resolution, device.status, device.owner_user_id
            ))
            device_id = cursor.lastrowid
            conn.commit()
            return device_id
    
    @staticmethod
    def get_by_id(device_id: int) -> Optional[Device]:
        """根据ID获取设备"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
            row = cursor.fetchone()
            if row:
                return Device(**BaseDAO.row_to_dict(row))
            return None
    
    @staticmethod
    def get_by_user_id(user_id: int) -> List[Device]:
        """获取用户的设备列表"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM devices WHERE owner_user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [Device(**BaseDAO.row_to_dict(row)) for row in rows]
    
    @staticmethod
    def update(device: Device) -> bool:
        """更新设备信息"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE devices SET device_name = ?, device_ip = ?, device_type = ?, 
                                 os_info = ?, screen_resolution = ?, status = ?, last_updated = ?
                WHERE device_id = ?
            """, (
                device.device_name, device.device_ip, device.device_type,
                device.os_info, device.screen_resolution, device.status, 
                datetime.now().isoformat(), device.device_id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    @staticmethod
    def delete(device_id: int) -> bool:
        """删除设备"""
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM devices WHERE device_id = ?", (device_id,))
            conn.commit()
            return cursor.rowcount > 0 