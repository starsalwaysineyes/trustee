"""
Trustee 后端API服务
整合数据库操作、AI自动化和任务管理功能
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import traceback

# 导入数据库模块
from database.database import db_manager
from database.dao import TaskDAO, TaskStepDAO, ScreenshotDAO, AIAnalysisDAO, ExecutionDAO, UserDAO, DeviceDAO
from database.models import Task, TaskStep, Screenshot, AIAnalysis, Execution, User, Device
from database.workflow_service import WorkflowService

# 导入AI自动化服务
from LLM.ai_automation_service import AIAutomationService, AIAutomationWorkflow

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'trustee_secret_key_2024'  # 生产环境请使用更安全的密钥
CORS(app)

# 初始化服务
workflow_service = WorkflowService()
ai_automation_service = AIAutomationService()

# 确保数据库表存在
db_manager.create_database()

# ==================== 用户认证相关 ====================

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        # 硬编码admin用户验证（临时解决方案）
        if username == 'admin' and password == 'admin':
            # 创建一个临时session
            session['user_id'] = 1
            session['username'] = 'admin'
            return jsonify({
                'success': True,
                'message': '登录成功',
                'user': {
                    'id': 1,
                    'username': 'admin',
                    'email': 'admin@trustee.com',
                    'permission_level': 'admin'
                }
            })
        
        # 查找用户
        user = UserDAO.get_by_username(username)
        if user and user.password_hash == password:  # 简化版密码验证
            session['user_id'] = user.user_id
            session['username'] = user.username
            return jsonify({
                'success': True,
                'message': '登录成功',
                'user': {
                    'id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'permission_level': user.permission_level
                }
            })
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
            
    except Exception as e:
        logger.error(f"登录错误: {str(e)}")
        return jsonify({'success': False, 'message': '登录失败'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'success': False, 'message': '所有字段都是必填的'}), 400
        
        # 检查用户是否已存在
        existing_user = UserDAO.get_by_username(username)
        if existing_user:
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            password_hash=password,  # 实际应用中需要哈希加密
            permission_level='user'
        )
        
        user_id = UserDAO.create(user)
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user_id': user_id
        })
        
    except Exception as e:
        logger.error(f"注册错误: {str(e)}")
        return jsonify({'success': False, 'message': '注册失败'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True, 'message': '登出成功'})

# ==================== 设备管理API ====================

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取设备列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        devices = DeviceDAO.get_by_user_id(user_id)
        devices_data = []
        
        for device in devices:
            devices_data.append({
                'device_id': device.device_id,
                'device_name': device.device_name,
                'device_ip': device.device_ip,
                'device_type': device.device_type,
                'os_info': device.os_info,
                'screen_resolution': device.screen_resolution,
                'status': device.status,
                'created_at': device.created_at,
                'last_updated': device.last_updated
            })
        
        return jsonify({
            'success': True,
            'devices': devices_data,
            'total': len(devices_data)
        })
        
    except Exception as e:
        logger.error(f"获取设备列表错误: {str(e)}")
        return jsonify({'success': False, 'message': '获取设备列表失败'}), 500

@app.route('/api/devices', methods=['POST'])
def create_device():
    """创建新设备"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json()
        
        device = Device(
            device_name=data.get('device_name'),
            device_ip=data.get('device_ip'),
            device_type=data.get('device_type', 'computer'),
            os_info=data.get('os_info', ''),
            screen_resolution=data.get('screen_resolution', '1920x1080'),
            status='online',
            owner_user_id=user_id
        )
        
        device_id = DeviceDAO.create(device)
        
        return jsonify({
            'success': True,
            'message': '设备创建成功',
            'device_id': device_id
        })
        
    except Exception as e:
        logger.error(f"创建设备错误: {str(e)}")
        return jsonify({'success': False, 'message': '创建设备失败'}), 500

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """删除设备"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 验证设备所有权
        device = DeviceDAO.get_by_id(device_id)
        if not device or device.owner_user_id != user_id:
            return jsonify({'success': False, 'message': '设备不存在或无权限删除'}), 404
        
        # 删除设备
        success = DeviceDAO.delete(device_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '设备删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '删除设备失败'
            }), 500
        
    except Exception as e:
        logger.error(f"删除设备错误: {str(e)}")
        return jsonify({'success': False, 'message': '删除设备失败'}), 500

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """更新设备信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 验证设备所有权
        device = DeviceDAO.get_by_id(device_id)
        if not device or device.owner_user_id != user_id:
            return jsonify({'success': False, 'message': '设备不存在或无权限修改'}), 404
        
        data = request.get_json()
        
        # 更新设备属性
        if 'device_name' in data:
            device.device_name = data['device_name']
        if 'device_ip' in data:
            device.device_ip = data['device_ip']
        if 'device_type' in data:
            device.device_type = data['device_type']
        if 'os_info' in data:
            device.os_info = data['os_info']
        if 'screen_resolution' in data:
            device.screen_resolution = data['screen_resolution']
        if 'status' in data:
            device.status = data['status']
        
        success = DeviceDAO.update(device)
        
        if success:
            return jsonify({
                'success': True,
                'message': '设备更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '更新设备失败'
            }), 500
        
    except Exception as e:
        logger.error(f"更新设备错误: {str(e)}")
        return jsonify({'success': False, 'message': '更新设备失败'}), 500

