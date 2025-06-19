"""
Trustee 后端API服务
整合数据库操作、AI自动化和任务管理功能
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import traceback
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# 导入数据库模块
from database.database import db_manager
from database.dao import TaskDAO, TaskStepDAO, ScreenshotDAO, AIAnalysisDAO, ExecutionDAO, UserDAO, DeviceDAO, AnalysisLogDAO
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

@app.route('/api/devices/test-connection', methods=['POST'])
def test_device_connection():
    """测试设备连接"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json()
        device_id = data.get('device_id')
        
        if not device_id:
            return jsonify({'success': False, 'message': '设备ID不能为空'}), 400
        
        # 验证设备所有权
        device = DeviceDAO.get_by_id(device_id)
        if not device or device.owner_user_id != user_id:
            return jsonify({'success': False, 'message': '设备不存在或无权限访问'}), 404
        
        # 测试网络连接
        import subprocess
        import time
        
        start_time = time.time()
        
        try:
            # 如果是本地设备
            if not device.device_ip or device.device_ip in ['localhost', '127.0.0.1', '0.0.0.0', '本机']:
                # 本地设备始终在线
                latency = int((time.time() - start_time) * 1000)
                
                # 更新设备状态
                device.status = 'online'
                device.last_seen = datetime.now()
                DeviceDAO.update(device)
                
                return jsonify({
                    'success': True,
                    'message': '本地设备连接正常',
                    'latency': latency,
                    'device_type': '本地设备'
                })
            
            # 对于远程设备，使用ping测试连接
            else:
                import platform
                system = platform.system().lower()
                
                if system == "windows":
                    cmd = ["ping", "-n", "1", "-w", "3000", device.device_ip]
                else:
                    cmd = ["ping", "-c", "1", "-W", "3", device.device_ip]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                latency = int((time.time() - start_time) * 1000)
                
                if result.returncode == 0:
                    # 连接成功，更新设备状态
                    device.status = 'online'
                    device.last_seen = datetime.now()
                    DeviceDAO.update(device)
                    
                    return jsonify({
                        'success': True,
                        'message': f'设备 {device.device_ip} 连接正常',
                        'latency': latency,
                        'device_type': '远程设备'
                    })
                else:
                    # 连接失败，更新设备状态
                    device.status = 'offline'
                    DeviceDAO.update(device)
                    
                    return jsonify({
                        'success': False,
                        'message': f'无法连接到设备 {device.device_ip}，请检查网络连接和IP地址',
                        'latency': latency
                    })
                    
        except subprocess.TimeoutExpired:
            device.status = 'offline'
            DeviceDAO.update(device)
            return jsonify({
                'success': False,
                'message': '连接超时，设备可能离线'
            })
        except Exception as e:
            logger.error(f"网络测试错误: {str(e)}")
            device.status = 'offline'
            DeviceDAO.update(device)
            return jsonify({
                'success': False,
                'message': f'连接测试失败: {str(e)}'
            })
            
    except Exception as e:
        logger.error(f"测试设备连接错误: {str(e)}")
        return jsonify({'success': False, 'message': '服务器错误'}), 500

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
        
        # 检查是否包含AI分析结果
        ai_analysis = data.get('ai_analysis')
        task_type = data.get('task_type', 'manual')
        
        # 创建任务
        task_id = workflow_service.create_task(
            user_id=user_id,
            task_name=data.get('task_name'),
            natural_language_input=data.get('natural_language_input'),
            device_id=data.get('device_id'),
            task_type=task_type
        )
        
        # 如果有AI分析结果，创建任务步骤
        if ai_analysis and task_type == 'ai_automation':
            # 保存AI分析记录
            # 如果有多轮分析，使用最终的置信度
            final_confidence = ai_analysis.get('confidence_score', 0.8)
            if 'multi_round_analysis' in ai_analysis:
                final_confidence = ai_analysis['multi_round_analysis'].get('final_confidence', final_confidence)
            
            analysis_id = AnalysisLogDAO.create_analysis_log(
                user_id=user_id,
                screenshot_id=None,  # 可以后续关联
                user_instruction=data.get('natural_language_input'),
                ai_response=ai_analysis.get('ai_response', ''),
                confidence_score=final_confidence,
                parsed_action=ai_analysis.get('parsed_action', {}),
                pyautogui_code=ai_analysis.get('pyautogui_code', ''),
                target_resolution=ai_analysis.get('target_resolution', 'auto')
            )
            
            # 创建任务步骤，包含完整的AI分析信息
            step_description = f"AI自动化执行: {data.get('natural_language_input')}"
            if 'multi_round_analysis' in ai_analysis:
                multi_round = ai_analysis['multi_round_analysis']
                step_description += f" (经过{multi_round.get('total_rounds', 1)}轮AI分析)"
            
            workflow_service.create_task_step(
                task_id=task_id,
                step_sequence=1,
                step_type='ai_automation',
                step_description=step_description,
                ai_analysis_id=analysis_id,
                execution_code=ai_analysis.get('pyautogui_code', '')
            )
            
            # 更新任务总步骤数
            task = TaskDAO.get_by_id(task_id)
            if task:
                task.total_steps = 1
                TaskDAO.update(task)
        
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
def analyze_screenshot_api():
    """AI分析截图的API端点"""
    if 'screenshot' not in request.files:
        return jsonify({"success": False, "error": "缺少截图文件"}), 400
    
    screenshot = request.files['screenshot']
    instruction = request.form.get('instruction')
    target_resolution = request.form.get('target_resolution', 'auto')
    # 如果未登录，默认使用 user_id=1 (管理员)
    user_id = session.get('user_id', 1)

    if not instruction:
        return jsonify({"success": False, "error": "缺少操作指令"}), 400

    # 保存截图文件
    screenshots_dir = app.config.get('SCREENSHOTS_FOLDER', 'screenshots')
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"upload_{user_id}_{timestamp}_{secure_filename(screenshot.filename)}"
    filepath = os.path.join(screenshots_dir, filename)
    screenshot.save(filepath)

    # 调用AI服务进行分析
    analysis_result = ai_automation_service.analyze_screenshot(
        user_id=user_id,
        image_path=filepath,
        user_instruction=instruction,
        target_resolution=target_resolution
    )

    if analysis_result.get("success"):
        return jsonify(analysis_result)
    else:
        return jsonify({"success": False, "error": analysis_result.get("error", "未知错误")}), 500

