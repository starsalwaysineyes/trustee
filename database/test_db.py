"""
数据库测试脚本
演示完整的AI工作流程和数据库操作
"""

import json
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_service import WorkflowService
from database import db_manager

def test_complete_workflow():
    """测试完整的AI工作流程"""
    print("🚀 开始测试AI工作流数据库操作...")
    
    # 初始化工作流服务
    workflow = WorkflowService()
    
    # 初始化示例数据
    db_manager.init_sample_data()
    print("✅ 示例数据初始化完成")
    
    # 1. 创建任务
    task_id = workflow.create_task(
        user_id=1,
        task_name="关闭Typora应用",
        natural_language_input="请帮我关闭Typora窗口",
        device_id=1
    )
    print(f"✅ 创建任务成功，任务ID: {task_id}")
    
    # 2. 开始任务执行
    workflow.start_task_execution(task_id)
    print("✅ 任务开始执行")
    
    # 3. 模拟第一步：屏幕截图
    step1_id = workflow.create_capture_step(task_id, 1, "捕获当前屏幕状态")
    screenshot1_path = workflow.generate_screenshot_path(task_id, 1, "initial")
    
    # 模拟创建截图文件（实际使用中会是真实截图）
    import os
    with open(screenshot1_path, 'w') as f:
        f.write("mock screenshot data")
    
    screenshot1_id = workflow.record_screenshot(
        task_id=task_id,
        step_id=step1_id,
        image_path=screenshot1_path,
        screen_resolution="2560x1600",
        purpose="initial"
    )
    print(f"✅ 记录初始截图，ID: {screenshot1_id}")
    
    # 4. 模拟第二步：AI分析
    step2_id = workflow.create_analysis_step(
        task_id=task_id,
        step_sequence=2,
        screenshot_id=screenshot1_id,
        description="AI分析屏幕内容，识别Typora关闭按钮"
    )
    
    # 模拟AI分析结果
    mock_ai_response = """根据屏幕分析，我发现了Typora窗口的关闭按钮。
关闭按钮位于窗口的右上角，坐标范围是：
```json
{
    "find": true,
    "x1": 2520,
    "y1": 50,
    "x2": 2550,
    "y2": 80,
    "confidence": 0.95
}
```"""
    
    extracted_data = {
        "find": True,
        "x1": 2520,
        "y1": 50,
        "x2": 2550,
        "y2": 80,
        "confidence": 0.95
    }
    
    analysis_id = workflow.record_ai_analysis(
        task_id=task_id,
        step_id=step2_id,
        screenshot_id=screenshot1_id,
        prompt_text="我的屏幕像素是2560*1600；我想要关闭typora窗口，请告诉我关闭按钮的坐标",
        ai_response=mock_ai_response,
        model_name="qwen2.5-vl-72b-instruct",
        extracted_data=extracted_data,
        coordinates=(2520, 50, 2550, 80),
        processing_time_ms=2500,
        api_cost=0.01,
        conversation_context="[]"
    )
    print(f"✅ 记录AI分析结果，ID: {analysis_id}")
    
    # 5. 模拟第三步：操作执行
    step3_id = workflow.create_execution_step(
        task_id=task_id,
        step_sequence=3,
        analysis_id=analysis_id,
        description="执行鼠标点击操作，关闭Typora窗口"
    )
    
    # 计算点击坐标（取中心点）
    center_x = (2520 + 2550) // 2
    center_y = (50 + 80) // 2
    
    execution_id = workflow.record_execution(
        task_id=task_id,
        step_id=step3_id,
        analysis_id=analysis_id,
        operation_type="click",
        target_x=center_x,
        target_y=center_y,
        success=True,
        execution_duration_ms=150,
        operation_params={"button": "left", "clicks": 1}
    )
    print(f"✅ 记录操作执行结果，ID: {execution_id}")
    
    # 6. 模拟第四步：验证截图
    step4_id = workflow.create_capture_step(task_id, 4, "验证操作结果")
    screenshot2_path = workflow.generate_screenshot_path(task_id, 4, "verification")
    
    with open(screenshot2_path, 'w') as f:
        f.write("mock verification screenshot data")
    
    screenshot2_id = workflow.record_screenshot(
        task_id=task_id,
        step_id=step4_id,
        image_path=screenshot2_path,
        screen_resolution="2560x1600",
        purpose="verification"
    )
    print(f"✅ 记录验证截图，ID: {screenshot2_id}")
    
    # 7. 更新任务进度和完成状态
    workflow.update_task_progress(task_id)
    workflow.complete_task(task_id, success=True)
    print("✅ 任务执行完成")
    
    # 8. 获取任务摘要
    summary = workflow.get_task_summary(task_id)
    print("\n📊 任务执行摘要:")
    print(f"   任务名称: {summary['task'].task_name}")
    print(f"   执行状态: {summary['task'].status}")
    print(f"   总步骤数: {summary['total_steps']}")
    print(f"   完成步骤: {summary['completed_steps']}")
    print(f"   总成本: ${summary['total_cost']:.4f}")
    
    print("\n📋 详细步骤:")
    for i, step in enumerate(summary['steps'], 1):
        print(f"   步骤{i}: {step.step_type} - {step.step_description} ({step.status})")
    
    return task_id

def test_data_queries():
    """测试数据查询功能"""
    print("\n🔍 测试数据查询功能...")
    
    from dao import TaskDAO, UserDAO, DeviceDAO
    
    # 查询用户任务
    user_tasks = TaskDAO.get_by_user_id(1)
    print(f"✅ 用户1的任务数量: {len(user_tasks)}")
    
    # 查询用户信息
    user = UserDAO.get_by_username("admin")
    if user:
        print(f"✅ 查询到用户: {user.username} (权限级别: {user.permission_level})")
    
    # 查询设备信息
    devices = DeviceDAO.get_by_user_id(1)
    print(f"✅ 用户1的设备数量: {len(devices)}")

def test_database_performance():
    """测试数据库性能"""
    print("\n⚡ 测试数据库性能...")
    
    import time
    from workflow_service import WorkflowService
    
    workflow = WorkflowService()
    
    # 批量创建任务测试
    start_time = time.time()
    task_ids = []
    
    for i in range(10):
        task_id = workflow.create_task(
            user_id=1,
            task_name=f"性能测试任务{i+1}",
            natural_language_input=f"执行性能测试操作{i+1}",
            device_id=1
        )
        task_ids.append(task_id)
    
    end_time = time.time()
    print(f"✅ 创建10个任务耗时: {(end_time - start_time):.3f}秒")
    
    # 批量查询测试
    start_time = time.time()
    for task_id in task_ids:
        workflow.get_task_summary(task_id)
    end_time = time.time()
    print(f"✅ 查询10个任务摘要耗时: {(end_time - start_time):.3f}秒")

if __name__ == "__main__":
    try:
        # 测试完整工作流
        task_id = test_complete_workflow()
        
        # 测试数据查询
        test_data_queries()
        
        # 测试性能
        test_database_performance()
        
        print(f"\n🎉 所有测试完成！创建的演示任务ID: {task_id}")
        print("📁 数据库文件: trustee.db")
        print("📁 截图目录: screenshots/")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 