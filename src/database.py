# database.py
import sqlite3
import os

DATABASE_NAME = "bill_database.db"

def get_db_connection():
    """获取数据库连接，并设置 row_factory 以便返回字典。"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # 这允许我们按列名访问数据
    return conn

def init_db():
    """初始化数据库，创建 bills 表。"""
    if os.path.exists(DATABASE_NAME):
        print("Database already exists.")
        # return # 在开发中，我们可能想每次都重新创建
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 我们需要一个 timestamp 列来进行月度和年度统计
    # tags 将存储为 JSON 字符串
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        amount INTEGER NOT NULL,
        flag TEXT NOT NULL CHECK(flag IN ('income', 'expense')),
        category TEXT NOT NULL,
        tags TEXT, -- 存储为 JSON 列表: '["food", "travel"]'
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    # 可以直接运行 python database.py 来初始化数据库
    init_db()