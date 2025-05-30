"""
AI自动化服务演示脚本
展示如何使用AIAutomationService进行图像分析和操作自动化
"""

import os
import time
from ai_automation_service import AIAutomationService, AIAutomationWorkflow, quick_automation

def demo_basic_usage():
    """基础用法演示"""
    print("\n🚀 AI自动化服务 - 基础用法演示")
    print("=" * 60)
    
    # 检查测试图片
    test_image = "LLM/pics/test1.png"
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    print(f"📸 使用测试图片: {test_image}")
    
    # 1. 快速自动化（最简单的方式）
    print("\n1️⃣ 快速自动化演示")
    result = quick_automation(
        image_path=test_image,
        instruction="分析这个截图并找到窗口最大化按钮",
        execute=False,  # 演练模式
        show_preview=False
    )
    
    if result.get("success"):
        print("✅ 分析成功")
        action = result["parsed_action"]
        print(f"   思考过程: {action.get('thought', '无')}")
        print(f"   计划动作: {action.get('action', '无')}")
    else:
        print(f"❌ 分析失败: {result.get('error')}")

def demo_service_class():
    """服务类用法演示"""
    print("\n\n2️⃣ 服务类详细用法演示")
    print("=" * 60)
    
    # 初始化服务
    service = AIAutomationService()
    
    test_image = "LLM/pics/test1.png"
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    # 分析截图
    result = service.analyze_screenshot(
        image_path=test_image,
        user_instruction="找到并点击窗口的最大化按钮",
        show_visualization=False
    )
    
    if result.get("success"):
        print("📊 详细分析结果:")
        print(f"   图片尺寸: {result['image_info']['size']}")
        print(f"   处理时间: {result['ai_response']['processing_time_ms']}ms")
        print(f"   AI回复长度: {len(result['ai_response']['raw_text'])}字符")
        
        # 显示生成的代码
        code = result.get("pyautogui_code", "")
        if code and "无可执行的操作" not in code:
            print(f"\n🔧 生成的PyAutoGUI代码:")
            print("-" * 40)
            print(code)
            print("-" * 40)
        
        # 保存分析报告
        report_saved = service.save_analysis_report(result, "demo_analysis_report.json")
        if report_saved:
            print("💾 分析报告已保存到 demo_analysis_report.json")
    
    else:
        print(f"❌ 分析失败: {result.get('error')}")

def demo_batch_processing():
    """批量处理演示"""
    print("\n\n3️⃣ 批量处理演示")
    print("=" * 60)
    
    # 准备测试任务
    tasks = [
        {
            "image_path": "LLM/pics/test1.png",
            "instruction": "分析界面元素"
        }
    ]
    
    # 过滤存在的图片
    valid_tasks = []
    for task in tasks:
        if os.path.exists(task["image_path"]):
            valid_tasks.append(task)
        else:
            print(f"⚠️  跳过不存在的图片: {task['image_path']}")
    
    if not valid_tasks:
        print("❌ 没有有效的测试图片")
        return
    
    # 批量处理
    service = AIAutomationService()
    print(f"📦 批量处理 {len(valid_tasks)} 个任务...")
    
    start_time = time.time()
    results = service.batch_process(valid_tasks, execute=False)
    total_time = time.time() - start_time
    
    # 统计结果
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n📈 批量处理完成:")
    print(f"   总任务数: {len(results)}")
    print(f"   成功任务: {success_count}")
    print(f"   失败任务: {len(results) - success_count}")
    print(f"   总耗时: {total_time:.2f}秒")

def demo_workflow_class():
    """工作流类演示"""
    print("\n\n4️⃣ 工作流类演示")
    print("=" * 60)
    
    test_image = "LLM/pics/test1.png"
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    # 创建工作流
    service = AIAutomationService()
    workflow = AIAutomationWorkflow(service)
    
    # 运行单个任务
    result = workflow.run_single_task(
        image_path=test_image,
        instruction="检测界面中的可点击元素",
        auto_execute=False,  # 演练模式
        show_preview=False
    )
    
    print(f"\n📊 工作流会话统计:")
    print(f"   处理任务数: {len(workflow.session_results)}")

def demo_error_handling():
    """错误处理演示"""
    print("\n\n5️⃣ 错误处理演示")
    print("=" * 60)
    
    service = AIAutomationService()
    
    # 测试不存在的图片
    result = service.analyze_screenshot(
        image_path="不存在的图片.png",
        user_instruction="测试错误处理"
    )
    
    print("🧪 测试不存在图片的错误处理:")
    if not result.get("success"):
        print(f"✅ 正确捕获错误: {result.get('error')}")
    else:
        print("❌ 应该返回错误但没有")

def interactive_demo():
    """交互式演示"""
    print("\n\n6️⃣ 交互式模式演示")
    print("=" * 60)
    print("提示：在交互模式中，你可以：")
    print("- 输入图片路径和操作指令")
    print("- 输入 'help' 查看帮助")
    print("- 输入 'quit' 退出")
    print("- 选择是否实际执行操作")
    
    choice = input("\n是否进入交互模式? (y/N): ").strip().lower()
    if choice == 'y':
        service = AIAutomationService()
        workflow = AIAutomationWorkflow(service)
        workflow.interactive_mode()
    else:
        print("跳过交互模式演示")

def main():
    """主演示函数"""
    print("🤖 AI自动化服务完整演示")
    print("该演示将展示AI自动化服务的各种功能")
    print("注意：所有操作都在演练模式下运行，不会实际执行桌面操作")
    
    try:
        # 运行各种演示
        demo_basic_usage()
        demo_service_class() 
        demo_batch_processing()
        demo_workflow_class()
        demo_error_handling()
        
        # 可选的交互式演示
        interactive_demo()
        
        print("\n🎉 演示完成！")
        print("\n📁 生成的文件:")
        if os.path.exists("demo_analysis_report.json"):
            print("   - demo_analysis_report.json (分析报告)")
        
        print("\n💡 使用建议:")
        print("   1. 先在演练模式下测试，确认操作正确")
        print("   2. 确保桌面环境与截图一致")
        print("   3. 重要操作前备份数据")
        print("   4. 可以通过日志查看详细信息")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 