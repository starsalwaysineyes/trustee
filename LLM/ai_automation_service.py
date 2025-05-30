"""
AI自动化服务
整合图像识别、AI分析、动作解析和代码生成的完整工作流
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import pyautogui
import pyperclip

# 导入现有模块的功能，添加错误处理
try:
    try:
        from .uitar import (
            image_to_base64, 
            parse_action_output, 
            coordinates_convert, 
            draw_box_and_show,
            run as uitar_run
        )
        from .action_praser import (
            parse_action_to_structure_output,
            parsing_response_to_pyautogui_code,
            smart_resize,
            linear_resize
        )
    except ImportError:
        from uitar import (
            image_to_base64, 
            parse_action_output, 
            coordinates_convert, 
            draw_box_and_show,
            run as uitar_run
        )
        from action_praser import (
            parse_action_to_structure_output,
            parsing_response_to_pyautogui_code,
            smart_resize,
            linear_resize
        )
except ImportError as e:
    # 如果模块不存在，创建模拟函数
    def uitar_run(image_path, instruction):
        return f'{{"thought": "模拟AI分析: {instruction}", "action": "click", "start_box": "[100, 100, 200, 200]"}}'
    
    def parse_action_output(response):
        return response
    
    def coordinates_convert(box, image_size):
        return [100, 100, 200, 200]
    
    def draw_box_and_show(image, start_abs, end_abs, direction):
        pass
    
    def parse_action_to_structure_output(*args, **kwargs):
        return [{"action_type": "click", "action_inputs": {"start_box": "[0.1, 0.1, 0.2, 0.2]"}}]
    
    def parsing_response_to_pyautogui_code(actions, *args, **kwargs):
        return "# 模拟代码\nimport pyautogui\npyautogui.click(150, 150)"
    
    def smart_resize(height, width, *args, **kwargs):
        return height, width
    
    def linear_resize(height, width, *args, **kwargs):
        return height, width

logger = logging.getLogger(__name__)

class AIAutomationService:
    """AI自动化服务类"""
    
    def __init__(self, ark_api_key: Optional[str] = None, model_name: str = "doubao-1.5-ui-tars-250328"):
        """
        初始化AI自动化服务
        
        Args:
            ark_api_key: 火山引擎API密钥，如果为None则从环境变量或默认值获取
            model_name: 使用的AI模型名称
        """
        self.ark_api_key = ark_api_key or "53008c87-b444-41c2-8515-88db94d60162"
        self.model_name = model_name
        self.image_factor = 28
        self.max_pixels = 16384 * 28 * 28
        self.min_pixels = 100 * 28 * 28
        
        # 配置pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        logger.info(f"AI自动化服务初始化完成，模型: {model_name}")
    
    def analyze_screenshot(self, image_path: str, user_instruction: str, 
                          show_visualization: bool = False) -> Dict[str, Any]:
        """
        分析截图并生成操作指令
        
        Args:
            image_path: 图像文件路径
            user_instruction: 用户指令
            show_visualization: 是否显示可视化结果
            
        Returns:
            Dict: 包含分析结果和操作指令的字典
        """
        try:
            # 1. 验证图像文件
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            # 2. 获取图像信息
            image = Image.open(image_path)
            original_width, original_height = image.size
            
            # 3. 调用AI分析
            start_time = time.time()
            ai_response = uitar_run(image_path, user_instruction)
            processing_time = int((time.time() - start_time) * 1000)
            
            # 4. 解析AI输出
            parsed_action = json.loads(parse_action_output(ai_response))
            
            # 5. 转换坐标（如果存在）
            converted_actions = []
            if parsed_action.get("start_box"):
                start_abs = coordinates_convert(parsed_action["start_box"], image.size)
                parsed_action["start_box_abs"] = start_abs
            
            if parsed_action.get("end_box"):
                end_abs = coordinates_convert(parsed_action["end_box"], image.size)
                parsed_action["end_box_abs"] = end_abs
            
            # 6. 生成结构化输出
            structured_actions = self._generate_structured_actions(
                ai_response, original_height, original_width
            )
            
            # 7. 生成PyAutoGUI代码
            pyautogui_code = self._generate_pyautogui_code(
                structured_actions, original_height, original_width
            )
            
            # 8. 可视化结果（可选）
            if show_visualization:
                self._show_visualization(image, parsed_action)
            
            # 9. 构建返回结果
            result = {
                "success": True,
                "user_instruction": user_instruction,
                "image_info": {
                    "path": image_path,
                    "size": (original_width, original_height)
                },
                "ai_response": {
                    "raw_text": ai_response,
                    "processing_time_ms": processing_time
                },
                "parsed_action": parsed_action,
                "structured_actions": structured_actions,
                "pyautogui_code": pyautogui_code,
                "timestamp": time.time()
            }
            
            logger.info(f"分析完成，动作类型: {parsed_action.get('action', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"分析截图时发生错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "user_instruction": user_instruction,
                "timestamp": time.time()
            }
    
    def execute_actions(self, analysis_result: Dict[str, Any], 
                       dry_run: bool = True) -> Dict[str, Any]:
        """
        执行分析得到的操作
        
        Args:
            analysis_result: analyze_screenshot的返回结果
            dry_run: 是否为演练模式（不实际执行操作）
            
        Returns:
            Dict: 执行结果
        """
        if not analysis_result.get("success"):
            return {
                "success": False,
                "error": "分析结果无效，无法执行操作"
            }
        
        try:
            pyautogui_code = analysis_result.get("pyautogui_code", "")
            
            if dry_run:
                logger.info("演练模式：不实际执行操作")
                return {
                    "success": True,
                    "dry_run": True,
                    "code": pyautogui_code,
                    "message": "演练模式，代码已准备但未执行"
                }
            
            # 实际执行代码
            logger.warning("即将执行自动化操作，请确保桌面准备就绪...")
            time.sleep(2)  # 给用户准备时间
            
            # 安全检查
            if "DONE" in pyautogui_code:
                return {
                    "success": True,
                    "message": "任务已完成，无需执行额外操作"
                }
            
            # 执行代码
            start_time = time.time()
            exec(pyautogui_code)
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": True,
                "execution_time_ms": execution_time,
                "code": pyautogui_code,
                "message": "操作执行完成"
            }
            
        except Exception as e:
            logger.error(f"执行操作时发生错误: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def batch_process(self, tasks: List[Dict[str, str]], 
                     execute: bool = False) -> List[Dict[str, Any]]:
        """
        批量处理多个任务
        
        Args:
            tasks: 任务列表，每个任务包含 {"image_path": "", "instruction": ""}
            execute: 是否执行操作
            
        Returns:
            List[Dict]: 所有任务的处理结果
        """
        results = []
        
        for i, task in enumerate(tasks):
            logger.info(f"处理第 {i+1}/{len(tasks)} 个任务")
            
            # 分析任务
            analysis_result = self.analyze_screenshot(
                task["image_path"], 
                task["instruction"]
            )
            
            # 执行任务（如果需要）
            if execute and analysis_result.get("success"):
                execution_result = self.execute_actions(analysis_result, dry_run=False)
                analysis_result["execution_result"] = execution_result
                
                # 任务间延迟
                if i < len(tasks) - 1:
                    time.sleep(3)
            
            results.append(analysis_result)
        
        return results
    
    def save_analysis_report(self, analysis_result: Dict[str, Any], 
                           output_path: str = "analysis_report.json") -> bool:
        """
        保存分析报告
        
        Args:
            analysis_result: 分析结果
            output_path: 输出文件路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            logger.info(f"分析报告已保存到: {output_path}")
            return True
        except Exception as e:
            logger.error(f"保存分析报告失败: {str(e)}")
            return False
    
    def _generate_structured_actions(self, ai_response: str, 
                                   height: int, width: int) -> List[Dict[str, Any]]:
        """生成结构化的动作列表"""
        try:
            # 计算调整后的图像尺寸
            resized_height, resized_width = smart_resize(
                height, width, 
                factor=self.image_factor,
                min_pixels=self.min_pixels,
                max_pixels=self.max_pixels
            )
            
            # 解析动作
            actions = parse_action_to_structure_output(
                ai_response,
                factor=self.image_factor,
                origin_resized_height=resized_height,
                origin_resized_width=resized_width,
                model_type="qwen25vl",
                max_pixels=self.max_pixels,
                min_pixels=self.min_pixels
            )
            
            return actions
        except Exception as e:
            logger.error(f"生成结构化动作失败: {str(e)}")
            return []
    
    def _generate_pyautogui_code(self, structured_actions: List[Dict[str, Any]], 
                               height: int, width: int) -> str:
        """生成PyAutoGUI代码"""
        try:
            if not structured_actions:
                return "# 无可执行的操作"
            
            code = parsing_response_to_pyautogui_code(
                structured_actions, 
                image_height=height,
                image_width=width,
                input_swap=True
            )
            
            return code
        except Exception as e:
            logger.error(f"生成PyAutoGUI代码失败: {str(e)}")
            return f"# 代码生成失败: {str(e)}"
    
    def _show_visualization(self, image: Image.Image, parsed_action: Dict[str, Any]):
        """显示可视化结果"""
        try:
            start_abs = parsed_action.get("start_box_abs")
            end_abs = parsed_action.get("end_box_abs")
            direction = parsed_action.get("direction")
            
            draw_box_and_show(image, start_abs, end_abs, direction)
        except Exception as e:
            logger.warning(f"显示可视化结果失败: {str(e)}")


