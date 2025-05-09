import pyautogui
import time

# --- 鼠标控制函数 ---

def mouse_move_to(x: int, y: int, duration: float = 0.25):
    """
    将鼠标移动到指定的屏幕坐标。

    参数:
        x (int): 目标x坐标。
        y (int): 目标y坐标。
        duration (float): 移动鼠标所需的时间（秒）。默认为0.25秒。
    """
    try:
        pyautogui.moveTo(x, y, duration=duration)
        # print(f"鼠标已移动到: ({x}, {y})") # 可选：操作提示
    except Exception as e:
        print(f"鼠标移动失败: {e}")

def mouse_left_click(x: int = None, y: int = None, duration: float = 0.1, clicks: int = 1, interval: float = 0.1):
    """
    在指定坐标或当前鼠标位置执行鼠标左键单击。

    参数:
        x (int, optional): 单击的x坐标。如果为None，则在当前鼠标位置单击。
        y (int, optional): 单击的y坐标。如果为None，则在当前鼠标位置单击。
        duration (float): 如果提供了x, y，移动到目标位置所需的时间。默认为0.1秒。
        clicks (int): 点击次数。默认为1。
        interval (float): 多次点击之间的间隔时间（秒）。默认为0.1秒。
    """
    try:
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, duration=duration, clicks=clicks, interval=interval, button='left')
        else:
            pyautogui.click(clicks=clicks, interval=interval, button='left')
        # print(f"鼠标左键点击完成: 坐标=({x}, {y}) if provided else current") # 可选
    except Exception as e:
        print(f"鼠标左键点击失败: {e}")

def mouse_right_click(x: int = None, y: int = None, duration: float = 0.1):
    """
    在指定坐标或当前鼠标位置执行鼠标右键单击。

    参数:
        x (int, optional): 单击的x坐标。如果为None，则在当前鼠标位置单击。
        y (int, optional): 单击的y坐标。如果为None，则在当前鼠标位置单击。
        duration (float): 如果提供了x, y，移动到目标位置所需的时间。默认为0.1秒。
    """
    try:
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y, duration=duration, button='right')
        else:
            pyautogui.click(button='right')
        # print(f"鼠标右键点击完成: 坐标=({x}, {y}) if provided else current") # 可选
    except Exception as e:
        print(f"鼠标右键点击失败: {e}")

def mouse_left_press(x: int = None, y: int = None):
    """
    在指定坐标或当前鼠标位置按下鼠标左键（不松开）。

    参数:
        x (int, optional): 按下位置的x坐标。如果为None，则在当前鼠标位置操作。
        y (int, optional): 按下位置的y坐标。如果为None，则在当前鼠标位置操作。
    """
    try:
        if x is not None and y is not None:
            pyautogui.mouseDown(x=x, y=y, button='left')
        else:
            pyautogui.mouseDown(button='left')
        # print(f"鼠标左键已按下: 坐标=({x}, {y}) if provided else current") # 可选
    except Exception as e:
        print(f"鼠标左键按下失败: {e}")

def mouse_left_release(x: int = None, y: int = None):
    """
    在指定坐标或当前鼠标位置松开鼠标左键。

    参数:
        x (int, optional): 松开位置的x坐标。如果为None，则在当前鼠标位置操作。
        y (int, optional): 松开位置的y坐标。如果为None，则在当前鼠标位置操作。
    """
    try:
        if x is not None and y is not None:
            pyautogui.mouseUp(x=x, y=y, button='left')
        else:
            pyautogui.mouseUp(button='left')
        # print(f"鼠标左键已松开: 坐标=({x}, {y}) if provided else current") # 可选
    except Exception as e:
        print(f"鼠标左键松开失败: {e}")

def mouse_right_press(x: int = None, y: int = None):
    """
    在指定坐标或当前鼠标位置按下鼠标右键（不松开）。

    参数:
        x (int, optional): 按下位置的x坐标。如果为None，则在当前鼠标位置操作。
        y (int, optional): 按下位置的y坐标。如果为None，则在当前鼠标位置操作。
    """
    try:
        if x is not None and y is not None:
            pyautogui.mouseDown(x=x, y=y, button='right')
        else:
            pyautogui.mouseDown(button='right')
        # print(f"鼠标右键已按下: 坐标=({x}, {y}) if provided else current") # 可选
    except Exception as e:
        print(f"鼠标右键按下失败: {e}")

def mouse_right_release(x: int = None, y: int = None):
    """
    在指定坐标或当前鼠标位置松开鼠标右键。

    参数:
        x (int, optional): 松开位置的x坐标。如果为None，则在当前鼠标位置操作。
        y (int, optional): 松开位置的y坐标。如果为None，则在当前鼠标位置操作。
    """
    try:
        if x is not None and y is not None:
            pyautogui.mouseUp(x=x, y=y, button='right')
        else:
            pyautogui.mouseUp(button='right')
        # print(f"鼠标右键已松开: 坐标=({x}, {y}) if provided else current") # 可选
    except Exception as e:
        print(f"鼠标右键松开失败: {e}")

