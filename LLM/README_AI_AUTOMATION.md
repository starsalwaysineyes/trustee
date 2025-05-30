# AI自动化服务 (AI Automation Service)

基于AI视觉识别的智能桌面自动化工具，整合了图像分析、动作解析和操作执行的完整工作流程。

## 🚀 功能特性

- **🔍 智能图像分析**: 使用火山引擎AI模型分析截图，理解界面元素
- **🎯 精确动作识别**: 自动识别点击、输入、拖拽等操作目标
- **🤖 代码自动生成**: 将AI分析结果转换为可执行的PyAutoGUI代码
- **⚡ 一键执行**: 支持演练模式和实际执行模式
- **📦 批量处理**: 支持多任务批量自动化处理
- **🛡️ 安全可控**: 多重安全检查，支持演练模式
- **📊 详细报告**: 生成完整的分析和执行报告

## 📁 文件结构

```
LLM/
├── ai_automation_service.py  # 核心服务类
├── demo_automation.py        # 演示脚本
├── uitar.py                 # AI图像分析模块
├── action_praser.py         # 动作解析模块
├── pics/
│   └── test1.png           # 测试图片
└── README_AI_AUTOMATION.md  # 使用说明
```

## 🛠️ 依赖安装

```bash
pip install pillow matplotlib pyautogui pyperclip volcengine-python-sdk[ark]
```

## 📖 快速开始

### 1. 最简单的使用方式

```python
from ai_automation_service import quick_automation

# 快速分析和操作
result = quick_automation(
    image_path="screenshot.png",
    instruction="点击登录按钮",
    execute=False,  # 演练模式
    show_preview=True
)

print(f"分析结果: {result['success']}")
```

### 2. 服务类详细用法

```python
from ai_automation_service import AIAutomationService

# 初始化服务
service = AIAutomationService()

# 分析截图
result = service.analyze_screenshot(
    image_path="screenshot.png",
    user_instruction="在搜索框输入Python",
    show_visualization=True
)

# 执行操作
if result['success']:
    execution_result = service.execute_actions(result, dry_run=False)
```

### 3. 工作流类使用

```python
from ai_automation_service import AIAutomationService, AIAutomationWorkflow

# 创建工作流
service = AIAutomationService()
workflow = AIAutomationWorkflow(service)

# 运行任务
result = workflow.run_single_task(
    image_path="screenshot.png",
    instruction="双击桌面上的Chrome图标",
    auto_execute=True
)
```

### 4. 批量处理

```python
# 准备任务列表
tasks = [
    {"image_path": "screen1.png", "instruction": "点击开始菜单"},
    {"image_path": "screen2.png", "instruction": "搜索记事本"},
    {"image_path": "screen3.png", "instruction": "打开记事本"}
]

# 批量执行
results = service.batch_process(tasks, execute=True)
```

## 🎮 交互式模式

```bash
python ai_automation_service.py
```

交互式模式支持：
- 拖拽图片文件
- 实时输入操作指令
- 选择是否执行操作
- 查看帮助信息

## 📋 支持的操作类型

### 鼠标操作
- **click**: 单击
- **left_double**: 双击
- **right_single**: 右键单击
- **hover**: 悬停
- **drag**: 拖拽

### 键盘操作
- **type**: 文本输入
- **hotkey**: 快捷键组合
- **press**: 按键
- **scroll**: 滚动

### 复合操作
- **finished**: 任务完成
- **wait**: 等待

## 💡 使用示例

### 示例1: 窗口操作
```python
result = quick_automation(
    "desktop.png", 
    "最大化当前窗口",
    execute=False
)
```

### 示例2: 文本输入
```python
result = quick_automation(
    "search_page.png",
    "在搜索框输入'人工智能'并按回车",
    execute=False
)
```

### 示例3: 文件操作
```python
result = quick_automation(
    "file_manager.png",
    "右键点击文件夹并选择新建文件夹",
    execute=False
)
```

## 🛡️ 安全说明

### 演练模式 (推荐)
```python
# 只分析不执行，查看生成的代码
result = service.execute_actions(analysis_result, dry_run=True)
```

### 实际执行模式
```python
# 实际执行操作，请谨慎使用
result = service.execute_actions(analysis_result, dry_run=False)
```

### 安全检查
- ✅ 文件存在性验证
- ✅ 图像格式检查
- ✅ 操作合法性验证
- ✅ 错误捕获和处理
- ✅ 用户确认机制

## 📊 返回结果格式

```json
{
  "success": true,
  "user_instruction": "点击登录按钮",
  "image_info": {
    "path": "screenshot.png",
    "size": [1920, 1080]
  },
  "ai_response": {
    "raw_text": "AI分析的原始文本...",
    "processing_time_ms": 1500
  },
  "parsed_action": {
    "thought": "AI的思考过程",
    "action": "click",
    "start_box": [100, 200, 150, 250],
    "content": null
  },
  "pyautogui_code": "import pyautogui\npyautogui.click(125, 225)",
  "timestamp": 1703123456.789
}
```

## 🔧 配置选项

### API配置
```python
service = AIAutomationService(
    ark_api_key="your_api_key",  # 火山引擎API密钥
    model_name="doubao-1.5-ui-tars-250328"  # AI模型名称
)
```

### PyAutoGUI配置
```python
import pyautogui
pyautogui.FAILSAFE = True    # 鼠标移动到屏幕角落停止
pyautogui.PAUSE = 0.5        # 操作间隔时间
```

## 🐛 常见问题

### Q: AI分析失败怎么办？
A: 检查图片质量、网络连接和API密钥是否正确。

### Q: 生成的代码不正确？
A: 先在演练模式下检查，可能需要调整指令描述或图片质量。

### Q: 执行操作时出错？
A: 确保桌面环境与截图一致，检查目标元素是否存在。

### Q: 如何提高识别准确率？
A: 使用高清截图、清晰的指令描述、确保界面元素清晰可见。

## 📝 演示脚本

运行完整演示：
```bash
python demo_automation.py
```

演示内容包括：
- 基础用法
- 服务类详细功能
- 批量处理
- 工作流使用
- 错误处理
- 交互式模式

## 🤝 扩展开发

### 自定义操作类型
可以在`action_praser.py`中添加新的操作类型支持。

### 集成其他AI模型
可以修改`uitar.py`中的模型调用接口。

### 添加新的安全检查
可以在`AIAutomationService`类中添加更多安全验证。

## 📄 许可证

本项目遵循项目根目录的许可证。

## 🆘 支持

如有问题或建议，请查看项目文档或提交Issue。 