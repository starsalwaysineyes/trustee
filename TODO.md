# Trustee Flask 手机端页面开发任务

- [x] 初始化 Flask 项目结构 (`app.py`, `templates/`, `static/`)
- [x] 配置 Flask 以使用 Tailwind CSS (参考 `test.html` - 使用 CDN)
- [x] **页面开发:**
    - [x] 设备连接页面 (`/` 或 `/devices`):
        - [x] 创建 `devices.html` 模板
        - [x] 仿照 `test.html` 设计布局和样式
        - [x] 添加静态设备列表数据
    - [x] 任务列表页面 (`/tasks`):
        - [x] 创建 `tasks.html` 模板
        - [x] 仿照 `test.html` 设计布局和样式
        - [x] 添加过滤按钮 (全部, 等待中, 执行中, 已完成)
        - [x] 添加静态任务列表数据及状态显示
    - [x] 创建任务页面 (`/tasks/new`):
        - [x] 创建 `create_task.html` 模板
        - [x] 仿照 `test.html` 设计布局和样式
        - [x] 添加任务名称、类型、时间、描述等表单字段
    - [x] 任务详情页面 (`/tasks/<task_id>`):
        - [x] 创建 `task_detail.html` 模板
        - [x] 仿照 `test.html` 设计布局和样式
        - [x] 显示任务进度、基本信息、配置、执行历史 (使用静态数据)
    - [x] 历史记录页面 (`/history`):
        - [x] 创建 `history.html` 模板
        - [x] 仿照 `test.html` 设计布局和样式
        - [x] 添加搜索框和过滤按钮
        - [x] 按日期分组显示静态历史记录
- [x] **Flask 路由:**
    - [x] 在 `app.py` 中为每个页面创建路由和视图函数
    - [x] 确保路由能够正确渲染对应的 HTML 模板
- [x] **基础导航:**
    - [x] 实现页面底部导航栏 (设备, 任务, 历史, 设置)
    - [x] 确保导航链接指向正确的路由

---

## 🗄️ 数据库设计方案 (SQLite)

### 核心设计思路
基于AI驱动的 **"图像感知 → 智能思考 → 操作执行"** 循环工作流，设计以任务为核心的关系型数据库架构。

### 📊 主要数据表设计

#### 1. **任务主表** `tasks`
```sql
CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    device_id INTEGER,
    task_name VARCHAR(255) NOT NULL,
    task_description TEXT,
    task_type VARCHAR(50), -- 'manual', 'scheduled', 'triggered'
    natural_language_input TEXT, -- 用户的自然语言指令
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'paused', 'completed', 'failed'
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_steps INTEGER DEFAULT 0,
    completed_steps INTEGER DEFAULT 0,
    error_message TEXT,
    config_json TEXT, -- 任务配置参数 (JSON格式)
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);
```

#### 2. **任务执行步骤表** `task_steps`
```sql
CREATE TABLE task_steps (
    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    step_sequence INTEGER NOT NULL, -- 步骤序号
    step_type VARCHAR(50), -- 'capture', 'analyze', 'execute', 'verify'
    step_description TEXT,
    screenshot_id INTEGER, -- 关联截图
    ai_analysis_id INTEGER, -- 关联AI分析
    execution_id INTEGER, -- 关联操作执行
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER, -- 执行耗时(毫秒)
    retry_count INTEGER DEFAULT 0,
    error_details TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (screenshot_id) REFERENCES screenshots(screenshot_id),
    FOREIGN KEY (ai_analysis_id) REFERENCES ai_analysis(analysis_id),
    FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
);
```

#### 3. **屏幕截图表** `screenshots`
```sql
CREATE TABLE screenshots (
    screenshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    step_id INTEGER,
    image_path VARCHAR(500) NOT NULL, -- 图片文件路径
    image_base64 TEXT, -- base64编码 (可选，小图片)
    screen_resolution VARCHAR(20), -- 如 "2560x1600"
    capture_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER, -- 文件大小(字节)
    image_hash VARCHAR(64), -- 图片哈希值，用于去重
    purpose VARCHAR(50), -- 'initial', 'verification', 'error'
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (step_id) REFERENCES task_steps(step_id)
);
```

#### 4. **AI分析记录表** `ai_analysis`
```sql
CREATE TABLE ai_analysis (
    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    step_id INTEGER,
    screenshot_id INTEGER NOT NULL,
    prompt_text TEXT NOT NULL, -- 发送给AI的提示词
    model_name VARCHAR(100), -- 使用的模型名称
    ai_response TEXT NOT NULL, -- AI的完整回复
    extracted_json TEXT, -- 提取的JSON结果
    coordinates_x1 INTEGER, -- 识别的坐标
    coordinates_y1 INTEGER,
    coordinates_x2 INTEGER,
    coordinates_y2 INTEGER,
    confidence_score FLOAT, -- 置信度
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER, -- AI处理耗时
    api_cost DECIMAL(10,4), -- API调用成本
    conversation_context TEXT, -- 对话上下文
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (step_id) REFERENCES task_steps(step_id),
    FOREIGN KEY (screenshot_id) REFERENCES screenshots(screenshot_id)
);
```