# --- 键盘控制函数 ---

def keyboard_press_key(key_name: str):
    """
    模拟按下并立即松开单个按键。
    对于组合键 (如 Ctrl+C)，请使用 keyboard_hotkey 函数。

    参数:
        key_name (str): 要按下的键名 (例如 'enter', 'a', 'ctrl', 'shift', 'f1', 'space')。
                        有效键名列表请参考 pyautogui 文档。
    """
    try:
        pyautogui.press(key_name)
        # print(f"按键 '{key_name}' 已按下并松开") # 可选
    except Exception as e:
        print(f"按键 '{key_name}' 操作失败: {e}")

def keyboard_key_down(key_name: str):
    """
    模拟按下单个按键（不松开）。

    参数:
        key_name (str): 要按下的键名。
    """
    try:
        pyautogui.keyDown(key_name)
        # print(f"按键 '{key_name}' 已按下") # 可选
    except Exception as e:
        print(f"按键 '{key_name}' 按下失败: {e}")

def keyboard_key_up(key_name: str):
    """
    模拟松开单个按键。

    参数:
        key_name (str): 要松开的键名。
    """
    try:
        pyautogui.keyUp(key_name)
        # print(f"按键 '{key_name}' 已松开") # 可选
    except Exception as e:
        print(f"按键 '{key_name}' 松开失败: {e}")

def keyboard_write_text(text: str, interval: float = 0.05):
    """
    模拟键盘输入一段文本（逐字按下）。

    参数:
        text (str): 要输入的文本。
        interval (float): 每个字符之间的输入间隔（秒）。默认为0.05秒。
    """
    try:
        pyautogui.write(text, interval=interval)
        # print(f"文本 '{text}' 已输入") # 可选
    except Exception as e:
        print(f"文本输入 '{text}' 失败: {e}")

def keyboard_hotkey(*args):
    """
    模拟按下组合键 (例如 Ctrl+Shift+Esc)。
    按键会按照传入的顺序按下，然后以相反的顺序松开。

    参数:
        *args (str): 一个或多个键名字符串。
    """
    try:
        pyautogui.hotkey(*args)
        # print(f"组合键 {args} 已执行") # 可选
    except Exception as e:
        print(f"组合键 {args} 操作失败: {e}")


if __name__ == '__main__':
    print("模拟键鼠操作测试开始...")
    print("请在5秒内将鼠标移动到安全区域，测试将开始移动鼠标并进行点击。")
    time.sleep(5)

    # 示例：鼠标操作
    print("\n--- 鼠标操作测试 ---")
    current_x, current_y = pyautogui.position() # 获取当前鼠标位置
    print(f"当前鼠标位置: ({current_x}, {current_y})")
    
    target_x, target_y = 300, 300
    print(f"1. 移动鼠标到 ({target_x}, {target_y})")
    mouse_move_to(target_x, target_y, duration=0.5)
    time.sleep(1)

    print("2. 在当前位置进行左键单击")
    mouse_left_click()
    time.sleep(1)

    print(f"3. 移动鼠标到 ({target_x + 100}, {target_y + 100}) 并进行右键单击")
    mouse_right_click(target_x + 100, target_y + 100)
    time.sleep(1)

    print("4. 模拟拖拽 (左键按下 -> 移动 -> 左键松开)")
    print(f"  - 在 ({target_x}, {target_y}) 按下左键")
    mouse_left_press(target_x, target_y)
    time.sleep(0.5)
    print(f"  - 移动到 ({target_x + 200}, {target_y + 50})")
    mouse_move_to(target_x + 200, target_y + 50, duration=1)
    time.sleep(0.5)
    print(f"  - 在当前位置松开左键")
    mouse_left_release()
    time.sleep(1)

    # 示例：键盘操作
    print("\n--- 键盘操作测试 ---")
    print("5. 输入文本 'Hello, PyAutoGUI!' (请确保焦点在文本输入框中，例如记事本)")
    print("   测试将在3秒后开始输入...")
    time.sleep(3)
    keyboard_write_text("Hello, PyAutoGUI!\n", interval=0.1)
    time.sleep(1)

    print("6. 按下 'enter' 键")
    keyboard_press_key('enter')
    time.sleep(1)

    print("7. 模拟按下 Ctrl+A (全选)")
    print("   测试将在2秒后开始...")
    time.sleep(2)
    keyboard_hotkey('ctrl', 'a')
    time.sleep(1)

    print("8. 模拟按下 'capslock'，等待1秒，再按一次松开 (切换大小写)")
    print("   测试将在2秒后开始...")
    time.sleep(2)
    keyboard_key_down('capslock')
    time.sleep(1)
    keyboard_key_up('capslock')
    print("   (再次按下以恢复原始状态)")
    keyboard_key_down('capslock')
    time.sleep(0.2)
    keyboard_key_up('capslock')
    time.sleep(1)

    print("\n模拟键鼠操作测试结束。")
    print("请检查操作结果。注意：某些操作（如键盘输入）需要有合适的窗口获取焦点。")
