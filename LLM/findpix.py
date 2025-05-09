from openai import OpenAI
import os
import base64
import json

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
        print(f"图片已成功添加红点并保存至: {output_path}") # 可选：操作成功提示

    except FileNotFoundError:
        print(f"错误: 输入图片文件未找到 '{img_path}'")
        # 根据实际需求，这里可以考虑抛出异常而不是仅打印
        # raise FileNotFoundError(f"输入图片文件未找到 '{img_path}'")
    except Exception as e:
        print(f"处理图片时发生错误: {e}")
        # 根据实际需求，这里可以考虑抛出异常
        # raise e


#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class Ask_img:
    def __init__(self):
        self.client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
            api_key="sk-0fc8d0ebe02649e191e148da43d67e7b", # 请确保使用您的有效API Key
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.messages = []
        self._initialize_system_message()

    def _initialize_system_message(self):
        """初始化或重置系统消息。"""
        self.messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant. Please respond in Chinese."}] # 根据需要调整系统提示
            }
        ]

    def clear_memory(self):
        """清空对话历史并重置系统消息，作为专门的记忆重置函数。"""
        self._initialize_system_message()
        print("对话记忆已清空。")

    def ask_img(self, text_prompt: str, image_path: str = None):
        """
        向模型发送请求，包含当前文本提示和可选图片，并维护对话历史。

        :param text_prompt: str, 当前回合的文本提示。
        :param image_path: str, optional, 当前回合的图片路径。
        :return: str, 模型的文本回复。
        """
        current_user_content = []

        if image_path:
            try:
                base64_image = encode_image(image_path)
                image_format = image_path.split('.')[-1].lower()
                mime_type = "image/png" # 默认为 png
                if image_format == "jpg" or image_format == "jpeg":
                    mime_type = "image/jpeg"
                elif image_format == "webp":
                    mime_type = "image/webp"
                
                current_user_content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                    }
                )
            except FileNotFoundError:
                print(f"错误: 图片文件未找到 '{image_path}'")
                # 可以选择在这里返回错误信息或抛出异常
                return "错误: 图片文件未找到。"
            except Exception as e:
                print(f"编码图片时发生错误: {e}")
                return f"错误: 编码图片失败 - {e}"

        current_user_content.append({"type": "text", "text": text_prompt})
        
        self.messages.append({"role": "user", "content": current_user_content})
        
        try:
            completion = self.client.chat.completions.create(
                model="qwen2.5-vl-72b-instruct", # 模型名称
                messages=self.messages # 使用包含历史的完整消息列表
            )
            
            assistant_completion_message = completion.choices[0].message
            assistant_response_text = ""

            # 处理模型回复的 content 格式
            if isinstance(assistant_completion_message.content, str):
                assistant_response_text = assistant_completion_message.content
            elif isinstance(assistant_completion_message.content, list): 
                for part in assistant_completion_message.content:
                    if part.get("type") == "text":
                        assistant_response_text += part.get("text", "")
            
            # 将模型的回复以标准格式存入历史
            assistant_message_for_history = {
                "role": assistant_completion_message.role,
                "content": [{"type": "text", "text": assistant_response_text}]
            }
            self.messages.append(assistant_message_for_history)
            
            # print(f"模型回复: {assistant_response_text}") # 用于调试
            return assistant_response_text
        except Exception as e:
            print(f"调用API时发生错误: {e}")
            # 可以将错误信息追加到历史记录中，或者直接返回
            self.messages.append({
                "role": "assistant",
                "content": [{"type": "text", "text": f"API调用错误: {e}"}]
            })
            return f"错误: 调用API失败 - {e}"


def get_json_from_text(text_content):
    # 从text中提取json字符串
    json_str = text_content.split("```json")[1].split("```")[0]
    return json.loads(json_str)


def get_x_y_from_json(json_data): # Renamed parameter for clarity
    return json_data["x1"], json_data["y1"], json_data["x2"], json_data["y2"]

def get_x_y(json_data):
    x1, y1, x2, y2 = get_x_y_from_json(json_data)
    x = (x1 + x2) 
    y = (y1 + y2) 
    return x, y

if __name__ == "__main__":
    # 实例化 Ask_img 类
    image_qa_session = Ask_img()

    # 第一个问题
    img_path1 = "D:/Code/综合项目实践/trustee/LLM/pics/test1.png"
    prompt1 = "我的屏幕像素是2560*1600；我想要关闭typora窗口，请告诉我关闭按钮的坐标，坐标范围是关闭按钮的左上角和右下角。回答最后按照json格式返回,内部只有find=flase(初始默认),x1和y1，x2,y2五个参数,只要有偏移就find返回false"
    
    print(f"用户 (图片: {os.path.basename(img_path1)}): {prompt1}")
    response1 = image_qa_session.ask_img(text_prompt=prompt1, image_path=img_path1)
    print(f"助手: {response1}")

    try:
        json_data = get_json_from_text(response1)
        print(f"提取的JSON: {json_data}")
        x, y = get_x_y(json_data)
        print(f"坐标: x={x}, y={y}")

        output_img_path = "D:/Code/综合项目实践/trustee/LLM/pics/test1_red.png"
        add_red_dot_on_image(img_path1, output_img_path, x, y, 10)
        print(f"已在 {output_img_path} 上标记红点")

        # 第二个问题，利用上下文记忆
        prompt2 = "确认是否是这个地方，我在图片中用红点标记了你给的坐标,如果精准，在json中返回find=true,否则返回find=false和新的x1和y1，x2,y2,新的坐标应该按照相对位置进行微调，而不是重新计算，注意这里先明确往哪里偏，然后去返回新的坐标"
        print(f"用户 (图片: {os.path.basename(output_img_path)}): {prompt2}")
        response2 = image_qa_session.ask_img(text_prompt=prompt2, image_path=output_img_path) # 使用带红点的新图片
        print(f"助手: {response2}")

        json_data = get_json_from_text(response2)
        print(f"提取的JSON: {json_data}")
        
        if json_data["find"] == "true":
            print("找到坐标")
        else:
            print("未找到坐标")
        
            x, y = get_x_y(json_data)
            print(f"坐标: x={x}, y={y}")
            add_red_dot_on_image(img_path1, output_img_path, x, y, 10)
            print(f"已在 {output_img_path} 上标记红点")

        # 示例：清空记忆并开始新的对话
        # print("\n--- 清空记忆后的新对话 ---")
        # image_qa_session.clear_memory()
        # prompt3 = "这张图片里有什么内容？"
        # img_path3 = "D:/Code/综合项目实践/trustee/LLM/pics/test.png" # 可以是另一张图片
        # print(f"用户 (图片: {os.path.basename(img_path3)}): {prompt3}")
        # response3 = image_qa_session.ask_img(text_prompt=prompt3, image_path=img_path3)
        # print(f"助手: {response3}")

    except (IndexError, KeyError, json.JSONDecodeError) as e:
        print(f"处理JSON或提取坐标时出错: {e}")
    except FileNotFoundError as e:
        print(f"文件未找到错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")