@app.route('/api/ai/execute', methods=['POST'])
def ai_execute_action():
    """执行AI生成的操作"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '缺少分析结果'}), 400
    
    analysis_result = data.get('analysis_result')
    dry_run = data.get('dry_run', True)
    
    # 执行操作
    execution_result = ai_automation_service.execute_actions(
        analysis_result=analysis_result,
        dry_run=dry_run
    )
    
    return jsonify(execution_result)

@app.route('/api/screenshot/capture', methods=['POST'])
def capture_screenshot():
    """自动截图API"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json() or {}
        delay = data.get('delay', 1000)  # 默认1秒延迟
        
        # 延迟一段时间，让用户准备
        import time
        time.sleep(delay / 1000.0)
        
        # 使用项目优化的截图工具模块
        from utils.screenshot_utils import capture_screen_with_fallback, generate_screenshot_filename
        
        # 生成文件名
        filename = generate_screenshot_filename("auto_screenshot")
        filepath = os.path.join(workflow_service.screenshot_dir, filename)
        
        # 使用带备用方案的截图功能
        success, screenshot, method_used = capture_screen_with_fallback(filepath)
        
        if not success:
            raise Exception("所有截图方法都失败了，请检查系统权限和环境配置")
        
        logger.info(f"截图成功，使用方法: {method_used}, 文件: {filename}")
        
        # 生成访问URL
        screenshot_url = f"/api/screenshot/{filename}"
        
        return jsonify({
            'success': True,
            'message': '截图成功',
            'filename': filename,
            'filepath': filepath,
            'screenshot_url': screenshot_url
        })
        
    except Exception as e:
        logger.error(f"自动截图错误: {str(e)}")
        return jsonify({'success': False, 'message': '自动截图失败', 'error': str(e)}), 500