# ==================== 任务管理API ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        status = request.args.get('status')  # 可选的状态过滤
        tasks = TaskDAO.get_by_user_id(user_id, status)
        
        tasks_data = []
        for task in tasks:
            # 获取任务的详细信息
            steps = TaskStepDAO.get_by_task_id(task.task_id)
            task_summary = workflow_service.get_task_summary(task.task_id)
            
            tasks_data.append({
                'task_id': task.task_id,
                'task_name': task.task_name,
                'task_description': task.task_description,
                'task_type': task.task_type,
                'natural_language_input': task.natural_language_input,
                'status': task.status,
                'priority': task.priority,
                'progress': task.progress_percentage,
                'completed_steps': task.completed_steps,
                'total_steps': task.total_steps,
                'created_at': task.created_at,
                'started_at': task.started_at,
                'completed_at': task.completed_at,
                'last_updated': task.last_updated,
                'estimated_duration': task.estimated_duration,
                'steps_count': len(steps),
                'total_cost': task_summary.get('total_cost', 0) if task_summary else 0
            })
        
        return jsonify({
            'success': True,
            'tasks': tasks_data,
            'total': len(tasks_data)
        })
        
    except Exception as e:
        logger.error(f"获取任务列表错误: {str(e)}")
        return jsonify({'success': False, 'message': '获取任务列表失败'}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """创建新任务"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json()
        
        # 创建任务
        task_id = workflow_service.create_task(
            user_id=user_id,
            task_name=data.get('task_name'),
            natural_language_input=data.get('natural_language_input'),
            device_id=data.get('device_id')
        )
        
        return jsonify({
            'success': True,
            'message': '任务创建成功',
            'task_id': task_id
        })
        
    except Exception as e:
        logger.error(f"创建任务错误: {str(e)}")
        return jsonify({'success': False, 'message': '创建任务失败'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task_detail(task_id):
    """获取任务详情"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取任务基本信息
        task = TaskDAO.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return jsonify({'success': False, 'message': '任务不存在或无权限访问'}), 404
        
        # 获取任务详细信息
        task_summary = workflow_service.get_task_summary(task_id)
        
        return jsonify({
            'success': True,
            'task': {
                'task_id': task.task_id,
                'task_name': task.task_name,
                'task_description': task.task_description,
                'natural_language_input': task.natural_language_input,
                'status': task.status,
                'priority': task.priority,
                'progress': task.progress_percentage,
                'created_at': task.created_at,
                'started_at': task.started_at,
                'completed_at': task.completed_at,
                'error_message': task.error_message
            },
            'summary': task_summary
        })
        
    except Exception as e:
        logger.error(f"获取任务详情错误: {str(e)}")
        return jsonify({'success': False, 'message': '获取任务详情失败'}), 500

@app.route('/api/tasks/<int:task_id>/execute', methods=['POST'])
def execute_task(task_id):
    """执行任务"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取任务信息
        task = TaskDAO.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return jsonify({'success': False, 'message': '任务不存在或无权限访问'}), 404
        
        # 开始执行任务
        success = workflow_service.start_task_execution(task_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '任务开始执行'
            })
        else:
            return jsonify({
                'success': False,
                'message': '任务执行失败'
            }), 500
        
    except Exception as e:
        logger.error(f"执行任务错误: {str(e)}")
        return jsonify({'success': False, 'message': '执行任务失败'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """删除任务"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 验证任务所有权
        task = TaskDAO.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return jsonify({'success': False, 'message': '任务不存在或无权限删除'}), 404
        
        # 如果任务正在运行，不允许删除
        if task.status == 'running':
            return jsonify({'success': False, 'message': '任务正在运行中，无法删除'}), 400
        
        # 删除任务及相关数据
        success = workflow_service.delete_task(task_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '任务删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '删除任务失败'
            }), 500
        
    except Exception as e:
        logger.error(f"删除任务错误: {str(e)}")
        return jsonify({'success': False, 'message': '删除任务失败'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """更新任务"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 验证任务所有权
        task = TaskDAO.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return jsonify({'success': False, 'message': '任务不存在或无权限修改'}), 404
        
        data = request.get_json()
        
        # 更新任务属性
        if 'task_name' in data:
            task.task_name = data['task_name']
        if 'task_description' in data:
            task.task_description = data['task_description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
        
        success = TaskDAO.update(task)
        
        if success:
            return jsonify({
                'success': True,
                'message': '任务更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '更新任务失败'
            }), 500
        
    except Exception as e:
        logger.error(f"更新任务错误: {str(e)}")
        return jsonify({'success': False, 'message': '更新任务失败'}), 500

# ==================== AI自动化API ====================

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze_screenshot():
    """AI分析截图"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 处理文件上传或接收base64图片
        if 'screenshot' in request.files:
            file = request.files['screenshot']
            if file.filename == '':
                return jsonify({'success': False, 'message': '未选择文件'}), 400
            
            # 保存上传的图片
            filename = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join(workflow_service.screenshot_dir, filename)
            file.save(filepath)
        else:
            data = request.get_json()
            filepath = data.get('image_path')
            if not filepath or not os.path.exists(filepath):
                return jsonify({'success': False, 'message': '图片路径无效'}), 400
        
        instruction = request.form.get('instruction') or request.get_json().get('instruction')
        if not instruction:
            return jsonify({'success': False, 'message': '请提供操作指令'}), 400
        
        # AI分析
        result = ai_automation_service.analyze_screenshot(
            image_path=filepath,
            user_instruction=instruction,
            show_visualization=False
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI分析错误: {str(e)}")
        return jsonify({'success': False, 'message': 'AI分析失败', 'error': str(e)}), 500

@app.route('/api/ai/execute', methods=['POST'])
def ai_execute_action():
    """执行AI生成的操作"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json()
        analysis_result = data.get('analysis_result')
        dry_run = data.get('dry_run', True)
        
        if not analysis_result:
            return jsonify({'success': False, 'message': '缺少分析结果'}), 400
        
        # 执行操作
        execution_result = ai_automation_service.execute_actions(
            analysis_result=analysis_result,
            dry_run=dry_run
        )
        
        return jsonify(execution_result)
        
    except Exception as e:
        logger.error(f"执行AI操作错误: {str(e)}")
        return jsonify({'success': False, 'message': '执行操作失败', 'error': str(e)}), 500

# ==================== 任务步骤和历史API ====================

@app.route('/api/tasks/<int:task_id>/steps', methods=['GET'])
def get_task_steps(task_id):
    """获取任务步骤列表"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 验证任务权限
        task = TaskDAO.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return jsonify({'success': False, 'message': '任务不存在或无权限访问'}), 404
        
        steps = TaskStepDAO.get_by_task_id(task_id)
        steps_data = []
        
        for step in steps:
            steps_data.append({
                'step_id': step.step_id,
                'step_sequence': step.step_sequence,
                'step_type': step.step_type,
                'step_description': step.step_description,
                'status': step.status,
                'created_at': step.created_at,
                'started_at': step.started_at,
                'completed_at': step.completed_at,
                'duration_ms': step.duration_ms,
                'screenshot_id': step.screenshot_id,
                'ai_analysis_id': step.ai_analysis_id,
                'execution_id': step.execution_id,
                'error_details': step.error_details
            })
        
        return jsonify({
            'success': True,
            'steps': steps_data,
            'total': len(steps_data)
        })
        
    except Exception as e:
        logger.error(f"获取任务步骤错误: {str(e)}")
        return jsonify({'success': False, 'message': '获取任务步骤失败'}), 500

@app.route('/api/history', methods=['GET'])
def get_execution_history():
    """获取执行历史"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取用户的所有已完成任务
        completed_tasks = TaskDAO.get_by_user_id(user_id, 'completed')
        failed_tasks = TaskDAO.get_by_user_id(user_id, 'failed')
        
        all_tasks = completed_tasks + failed_tasks
        
        # 按日期分组
        history_groups = {}
        
        for task in all_tasks:
            if task.completed_at:
                date_str = task.completed_at.split(' ')[0]  # 提取日期部分
                
                if date_str not in history_groups:
                    history_groups[date_str] = []
                
                history_groups[date_str].append({
                    'task_id': task.task_id,
                    'task_name': task.task_name,
                    'status': task.status,
                    'completed_at': task.completed_at,
                    'duration': task.actual_duration,
                    'progress': task.progress_percentage
                })
        
        # 转换为前端需要的格式
        history_data = []
        for date_str, tasks in sorted(history_groups.items(), reverse=True):
            history_data.append({
                'date': date_str,
                'tasks': tasks
            })
        
        return jsonify({
            'success': True,
            'history': history_data,
            'total': len(all_tasks)
        })
        
    except Exception as e:
        logger.error(f"获取执行历史错误: {str(e)}")
        return jsonify({'success': False, 'message': '获取执行历史失败'}), 500

# ==================== 统计信息API ====================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """获取仪表板统计信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取各种统计数据
        all_tasks = TaskDAO.get_by_user_id(user_id)
        running_tasks = TaskDAO.get_by_user_id(user_id, 'running')
        completed_tasks = TaskDAO.get_by_user_id(user_id, 'completed')
        failed_tasks = TaskDAO.get_by_user_id(user_id, 'failed')
        devices = DeviceDAO.get_by_user_id(user_id)
        
        # 计算成功率
        total_finished = len(completed_tasks) + len(failed_tasks)
        success_rate = (len(completed_tasks) / total_finished * 100) if total_finished > 0 else 0
        
        # 在线设备数
        online_devices = len([d for d in devices if d.status == 'online'])
        
        stats = {
            'total_tasks': len(all_tasks),
            'running_tasks': len(running_tasks),
            'completed_tasks': len(completed_tasks),
            'failed_tasks': len(failed_tasks),
            'success_rate': round(success_rate, 2),
            'total_devices': len(devices),
            'online_devices': online_devices,
            'offline_devices': len(devices) - online_devices
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"获取统计信息错误: {str(e)}")
        return jsonify({'success': False, 'message': '获取统计信息失败'}), 500

# ==================== 前端页面路由 ====================

@app.route('/')
def index():
    """主页 - 重定向到登录页面或设备页面"""
    if 'user_id' in session:
        return redirect('/devices')
    return redirect('/login')

@app.route('/login')
def login_page():
    """登录页面"""
    if 'user_id' in session:
        return redirect('/devices')
    return render_template('login.html')

@app.route('/devices')
def devices_page():
    """设备管理页面"""
    return render_template('devices.html')

@app.route('/tasks')
def task_list():
    """任务管理页面"""
    return render_template('tasks.html', current_page='tasks')

@app.route('/tasks/new')
def create_task_form():
    """创建任务页面"""
    return render_template('create_task.html', current_page='tasks')

@app.route('/tasks/<int:task_id>')
def task_detail(task_id):
    """任务详情页面"""
    return render_template('task_detail.html', current_page='tasks', task_id=task_id)

@app.route('/history')
def history_list():
    """执行历史页面"""
    return render_template('history.html', current_page='history')

@app.route('/ai-studio')
def ai_studio():
    """AI工作室页面"""
    return render_template('ai_studio.html', current_page='ai-studio')

# ==================== 错误处理 ====================

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success': False, 'message': '页面不存在'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 创建测试用户（如果不存在）
    test_user = UserDAO.get_by_username('admin')
    if not test_user:
        admin_user = User(
            username='admin',
            email='admin@trustee.com',
            password_hash='admin123',
            permission_level='admin'
        )
        UserDAO.create(admin_user)
        logger.info("已创建测试管理员用户: admin/admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 