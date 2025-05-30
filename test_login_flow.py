#!/usr/bin/env python3
"""
Trustee 登录流程完整测试脚本
测试登录、跳转和所有主要页面的访问
"""

import requests
import time
import sys

BASE_URL = 'http://localhost:5000'

def test_login_flow():
    """测试完整的登录和页面访问流程"""
    session = requests.Session()
    
    print("🧪 开始测试 Trustee 登录流程...")
    print("=" * 50)
    
    # 测试1: 未登录时访问首页应该跳转到登录页
    print("1️⃣ 测试未登录时的重定向...")
    try:
        response = session.get(f'{BASE_URL}/', allow_redirects=True)
        if response.status_code == 200 and '登录' in response.text:
            print("✅ 未登录时正确跳转到登录页")
        else:
            print("❌ 未登录时跳转失败")
            return False
    except Exception as e:
        print(f"❌ 访问首页失败: {e}")
        return False
    
    # 测试2: 管理员登录
    print("\n2️⃣ 测试管理员登录...")
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        response = session.post(f'{BASE_URL}/api/login', json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 登录成功: {data.get('message')}")
                print(f"   用户信息: {data.get('user', {}).get('username')}")
            else:
                print(f"❌ 登录失败: {data.get('message')}")
                return False
        else:
            print(f"❌ 登录请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 登录请求异常: {e}")
        return False
    
    # 测试3: 登录后访问首页应该跳转到设备页面
    print("\n3️⃣ 测试登录后的重定向...")
    try:
        response = session.get(f'{BASE_URL}/', allow_redirects=True)
        if response.status_code == 200 and '设备管理' in response.text:
            print("✅ 登录后正确跳转到设备页面")
        else:
            print("❌ 登录后跳转失败")
            return False
    except Exception as e:
        print(f"❌ 访问首页失败: {e}")
        return False
    
    # 测试4: 访问各个页面
    pages = [
        ('/devices', '设备管理'),
        ('/tasks', '任务管理'),
        ('/ai-studio', 'AI工作室'),
    ]
    
    print("\n4️⃣ 测试各页面访问...")
    for url, expected_text in pages:
        try:
            response = session.get(f'{BASE_URL}{url}')
            if response.status_code == 200 and expected_text in response.text:
                print(f"✅ {url} 页面访问正常")
            else:
                print(f"❌ {url} 页面访问失败")
                return False
        except Exception as e:
            print(f"❌ 访问 {url} 异常: {e}")
            return False
    
    # 测试5: API调用
    print("\n5️⃣ 测试API访问...")
    api_endpoints = [
        ('/api/devices', '设备列表'),
        ('/api/tasks', '任务列表'),
        ('/api/dashboard/stats', '统计信息'),
    ]
    
    for endpoint, desc in api_endpoints:
        try:
            response = session.get(f'{BASE_URL}{endpoint}')
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ {desc} API 调用成功")
                else:
                    print(f"❌ {desc} API 返回失败")
                    return False
            else:
                print(f"❌ {desc} API 调用失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {desc} API 调用异常: {e}")
            return False
    
    # 测试6: 登出功能
    print("\n6️⃣ 测试登出功能...")
    try:
        response = session.post(f'{BASE_URL}/api/logout')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 登出成功")
            else:
                print("❌ 登出失败")
                return False
        else:
            print(f"❌ 登出请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 登出请求异常: {e}")
        return False
    
    # 测试7: 登出后访问保护页面应该返回401或重定向
    print("\n7️⃣ 测试登出后的访问控制...")
    try:
        response = session.get(f'{BASE_URL}/api/devices')
        if response.status_code == 401:
            print("✅ 登出后正确拒绝API访问")
        else:
            data = response.json()
            if not data.get('success'):
                print("✅ 登出后正确拒绝API访问")
            else:
                print("❌ 登出后仍可访问保护资源")
                return False
    except Exception as e:
        print(f"❌ 测试访问控制异常: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 Trustee 系统集成测试")
    print("请确保服务器正在运行: python3 api.py")
    print("")
    
    # 等待服务器启动
    print("⏳ 检查服务器状态...")
    try:
        response = requests.get(f'{BASE_URL}/login', timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print("❌ 服务器状态异常")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保服务器正在运行在 http://localhost:5000")
        sys.exit(1)
    
    print("")
    
    # 运行测试
    if test_login_flow():
        print("\n" + "=" * 50)
        print("🎉 所有测试通过！系统运行正常")
        print("\n🎊 可以开始使用 Trustee 系统了！")
        print("访问地址: http://localhost:5000")
        print("默认账号: admin / admin")
    else:
        print("\n" + "=" * 50)
        print("❌ 测试失败！请检查系统配置")
        sys.exit(1)

if __name__ == "__main__":
    main() 