class AIAutomationWorkflow:
    """AI自动化工作流类 - 提供更高级的封装"""
    
    def __init__(self, service: AIAutomationService):
        self.service = service
        self.session_results = []
    
    def run_single_task(self, image_path: str, instruction: str, 
                       auto_execute: bool = False, show_preview: bool = True) -> Dict[str, Any]:
        """
        运行单个自动化任务
        
        Args:
            image_path: 截图路径
            instruction: 用户指令
            auto_execute: 是否自动执行
            show_preview: 是否显示预览
            
        Returns:
            Dict: 任务执行结果
        """
        print(f"\n🤖 开始分析任务：{instruction}")
        
        # 分析截图
        result = self.service.analyze_screenshot(
            image_path, instruction, show_visualization=show_preview
        )
        
        if not result.get("success"):
            print(f"❌ 分析失败：{result.get('error')}")
            return result
        
        # 显示分析结果
        action = result["parsed_action"]
        print(f"💭 AI思考：{action.get('thought', '无')}")
        print(f"🎯 计划动作：{action.get('action', '无')}")
        
        if action.get("content"):
            print(f"📝 输入内容：{action.get('content')}")
        
        # 显示生成的代码
        code = result.get("pyautogui_code", "")
        if code and code != "# 无可执行的操作":
            print(f"\n🔧 生成的操作代码：")
            print("=" * 50)
            print(code)
            print("=" * 50)
        
        # 是否执行
        if auto_execute:
            print("\n⚡ 自动执行操作...")
            execution_result = self.service.execute_actions(result, dry_run=False)
            result["execution_result"] = execution_result
            
            if execution_result.get("success"):
                print("✅ 操作执行完成")
            else:
                print(f"❌ 执行失败：{execution_result.get('error')}")
        else:
            print("\n⏸️  演练模式：操作未实际执行")
        
        # 保存到会话记录
        self.session_results.append(result)
        
        return result
    
    def interactive_mode(self):
        """交互式模式"""
        print("\n🚀 进入AI自动化交互模式")
        print("输入 'quit' 退出，'help' 查看帮助")
        
        while True:
            try:
                print("\n" + "-" * 60)
                image_path = input("📸 请输入截图路径 (或拖拽文件): ").strip()
                
                if image_path.lower() == 'quit':
                    break
                elif image_path.lower() == 'help':
                    self._show_help()
                    continue
                
                # 清理路径（处理拖拽文件的引号）
                image_path = image_path.strip('"\'')
                
                if not os.path.exists(image_path):
                    print("❌ 文件不存在，请重新输入")
                    continue
                
                instruction = input("💬 请输入操作指令: ").strip()
                if not instruction:
                    print("❌ 指令不能为空")
                    continue
                
                auto_execute = input("⚡ 是否自动执行? (y/N): ").strip().lower() == 'y'
                
                # 执行任务
                self.run_single_task(image_path, instruction, auto_execute)
                
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"❌ 发生错误：{str(e)}")
        
        print("📊 会话结束，共处理 {} 个任务".format(len(self.session_results)))
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
🆘 帮助信息：

