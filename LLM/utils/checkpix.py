from PIL import Image, ImageDraw

def add_red_dot_on_image(img_path: str, output_path: str, x: int, y: int, radius: int = 5):
    """
    打开指定路径的图片，在给定的(x, y)坐标处绘制一个红色圆点，并将修改后的图片保存到指定的输出路径。

    :param img_path: str, 输入图片的路径。
    :param output_path: str, 处理后图片的保存路径。
    :param x: int, 红色圆点圆心的x坐标。
    :param y: int, 红色圆点圆心的y坐标。
    :param radius: int, 红色圆点的半径，默认为5像素。
    """
    try:
        # 打开图片
        img = Image.open(img_path)
        # 创建一个绘图对象
        draw = ImageDraw.Draw(img)

        # 计算红点绘制的边界框 (left, top, right, bottom)
        # (x, y) 是圆心
        left = x - radius
        top = y - radius
        right = x + radius
        bottom = y + radius
        
        bounding_box = (left, top, right, bottom)
        
        # 定义红色
        red_color = (255, 0, 0)
        
        # 绘制一个红色的实心圆点
        draw.ellipse(bounding_box, fill=red_color, outline=red_color)
        
        # 保存修改后的图片
        img.save(output_path)
        # print(f"图片已成功添加红点并保存至: {output_path}") # 可选：操作成功提示

    except FileNotFoundError:
        print(f"错误: 输入图片文件未找到 '{img_path}'")
        # 根据实际需求，这里可以考虑抛出异常而不是仅打印
        # raise FileNotFoundError(f"输入图片文件未找到 '{img_path}'")
    except Exception as e:
        print(f"处理图片时发生错误: {e}")
        # 根据实际需求，这里可以考虑抛出异常
        # raise e


if __name__ == "__main__":
    add_red_dot_on_image("D:/Code/综合项目实践/trustee/LLM/pics/test.png", "D:/Code/综合项目实践/trustee/LLM/pics/test_red.png", 100, 100,10)

