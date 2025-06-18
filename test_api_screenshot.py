#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试截图API功能
"""

import requests
import json
import time

def test_screenshot_api():
    """测试截图API"""
    print("🧪 测试截图API功能...")
    
    # API端点
    url = "http://127.0.0.1:5000/api/screenshot/capture"
    
    # 请求数据
    data = {
        "delay": 1000
    }
    
    try:
        print("📡 发送截图请求...")
        response = requests.post(
            url, 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 截图API调用成功！")
            print(f"   文件名: {result.get('filename', 'N/A')}")
            print(f"   文件路径: {result.get('filepath', 'N/A')}")
            print(f"   访问URL: {result.get('screenshot_url', 'N/A')}")
            
            # 测试文件访问
            if 'screenshot_url' in result:
                file_url = f"http://127.0.0.1:5000{result['screenshot_url']}"
                print(f"🔗 测试文件访问: {file_url}")
                
                file_response = requests.get(file_url, timeout=5)
                if file_response.status_code == 200:
                    print(f"✅ 文件访问成功！文件大小: {len(file_response.content)} 字节")
                else:
                    print(f"❌ 文件访问失败: {file_response.status_code}")
            
        elif response.status_code == 401:
            print("❌ 需要登录认证")
            print("提示: 请先在浏览器中登录，然后再测试")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            try:
                error_info = response.json()
                print(f"   错误信息: {error_info.get('message', 'Unknown error')}")
            except:
                print(f"   响应内容: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 服务器未运行或端口不可访问")
        print("请确保运行了: python api.py")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    print("🚀 开始测试截图API功能")
    print("=" * 50)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(2)
    
    test_screenshot_api()

if __name__ == "__main__":
    main() 