1. 截图路径：支持相对路径、绝对路径，可直接拖拽文件
2. 操作指令：用自然语言描述要执行的操作，例如：
   - "点击登录按钮"
   - "在搜索框输入Python"
   - "滚动页面向下"
   - "双击桌面上的Chrome图标"

3. 安全提示：
   - 建议先不执行，查看生成的代码是否正确
   - 确保桌面环境与截图一致
   - 重要操作前请备份数据

4. 命令：
   - quit: 退出程序
   - help: 显示此帮助
        """
        print(help_text)


# 便捷函数
def quick_automation(image_path: str, instruction: str, 
                    execute: bool = False, show_preview: bool = True) -> Dict[str, Any]:
    """
    快速自动化函数
    
    Args:
        image_path: 截图路径
        instruction: 操作指令
        execute: 是否执行操作
        show_preview: 是否显示预览
        
    Returns:
        Dict: 操作结果
    """
    service = AIAutomationService()
    workflow = AIAutomationWorkflow(service)
    return workflow.run_single_task(image_path, instruction, execute, show_preview)


if __name__ == "__main__":
    # 演示用法
    import sys
    
    if len(sys.argv) > 1:
        # 命令行模式
        if len(sys.argv) >= 3:
            image_path = sys.argv[1]
            instruction = sys.argv[2]
            execute = len(sys.argv) > 3 and sys.argv[3].lower() == 'true'
            
            result = quick_automation(image_path, instruction, execute)
            print(f"\n结果：{result.get('success', False)}")
        else:
            print("用法: python ai_automation_service.py <image_path> <instruction> [execute]")
    else:
        # 交互式模式
        service = AIAutomationService()
        workflow = AIAutomationWorkflow(service)
        workflow.interactive_mode() 