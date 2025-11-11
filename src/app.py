# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from bill_service import BillService
from database import init_db
import sqlite3
from datetime import datetime

# 初始化 Flask 应用和 BillService
app = Flask(__name__)
# 允许所有来源的前端跨域请求
CORS(app) 
bill_service = BillService()

# --- 错误处理 ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": str(error)}), 400

@app.errorhandler(Exception)
def handle_exception(e):
    # 记录日志
    app.logger.error(f"An unexpected error occurred: {e}")
    # 隐藏内部错误细节
    return jsonify({"error": "Internal Server Error"}), 500

# --- API 路由 ---

@app.route('/bill', methods=['POST'])
def route_upload_bill():
    """
    上传一个新账单
    JSON Body: {
        "name": "Dinner", "amount": 150, "flag": "expense", 
        "category": "Food", "tags": ["restaurant", "date"],
        "timestamp": "2025-10-28T20:00:00" (可选)
    }
    """
    data = request.json
    if not data or 'name' not in data or 'amount' not in data or 'flag' not in data or 'category' not in data:
        return bad_request("Missing required fields: name, amount, flag, category")
        
    try:
        new_bill_id = bill_service.upload_bill(data)
        return jsonify({"message": "Bill uploaded successfully", "bill_id": new_bill_id}), 201
    except Exception as e:
        return handle_exception(e)

@app.route('/bill/<int:bill_id>', methods=['GET'])
def route_fetch_bill(bill_id):
    """按 ID 获取单个账单。"""
    bill = bill_service.fetch_bill(bill_id)
    if bill:
        return jsonify(bill), 200
    else:
        return not_found(f"Bill with id {bill_id} not found")

@app.route('/bill/<int:bill_id>', methods=['PUT'])
def route_update_bill(bill_id):
    """按 ID 更新一个账单。"""
    data = request.json
    if not data:
        return bad_request("No data provided for update")

    success = bill_service.update_bill(bill_id, data)
    if success:
        return jsonify({"message": "Bill updated successfully", "bill_id": bill_id}), 200
    else:
        return not_found(f"Bill with id {bill_id} not found")

@app.route('/bill/<int:bill_id>', methods=['DELETE'])
def route_delete_bill(bill_id):
    """按 ID 删除一个账单。"""
    success = bill_service.delete_bill(bill_id)
    if success:
        return jsonify({"message": "Bill deleted successfully", "bill_id": bill_id}), 200
    else:
        return not_found(f"Bill with id {bill_id} not found")

@app.route('/bills', methods=['GET'])
def route_fetch_bills():
    """
    获取账单列表，可按 category, tags, start_date, end_date 过滤
    查询参数:
    /bills?category=Food
    /bills?tag=work&tag=clientA  (注意：多个 tag 参数)
    /bills?start_date=2025-01-01&end_date=2025-01-31
    """
    category = request.args.get('category')
    tags = request.args.getlist('tag')  # 使用 getlist 获取所有 'tag' 参数
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    bills = bill_service.fetch_bills(category, tags if tags else None, start_date, end_date)
    return jsonify(bills), 200

@app.route('/statistics', methods=['GET'])
def route_get_statistics():
    """
    获取统计数据
    查询参数:
    /statistics?start_date=2025-01-01&end_date=2025-01-31
    /statistics?start_date=...&end_date=...&category=Food
    /statistics?start_date=...&end_date=...&tag=work
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 前端可能只传年份或月份
    # 例如 /statistics?year=2025&month=10
    year = request.args.get('year')
    month = request.args.get('month')

    if not start_date and year:
        if month:
            # 月度统计
            start_date = f"{year}-{int(month):02d}-01"
            # 找到下个月的第一天，然后减一天
            next_month_year = int(year)
            next_month = int(month) + 1
            if next_month > 12:
                next_month = 1
                next_month_year += 1
            last_day = datetime(next_month_year, next_month, 1) - datetime.timedelta(days=1)
            end_date = last_day.strftime('%Y-%m-%d')
        else:
            # 年度统计
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"

    if not start_date or not end_date:
        return bad_request("Missing required query parameters: (start_date and end_date) or (year)")

    category = request.args.get('category')
    tags = request.args.getlist('tag')
    
    stats = bill_service.get_statistics(start_date, end_date, category, tags if tags else None)
    return jsonify(stats), 200

# --- 运行应用 ---
if __name__ == '__main__':
    print("Initializing database...")
    init_db()  # 确保数据库和表已创建
    print("Starting Flask server...")
    # debug=True 会在代码更改时自动重启服务器
    app.run(debug=True, port=5000)