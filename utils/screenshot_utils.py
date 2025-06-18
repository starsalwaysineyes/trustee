#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图工具模块
基于项目现有的get_pic.py优化而来
"""

import os
import logging
from datetime import datetime
from PIL import ImageGrab, Image
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def capture_full_screen(imgpath: str, scale_factor: float = 0.5) -> bool:
    """
    截取完整屏幕并保存到指定的图像路径。
    
    参数:
        imgpath (str): 图像保存的完整路径 (例如: "D:/screenshots/screen.png")
        scale_factor (float): 缩放因子，默认0.5（缩放到原尺寸的50%）
        
    返回:
        bool: 截图是否成功
    """
    try:
        # 截取整个屏幕
        im = ImageGrab.grab()
        logger.info(f"截图成功，原始尺寸: {im.size}")
        
        # 获取原始尺寸
        original_width, original_height = im.size
        
        # 计算新尺寸
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        # 缩放图像
        resized_im = im.resize((new_width, new_height))
        logger.info(f"图像已缩放至: {resized_im.size}")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(imgpath), exist_ok=True)
        
        # 保存图像
        resized_im.save(imgpath)
        logger.info(f"屏幕截图已缩放并保存到: {imgpath}")
        
        return True
        
    except Exception as e:
        logger.error(f"截图失败: {e}")
        return False

def capture_screen_smart(imgpath: str, max_width: int = 1920, max_height: int = 1080) -> Tuple[bool, Optional[Image.Image]]:
    """
    智能截图：根据屏幕尺寸自动调整缩放比例
    
    参数:
        imgpath (str): 图像保存路径
        max_width (int): 最大宽度
        max_height (int): 最大高度
        
    返回:
        Tuple[bool, Optional[Image.Image]]: (是否成功, PIL图像对象)
    """
    try:
        # 截取整个屏幕
        screenshot = ImageGrab.grab()
        original_width, original_height = screenshot.size
        logger.info(f"原始截图尺寸: {original_width}x{original_height}")
        
        # 计算是否需要缩放
        if original_width > max_width or original_height > max_height:
            # 计算缩放比例，保持宽高比
            scale_factor = min(max_width / original_width, max_height / original_height)
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # 缩放图像
            screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.info(f"图像已智能缩放至: {new_width}x{new_height} (缩放比例: {scale_factor:.2f})")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(imgpath), exist_ok=True)
        
        # 保存图像
        screenshot.save(imgpath, optimize=True, quality=85)
        logger.info(f"智能截图已保存到: {imgpath}")
        
        return True, screenshot
        
    except Exception as e:
        logger.error(f"智能截图失败: {e}")
        return False, None

def capture_screen_with_fallback(imgpath: str) -> Tuple[bool, Optional[Image.Image], str]:
    """
    带备用方案的截图函数
    
    参数:
        imgpath (str): 图像保存路径
        
    返回:
        Tuple[bool, Optional[Image.Image], str]: (是否成功, PIL图像对象, 使用的方法)
    """
    methods = [
        ("PIL ImageGrab", _capture_with_pil),
        ("MSS", _capture_with_mss),
        ("PyAutoGUI", _capture_with_pyautogui)
    ]
    
    for method_name, capture_func in methods:
        try:
            logger.info(f"尝试使用 {method_name} 进行截图...")
            success, screenshot = capture_func()
            
            if success and screenshot:
                # 智能缩放
                original_width, original_height = screenshot.size
                if original_width > 1920 or original_height > 1080:
                    scale_factor = min(1920 / original_width, 1080 / original_height)
                    new_width = int(original_width * scale_factor)
                    new_height = int(original_height * scale_factor)
                    screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    logger.info(f"图像已缩放至: {new_width}x{new_height}")
                
                # 保存图像
                os.makedirs(os.path.dirname(imgpath), exist_ok=True)
                screenshot.save(imgpath, optimize=True, quality=85)
                logger.info(f"{method_name} 截图成功，已保存到: {imgpath}")
                
                return True, screenshot, method_name
                
        except Exception as e:
            logger.warning(f"{method_name} 截图失败: {e}")
            continue
    
    logger.error("所有截图方法都失败了")
    return False, None, "None"

def _capture_with_pil() -> Tuple[bool, Optional[Image.Image]]:
    """使用PIL ImageGrab截图"""
    try:
        screenshot = ImageGrab.grab()
        return True, screenshot
    except Exception as e:
        logger.debug(f"PIL截图失败: {e}")
        return False, None

def _capture_with_mss() -> Tuple[bool, Optional[Image.Image]]:
    """使用MSS截图"""
    try:
        import mss
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # 主显示器
            screenshot_data = sct.grab(monitor)
            
            # 转换为PIL Image
            screenshot = Image.frombytes("RGB", screenshot_data.size, screenshot_data.bgra, "raw", "BGRX")
            return True, screenshot
            
    except ImportError:
        logger.debug("MSS库未安装")
        return False, None
    except Exception as e:
        logger.debug(f"MSS截图失败: {e}")
        return False, None

def _capture_with_pyautogui() -> Tuple[bool, Optional[Image.Image]]:
    """使用PyAutoGUI截图"""
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        
        screenshot = pyautogui.screenshot()
        return True, screenshot
        
    except Exception as e:
        logger.debug(f"PyAutoGUI截图失败: {e}")
        return False, None

def generate_screenshot_filename(prefix: str = "screenshot", extension: str = "png") -> str:
    """
    生成带时间戳的截图文件名
    
    参数:
        prefix (str): 文件名前缀
        extension (str): 文件扩展名
        
    返回:
        str: 生成的文件名
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"

if __name__ == '__main__':
    # 测试截图功能
    test_dir = "screenshots"
    os.makedirs(test_dir, exist_ok=True)
    
    # 测试基础截图
    test_file1 = os.path.join(test_dir, generate_screenshot_filename("test_basic"))
    success1 = capture_full_screen(test_file1)
    print(f"基础截图测试: {'成功' if success1 else '失败'}")
    
    # 测试智能截图
    test_file2 = os.path.join(test_dir, generate_screenshot_filename("test_smart"))
    success2, img2 = capture_screen_smart(test_file2)
    print(f"智能截图测试: {'成功' if success2 else '失败'}")
    
    # 测试备用方案截图
    test_file3 = os.path.join(test_dir, generate_screenshot_filename("test_fallback"))
    success3, img3, method = capture_screen_with_fallback(test_file3)
    print(f"备用方案截图测试: {'成功' if success3 else '失败'}, 使用方法: {method}") 