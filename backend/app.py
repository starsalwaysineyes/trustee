from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
import time
from modules.user_interface import UserInterface
from modules.visual_perception import VisualPerception
from modules.task_understanding import TaskUnderstanding
from modules.operation_execution import OperationExecution
from modules.security_control import SecurityControl
from modules.windows_system import WindowsSystem

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 初始化各模块
ui = UserInterface()
visual = VisualPerception()
task = TaskUnderstanding()
operation = OperationExecution()
security = SecurityControl()
windows = WindowsSystem()

# 全局会话存储
sessions = {}

@app.route('/api/task/execute', methods=['POST'])
def execute_task():
    """处理用户的自然语言指令并执行任务"""
    data = request.json
    instruction = data.get('instruction', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    
    # 如果是新会话，创建会话记录
    if session_id not in sessions:
        sessions[session_id] = {
            'status': 'initialized',
            'history': [],
            'current_screen': None,
            'task_plan': None,
            'operation_sequence': None
        }
    
    # 记录用户指令
    sessions[session_id]['history'].append({
        'type': 'user_instruction',
        'content': instruction,
        'timestamp': time.time()
    })
    
    # 1. 解析用户指令
    task_plan = task.parse_instruction(instruction)
    sessions[session_id]['task_plan'] = task_plan
    
    # 2. 检查操作权限
    permission_result = security.check_operation_permission(task_plan)
    if not permission_result['granted']:
        return jsonify({
            'success': False,
            'message': '权限验证失败: ' + permission_result['reason'],
            'session_id': session_id
        })
    
    # 3. 捕获当前屏幕状态
    screen_state = visual.capture_screen()
    sessions[session_id]['current_screen'] = screen_state
    
    # 4. 结合屏幕状态细化任务
    operation_sequence = task.refine_task_with_screen(task_plan, screen_state)
    sessions[session_id]['operation_sequence'] = operation_sequence
    
    # 5. 执行操作序列
    execution_result = operation.execute_operation_sequence(operation_sequence)
    
    # 6. 捕获执行后屏幕状态
    post_execution_screen = visual.capture_screen()
    screen_analysis = visual.analyze_execution_result(post_execution_screen)
    
    # 7. 评估任务完成情况
    task_evaluation = task.evaluate_task_completion(screen_analysis, task_plan)
    
    # 如果任务未完成，调整策略
    if not task_evaluation['completed']:
        adjusted_operations = task.adjust_execution_strategy(task_evaluation, screen_analysis)
        execution_result = operation.execute_operation_sequence(adjusted_operations)
        post_execution_screen = visual.capture_screen()
        screen_analysis = visual.analyze_execution_result(post_execution_screen)
        task_evaluation = task.evaluate_task_completion(screen_analysis, task_plan)
    
    # 8. 记录操作日志
    security.record_operation_log(session_id, task_plan, operation_sequence, execution_result)
    
    # 9. 返回执行结果
    return jsonify({
        'success': True,
        'message': '任务执行完成',
        'session_id': session_id,
        'task_completed': task_evaluation['completed'],
        'result': {
            'task_plan': task_plan,
            'execution_result': execution_result,
            'screen_analysis': screen_analysis,
            'task_evaluation': task_evaluation
        }
    })

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取指定会话的详细信息"""
    if session_id not in sessions:
        return jsonify({
            'success': False,
            'message': '会话不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'session': sessions[session_id]
    })

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """接收用户对任务执行的反馈"""
    data = request.json
    session_id = data.get('session_id')
    feedback = data.get('feedback')
    
    if not session_id or session_id not in sessions:
        return jsonify({
            'success': False,
            'message': '会话不存在'
        }), 404
    
    # 记录用户反馈
    sessions[session_id]['history'].append({
        'type': 'user_feedback',
        'content': feedback,
        'timestamp': time.time()
    })
    
    # 更新任务知识库
    task.update_knowledge_base(feedback)
    
    return jsonify({
        'success': True,
        'message': '反馈已接收并处理'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 