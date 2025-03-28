# Trustee系统后端

Trustee系统是一个智能任务执行助手，能够通过自然语言指令完成Windows系统上的各种操作任务。此项目实现了Trustee系统的后端服务，基于Flask框架构建，支持RESTful API接口。

## 架构设计

系统采用分层架构设计，各层职责明确：

1. **用户交互层**：处理用户输入和结果展示
2. **视觉感知层**：负责屏幕内容捕获和UI元素识别
3. **任务理解层**：解析用户指令并规划任务执行步骤
4. **操作执行层**：执行具体的操作指令
5. **安全控制层**：管理系统权限和操作安全
6. **Windows系统层**：底层操作系统接口

## 功能特点

- 接收自然语言指令
- 解析指令并创建任务执行计划
- 权限验证和安全控制
- 屏幕状态分析和UI元素识别
- 自动化操作执行
- 结果验证和任务评估
- 失败自动重试和策略调整
- 操作日志记录和审计
- 支持用户反馈和知识库更新

## 安装和运行

### 前提条件

- Python 3.8+
- Windows操作系统

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行服务

```bash
python app.py
```

服务默认在 http://localhost:5000 上运行。

## API接口

### 1. 执行任务

**请求：**

```
POST /api/task/execute
Content-Type: application/json

{
    "instruction": "自然语言指令",
    "session_id": "可选的会话ID"
}
```

**响应：**

```json
{
    "success": true,
    "message": "任务执行完成",
    "session_id": "会话ID",
    "task_completed": true,
    "result": {
        "task_plan": { ... },
        "execution_result": { ... },
        "screen_analysis": { ... },
        "task_evaluation": { ... }
    }
}
```

### 2. 获取会话信息

**请求：**

```
GET /api/session/{session_id}
```

**响应：**

```json
{
    "success": true,
    "session": {
        "status": "completed",
        "history": [ ... ],
        "current_screen": { ... },
        "task_plan": { ... },
        "operation_sequence": [ ... ]
    }
}
```

### 3. 提交反馈

**请求：**

```
POST /api/feedback
Content-Type: application/json

{
    "session_id": "会话ID",
    "feedback": "用户反馈内容"
}
```

**响应：**

```json
{
    "success": true,
    "message": "反馈已接收并处理"
}
```

## 测试界面

项目包含一个简单的HTML测试界面，可通过访问 http://localhost:5000/static/index.html 使用。

## 注意事项

- 当前实现中，许多功能使用模拟数据，实际生产环境需实现真实的屏幕捕获、元素识别和操作执行功能
- 操作系统交互部分需要实际的Win32 API调用，当前只是模拟实现
- 安全控制机制需要根据实际部署环境进行调整

## 后续开发

- 实现实际的屏幕捕获和OCR识别功能
- 集成真实的Windows API调用
- 增强任务理解层的NLP能力
- 改进安全模型和权限系统
- 添加更多操作类型支持

## 许可证

MIT 