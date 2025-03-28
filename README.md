# Trustee系统

Trustee是一个智能Windows任务执行助手，能够通过自然语言指令理解用户意图并自动执行相应的操作任务，帮助用户高效完成Windows系统上的各种操作。

## 项目结构

```
trustee/
├── backend/          # Flask后端服务
│   ├── app.py        # 主应用入口
│   ├── modules/      # 核心功能模块
│   ├── static/       # 前端静态文件
│   └── README.md     # 后端说明文档
└── README.md         # 项目总体说明
```

## 核心功能

- **自然语言指令理解**：通过NLP技术解析用户意图
- **任务规划与执行**：将复杂指令拆解为可执行的操作序列
- **视觉感知与交互**：分析屏幕状态，识别UI元素并进行交互
- **安全管控**：对敏感操作进行权限验证
- **用户反馈学习**：根据用户反馈优化执行策略

## 技术栈

- **后端**：Python + Flask
- **前端**：HTML + CSS + JavaScript
- **系统交互**：Win32 API
- **视觉识别**：模拟实现（可扩展为真实OCR）

## 快速开始

### 安装与运行

1. 克隆仓库
```bash
git clone https://github.com/yourusername/trustee.git
cd trustee
```

2. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

3. 启动后端服务
```bash
python app.py
```

4. 访问测试界面
打开浏览器访问 http://localhost:5000/static/index.html

## 使用示例

通过测试界面输入以下自然语言指令：

- "打开计算器应用"
- "创建一个新文件夹命名为'我的项目'"
- "查找最近的文档并按日期排序"
- "截取当前屏幕并保存到桌面"

## 系统架构

系统采用分层设计，包括：
1. 用户交互层
2. 视觉感知层
3. 任务理解层
4. 操作执行层
5. 安全控制层
6. Windows系统层

详细架构说明请参考 `backend/README.md`。

## 开发说明

当前版本为概念验证实现，部分功能使用模拟数据。若要扩展为生产系统，需进一步实现：

- 真实屏幕捕获和OCR识别
- Win32 API实际调用
- 更复杂的自然语言处理
- 完整的安全控制

## 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

MIT






