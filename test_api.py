#!/usr/bin/env python3
"""
API测试脚本
用于验证后端API功能是否正常
"""

import requests
import json
from datetime import datetime, date

def test_api():
    """测试API接口"""
    base_url = "http://localhost:5000/api"
    
    print("🧪 开始测试API接口...")
    
    try:
        # 测试配置接口
        print("\n1. 测试配置接口...")
        response = requests.get(f"{base_url}/config")
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            config = response.json()
            print(f"   📊 配置信息: {len(config)} 个配置项")
        
        # 测试仪表盘接口
        print("\n2. 测试仪表盘接口...")
        response = requests.get(f"{base_url}/dashboard-summary")
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   💰 总收入: ¥{data.get('totalIncome', 0)}")
            print(f"   💸 总支出: ¥{data.get('totalExpense', 0)}")
            print(f"   💎 结余: ¥{data.get('balance', 0)}")
            print(f"   📈 健康分数: {data.get('healthScore', 0)}")
        
        # 测试账单接口
        print("\n3. 测试账单接口...")
        response = requests.get(f"{base_url}/bills")
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            bills = response.json()
            print(f"   📝 账单数量: {len(bills)}")
        
        # 测试储蓄目标接口
        print("\n4. 测试储蓄目标接口...")
        response = requests.get(f"{base_url}/savings-goals")
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            goals = response.json()
            print(f"   🎯 储蓄目标数量: {len(goals)}")
        
        # 测试理财产品接口
        print("\n5. 测试理财产品接口...")
        response = requests.get(f"{base_url}/financial-products")
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"   💼 理财产品数量: {len(products)}")
        
        # 测试问卷接口
        print("\n6. 测试问卷接口...")
        response = requests.get(f"{base_url}/questionnaires")
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 200:
            questionnaires = response.json()
            print(f"   📋 问卷数量: {len(questionnaires)}")
        
        # 测试创建账单
        print("\n7. 测试创建账单...")
        new_bill = {
            'type': 'expense',
            'amount': 100,
            'category': 'food',
            'date': date.today().isoformat(),
            'note': '测试账单'
        }
        response = requests.post(f"{base_url}/bills", json=new_bill)
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 201:
            created_bill = response.json()
            print(f"   🆔 创建成功，ID: {created_bill['id']}")
        
        print("\n🎉 API测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("❌ 错误: 无法连接到服务器，请确保应用已启动")
        print("   运行: python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == '__main__':
    test_api()