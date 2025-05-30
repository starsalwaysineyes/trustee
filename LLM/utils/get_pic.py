from PIL import ImageGrab

def capture_full_screen(imgpath: str):
    """
    截取完整屏幕并保存到指定的图像路径。

    参数:
        imgpath (str): 图像保存的完整路径 (例如: "D:/screenshots/screen.png")
    """
    try:
        # 截取整个屏幕
        im = ImageGrab.grab()
        # 获取原始尺寸
        original_width, original_height = im.size
        # 计算新尺寸
        new_width = int(original_width * 0.5)
        new_height = int(original_height * 0.5)
        # 缩放图像
        resized_im = im.resize((new_width, new_height))
        # 保存图像
        resized_im.save(imgpath)
        print(f"屏幕截图已缩放并保存到: {imgpath}")
    except Exception as e:
        print(f"截图失败: {e}")

if __name__ == '__main__':
    # 示例用法:
    # 请确保 'screenshots' 文件夹存在，或者修改为有效的路径
    import os
    # if not os.path.exists("screenshots"):
    #     os.makedirs("screenshots")
    capture_full_screen("D:/Code/综合项目实践/trustee/LLM/pics/test1.png")
