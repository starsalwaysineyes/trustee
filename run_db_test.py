#!/usr/bin/env python3
"""
数据库测试运行脚本
在项目根目录运行此脚本来测试数据库功能
"""

import sys
import os

# 确保能导入database模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    try:
        # 导入并运行数据库测试
        from database.workflow_service import WorkflowService
        from database.database import db_manager
        from database.dao import TaskDAO, UserDAO, DeviceDAO
        
        print("🚀 开始测试数据库功能...")
        
        # 1. 初始化工作流服务
        workflow = WorkflowService()
        
        # 2. 初始化示例数据
        db_manager.init_sample_data()
        print("✅ 示例数据初始化完成")
        
        # 3. 创建测试任务
        task_id = workflow.create_task(
            user_id=1,
            task_name="关闭Typora应用",
            natural_language_input="请帮我关闭Typora窗口",
            device_id=1
        )
        print(f"✅ 创建任务成功，任务ID: {task_id}")
        
        # 4. 开始执行任务
        workflow.start_task_execution(task_id)
        print("✅ 任务开始执行")
        
        # 5. 模拟完整执行流程
        # 第一步：屏幕截图
        step1_id = workflow.create_capture_step(task_id, 1, "捕获当前屏幕状态")
        screenshot1_path = workflow.generate_screenshot_path(task_id, 1, "initial")
        
        # 创建模拟截图文件
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
        
        # 第二步：AI分析
        step2_id = workflow.create_analysis_step(
            task_id=task_id,
            step_sequence=2,
            screenshot_id=screenshot1_id,
            description="AI分析屏幕内容，识别Typora关闭按钮"
        )
        
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
            prompt_text="我想要关闭typora窗口，请告诉我关闭按钮的坐标",
            ai_response="找到了Typora关闭按钮",
            model_name="qwen2.5-vl-72b-instruct",
            extracted_data=extracted_data,
            coordinates=(2520, 50, 2550, 80),
            processing_time_ms=2500,
            api_cost=0.01
        )
        print(f"✅ 记录AI分析结果，ID: {analysis_id}")
        
        # 第三步：操作执行
        step3_id = workflow.create_execution_step(
            task_id=task_id,
            step_sequence=3,
            analysis_id=analysis_id,
            description="执行鼠标点击操作"
        )
        
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
        
        # 6. 完成任务
        workflow.update_task_progress(task_id)
        workflow.complete_task(task_id, success=True)
        print("✅ 任务执行完成")
        
        # 7. 获取任务摘要
        summary = workflow.get_task_summary(task_id)
        print("\n📊 任务执行摘要:")
        print(f"   任务名称: {summary['task'].task_name}")
        print(f"   执行状态: {summary['task'].status}")
        print(f"   总步骤数: {summary['total_steps']}")
        print(f"   完成步骤: {summary['completed_steps']}")
        print(f"   总成本: ${summary['total_cost']:.4f}")
        
        # 8. 测试查询功能
        print("\n🔍 测试数据查询功能...")
        user_tasks = TaskDAO.get_by_user_id(1)
        print(f"✅ 用户1的任务数量: {len(user_tasks)}")
        
        user = UserDAO.get_by_username("admin")
        if user:
            print(f"✅ 查询到用户: {user.username}")
        
        devices = DeviceDAO.get_by_user_id(1)
        print(f"✅ 用户1的设备数量: {len(devices)}")
        
        print(f"\n🎉 数据库测试完成！演示任务ID: {task_id}")
        print("📁 数据库文件: trustee.db")
        print("📁 截图目录: screenshots/")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 