import time
import json
import random
import hashlib
import os

class SecurityControl:
    """安全控制层 - 管理系统权限和操作安全"""
    
    def __init__(self):
        """初始化安全控制层"""
        self.permission_rules = {
            "default": {
                "launch_application": True,
                "click": True,
                "input_text": True,
                "generic_action": True
            },
            "restricted": {
                "launch_application": False,
                "click": True,
                "input_text": True,
                "generic_action": False
            },
            "admin": {
                "launch_application": True,
                "click": True,
                "input_text": True,
                "generic_action": True,
                "system_config": True
            }
        }
        self.audit_logs = []
        self.current_user_role = "default"
    
    def check_operation_permission(self, task_plan):
        """检查操作权限
        
        根据任务计划和用户角色检查操作权限
        """
        if not task_plan:
            return {
                "granted": False,
                "reason": "无效的任务计划"
            }
        
        # 获取当前用户角色的权限规则
        role_permissions = self.permission_rules.get(self.current_user_role, {})
        
        # 检查每个必要动作的权限
        required_actions = task_plan.get("required_actions", [])
        denied_actions = []
        
        for action in required_actions:
            action_type = action.get("action_type", "")
            
            # 检查该动作类型是否有权限
            if action_type not in role_permissions or not role_permissions[action_type]:
                denied_actions.append(action_type)
        
        # 生成权限检查结果
        permission_result = {
            "granted": len(denied_actions) == 0,
            "timestamp": time.time(),
            "user_role": self.current_user_role,
            "task_id": task_plan.get("task_id", "unknown")
        }
        
        if not permission_result["granted"]:
            permission_result["reason"] = f"以下操作类型无权执行: {', '.join(denied_actions)}"
            permission_result["denied_actions"] = denied_actions
        
        # 记录权限检查日志
        self._log_permission_check(permission_result, task_plan)
        
        return permission_result
    
    def record_operation_log(self, session_id, task_plan, operation_sequence, execution_result):
        """记录操作日志
        
        保存任务执行的详细日志，用于审计和分析
        """
        if not task_plan or not execution_result:
            return False
        
        # 生成操作日志
        log_entry = {
            "log_id": self._generate_log_id(),
            "timestamp": time.time(),
            "session_id": session_id,
            "user_role": self.current_user_role,
            "task_id": task_plan.get("task_id", "unknown"),
            "task_summary": {
                "original_instruction": task_plan.get("original_instruction", ""),
                "parsed_intent": task_plan.get("parsed_intent", {})
            },
            "operation_count": len(operation_sequence) if operation_sequence else 0,
            "execution_summary": {
                "success": execution_result.get("success", False),
                "start_time": execution_result.get("start_time", 0),
                "end_time": execution_result.get("end_time", 0),
                "duration": execution_result.get("duration", 0)
            },
            "sensitive_data_accessed": self._check_sensitive_data_access(operation_sequence)
        }
        
        # 存储日志
        self.audit_logs.append(log_entry)
        
        return True
    
    def store_audit_information(self, audit_data):
        """存储审计信息
        
        保存系统操作的审计信息，用于合规性和追踪
        """
        if not audit_data:
            return False
        
        # 为审计数据添加元数据
        enriched_audit_data = {
            "audit_id": self._generate_log_id(),
            "timestamp": time.time(),
            "data": audit_data
        }
        
        # 存储审计数据
        # 在实际实现中，这里应该将数据存储到安全的数据库或日志系统
        # 在此模拟实现中，只是添加到内存中的列表
        self.audit_logs.append(enriched_audit_data)
        
        return True
    
    def _generate_log_id(self):
        """生成唯一的日志ID"""
        random_bytes = os.urandom(16)
        return hashlib.md5(random_bytes).hexdigest()
    
    def _log_permission_check(self, permission_result, task_plan):
        """记录权限检查日志"""
        log_entry = {
            "log_id": self._generate_log_id(),
            "log_type": "permission_check",
            "timestamp": time.time(),
            "user_role": self.current_user_role,
            "task_id": task_plan.get("task_id", "unknown"),
            "permission_granted": permission_result.get("granted", False)
        }
        
        if not permission_result.get("granted", False):
            log_entry["reason"] = permission_result.get("reason", "未知原因")
            log_entry["denied_actions"] = permission_result.get("denied_actions", [])
        
        self.audit_logs.append(log_entry)
    
    def _check_sensitive_data_access(self, operation_sequence):
        """检查操作序列是否访问了敏感数据"""
        if not operation_sequence:
            return False
        
        # 在实际实现中，这里应该根据操作类型和目标检查敏感数据访问
        # 在此模拟实现中，随机返回结果
        return random.random() < 0.1  # 10%的概率访问敏感数据 