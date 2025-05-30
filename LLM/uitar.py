from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import base64
import re
import json
import math
from pathlib import Path
import os

# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime._exceptions import ArkAPIError
from volcenginesdkarkruntime import Ark


def parse_action_output(output_text):
    # 提取Thought部分
    thought_match = re.search(r'Thought:(.*?)\nAction:', output_text, re.DOTALL)
    thought = thought_match.group(1).strip() if thought_match else ""

    # 提取Action部分
    action_match = re.search(r'Action:(.*?)(?:\n|$)', output_text, re.DOTALL)
    action_text = action_match.group(1).strip() if action_match else ""

    # 初始化结果字典
    result = {
        "thought": thought,
        "action": "",
        "key": None,
        "content": None,
        "start_box": None,
        "end_box": None,
        "direction": None
    }

    if not action_text:
        return json.dumps(result, ensure_ascii=False)

    # 解析action类型
    action_parts = action_text.split('(')
    action_type = action_parts[0]
    result["action"] = action_type

    # 解析参数
    if len(action_parts) > 1:
        params_text = action_parts[1].rstrip(')')
        params = {}

        # 处理键值对参数
        for param in params_text.split(','):
            param = param.strip()
            if '=' in param:
                key, value = param.split('=', 1)
                key = key.strip()
                value = value.strip().strip('\'"')

                # 处理bbox格式
                if 'box' in key:
                    # 提取坐标数字
                    numbers = re.findall(r'\d+', value)
                    if numbers:
                        coords = [int(num) for num in numbers]
                        if len(coords) == 4:
                            if key == 'start_box':
                                result["start_box"] = coords
                            elif key == 'end_box':
                                result["end_box"] = coords
                elif key == 'key':
                    result["key"] = value
                elif key == 'content':
                    # 处理转义字符
                    value = value.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
                    result["content"] = value
                elif key == 'direction':
                    result["direction"] = value

    return json.dumps(result, ensure_ascii=False, indent=2)


def coordinates_convert(relative_bbox, img_size):
    """
       将相对坐标[0,1000]转换为图片上的绝对像素坐标

       参数:
           relative_bbox: 相对坐标列表/元组 [x1, y1, x2, y2] (范围0-1000)
           img_size: 图片尺寸元组 (width, height)

       返回:
           绝对坐标列表 [x1, y1, x2, y2] (单位:像素)

       示例:
           >>> coordinates_convert([500, 500, 600, 600], (1000, 2000))
           [500, 1000, 600, 1200]  # 对于2000高度的图片，y坐标×2
       """
    # 参数校验
    if len(relative_bbox) != 4 or len(img_size) != 2:
        raise ValueError("输入参数格式应为: relative_bbox=[x1,y1,x2,y2], img_size=(width,height)")

    # 解包图片尺寸
    img_width, img_height = img_size

    # 计算绝对坐标
    abs_x1 = int(relative_bbox[0] * img_width / 1000)
    abs_y1 = int(relative_bbox[1] * img_height / 1000)
    abs_x2 = int(relative_bbox[2] * img_width / 1000)
    abs_y2 = int(relative_bbox[3] * img_height / 1000)

    return [abs_x1, abs_y1, abs_x2, abs_y2]


def draw_box_and_show(image, start_box=None, end_box=None, direction=None):
    """
    在图片上绘制两个边界框和指向箭头

    参数:
        image: PIL.Image对象或图片路径
        start_box: 起始框坐标 [x1,y1,x2,y2] (绝对坐标)
        end_box: 结束框坐标 [x1,y1,x2,y2] (绝对坐标)
        direction: 操作方向 ('up', 'down', 'left', 'right' 或 None)
    """
    box_color = "red"
    arrow_color = "blue"
    box_width = 10
    drag_arrow_length = 150  # drag操作箭头长度

    draw = ImageDraw.Draw(image)

    # 绘制起始框
    if start_box is not None:
        draw.rectangle(start_box, outline=box_color, width=box_width)

    # 绘制结束框
    if end_box is not None:
        draw.rectangle(end_box, outline=box_color, width=box_width)

    # 处理不同类型的操作
    if start_box is not None:
        start_center = ((start_box[0] + start_box[2]) / 2, (start_box[1] + start_box[3]) / 2)

        if end_box is not None:
            # 绘制两个框之间的连接线和箭头
            end_center = ((end_box[0] + end_box[2]) / 2, (end_box[1] + end_box[3]) / 2)
            draw.line([start_center, end_center], fill=arrow_color, width=box_width)
            draw_arrow_head(draw, start_center, end_center, arrow_color, box_width * 3)
        elif direction is not None:
            # 处理drag操作（只有start_box和direction）
            end_point = calculate_drag_endpoint(start_center, direction, drag_arrow_length)
            draw.line([start_center, end_point], fill=arrow_color, width=box_width)
            draw_arrow_head(draw, start_center, end_point, arrow_color, box_width * 3)

    # 显示结果图片
    plt.imshow(image)
    plt.axis('on')  # 不显示坐标轴
    plt.show()


