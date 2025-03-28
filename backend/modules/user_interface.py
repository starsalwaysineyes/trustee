class UserInterface:
    """用户交互层 - 处理用户输入和结果展示"""
    
    def __init__(self):
        """初始化用户交互层"""
        self.current_session = None
        self.instruction_history = []
    
    def process_instruction(self, instruction):
        """处理用户输入的自然语言指令"""
        if not instruction or not isinstance(instruction, str):
            return {
                "success": False,
                "message": "无效的指令",
                "parsed_instruction": None
            }
        
        # 记录用户指令
        self.instruction_history.append(instruction)
        
        # 简单清理和预处理指令
        cleaned_instruction = instruction.strip()
        
        return {
            "success": True,
            "message": "指令已接收",
            "parsed_instruction": cleaned_instruction
        }
    
    def display_task_execution_result(self, result):
        """展示任务执行结果"""
        return {
            "success": result.get("success", False),
            "task_completed": result.get("task_completed", False),
            "message": result.get("message", "任务执行结果"),
            "details": {
                "task_plan": result.get("task_plan"),
                "execution_summary": self._format_execution_summary(result),
                "visual_feedback": result.get("screen_analysis")
            }
        }
    
    def _format_execution_summary(self, result):
        """格式化执行结果摘要"""
        if not result or "execution_result" not in result:
            return "无执行结果"
        
        execution_result = result["execution_result"]
        
        # 格式化操作步骤和结果
        steps = execution_result.get("steps", [])
        formatted_steps = []
        
        for i, step in enumerate(steps):
            formatted_steps.append({
                "step_number": i + 1,
                "action": step.get("action", "unknown"),
                "status": step.get("status", "unknown"),
                "details": step.get("details", "")
            })
        
        return {
            "total_steps": len(steps),
            "successful_steps": sum(1 for step in steps if step.get("status") == "success"),
            "failed_steps": sum(1 for step in steps if step.get("status") == "failed"),
            "steps": formatted_steps
        } 