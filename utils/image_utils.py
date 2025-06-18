"""
图像处理工具模块
"""
import base64
import io
from PIL import Image

def image_to_base64(image_data, mime_type="image/png") -> str:
    """
    将图像数据（字节流或PIL.Image对象）转换为Base64编码的Data URL。

    :param image_data: 图片的字节流或PIL.Image对象。
    :param mime_type: 图像的MIME类型。
    :return: Base64编码的Data URL字符串。
    """
    if isinstance(image_data, Image.Image):
        buffered = io.BytesIO()
        image_data.save(buffered, format=mime_type.split('/')[-1].upper())
        img_bytes = buffered.getvalue()
    elif isinstance(image_data, bytes):
        img_bytes = image_data
    else:
        raise TypeError("image_data必须是bytes或PIL.Image.Image类型")

    base64_encoded_data = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:{mime_type};base64,{base64_encoded_data}" 