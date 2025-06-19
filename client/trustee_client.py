#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trustee客户端程序
在远程设备上运行此程序，以接收来自Trustee主机的截图和控制请求

安装要求:
pip install flask pillow pyautogui requests

使用方法:
python trustee_client.py --host 0.0.0.0 --port 8888
"""

import argparse
import socket
import json
import base64
import io
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import pyautogui
from PIL import Image

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trustee_client.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TrusteeClient:
    def __init__(self, host='0.0.0.0', port=8888, server_ips=None):
        """
        初始化Trustee客户端
        
        Args:
            host: 监听地址
            port: 监听端口  
            server_ips: 允许连接的服务器IP列表
        """
        self.host = host
        self.port = port
        self.server_ips = server_ips or []
        self.app = Flask(__name__)
        self.setup_routes()
        
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.before_request
        def check_authorization():
            """检查请求来源"""
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            
            # 如果指定了允许的服务器IP，则进行验证
            if self.server_ips and client_ip not in self.server_ips:
                logger.warning(f"拒绝来自 {client_ip} 的连接")
                return jsonify({'success': False, 'message': '无权限访问'}), 403
        
        @self.app.route('/api/ping', methods=['GET'])
        def ping():
            """健康检查"""
            return jsonify({
                'success': True,
                'message': 'Trustee Client is running',
                'timestamp': datetime.now().isoformat(),
                'client_info': {
                    'screen_size': pyautogui.size()
                }
            })
        
        @self.app.route('/api/screenshot', methods=['POST'])
        def take_screenshot():
            """截图接口"""
            try:
                logger.info("收到截图请求")
                
                # 获取屏幕截图
                screenshot = pyautogui.screenshot()
                
                # 转换为base64
                buffer = io.BytesIO()
                screenshot.save(buffer, format='PNG')
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                # 获取屏幕信息
                screen_width, screen_height = pyautogui.size()
                
                logger.info(f"截图成功 - 分辨率: {screen_width}x{screen_height}")
                
                return jsonify({
                    'success': True,
                    'message': '截图成功',
                    'screenshot_base64': img_base64,
                    'resolution': f"{screen_width}x{screen_height}",
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"截图失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'截图失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/system-info', methods=['GET'])
        def get_system_info():
            """获取系统信息"""
            try:
                import platform
                import psutil
                
                system_info = {
                    'platform': platform.platform(),
                    'processor': platform.processor(),
                    'memory': psutil.virtual_memory()._asdict(),
                    'disk': psutil.disk_usage('/')._asdict(),
                    'screen_size': list(pyautogui.size()),
                    'hostname': socket.gethostname(),
                    'ip': socket.gethostbyname(socket.gethostname())
                }
                
                return jsonify({
                    'success': True,
                    'system_info': system_info
                })
                
            except Exception as e:
                logger.error(f"获取系统信息失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'获取系统信息失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/click', methods=['POST'])
        def click():
            """点击操作"""
            try:
                data = request.get_json()
                x = data.get('x')
                y = data.get('y')
                
                if x is None or y is None:
                    return jsonify({
                        'success': False, 
                        'message': '坐标参数不能为空'
                    }), 400
                
                pyautogui.click(x, y)
                logger.info(f"执行点击操作: ({x}, {y})")
                
                return jsonify({
                    'success': True,
                    'message': f'点击成功 ({x}, {y})'
                })
                
            except Exception as e:
                logger.error(f"点击操作失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'点击操作失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/type', methods=['POST'])
        def type_text():
            """文本输入"""
            try:
                data = request.get_json()
                text = data.get('text')
                
                if not text:
                    return jsonify({
                        'success': False,
                        'message': '文本内容不能为空'
                    }), 400
                
                pyautogui.typewrite(text)
                logger.info(f"执行文本输入: {text[:50]}...")
                
                return jsonify({
                    'success': True,
                    'message': f'文本输入成功'
                })
                
            except Exception as e:
                logger.error(f"文本输入失败: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': f'文本输入失败: {str(e)}'
                }), 500
    
    def run(self):
        """启动客户端服务"""
        logger.info(f"Trustee客户端启动")
        logger.info(f"监听地址: {self.host}:{self.port}")
        if self.server_ips:
            logger.info(f"允许的服务器IP: {', '.join(self.server_ips)}")
        else:
            logger.warning("未设置服务器IP白名单，任何IP都可以连接")
        logger.info(f"当前设备IP: {socket.gethostbyname(socket.gethostname())}")
        
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                threaded=True
            )
        except KeyboardInterrupt:
            logger.info("客户端服务已停止")
        except Exception as e:
            logger.error(f"客户端服务错误: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Trustee客户端程序')
    
    parser.add_argument(
        '--host', 
        default='0.0.0.0',
        help='监听地址 (默认: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port', 
        type=int, 
        default=8888,
        help='监听端口 (默认: 8888)'
    )
    
    parser.add_argument(
        '--server-ips',
        nargs='*',
        help='允许连接的服务器IP地址列表'
    )
    
    args = parser.parse_args()
    
    # 创建并启动客户端
    client = TrusteeClient(
        host=args.host,
        port=args.port,
        server_ips=args.server_ips
    )
    
    client.run()

if __name__ == '__main__':
    main() 