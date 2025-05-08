from flask import Flask, render_template

app = Flask(__name__)

# Sample data (replace with actual data later)
devices = [
    {"name": "家庭电脑", "ip": "192.168.1.5", "connected": True},
    {"name": "办公室电脑", "ip": "192.168.1.10", "connected": False},
]

tasks = [
    {"id": 1, "name": "定时关机", "status": "执行中", "schedule": "今天 23:00 执行", "countdown": "3小时25分钟", "details": "关闭所有应用", "icon": "schedule"},
    {"id": 2, "name": "数据备份", "status": "等待中", "schedule": "每周五 18:00 执行", "details": "备份文件夹：D:/重要文档", "icon": "folder"},
    {"id": 3, "name": "屏幕录制", "status": "已完成", "schedule": "今天 14:30-15:30", "details": "录制时长：1小时，文件大小：120MB", "icon": "check_circle"},
]

history = [
    {"group": "今天", "items": [
        {"name": "屏幕录制", "time": "14:30-15:30", "status": "成功", "status_color": "green"}
    ]},
    {"group": "昨天", "items": [
        {"name": "系统更新检查", "time": "09:00", "status": "部分完成", "status_color": "yellow"},
        {"name": "定时关机", "time": "23:00", "status": "成功", "status_color": "green"}
    ]},
    {"group": "上周五", "items": [
        {"name": "数据备份", "time": "18:00", "status": "成功", "status_color": "green"},
        {"name": "文件下载", "time": "16:15", "status": "失败", "status_color": "red"}
    ]},
]

@app.route('/')
@app.route('/devices')
def device_list():
    return render_template('devices.html', current_page='devices', devices=devices)

@app.route('/tasks')
def task_list():
    # Add filtering logic later if needed
    return render_template('tasks.html', current_page='tasks', tasks=tasks)

@app.route('/tasks/new')
def create_task_form():
    return render_template('create_task.html', current_page='tasks') # Keep task active in nav

@app.route('/tasks/<int:task_id>')
def task_detail(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task:
        # Sample detail data (can be expanded based on task type)
        task_details_data = {
            "created": "2023-08-15 14:30",
            "last_run": "2023-08-22 18:00",
            "next_run": "2023-08-29 18:00",
            "frequency": "每周五 18:00",
            "source": "D:/重要文档",
            "target": "E:/备份/每周备份",
            "method": "增量备份",
            "compression": "ZIP格式, 中等压缩",
            "history": [
                {"date": "2023-08-22 18:00", "details": "文件: 183个, 大小: 1.2GB", "status": "成功", "status_color": "green"},
                {"date": "2023-08-15 18:00", "details": "文件: 176个, 大小: 1.1GB", "status": "成功", "status_color": "green"},
                {"date": "2023-08-08 18:00", "details": "文件: 164个, 大小: 980MB", "status": "失败", "status_color": "red"},
            ]
        }
        return render_template('task_detail.html', current_page='tasks', task=task, details=task_details_data)
    else:
        return "Task not found", 404

@app.route('/history')
def history_list():
    return render_template('history.html', current_page='history', history=history)

if __name__ == '__main__':
    app.run(debug=True) 