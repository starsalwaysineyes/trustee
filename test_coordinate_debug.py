"""
调试坐标转换问题的测试脚本
"""
import sys
sys.path.append('LLM')

from action_praser import parse_action_to_structure_output, parsing_response_to_pyautogui_code
import json

def test_coordinate_conversion():
    """测试坐标转换流程"""
    print("=== 坐标转换流程调试 ===")
    
    # 模拟AI输出（包含坐标 [987,42,987,42]）
    ai_response = """Thought: 我看到浏览器窗口右上角有个"x"按钮，这正是我要找的。关闭窗口的操作很简单，只要点击一下这个按钮就可以了。

Action: click(start_box='<bbox>987 42 987 42</bbox>')"""
    
    print(f"1. AI原始输出: {ai_response}")
    
    # 步骤1: parse_action_to_structure_output
    try:
        actions = parse_action_to_structure_output(
            text=ai_response,
            factor=28,
            origin_resized_height=1000,
            origin_resized_width=1000,
            model_type="qwen25vl"
        )
        print(f"2. 解析后的动作: {json.dumps(actions, indent=2, ensure_ascii=False)}")
        
        if actions and len(actions) > 0:
            action = actions[0]
            start_box = action.get('action_inputs', {}).get('start_box')
            print(f"3. 提取的start_box: {start_box}")
            
            if start_box:
                # 解析坐标
                coords = eval(start_box)
                print(f"4. 坐标数组: {coords}")
                print(f"5. 坐标类型检测: {[0 <= coord <= 1 for coord in coords]}")
                print(f"6. 是否全部在0-1范围: {all(0 <= coord <= 1 for coord in coords)}")
                
                # 模拟缩放逻辑
                target_width, target_height = 2560, 1600
                if len(coords) == 4:
                    x1, y1, x2, y2 = coords
                    if all(0 <= coord <= 1 for coord in coords):
                        # 归一化坐标处理
                        scaled_x1 = int(x1 * target_width)
                        scaled_y1 = int(y1 * target_height)
                        scaled_x2 = int(x2 * target_width)
                        scaled_y2 = int(y2 * target_height)
                        print(f"7. 归一化坐标缩放: [{scaled_x1},{scaled_y1},{scaled_x2},{scaled_y2}]")
                    else:
                        # 像素坐标处理
                        scale_x = target_width / 1000.0
                        scale_y = target_height / 1000.0
                        scaled_x1 = int(x1 * scale_x)
                        scaled_y1 = int(y1 * scale_y)
                        scaled_x2 = int(x2 * scale_x)
                        scaled_y2 = int(y2 * scale_y)
                        print(f"7. 像素坐标缩放: [{scaled_x1},{scaled_y1},{scaled_x2},{scaled_y2}]")
                    
                    # 计算最终点击坐标
                    final_x = (scaled_x1 + scaled_x2) / 2
                    final_y = (scaled_y1 + scaled_y2) / 2
                    print(f"8. 最终点击坐标: ({final_x}, {final_y})")
                    
                    # 使用parsing_response_to_pyautogui_code测试
                    test_action = {
                        'action_type': 'click',
                        'action_inputs': {
                            'start_box': f"[{scaled_x1},{scaled_y1},{scaled_x2},{scaled_y2}]"
                        }
                    }
                    
                    code = parsing_response_to_pyautogui_code(
                        [test_action], 
                        image_height=1,
                        image_width=1
                    )
                    print(f"9. 生成的PyAutoGUI代码:")
                    print(code)
                    
    except Exception as e:
        print(f"解析出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coordinate_conversion()