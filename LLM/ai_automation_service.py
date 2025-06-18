"""
AI自动化服务
整合图像识别、AI分析、动作解析和代码生成的完整工作流
"""

import os
import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw
import pyautogui
import pyperclip
from datetime import datetime
import io

# 导入新的图像工具
from utils.image_utils import image_to_base64

# 导入DAO
from database.dao import AnalysisLogDAO
from database.models import AnalysisLog

# 导入现有模块的功能
from LLM.action_praser import (
    parse_action_to_structure_output,
    parsing_response_to_pyautogui_code,
)
from LLM.uitar import (
    draw_box_and_show,
    run as uitar_run,
    parse_action_output
)
# 导入坐标工具
from utils.coordinate_utils import parse_box_coordinates, scale_coordinates_to_absolute

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
    
    def analyze_screenshot(self, user_id: int, image_path: str, user_instruction: str, 
                          show_visualization: bool = False, target_resolution: str = "auto") -> Dict[str, Any]:
        """
        分析截图并生成操作指令
        
        Args:
            user_id: 当前操作的用户ID
            image_path: 图像文件路径
            user_instruction: 用户指令
            show_visualization: 是否显示可视化结果
            target_resolution: 目标分辨率 (格式如 "1920x1080" 或 "auto")
            
        Returns:
            Dict: 包含分析结果和操作指令的字典
        """
        try:
            # 1. 验证图像文件并转为Base64
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            with open(image_path, "rb") as f:
                original_screenshot_base64 = image_to_base64(f.read())

            # 2. 获取图像信息
            image = Image.open(image_path)
            original_width, original_height = image.size
            
            # 3. 调用AI分析
            start_time = time.time()
            ai_response = uitar_run(image_path, user_instruction)
            processing_time = int((time.time() - start_time) * 1000)
            
            # 4. 解析AI输出 (仅用于获取原始 thought 和 action)
            raw_parsed_action = json.loads(parse_action_output(ai_response))
            
            # 5. 生成结构化操作
            structured_actions = self._generate_structured_actions(
                ai_response, original_height, original_width
            )

            # 6. 核心坐标处理：解析、缩放
            self._process_and_scale_coordinates(structured_actions, target_resolution, (original_width, original_height))

            # 7. 生成PyAutoGUI代码
            pyautogui_code = parsing_response_to_pyautogui_code(structured_actions)
            
            # 8. 创建可视化图片并获取其Base64
            annotated_screenshot_base64 = self._create_visualization_image_base64(image, structured_actions)
            
            # 9. 构建返回结果 (现在返回base64)
            result = {
                "success": True,
                "user_id": user_id,
                "user_instruction": user_instruction,
                "target_resolution": target_resolution,
                "image_info": {
                    "path": image_path,
                    "size": (original_width, original_height)
                },
                "ai_response": {
                    "raw_text": ai_response,
                    "processing_time_ms": processing_time
                },
                "parsed_action": raw_parsed_action,
                "structured_actions": structured_actions,
                "pyautogui_code": pyautogui_code,
                "annotated_screenshot_base64": annotated_screenshot_base64,
                "timestamp": time.time()
            }
            
            # 10. 保存分析记录到数据库
            self._save_analysis_log(
                user_id=user_id,
                user_instruction=user_instruction,
                original_screenshot_base64=original_screenshot_base64,
                annotated_screenshot_base64=annotated_screenshot_base64,
                analysis_result=result,
                target_resolution=target_resolution
            )

            logger.info(f"分析完成，动作类型: {raw_parsed_action.get('action', 'unknown')}")
            return result
            
        except Exception as e:
            logger.error(f"分析截图时发生错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "user_id": user_id,
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
                task["user_id"], 
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
        """从AI原始响应生成结构化操作"""
        return parse_action_to_structure_output(
            ai_response,
            factor=1000.0,
            origin_resized_height=height,
            origin_resized_width=width,
            model_type=self.model_name
        )

    def _process_and_scale_coordinates(self, 
                                     actions: List[Dict[str, Any]], 
                                     target_resolution_str: str,
                                     original_img_size: Tuple[int, int]):
        """
        统一处理所有操作的坐标解析和缩放。
        该函数会直接修改 `actions` 列表中的字典。
        """
        # 1. 解析目标分辨率
        if target_resolution_str == "auto":
            try:
                target_resolution = pyautogui.size()
            except Exception:
                logger.warning("无法自动获取屏幕分辨率，将使用截图原始分辨率。")
                target_resolution = original_img_size
        else:
            try:
                target_w, target_h = map(int, target_resolution_str.split('x'))
                target_resolution = (target_w, target_h)
            except ValueError:
                logger.warning(f"无效的目标分辨率格式: {target_resolution_str}，将使用截图原始分辨率。")
                target_resolution = original_img_size

        # 2. 遍历所有动作，处理坐标
        for action in actions:
            inputs = action.get("action_inputs", {})
            
            # 处理 start_box
            if "start_box" in inputs:
                box_coords = parse_box_coordinates(inputs["start_box"])
                if box_coords:
                    abs_x, abs_y = scale_coordinates_to_absolute(box_coords, target_resolution)
                    inputs["abs_x"] = abs_x
                    inputs["abs_y"] = abs_y
                    # 可选：为拖拽操作保存起始点
                    inputs["start_abs_x"] = abs_x
                    inputs["start_abs_y"] = abs_y

            # 处理 end_box (用于拖拽)
            if "end_box" in inputs:
                box_coords = parse_box_coordinates(inputs["end_box"])
                if box_coords:
                    abs_x, abs_y = scale_coordinates_to_absolute(box_coords, target_resolution)
                    # 为拖拽操作保存结束点
                    inputs["end_abs_x"] = abs_x
                    inputs["end_abs_y"] = abs_y

    def _create_visualization_image_base64(self, 
                                           original_image: Image.Image, 
                                           actions: List[Dict[str, Any]]) -> Optional[str]:
        """
        在原始截图上绘制操作的可视化标记，并返回Base64编码。
        """
        if not actions:
            return None

        try:
            # (之前的逻辑保持不变，只是最后不保存文件而是返回base64)
            target_resolution = original_image.size
            draw_image = original_image.copy()
            draw = ImageDraw.Draw(draw_image)
            action = actions[0]
            inputs = action.get("action_inputs", {})
            box_str = inputs.get("start_box")
            if not box_str: return None
            box_coords = parse_box_coordinates(box_str)
            if not box_coords: return None
            abs_x, abs_y = scale_coordinates_to_absolute(box_coords, target_resolution)
            radius = 15
            box = [abs_x - radius, abs_y - radius, abs_x + radius, abs_y + radius]
            draw.ellipse(box, fill="red", outline="red")
            halo_radius = radius + 7
            halo_box = [abs_x - halo_radius, abs_y - halo_radius, abs_x + halo_radius, abs_y + halo_radius]
            draw.ellipse(halo_box, outline="yellow", width=5)

            # 将图片转换为Base64
            img_str = image_to_base64(draw_image)
            
            return img_str

        except Exception as e:
            logger.error(f"创建可视化图片Base64失败: {e}")
            return None

    def _save_analysis_log(self, user_id: int, user_instruction: str, 
                           original_screenshot_base64: str, 
                           annotated_screenshot_base64: Optional[str],
                           analysis_result: Dict[str, Any], target_resolution: str):
        """将分析结果保存到数据库"""
        try:
            log = AnalysisLog(
                user_id=user_id,
                timestamp=datetime.fromtimestamp(analysis_result['timestamp']),
                user_instruction=user_instruction,
                original_screenshot_base64=original_screenshot_base64,
                annotated_screenshot_base64=annotated_screenshot_base64,
                analysis_result_json=json.dumps(analysis_result, ensure_ascii=False, indent=2),
                target_resolution=target_resolution
            )
            log_id = AnalysisLogDAO.add_analysis_log(log)
            if log_id:
                logger.info(f"成功将分析记录保存到数据库，日志ID: {log_id}")
            else:
                logger.warning("保存分析记录到数据库失败。")
        except Exception as e:
            logger.error(f"保存分析记录到数据库时发生异常: {e}")


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
            result["user_id"],
            image_path, 
            instruction, 
            show_visualization=show_preview
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