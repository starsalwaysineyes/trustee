# 🚀 Trustee 快速启动指南

## 一键启动 (5分钟搞定)

### 1. 环境检查
```bash
python3 --version  # 需要 Python 3.8+
```

### 2. 安装依赖
```bash
# 方式一：使用 uv (推荐)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# 方式二：使用 pip
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 启动服务
```bash
python3 api.py
```

### 4. 访问系统
- **地址**: http://localhost:5000
- **账号**: admin
- **密码**: admin

## 🧪 验证安装

运行自动化测试验证系统完整性：
```bash
python3 test_login_flow.py
```

预期输出：
```
🚀 Trustee 系统集成测试
✅ 服务器运行正常
✅ 未登录时正确跳转到登录页
✅ 登录成功: 登录成功
✅ 登录后正确跳转到设备页面
✅ /devices 页面访问正常
✅ /tasks 页面访问正常
✅ /ai-studio 页面访问正常
✅ 设备列表 API 调用成功
✅ 任务列表 API 调用成功
✅ 统计信息 API 调用成功
✅ 登出成功
✅ 登出后正确拒绝API访问

🎉 所有测试通过！系统运行正常
```

## 📱 功能体验

### 1. 设备管理
- 点击侧边栏"设备管理"
- 添加新设备：填写设备名称、IP地址等信息
- 查看设备状态和详细信息

### 2. 任务管理  
- 点击侧边栏"任务管理"
- 创建新任务：输入自然语言指令
- 监控任务执行状态和进度

### 3. AI工作室
- 点击侧边栏"AI工作室"
- 上传截图或选择图片
- 输入操作指令，查看AI分析结果

## 🔧 常见问题

### 端口被占用
```bash
# 查找占用进程
lsof -i :5000

# 杀掉进程
kill -9 <PID>
```

### 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 数据库错误
```bash
# 重新创建数据库
rm database/trustee.db
python3 api.py
```

## 📚 更多信息

- **完整文档**: [README.md](README.md)
- **API文档**: [README.md#api文档](README.md#api文档)
- **项目总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **测试报告**: [TEST_RESULTS_AND_DEPLOYMENT.md](TEST_RESULTS_AND_DEPLOYMENT.md)

---

**🎉 恭喜！您已成功启动 Trustee 智能自动化助手！** 