#### 5. **操作执行记录表** `executions`
```sql
CREATE TABLE executions (
    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    step_id INTEGER,
    analysis_id INTEGER, -- 基于哪次AI分析
    operation_type VARCHAR(50), -- 'click', 'type', 'key_press', 'drag', 'scroll'
    target_x INTEGER, -- 操作目标坐标
    target_y INTEGER,
    operation_params TEXT, -- 操作参数 (JSON格式)
    execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_duration_ms INTEGER,
    success BOOLEAN DEFAULT FALSE,
    verification_screenshot_id INTEGER, -- 执行后的验证截图
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (step_id) REFERENCES task_steps(step_id),
    FOREIGN KEY (analysis_id) REFERENCES ai_analysis(analysis_id),
    FOREIGN KEY (verification_screenshot_id) REFERENCES screenshots(screenshot_id)
);
```

#### 6. **用户表** `users`
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    permission_level INTEGER DEFAULT 1, -- 1=普通用户, 2=高级用户, 3=管理员
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    preferences_json TEXT -- 用户偏好设置
);
```

#### 7. **设备表** `devices`
```sql
CREATE TABLE devices (
    device_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name VARCHAR(255) NOT NULL,
    device_ip VARCHAR(45),
    device_type VARCHAR(50), -- 'local', 'remote'
    os_info VARCHAR(255),
    screen_resolution VARCHAR(20),
    last_online TIMESTAMP,
    status VARCHAR(20) DEFAULT 'offline', -- 'online', 'offline', 'busy'
    owner_user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_user_id) REFERENCES users(user_id)
);
```

### 🔄 AI工作流存储逻辑

#### 工作流程：
1. **任务创建** → `tasks` 表新增记录
2. **步骤开始** → `task_steps` 表新增记录
3. **屏幕截图** → `screenshots` 表存储图像
4. **AI分析** → `ai_analysis` 表记录思考过程
5. **操作执行** → `executions` 表记录具体操作
6. **验证截图** → 再次存储到 `screenshots` 表
7. **循环下一步** → 重复步骤2-6

#### 关键特性：
- **完整追踪**：每个任务的完整执行链路都被记录
- **上下文保持**：AI对话历史存储在 `conversation_context` 字段
- **性能监控**：记录每个环节的耗时和成本
- **错误恢复**：详细的错误信息和重试机制
- **数据去重**：通过图片哈希避免重复存储

### 📈 索引优化建议

```sql
-- 任务查询优化
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

-- 步骤查询优化  
CREATE INDEX idx_steps_task_sequence ON task_steps(task_id, step_sequence);

-- AI分析查询优化
CREATE INDEX idx_analysis_task_timestamp ON ai_analysis(task_id, analysis_timestamp);

-- 执行记录查询优化
CREATE INDEX idx_executions_task_timestamp ON executions(task_id, execution_timestamp);
```

### 🛠️ 实现计划

- [x] **数据库初始化**
    - [x] 创建SQLite数据库文件
    - [x] 执行建表SQL脚本
    - [x] 创建必要的索引
    - [x] 插入初始测试数据

- [x] **ORM模型定义**
    - [x] 使用dataclass定义模型类
    - [x] 实现模型之间的关联关系
    - [x] 添加数据验证和约束

- [x] **数据访问层**
    - [x] 实现任务CRUD操作
    - [x] 实现AI工作流数据记录
    - [x] 实现查询和统计功能
    - [x] 添加数据库连接池

- [x] **AI工作流服务**
    - [x] 实现完整的工作流管理
    - [x] 整合截图-分析-执行流程
    - [x] 任务进度跟踪
    - [x] 数据完整性保证

- [x] **API接口**
    - [x] 基础数据库操作接口
    - [x] 工作流服务接口
    - [x] 任务状态查询接口
    - [x] 测试和演示脚本

### 📁 已创建的文件结构

```
database/
├── __init__.py          # 模块初始化文件
├── database.py          # 数据库连接和表创建
├── models.py            # 数据模型定义
├── dao.py               # 数据访问对象
├── workflow_service.py  # AI工作流服务
└── test_db.py          # 数据库测试脚本
```

### 🚀 快速开始

运行数据库测试：
```bash
cd database
python test_db.py
```

这将：
1. 创建数据库表结构
2. 初始化示例数据  
3. 演示完整的AI工作流程
4. 测试数据库性能
5. 生成演示任务和截图
