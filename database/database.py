"""
数据库连接管理和初始化模块
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "trustee.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """确保数据库文件存在"""
        if not os.path.exists(self.db_path):
            logger.info(f"创建新的数据库文件: {self.db_path}")
            self.create_database()
        else:
            logger.info(f"使用现有数据库: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库操作错误: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def create_database(self):
        """创建数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    permission_level INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    preferences_json TEXT
                )
            """)
            
            # 创建设备表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS devices (
                    device_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_name VARCHAR(255) NOT NULL,
                    device_ip VARCHAR(45),
                    device_type VARCHAR(50),
                    os_info VARCHAR(255),
                    screen_resolution VARCHAR(20),
                    last_online TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'offline',
                    owner_user_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_user_id) REFERENCES users(user_id)
                )
            """)
            
            # 创建任务主表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    device_id INTEGER,
                    task_name VARCHAR(255) NOT NULL,
                    task_description TEXT,
                    task_type VARCHAR(50),
                    natural_language_input TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_steps INTEGER DEFAULT 0,
                    completed_steps INTEGER DEFAULT 0,
                    error_message TEXT,
                    config_json TEXT,
                    estimated_duration VARCHAR(50),
                    actual_duration VARCHAR(50),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (device_id) REFERENCES devices(device_id)
                )
            """)
            
            # 创建任务执行步骤表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_steps (
                    step_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    step_sequence INTEGER NOT NULL,
                    step_type VARCHAR(50),
                    step_description TEXT,
                    screenshot_id INTEGER,
                    ai_analysis_id INTEGER,
                    execution_id INTEGER,
                    status VARCHAR(20) DEFAULT 'pending',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration_ms INTEGER,
                    retry_count INTEGER DEFAULT 0,
                    error_details TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
                )
            """)
            
            # 创建屏幕截图表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS screenshots (
                    screenshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    step_id INTEGER,
                    image_path VARCHAR(500) NOT NULL,
                    image_base64 TEXT,
                    screen_resolution VARCHAR(20),
                    capture_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_size INTEGER,
                    image_hash VARCHAR(64),
                    purpose VARCHAR(50),
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                    FOREIGN KEY (step_id) REFERENCES task_steps(step_id)
                )
            """)
            
            # 创建AI分析记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    step_id INTEGER,
                    screenshot_id INTEGER NOT NULL,
                    prompt_text TEXT NOT NULL,
                    model_name VARCHAR(100),
                    ai_response TEXT NOT NULL,
                    extracted_json TEXT,
                    coordinates_x1 INTEGER,
                    coordinates_y1 INTEGER,
                    coordinates_x2 INTEGER,
                    coordinates_y2 INTEGER,
                    confidence_score FLOAT,
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_time_ms INTEGER,
                    api_cost DECIMAL(10,4),
                    conversation_context TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                    FOREIGN KEY (step_id) REFERENCES task_steps(step_id),
                    FOREIGN KEY (screenshot_id) REFERENCES screenshots(screenshot_id)
                )
            """)
            
            # 创建操作执行记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    step_id INTEGER,
                    analysis_id INTEGER,
                    operation_type VARCHAR(50),
                    target_x INTEGER,
                    target_y INTEGER,
                    operation_params TEXT,
                    execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    execution_duration_ms INTEGER,
                    success BOOLEAN DEFAULT FALSE,
                    verification_screenshot_id INTEGER,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
                    FOREIGN KEY (step_id) REFERENCES task_steps(step_id),
                    FOREIGN KEY (analysis_id) REFERENCES ai_analysis(analysis_id),
                    FOREIGN KEY (verification_screenshot_id) REFERENCES screenshots(screenshot_id)
                )
            """)
            
            # 创建分析日志表 (AnalysisLog)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    timestamp TIMESTAMP NOT NULL,
                    user_instruction TEXT NOT NULL,
                    original_screenshot_base64 TEXT,
                    annotated_screenshot_base64 TEXT,
                    analysis_result_json TEXT NOT NULL,
                    target_resolution TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            conn.commit()
            self.create_indexes(cursor)
            conn.commit()
            logger.info("数据库表创建完成")
    
    def create_indexes(self, cursor):
        """创建索引以优化查询性能"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_tasks_user_status ON tasks(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_steps_task_sequence ON task_steps(task_id, step_sequence)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_task_timestamp ON ai_analysis(task_id, analysis_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_executions_task_timestamp ON executions(task_id, execution_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_screenshots_task_timestamp ON screenshots(task_id, capture_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_analysis_log_user_timestamp ON analysis_log(user_id, timestamp)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        logger.info("数据库索引创建完成")
    
    def init_sample_data(self):
        """初始化示例数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否已有数据
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # 插入示例用户
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, permission_level)
                    VALUES ('admin', 'admin@trustee.com', 'hashed_password_123', 3)
                """)
                
                user_id = cursor.lastrowid
                
                # 插入示例设备
                cursor.execute("""
                    INSERT INTO devices (device_name, device_ip, device_type, screen_resolution, status, owner_user_id)
                    VALUES ('家庭电脑', '192.168.1.5', 'local', '2560x1600', 'online', ?)
                """, (user_id,))
                
                device_id = cursor.lastrowid
                
                # 插入示例任务
                cursor.execute("""
                    INSERT INTO tasks (user_id, device_id, task_name, task_description, natural_language_input, status)
                    VALUES (?, ?, '关闭Typora应用', '自动关闭Typora应用程序', '请帮我关闭Typora窗口', 'completed')
                """, (user_id, device_id))
                
                conn.commit()
                logger.info("示例数据初始化完成")

# 全局数据库管理器实例
db_manager = DatabaseManager() 