@app.route('/api/screenshot/<filename>')
def get_screenshot(filename):
    """获取截图文件（包括原始截图和标注后的图片）"""
    return send_from_directory(app.config.get('SCREENSHOTS_FOLDER', 'screenshots'), filename)

@app.route('/api/remote/screenshot', methods=['POST'])
def capture_remote_screenshot():
    """远程设备截图接口"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json()
        device_id = data.get('device_id')
        device_ip = data.get('device_ip')
        
        if not device_id:
            return jsonify({'success': False, 'message': '设备ID不能为空'}), 400
        
        # 验证设备所有权
        device = DeviceDAO.get_by_id(device_id)
        if not device or device.owner_user_id != user_id:
            return jsonify({'success': False, 'message': '无权访问此设备'}), 403
        
        # 检查设备是否在线
        if device.status != 'online':
            return jsonify({'success': False, 'message': '设备离线，无法截图'}), 400
        
        # 如果是本地设备(没有IP或IP是本机)，直接截图
        if not device_ip or device_ip in ['localhost', '127.0.0.1', '0.0.0.0', '本机']:
            # 使用现有的截图功能
            from utils.screenshot_utils import capture_screen_with_fallback, generate_screenshot_filename
            import time
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = generate_screenshot_filename(f"remote_{device_id}")
            filepath = os.path.join(workflow_service.screenshot_dir, filename)
            
            # 使用带备用方案的截图功能
            success, screenshot, method_used = capture_screen_with_fallback(filepath)
            
            if not success:
                raise Exception("截图失败，请检查系统权限")
            
            # 获取分辨率信息
            resolution = f"{screenshot.width}x{screenshot.height}" if screenshot else "未知"
            
            logger.info(f"远程截图成功 - 设备: {device.device_name}, 方法: {method_used}")
            
            return jsonify({
                'success': True,
                'message': '远程截图成功',
                'filename': filename,
                'screenshot_url': f'/api/screenshot/{filename}',
                'resolution': resolution,
                'timestamp': timestamp,
                'device_name': device.device_name,
                'method_used': method_used
            })
            
        else:
            # 对于真正的远程设备，使用Trustee客户端协议
            logger.info(f"尝试连接远程设备 {device_ip}")
            
            try:
                import requests
                
                # 尝试连接Trustee客户端
                client_url = f"http://{device_ip}:8888"
                
                # 先测试连接
                try:
                    ping_response = requests.get(f"{client_url}/api/ping", timeout=5)
                    if ping_response.status_code != 200:
                        raise Exception("客户端响应异常")
                except Exception as e:
                    logger.warning(f"Trustee客户端连接失败: {str(e)}")
                    
                    # 回退到本地截图演示模式
                    from utils.screenshot_utils import capture_screen_with_fallback, generate_screenshot_filename
                    
                    filename = generate_screenshot_filename(f"remote_demo_{device_id}")
                    filepath = os.path.join(workflow_service.screenshot_dir, filename)
                    
                    success, screenshot, method_used = capture_screen_with_fallback(filepath)
                    
                    if success:
                        resolution = f"{screenshot.width}x{screenshot.height}" if screenshot else "未知"
                        
                        return jsonify({
                            'success': True,
                            'message': f'远程设备 {device_ip} 连接失败，显示本地屏幕作为演示',
                            'filename': filename,
                            'screenshot_url': f'/api/screenshot/{filename}',
                            'resolution': resolution,
                            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                            'device_name': device.device_name,
                            'method_used': f"本地演示({method_used})",
                            'note': f'无法连接到 {device_ip}:8888 上的Trustee客户端，请确保目标设备已安装并运行客户端程序'
                        })
                    else:
                        return jsonify({
                            'success': False,
                            'message': f'无法连接到远程设备 {device_ip}，且本地截图也失败'
                        }), 500
                
                # 发送截图请求到客户端
                screenshot_response = requests.post(f"{client_url}/api/screenshot", json={}, timeout=10)
                
                if screenshot_response.status_code == 200:
                    result = screenshot_response.json()
                    
                    if result.get('success'):
                        # 获取base64截图数据
                        screenshot_base64 = result.get('screenshot_base64')
                        
                        if screenshot_base64:
                            # 保存截图文件
                            import base64
                            from utils.screenshot_utils import generate_screenshot_filename
                            
                            filename = generate_screenshot_filename(f"remote_{device_id}")
                            filepath = os.path.join(workflow_service.screenshot_dir, filename)
                            
                            # 解码并保存图片
                            screenshot_data = base64.b64decode(screenshot_base64)
                            with open(filepath, 'wb') as f:
                                f.write(screenshot_data)
                            
                            logger.info(f"远程截图成功 - 设备: {device.device_name} ({device_ip})")
                            
                            return jsonify({
                                'success': True,
                                'message': f'远程设备 {device_ip} 截图成功',
                                'filename': filename,
                                'screenshot_url': f'/api/screenshot/{filename}',
                                'resolution': result.get('resolution', '未知'),
                                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                                'device_name': device.device_name,
                                'method_used': "Trustee客户端",
                                'remote_timestamp': result.get('timestamp')
                            })
                        else:
                            raise Exception("客户端返回的截图数据为空")
                    else:
                        raise Exception(result.get('message', '客户端截图失败'))
                else:
                    raise Exception(f"客户端响应错误: HTTP {screenshot_response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"远程连接错误: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'无法连接到远程设备 {device_ip}:8888，请检查: 1) 网络连接 2) 防火墙设置 3) Trustee客户端是否运行'
                }), 500
            except Exception as e:
                logger.error(f"远程截图错误: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'远程截图失败: {str(e)}'
                }), 500
        
    except Exception as e:
        logger.error(f"远程截图错误: {str(e)}")
        return jsonify({'success': False, 'message': f'远程截图失败: {str(e)}'}), 500

# ==================== 历史记录页面和API ====================
@app.route('/history')
def history_page():
    """渲染执行历史页面"""
    return render_template('history.html', current_page='history')

@app.route('/api/history/logs', methods=['GET'])
def get_history_logs():
    """分页获取AI分析历史记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        result = AnalysisLogDAO.get_analysis_logs_paginated(page, per_page)
        
        return jsonify({
            "success": True,
            "logs": [log.__dict__ for log in result["logs"]],
            "total": result["total"],
            "page": page,
            "per_page": per_page,
            "total_pages": (result["total"] + per_page - 1) // per_page
        })
    except Exception as e:
        logger.error(f"获取分析历史记录失败: {e}")
        return jsonify({"success": False, "error": "获取历史记录失败"}), 500

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
            step_data = {
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
            }
            
            # 如果有AI分析ID，获取AI分析详情
            if hasattr(step, 'ai_analysis_id') and step.ai_analysis_id:
                try:
                    # 从分析日志中获取AI分析信息
                    import json
                    analysis_logs = AnalysisLogDAO.get_analysis_logs_paginated(1, 1000)
                    for log in analysis_logs['logs']:
                        if hasattr(log, 'log_id') and log.log_id == step.ai_analysis_id:
                            if log.analysis_result_json:
                                analysis_data = json.loads(log.analysis_result_json)
                                step_data['ai_analysis'] = {
                                    'parsed_action': analysis_data.get('parsed_action', {}),
                                    'pyautogui_code': analysis_data.get('pyautogui_code', ''),
                                    'confidence_score': analysis_data.get('confidence_score', 0),
                                    'ai_response': analysis_data.get('ai_response', ''),
                                    'target_resolution': log.target_resolution,
                                    'multi_round_analysis': analysis_data.get('multi_round_analysis')  # 包含多轮分析信息
                                }
                            break
                except Exception as e:
                    logger.warning(f"获取AI分析详情失败: {str(e)}")
            
            steps_data.append(step_data)
        
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