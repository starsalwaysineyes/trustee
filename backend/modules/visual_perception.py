import time
import json
import base64
from datetime import datetime

class VisualPerception:
    """视觉感知层 - 负责屏幕内容捕获和UI元素识别"""
    
    def __init__(self):
        """初始化视觉感知层"""
        self.screen_capture_count = 0
        self.last_capture_time = None
        self.screen_history = []
    
    def capture_screen(self):
        """捕获当前屏幕状态
        
        在实际实现中，这里会调用屏幕捕获和OCR识别技术
        在此模拟实现中，返回一个模拟的屏幕状态
        """
        self.screen_capture_count += 1
        self.last_capture_time = datetime.now()
        
        # 模拟屏幕捕获结果
        screen_capture = {
            "timestamp": time.time(),
            "capture_id": f"screen_{self.screen_capture_count}",
            "resolution": {"width": 1920, "height": 1080},
            "elements": self._generate_mock_ui_elements(),
            "text_content": self._generate_mock_text_content()
        }
        
        # 存储屏幕历史记录
        self.screen_history.append({
            "capture_id": screen_capture["capture_id"],
            "timestamp": screen_capture["timestamp"]
        })
        
        return screen_capture
    
    def identify_ui_elements(self, screen_capture):
        """识别屏幕上的UI元素
        
        分析屏幕截图，识别其中的按钮、文本框、图标等UI元素
        """
        if not screen_capture:
            return []
        
        # 如果传入的是屏幕捕获ID，则从历史记录中查找
        if isinstance(screen_capture, str):
            for capture in self.screen_history:
                if capture["capture_id"] == screen_capture:
                    # 在实际实现中，这里应该返回存储的屏幕状态
                    return self._generate_mock_ui_elements()
            return []
        
        # 如果已经包含识别的元素，则直接返回
        if "elements" in screen_capture:
            return screen_capture["elements"]
        
        # 否则进行元素识别（这里是模拟实现）
        return self._generate_mock_ui_elements()
    
    def analyze_execution_result(self, screen_capture):
        """分析执行结果
        
        比较执行前后的屏幕状态，分析操作执行的效果
        """
        if not screen_capture:
            return {
                "success": False,
                "message": "无效的屏幕捕获"
            }
        
        # 在实际实现中，这里会比较执行前后的屏幕状态
        # 在此模拟实现中，随机生成分析结果
        
        ui_elements = self.identify_ui_elements(screen_capture)
        text_content = screen_capture.get("text_content", self._generate_mock_text_content())
        
        analysis_result = {
            "timestamp": time.time(),
            "screen_state_changed": True,
            "ui_elements_count": len(ui_elements),
            "text_content_count": len(text_content),
            "detected_changes": [
                {"type": "text_changed", "location": "main_content", "confidence": 0.95},
                {"type": "new_element", "element_type": "button", "location": "bottom_right", "confidence": 0.88}
            ],
            "operation_effect": {
                "visible_feedback": True,
                "expected_changes_found": True,
                "unexpected_changes": []
            }
        }
        
        return analysis_result
    
    def _generate_mock_ui_elements(self):
        """生成模拟的UI元素列表（用于演示）"""
        return [
            {
                "element_id": "btn_submit",
                "element_type": "button",
                "text": "提交",
                "bounding_box": {"x": 100, "y": 200, "width": 80, "height": 30},
                "is_enabled": True,
                "is_visible": True,
                "confidence": 0.98
            },
            {
                "element_id": "txt_input",
                "element_type": "textbox",
                "text": "",
                "bounding_box": {"x": 100, "y": 150, "width": 200, "height": 30},
                "is_enabled": True,
                "is_visible": True,
                "confidence": 0.95
            },
            {
                "element_id": "lbl_title",
                "element_type": "label",
                "text": "任务执行系统",
                "bounding_box": {"x": 50, "y": 50, "width": 200, "height": 40},
                "is_enabled": True,
                "is_visible": True,
                "confidence": 0.99
            }
        ]
    
    def _generate_mock_text_content(self):
        """生成模拟的文本内容（用于演示）"""
        return [
            {
                "text": "任务执行系统",
                "bounding_box": {"x": 50, "y": 50, "width": 200, "height": 40},
                "confidence": 0.99
            },
            {
                "text": "请输入执行指令：",
                "bounding_box": {"x": 50, "y": 120, "width": 150, "height": 20},
                "confidence": 0.97
            },
            {
                "text": "提交",
                "bounding_box": {"x": 100, "y": 200, "width": 80, "height": 30},
                "confidence": 0.98
            }
        ] 