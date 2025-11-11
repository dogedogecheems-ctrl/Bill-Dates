#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和初始化默认数据
"""

import os
import sys
from app import app, db
from models import Bill, SavingsGoal, FinancialProfile, RiskProfile, Questionnaire, FinancialProduct, UserPreference, AIAdvice
from config import Config
from datetime import datetime, date, timedelta
import random

def create_sample_data():
    """创建示例数据"""
    print("正在创建示例数据...")
    
    # 创建示例账单数据
    sample_bills = [
        {
            'type': 'income',
            'amount': 8000,
            'category': 'salary',
            'date': date.today().replace(day=1),
            'note': '月工资收入'
        },
        {
            'type': 'expense',
            'amount': 150,
            'category': 'food',
            'date': date.today() - timedelta(days=1),
            'note': '午餐费用'
        },
        {
            'type': 'expense',
            'amount': 50,
            'category': 'transport',
            'date': date.today() - timedelta(days=2),
            'note': '地铁交通卡'
        },
        {
            'type': 'expense',
            'amount': 200,
            'category': 'shopping',
            'date': date.today() - timedelta(days=3),
            'note': '生活用品'
        },
        {
            'type': 'expense',
            'amount': 100,
            'category': 'entertainment',
            'date': date.today() - timedelta(days=4),
            'note': '电影票'
        },
        {
            'type': 'income',
            'amount': 500,
            'category': 'bonus',
            'date': date.today() - timedelta(days=5),
            'note': '项目奖金'
        }
    ]
    
    for bill_data in sample_bills:
        bill = Bill(**bill_data)
        db.session.add(bill)
    
    # 创建示例储蓄目标
    sample_goals = [
        {
            'name': '应急基金',
            'targetAmount': 10000,
            'currentAmount': 3500,
            'type': 'emergency',
            'targetDate': date.today() + timedelta(days=365)
        },
        {
            'name': '旅游基金',
            'targetAmount': 5000,
            'currentAmount': 1200,
            'type': 'vacation',
            'targetDate': date.today() + timedelta(days=180)
        },
        {
            'name': '购车基金',
            'targetAmount': 50000,
            'currentAmount': 8000,
            'type': 'car',
            'targetDate': date.today() + timedelta(days=730)
        }
    ]
    
    for goal_data in sample_goals:
        goal = SavingsGoal(**goal_data)
        db.session.add(goal)
    
    # 创建示例AI建议
    sample_advice = [
        {
            'userId': 'default_user',
            'adviceType': 'financial_planning',
            'content': '基于您的财务状况分析，建议：1. 继续保持良好的储蓄习惯，将收入的20%用于储蓄和投资；2. 建立应急基金，目标为3-6个月的生活费用；3. 考虑分散投资，降低风险；4. 定期review您的财务目标和计划。',
            'context': {'dashboard_data': {'totalIncome': 8500, 'totalExpense': 500, 'balance': 8000}}
        },
        {
            'userId': 'default_user',
            'adviceType': 'investment',
            'content': '根据您的风险承受能力，推荐以下投资策略：1. 40%投资于低风险的货币基金或银行存款；2. 30%投资于中等风险的债券基金；3. 20%投资于股票型基金进行长期增值；4. 10%保留现金作为流动性储备。建议定期调整资产配置。',
            'context': {'risk_level': 'balanced', 'recommended_products': ['fund', 'bond', 'deposit']}
        }
    ]
    
    for advice_data in sample_advice:
        advice = AIAdvice(**advice_data)
        db.session.add(advice)
    
    db.session.commit()
    print("示例数据创建完成")

def main():
    """主函数"""
    print("开始初始化数据库...")
    
    with app.app_context():
        try:
            # 创建数据库表
            print("正在创建数据库表...")
            db.create_all()
            print("数据库表创建完成")
            
            # 检查是否已有数据
            if FinancialProduct.query.first():
                print("数据库中已有数据，跳过初始化")
                return
            
            # 初始化默认数据
            print("正在初始化默认数据...")
            
            # 创建默认问卷
            for key, questionnaire_data in Config.QUESTIONNAIRES.items():
                questionnaire = Questionnaire(
                    name=questionnaire_data['name'],
                    description=questionnaire_data['description'],
                    questions=questionnaire_data['questions'],
                    type=key
                )
                db.session.add(questionnaire)
            
            # 创建默认理财产品
            for product_data in Config.DEFAULT_PRODUCTS:
                product = FinancialProduct(**product_data)
                db.session.add(product)
            
            # 创建默认用户偏好
            preference = UserPreference(
                userId='default_user',
                preferenceType='notification',
                preferenceValue={'enabled': True, 'types': ['bill_reminder', 'goal_achievement']}
            )
            db.session.add(preference)
            
            db.session.commit()
            print("默认数据初始化完成")
            
            # 创建示例数据
            create_sample_data()
            
            print("数据库初始化完成！")
            
        except Exception as e:
            print(f"初始化失败: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    main()