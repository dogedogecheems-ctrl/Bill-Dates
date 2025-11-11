# bill_service.py
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from database import get_db_connection

class BillService:
    
    def __init__(self):
        # 确保数据库已初始化
        self.init_db_check()

    def init_db_check(self):
        """检查表是否存在，如果不存在则创建。"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bills';")
        if not cursor.fetchone():
            print("Table 'bills' not found, initializing database...")
            # 这是简化的做法，实际应调用 database.py 中的 init_db
            # 为简单起见，我们在这里复制建表语句
            cursor.execute("""
            CREATE TABLE bills (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                flag TEXT NOT NULL CHECK(flag IN ('income', 'expense')),
                category TEXT NOT NULL,
                tags TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()
            print("Database initialized.")
        conn.close()
        
    def _format_bill(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典，并解析 tags。"""
        if not row:
            return None
        bill = dict(row)
        # 将 JSON 字符串转回 Python 列表
        try:
            bill['tags'] = json.loads(bill['tags']) if bill['tags'] else []
        except json.JSONDecodeError:
            bill['tags'] = []
        return bill

    def fetch_bill(self, bill_id: int) -> Optional[Dict[str, Any]]:
        """按 bill_id 获取单个账单。"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bills WHERE bill_id = ?", (bill_id,))
        row = cursor.fetchone()
        conn.close()
        return self._format_bill(row)

    def fetch_bills(self, 
                    category: Optional[str] = None, 
                    tags: Optional[List[str]] = None,
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        按类别、标签、日期范围获取多个账单。
        注意：按标签过滤 (tags) 在 Python 中完成，因为在 SQLite 中搜索 JSON 字符串列表很复杂。
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM bills WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            # 为了包含 end_date 当天，我们通常查到 23:59:59
            query += " AND timestamp <= ?"
            params.append(f"{end_date} 23:59:59")
            
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        # 格式化并进行 Python 层的 tags 过滤
        bills = [self._format_bill(row) for row in rows]
        
        if tags:
            filtered_bills = []
            tag_set = set(tags)
            for bill in bills:
                # 检查账单的 tags 和查询的 tags 是否有交集
                if not tag_set.isdisjoint(set(bill['tags'])):
                    filtered_bills.append(bill)
            return filtered_bills
            
        return bills

    def upload_bill(self, data: Dict[str, Any]) -> int:
        """上传新账单。"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 将 tags 列表转换为 JSON 字符串
        tags_json = json.dumps(data.get('tags', []))
        
        # 处理时间戳
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        cursor.execute(
            """
            INSERT INTO bills (name, amount, flag, category, tags, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data['name'],
                data['amount'],
                data['flag'],
                data['category'],
                tags_json,
                timestamp
            )
        )
        conn.commit()
        new_bill_id = cursor.lastrowid
        conn.close()
        return new_bill_id

    def update_bill(self, bill_id: int, data: Dict[str, Any]) -> bool:
        """更新现有账单。"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tags_json = json.dumps(data.get('tags', []))
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        cursor.execute(
            """
            UPDATE bills
            SET name = ?, amount = ?, flag = ?, category = ?, tags = ?, timestamp = ?
            WHERE bill_id = ?
            """,
            (
                data['name'],
                data['amount'],
                data['flag'],
                data['category'],
                tags_json,
                timestamp,
                bill_id
            )
        )
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_bill(self, bill_id: int) -> bool:
        """删除账单。"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bills WHERE bill_id = ?", (bill_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def get_statistics(self, 
                       start_date: str, 
                       end_date: str, 
                       category: Optional[str] = None, 
                       tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取指定时间范围内的统计数据。
        可以按类别和标签进行过滤。
        """
        # 复用 fetch_bills 来获取过滤后的数据
        bills = self.fetch_bills(category, tags, start_date, end_date)
        
        total_income = 0
        total_expense = 0
        by_category = {}  # {'food': {'expense': 1000}, 'salary': {'income': 5000}}
        by_tag = {}       # {'work': {'expense': 200}, 'personal': {'expense': 800}}

        for bill in bills:
            flag = bill['flag']
            amount = bill['amount']
            cat = bill['category']
            
            # 1. 累计总收入和总支出
            if flag == 'income':
                total_income += amount
            else:
                total_expense += amount
                
            # 2. 按分类统计
            if cat not in by_category:
                by_category[cat] = {'income': 0, 'expense': 0}
            by_category[cat][flag] += amount
            
            # 3. 按标签统计
            for tag in bill['tags']:
                if tag not in by_tag:
                    by_tag[tag] = {'income': 0, 'expense': 0}
                by_tag[tag][flag] += amount

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_total": total_income - total_expense,
            "by_category": by_category,
            "by_tag": by_tag,
            "filtered_bill_count": len(bills)
        }