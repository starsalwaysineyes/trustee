#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图功能测试脚本
用于诊断不同截图方法的可用性
"""

import os
import sys
from datetime import datetime

def test_pil_screenshot():
    """测试PIL ImageGrab截图"""
    print("🔍 测试PIL ImageGrab截图...")
    try:
        from PIL import ImageGrab
        screenshot = ImageGrab.grab()
        
        # 保存测试截图
        filename = f"test_pil_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join("screenshots", filename)
        os.makedirs("screenshots", exist_ok=True)
        
        screenshot.save(filepath)
        print(f"✅ PIL截图成功！保存为: {filepath}")
        print(f"   截图尺寸: {screenshot.size}")
        return True, filepath
        
    except Exception as e:
        print(f"❌ PIL截图失败: {e}")
        return False, str(e)

def test_pyautogui_screenshot():
    """测试PyAutoGUI截图"""
    print("🔍 测试PyAutoGUI截图...")
    try:
        import pyautogui
        
        # 禁用安全模式
        pyautogui.FAILSAFE = False
        
        screenshot = pyautogui.screenshot()
        
        # 保存测试截图
        filename = f"test_pyautogui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join("screenshots", filename)
        os.makedirs("screenshots", exist_ok=True)
        
        screenshot.save(filepath)
        print(f"✅ PyAutoGUI截图成功！保存为: {filepath}")
        print(f"   截图尺寸: {screenshot.size}")
        return True, filepath
        
    except Exception as e:
        print(f"❌ PyAutoGUI截图失败: {e}")
        return False, str(e)

def test_mss_screenshot():
    """测试MSS截图"""
    print("🔍 测试MSS截图...")
    try:
        import mss
        from PIL import Image
        
        with mss.mss() as sct:
            # 获取主显示器
            monitor = sct.monitors[1]
            print(f"   显示器信息: {monitor}")
            
            screenshot_data = sct.grab(monitor)
            
            # 转换为PIL Image
            screenshot = Image.frombytes("RGB", screenshot_data.size, screenshot_data.bgra, "raw", "BGRX")
            
            # 保存测试截图
            filename = f"test_mss_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            filepath = os.path.join("screenshots", filename)
            os.makedirs("screenshots", exist_ok=True)
            
            screenshot.save(filepath)
            print(f"✅ MSS截图成功！保存为: {filepath}")
            print(f"   截图尺寸: {screenshot.size}")
            return True, filepath
            
    except ImportError:
        print("❌ MSS库未安装，请运行: pip install mss")
        return False, "MSS库未安装"
    except Exception as e:
        print(f"❌ MSS截图失败: {e}")
        return False, str(e)

def test_system_info():
    """测试系统信息"""
    print("🖥️ 系统信息:")
    print(f"   操作系统: {os.name}")
    print(f"   Python版本: {sys.version}")
    
    try:
        import tkinter as tk
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        print(f"   屏幕分辨率: {screen_width}x{screen_height}")
    except Exception as e:
        print(f"   无法获取屏幕信息: {e}")

def main():
    """主测试函数"""
    print("🚀 开始截图功能诊断测试")
    print("=" * 50)
    
    # 测试系统信息
    test_system_info()
    print()
    
    # 测试各种截图方法
    methods = [
        ("PIL ImageGrab", test_pil_screenshot),
        ("PyAutoGUI", test_pyautogui_screenshot),
        ("MSS", test_mss_screenshot)
    ]
    
    results = []
    for method_name, test_func in methods:
        print(f"📸 测试 {method_name} 截图方法:")
        success, result = test_func()
        results.append((method_name, success, result))
        print()
    
    # 总结结果
    print("📊 测试结果总结:")
    print("=" * 50)
    
    working_methods = []
    for method_name, success, result in results:
        status = "✅ 可用" if success else "❌ 失败"
        print(f"{method_name}: {status}")
        if success:
            working_methods.append(method_name)
            print(f"   文件: {result}")
        else:
            print(f"   错误: {result}")
    
    print()
    if working_methods:
        print(f"🎉 可用的截图方法: {', '.join(working_methods)}")
        print("建议使用第一个可用的方法作为主要截图方案。")
    else:
        print("⚠️ 所有截图方法都失败了！")
        print("可能的解决方案:")
        print("1. 检查是否在远程桌面或虚拟环境中运行")
        print("2. 确保有图形界面访问权限")
        print("3. 尝试以管理员权限运行")
        print("4. 检查防病毒软件是否阻止了屏幕访问")

if __name__ == "__main__":
    main() 