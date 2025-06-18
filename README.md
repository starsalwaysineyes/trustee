# Trustee - 智能自动化助手

> 基于AI驱动的Windows智能自动化系统，支持自然语言操作指令和视觉识别自动化

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.3%2B-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)](https://github.com/yourusername/trustee)

## 📋 目录

> 💡 **提示**: 如需查看所有项目文档，请访问 **[📚 文档索引](DOCUMENTS_INDEX.md)**

- [项目简介](#项目简介)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [核心功能](#核心功能)
- [快速开始](#快速开始)
- [安装部署](#安装部署)
- [使用指南](#使用指南)
- [API文档](#api文档)
- [测试方法](#测试方法)
- [目录结构](#目录结构)
- [开发指南](#开发指南)
- [问题排查](#问题排查)
- [更新日志](#更新日志)

> 🚀 **快速体验**: 查看 **[快速启动指南](QUICK_START.md)** | 📊 **项目总结**: 查看 **[完整总结](PROJECT_SUMMARY.md)**

## 🚀 项目简介

Trustee是一个先进的智能自动化助手，结合了人工智能、计算机视觉和自然语言处理技术，为用户提供强大的Windows系统自动化操作能力。

### 主要特点

- 🤖 **AI驱动**: 集成阿里云百炼大语言模型，支持自然语言理解
- 🖼️ **视觉识别**: 基于截图的智能UI元素识别和定位
- 🎯 **精准操作**: 自动生成PyAutoGUI操作代码，实现精确的鼠标键盘控制
- 🌐 **Web界面**: 现代化响应式Web管理界面
- 📊 **任务管理**: 完整的任务创建、执行、监控和历史追踪
- 🔧 **设备管理**: 多设备支持和统一管理
- 🔐 **安全认证**: 完整的用户认证和权限管理系统

## 🏗️ 系统架构

### 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                         │
│                  (用户界面层)                           │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/HTTPS
┌─────────────────────▼───────────────────────────────────┐
│                Flask Web Server                        │
│                  (API服务层)                           │
├─────────────────────────────────────────────────────────┤
│  Authentication │ Device Mgmt │ Task Mgmt │ AI Service │
├─────────────────────────────────────────────────────────┤
│               Database Layer                            │
│              (SQLite/数据层)                           │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              External Services                          │
│          (阿里云百炼 AI API)                           │
└─────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. 前端层 (Frontend)
- **技术**: HTML5 + CSS3 + JavaScript
- **特性**: 响应式设计、现代化UI、实时交互
- **组件**: 登录页面、设备管理、任务管理、AI工作室

#### 2. 后端服务层 (Backend)
- **框架**: Flask + Python 3.8+
- **功能模块**:
  - 用户认证服务 (`api.py`)
  - 设备管理API
  - 任务管理API  
  - AI自动化服务 (`LLM/ai_automation_service.py`)
  - 工作流服务 (`database/workflow_service.py`)

#### 3. 数据存储层 (Database)
- **数据库**: SQLite
- **ORM**: 自定义DAO模式
- **表结构**: 7个核心数据表
  - users (用户表)
  - devices (设备表)
  - tasks (任务表)
  - task_steps (任务步骤表)
  - screenshots (截图表)
  - ai_analysis (AI分析表)
  - executions (执行记录表)

#### 4. AI服务层 (AI Services)
- **模型**: 阿里云百炼 doubao-1.5-ui-tars
- **功能**: 图像理解、指令解析、代码生成
- **服务**: `AIAutomationService` 类

## 🛠️ 技术栈

### 后端技术
- **Web框架**: Flask 2.3+
- **数据库**: SQLite 3
- **ORM**: 自定义DAO模式
- **AI集成**: 阿里云百炼API
- **自动化**: PyAutoGUI
- **图像处理**: Pillow (PIL)

### 前端技术
- **UI框架**: 原生HTML5/CSS3/JavaScript
- **图标**: Material Icons
- **样式**: CSS Grid + Flexbox
- **交互**: Fetch API

### 开发工具
- **语言**: Python 3.8+
- **包管理**: uv/pip
- **测试**: 自定义测试脚本
- **部署**: 本地Flask服务器

## ✨ 核心功能

### 1. 用户认证系统
- ✅ 用户注册/登录/登出
- ✅ Session管理
- ✅ 权限控制
- ✅ 默认管理员账户 (admin/admin)

### 2. 设备管理
- ✅ 设备注册和配置
- ✅ 设备状态监控
- ✅ 多设备支持
- ✅ 设备信息CRUD操作

### 3. 任务管理
- ✅ 自然语言任务创建
- ✅ 任务执行和监控
- ✅ 执行历史追踪
- ✅ 任务状态管理
- ✅ 进度实时更新

### 4. AI自动化
- ✅ 截图智能分析
- ✅ UI元素识别和定位
- ✅ 操作代码自动生成
- ✅ 演练模式和实际执行
- ✅ 自然语言指令理解

### 5. 数据统计
- ✅ 任务执行统计
- ✅ 成功率分析
- ✅ 设备状态统计
- ✅ 实时仪表板

## 🚀 快速开始

### 系统要求
- Python 3.8 或更高版本
- 2GB+ 内存
- 1GB+ 磁盘空间
- Windows/macOS/Linux

### 一键启动
```bash
# 1. 克隆项目
git clone https://github.com/yourusername/trustee.git
cd trustee

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python3 api.py

# 4. 访问应用
# 浏览器打开: http://localhost:5000
# 默认账号: admin / admin
```

## 📦 安装部署

### 环境准备

#### 使用uv (推荐)
```bash
# 安装uv包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -r requirements.txt
```

#### 使用标准pip
```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 配置设置

#### 环境变量 (可选)
```bash
# AI API配置
export ARK_API_KEY="your-volcengine-api-key"

# 数据库配置
export DB_PATH="./database/trustee.db"

# 服务器配置
export FLASK_ENV="development"
export FLASK_PORT="5000"
```

#### 数据库初始化
```bash
# 数据库会在首次启动时自动创建
python3 api.py
```

### 启动服务

#### 开发模式
```bash
python3 api.py
```

#### 生产模式
```bash
# 使用gunicorn (需要安装)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

## 📖 使用指南

### 1. 登录系统
1. 访问 http://localhost:5000
2. 使用默认账号: `admin` / `admin`
3. 登录后自动跳转到设备管理页面

### 2. 设备管理
1. 点击侧边栏"设备管理"
2. 点击"添加设备"按钮
3. 填写设备信息并保存
4. 查看设备状态和详细信息

### 3. 任务管理
1. 点击侧边栏"任务管理"
2. 点击"创建任务"按钮
3. 输入自然语言指令
4. 选择目标设备
5. 执行任务并监控进度

### 4. AI工作室
1. 点击侧边栏"AI工作室"
2. 上传截图或选择现有图片
3. 输入操作指令
4. 查看AI分析结果
5. 执行或下载生成的代码

## 📚 API文档

### 认证相关

#### 用户登录
```http
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

#### 用户注册
```http
POST /api/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123"
}
```

#### 用户登出
```http
POST /api/logout
```

### 设备管理

#### 获取设备列表
```http
GET /api/devices
```

#### 创建设备
```http
POST /api/devices
Content-Type: application/json

{
  "device_name": "我的电脑",
  "device_ip": "192.168.1.100",
  "device_type": "computer",
  "os_info": "Windows 11",
  "screen_resolution": "1920x1080"
}
```

#### 更新设备
```http
PUT /api/devices/{device_id}
Content-Type: application/json

{
  "device_name": "更新后的名称",
  "status": "online"
}
```

#### 删除设备
```http
DELETE /api/devices/{device_id}
```

### 任务管理

#### 获取任务列表
```http
GET /api/tasks?status=pending
```

#### 创建任务
```http
POST /api/tasks
Content-Type: application/json

{
  "task_name": "自动点击",
  "natural_language_input": "点击屏幕中的确定按钮",
  "device_id": 1
}
```

#### 执行任务
```http
POST /api/tasks/{task_id}/execute
```

#### 获取任务详情
```http
GET /api/tasks/{task_id}
```

### AI自动化

#### AI分析截图
```http
POST /api/ai/analyze
Content-Type: multipart/form-data

screenshot: [图片文件]
instruction: "点击OK按钮"
```

#### 执行AI生成的操作
```http
POST /api/ai/execute
Content-Type: application/json

{
  "analysis_result": { ... },
  "dry_run": true
}
```

### 统计信息

#### 获取仪表板统计
```http
GET /api/dashboard/stats
```

#### 获取执行历史
```http
GET /api/history
```

## 🧪 测试方法

### 自动化测试

#### 完整系统测试
```bash
# 运行完整的功能测试
python3 test_login_flow.py
```

测试覆盖范围：
- ✅ 用户认证流程
- ✅ 页面跳转逻辑
- ✅ API功能验证
- ✅ 权限控制测试
- ✅ 数据库操作测试

#### API测试示例
```bash
# 测试用户注册
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"123456"}' \
  http://localhost:5000/api/register

# 测试用户登录
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  -c cookies.txt http://localhost:5000/api/login

# 测试设备API
curl -H "Content-Type: application/json" -b cookies.txt \
  http://localhost:5000/api/devices

# 测试AI分析
curl -X POST -b cookies.txt \
  -F "screenshot=@test_image.png" \
  -F "instruction=点击确定按钮" \
  http://localhost:5000/api/ai/analyze
```

### 手动测试

#### 前端测试清单
- [ ] 登录页面加载正常
- [ ] 用户登录功能正常
- [ ] 页面导航切换正常
- [ ] 设备管理CRUD操作
- [ ] 任务创建和执行
- [ ] AI工作室图片上传
- [ ] 响应式设计测试

#### 后端测试清单
- [ ] 数据库连接正常
- [ ] API认证机制
- [ ] 数据库CRUD操作
- [ ] AI服务集成
- [ ] 错误处理机制
- [ ] 日志记录功能

## 📁 目录结构

```
trustee/
├── api.py                      # Flask主应用文件
├── requirements.txt            # Python依赖包
├── test_login_flow.py         # 自动化测试脚本
├── README.md                  # 项目文档
├── TEST_RESULTS_AND_DEPLOYMENT.md  # 测试结果文档
│
├── database/                  # 数据库模块
│   ├── __init__.py
│   ├── database.py           # 数据库管理器
│   ├── models.py             # 数据模型定义
│   ├── dao.py                # 数据访问对象
│   ├── workflow_service.py   # 工作流服务
│   ├── trustee.db           # SQLite数据库文件
│   └── screenshots/         # 截图存储目录
│
├── LLM/                      # AI模块
│   ├── __init__.py
│   ├── action_parser.py      # 动作解析器
│   ├── ai_automation_service.py  # AI自动化服务
│   └── prompt_templates.py   # 提示词模板
│
└── templates/                # HTML模板
    ├── base.html            # 基础模板
    ├── login.html           # 登录页面
    ├── devices.html         # 设备管理
    ├── tasks.html           # 任务管理
    └── ai_studio.html       # AI工作室
```

## 🔧 开发指南

### 添加新功能

#### 1. 数据库扩展
```python
# 在 database/models.py 中添加新模型
class NewModel:
    def __init__(self, ...):
        # 模型定义

# 在 database/dao.py 中添加DAO类
class NewModelDAO:
    @staticmethod
    def create(model):
        # 实现创建逻辑
```

#### 2. API接口扩展
```python
# 在 api.py 中添加新路由
@app.route('/api/new-feature', methods=['GET', 'POST'])
def new_feature():
    # API逻辑实现
    return jsonify({'success': True})
```

#### 3. 前端页面扩展
```html
<!-- 在 templates/ 中添加新模板 -->
{% extends "base.html" %}

{% block content %}
<!-- 页面内容 -->
{% endblock %}
```

### 代码规范

#### Python代码风格
- 遵循PEP 8规范
- 使用类型提示
- 添加完整的文档字符串
- 异常处理要具体明确

#### 前端代码风格
- 使用语义化HTML标签
- CSS类名采用kebab-case
- JavaScript使用camelCase
- 添加适当的注释

### 调试技巧

#### 后端调试
```python
# 启用Flask调试模式
app.run(debug=True)

# 添加日志输出
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("调试信息")
```

#### 前端调试
```javascript
// 浏览器开发者工具
console.log("调试信息");

// API请求调试
fetch('/api/endpoint')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('错误:', error));
```

## 🔍 问题排查

### 常见问题

#### 1. 服务启动失败
```bash
# 检查端口占用
lsof -i :5000

# 检查Python版本
python3 --version

# 检查依赖安装
pip list | grep flask
```

#### 2. 数据库错误
```bash
# 删除并重新创建数据库
rm database/trustee.db
python3 api.py
```

#### 3. AI功能异常
```bash
# 检查AI模块导入
python3 -c "from LLM.ai_automation_service import AIAutomationService"

# 检查网络连接
curl -I https://ark.cn-beijing.volces.com
```

#### 4. 前端页面异常
```bash
# 检查模板文件
ls -la templates/

# 检查静态资源
curl -I http://localhost:5000/static/style.css
```

### 日志分析

#### 查看应用日志
```bash
# 重定向日志到文件
python3 api.py > app.log 2>&1

# 实时查看日志
tail -f app.log
```

#### 数据库诊断
```bash
# SQLite完整性检查
sqlite3 database/trustee.db "PRAGMA integrity_check;"

# 查看表结构
sqlite3 database/trustee.db ".schema"
```

## 📊 性能优化

### 数据库优化
```sql
-- 重建索引
REINDEX;

-- 分析查询计划
EXPLAIN QUERY PLAN SELECT * FROM tasks WHERE user_id = 1;
```

### 内存优化
- 定期清理历史数据
- 限制并发AI请求数量
- 优化图片缓存策略

### 网络优化
- 启用GZIP压缩
- 配置静态文件缓存
- 使用CDN加速静态资源

## 🔒 安全考虑

### 认证安全
- Session超时机制
- 密码强度要求
- API访问频率限制

### 数据安全
- 敏感数据加密存储
- SQL注入防护
- XSS攻击防护

### 网络安全
- HTTPS配置
- CORS策略设置
- 防火墙规则配置

## 📝 更新日志

### v1.0.0 (2025-05-30)
- ✅ 完整的用户认证系统
- ✅ 设备管理功能
- ✅ 任务管理和执行
- ✅ AI自动化集成
- ✅ 现代化Web界面
- ✅ 完整的测试覆盖

### 已知问题
- 设置页面和帮助文档尚未实现 (返回404)
- AI功能依赖外部API服务
- 仅支持Windows系统自动化

### 计划功能
- [ ] 实时WebSocket通信
- [ ] 任务调度系统
- [ ] 多用户权限管理
- [ ] Docker容器化部署
- [ ] 移动端适配

## 🤝 贡献指南

### 贡献方式
1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 开发环境设置
```bash
# 克隆Fork的仓库
git clone https://github.com/yourusername/trustee.git

# 添加上游仓库
git remote add upstream https://github.com/original/trustee.git

# 创建开发分支
git checkout -b feature/new-feature

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 代码提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 其他修改

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目主页: https://github.com/yourusername/trustee
- 问题反馈: https://github.com/yourusername/trustee/issues
- 电子邮件: your.email@example.com

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [阿里云百炼](https://bailian.aliyun.com/) - AI大语言模型
- [PyAutoGUI](https://pyautogui.readthedocs.io/) - 自动化库
- [Material Icons](https://fonts.google.com/icons) - 图标库

---

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**






