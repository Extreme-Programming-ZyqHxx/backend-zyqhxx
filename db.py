import sqlite3
from sqlite3 import Connection
import os

# 修复：简化DB_PATH路径，确保创建在项目根目录的data文件夹
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'contacts.db')


def get_db_connection() -> Connection:
    """获取数据库连接（确保路径正确）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 支持按列名访问
    return conn


def init_db():
    """初始化数据库表（带完整日志）"""
    # 确保data文件夹存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    print(f"数据库文件路径：{DB_PATH}")

    conn = get_db_connection()
    try:
        # 1. 用户表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. 分组表
        conn.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE (group_name, user_id)
            )
        ''')

        # 3. 联系人表（新增收藏+多字段）
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone1 TEXT NOT NULL,
                phone2 TEXT,
                email1 TEXT,
                email2 TEXT,
                social_media TEXT,
                address TEXT,
                group_id INTEGER DEFAULT 0,
                user_id INTEGER NOT NULL,
                is_favorite INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE SET NULL,
                UNIQUE (phone1, user_id)  -- 同一用户手机号唯一
            )
        ''')

        conn.commit()
        print("✅ 数据库表初始化成功：users、groups、contacts")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ 初始化数据库失败：{str(e)}")
    finally:
        conn.close()


# 初始化数据库（启动时执行）
init_db()