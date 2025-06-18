#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试截图功能修复
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.screenshot_utils import capture_screen_with_fallback, generate_screenshot_filename

def test_screenshot_fix():
    """测试截图功能修复"""
    print("🧪 测试截图功能修复...")
    
    # 创建测试目录
    test_dir = "screenshots"
    os.makedirs(test_dir, exist_ok=True)
    
    # 生成测试文件名
    filename = generate_screenshot_filename("test_fix")
    filepath = os.path.join(test_dir, filename)
    
    print(f"📁 测试文件路径: {filepath}")
    
    # 执行截图
    success, screenshot, method_used = capture_screen_with_fallback(filepath)
    
    if success:
        print(f"✅ 截图成功！")
        print(f"   使用方法: {method_used}")
        print(f"   文件大小: {os.path.getsize(filepath)} 字节")
        print(f"   图像尺寸: {screenshot.size}")
        print(f"   保存路径: {filepath}")
        
        # 验证文件是否存在
        if os.path.exists(filepath):
            print("✅ 文件保存成功")
        else:
            print("❌ 文件保存失败")
            
    else:
        print("❌ 截图失败")
        print(f"   使用的方法: {method_used}")

if __name__ == "__main__":
    test_screenshot_fix() 