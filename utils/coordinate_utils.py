"""
坐标处理工具模块
"""
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def parse_box_coordinates(box_str: str) -> List[int]:
    """
    解析模型返回的各种格式的坐标字符串。

    支持格式:
    - '[863,107,863,107]'
    - '863,107,863,107'
    - '863 107 863 107'

    返回:
        一个包含4个整数的列表 [x1, y1, x2, y2]。
    """
    if not isinstance(box_str, str):
        logger.warning(f"坐标解析：输入不是字符串，将返回空: {box_str}")
        return []
    
    # 移除常见包装字符
    cleaned_str = box_str.strip().replace('[', '').replace(']', '').replace('(', '').replace(')', '')
    
    # 尝试用逗号或空格分割
    if ',' in cleaned_str:
        parts = cleaned_str.split(',')
    else:
        parts = cleaned_str.split()
        
    try:
        # 使用 float() 兼容整数和浮点数格式的字符串，然后转为 int
        coords = [int(float(p.strip())) for p in parts if p.strip()]
        if len(coords) == 2:
            # 如果只有(x,y)，扩展为(x,y,x,y)
            return coords + coords
        elif len(coords) == 4:
            return coords
        else:
            logger.warning(f"解析后的坐标数量不正确 ({len(coords)}): {box_str}")
            return []
    except ValueError as e:
        logger.error(f"无法将坐标部分解析为数字: '{box_str}' -> '{cleaned_str}' - {e}")
        return []

def scale_coordinates_to_absolute(
    box_coords: List[int],
    target_resolution: Tuple[int, int],
    standard_base: Tuple[int, int] = (1000, 1000)
) -> Tuple[int, int]:
    """
    将基于标准尺寸的坐标缩放到目标分辨率的绝对坐标。

    参数:
        box_coords (List[int]): 模型的标准坐标 [x1, y1, x2, y2]。
        target_resolution (Tuple[int, int]): 目标屏幕分辨率 (width, height)。
        standard_base (Tuple[int, int]): 模型输出坐标所基于的标准 (width, height)。

    返回:
        一个元组，包含点击点的绝对坐标 (x, y)。
    """
    if not box_coords or len(box_coords) != 4:
        raise ValueError("输入坐标 `box_coords` 必须是包含4个整数的列表。")

    target_w, target_h = target_resolution
    base_w, base_h = standard_base

    # 计算中心点
    center_x_base = (box_coords[0] + box_coords[2]) / 2
    center_y_base = (box_coords[1] + box_coords[3]) / 2

    # 计算缩放比例
    scale_x = target_w / base_w
    scale_y = target_h / base_h

    # 计算绝对坐标
    abs_x = int(center_x_base * scale_x)
    abs_y = int(center_y_base * scale_y)

    logger.info(f"坐标缩放: [{center_x_base}, {center_y_base}] (基准 {standard_base}) -> [{abs_x}, {abs_y}] (目标 {target_resolution})")
    
    return abs_x, abs_y 