def draw_arrow_head(draw, start, end, color, size):
    """
    绘制箭头头部
    """
    # 计算角度
    angle = math.atan2(end[1] - start[1], end[0] - start[0])

    # 计算箭头三个点的位置
    p1 = end
    p2 = (
        end[0] - size * math.cos(angle + math.pi / 6),
        end[1] - size * math.sin(angle + math.pi / 6)
    )
    p3 = (
        end[0] - size * math.cos(angle - math.pi / 6),
        end[1] - size * math.sin(angle - math.pi / 6)
    )

    # 绘制箭头
    draw.polygon([p1, p2, p3], fill=color)


def calculate_drag_endpoint(start_point, direction, length):
    """
    计算drag操作的箭头终点

    参数:
        start_point: 起点坐标 (x, y)
        direction: 方向 ('up', 'down', 'left', 'right')
        length: 箭头长度

    返回:
        终点坐标 (x, y)
    """
    x, y = start_point
    if direction == 'up':
        return (x, y - length)
    elif direction == 'down':
        return (x, y + length)
    elif direction == 'left':
        return (x - length, y)
    elif direction == 'right':
        return (x + length, y)
    else:
        return (x, y)  # 默认不移动

def image_to_base64(image_path):
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.svg': 'image/svg+xml',
    }
    with open(image_path, "rb") as image_file:
        binary_data = image_file.read()
        base64_data = base64.b64encode(binary_data).decode("utf-8")
    return f"data:{mime_types.get(ext, 'image/png')};base64,{base64_data}"


def run(img_path, user_prompt):
    # ark_api_key = os.environ.get("ARK_API_KEY")
    ark_api_key = "53008c87-b444-41c2-8515-88db94d60162"
    sp = "You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task.\n## Output Format\n```\nThought: ...\nAction: ...\n```\n## Action Space\nclick(start_box='[x1, y1, x2, y2]')\nleft_double(start_box='[x1, y1, x2, y2]')\nright_single(start_box='[x1, y1, x2, y2]')\ndrag(start_box='[x1, y1, x2, y2]', end_box='[x3, y3, x4, y4]')\nhotkey(key='')\ntype(content='') #If you want to submit your input, use \"\\n\" at the end of `content`.\nscroll(start_box='[x1, y1, x2, y2]', direction='down or up or right or left')\nwait() #Sleep for 5s and take a screenshot to check for any changes.\nfinished(content='xxx') # Use escape characters \\\\', \\\\\", and \\\\n in content part to ensure we can parse the content in normal python string format.\n## Note\n- Use Chinese in `Thought` part.\n- Write a small plan and finally summarize your next action (with its target element) in one sentence in `Thought` part.\n## User Instruction"

    client = Ark(api_key=ark_api_key, base_url="https://ark.cn-beijing.volces.com/api/v3/")
    try:
        response = client.chat.completions.create(
            model="doubao-1.5-ui-tars-250328",
            temperature=0.5,
            messages=[
                {
                    "role": "system",
                    "content": sp
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_to_base64(img_path)
                            }
                        }
                    ]
                }

            ],
        )
        print("【结果】\n", response.choices[0].message.content)
        return response.choices[0].message.content
    except ArkAPIError as e:
        print(e)


if __name__ == "__main__":
    image_path = "D:\Code\综合项目实践\\trustee\LLM\pics\\test1.png"
    image_path = "LLM/pics/test1.png"
    model_response = run(image_path, "帮我最大化typora的窗口")
    parsed_output = json.loads(parse_action_output(model_response))
    print(parsed_output)

    image = Image.open(image_path)

    # 转换坐标
    start_abs = coordinates_convert(parsed_output["start_box"], image.size) if parsed_output["start_box"] else None
    end_abs = coordinates_convert(parsed_output["end_box"], image.size) if parsed_output["end_box"] else None
    direction = parsed_output["direction"] if parsed_output["direction"] else None

    draw_box_and_show(image, start_abs, end_abs, direction)