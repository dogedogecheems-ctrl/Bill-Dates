import os
from datetime import datetime
from dotenv import load_dotenv

class Config:
    # 数据库配置
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///finance.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    OPENAI_BASE_URL = os.environ.get('BASE_URL') or 'https://api.openai.com/v1'
    # AI API配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    AI_MODEL = os.environ.get('AI_MODEL') or 'gpt-3.5-turbo'
    
    # 应用设置
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    
    # 问卷配置
    QUESTIONNAIRES = {
        'risk_assessment': {
            'name': '投资风险评估问卷',
            'description': '评估您的投资风险承受能力',
            'questions': [
                {
                    'id': 'q1',
                    'question': '您的年龄段是？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '18-30岁'},
                        {'value': 2, 'text': '31-45岁'},
                        {'value': 3, 'text': '46-60岁'},
                        {'value': 4, 'text': '60岁以上'}
                    ]
                },
                {
                    'id': 'q2',
                    'question': '您的投资经验如何？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '完全没有经验'},
                        {'value': 2, 'text': '有一些基础知识'},
                        {'value': 3, 'text': '有2-5年投资经验'},
                        {'value': 4, 'text': '有5年以上丰富经验'}
                    ]
                },
                {
                    'id': 'q3',
                    'question': '您的月收入水平？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '5000元以下'},
                        {'value': 2, 'text': '5000-15000元'},
                        {'value': 3, 'text': '15000-30000元'},
                        {'value': 4, 'text': '30000元以上'}
                    ]
                },
                {
                    'id': 'q4',
                    'question': '您计划投资的资金占总资产的比例？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '10%以下'},
                        {'value': 2, 'text': '10%-30%'},
                        {'value': 3, 'text': '30%-50%'},
                        {'value': 4, 'text': '50%以上'}
                    ]
                },
                {
                    'id': 'q5',
                    'question': '如果您的投资在一年内亏损20%，您会？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '立即卖出，无法承受损失'},
                        {'value': 2, 'text': '感到焦虑，考虑卖出'},
                        {'value': 3, 'text': '保持冷静，继续观望'},
                        {'value': 4, 'text': '考虑加仓，逢低买入'}
                    ]
                },
                {
                    'id': 'q6',
                    'question': '您的投资目标是什么？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '保值为主，追求稳定'},
                        {'value': 2, 'text': '稳健增值，跑赢通胀'},
                        {'value': 3, 'text': '追求较高收益'},
                        {'value': 4, 'text': '追求最大收益'}
                    ]
                },
                {
                    'id': 'q7',
                    'question': '您希望多长时间内看到投资回报？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '1年以内'},
                        {'value': 2, 'text': '1-3年'},
                        {'value': 3, 'text': '3-5年'},
                        {'value': 4, 'text': '5年以上'}
                    ]
                },
                {
                    'id': 'q8',
                    'question': '您更倾向于哪种投资方式？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '银行存款、国债等低风险产品'},
                        {'value': 2, 'text': '货币基金、债券基金等中低风险产品'},
                        {'value': 3, 'text': '股票基金、混合基金等中高风险产品'},
                        {'value': 4, 'text': '股票、期货等高风险产品'}
                    ]
                }
            ],
            'scoring': {
                'conservative': {'min': 8, 'max': 16, 'label': '保守型'},
                'balanced': {'min': 17, 'max': 24, 'label': '平衡型'},
                'aggressive': {'min': 25, 'max': 32, 'label': '积极型'}
            }
        },
        'financial_profile': {
            'name': '财务状况评估问卷',
            'description': '了解您的财务状况和目标',
            'questions': [
                {
                    'id': 'fp1',
                    'question': '您目前的职业状态？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 'employed', 'text': '全职工作'},
                        {'value': 'part_time', 'text': '兼职工作'},
                        {'value': 'self_employed', 'text': '自主创业'},
                        {'value': 'unemployed', 'text': '待业'},
                        {'value': 'retired', 'text': '退休'}
                    ]
                },
                {
                    'id': 'fp2',
                    'question': '您每月的固定支出大约是多少？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '2000元以下'},
                        {'value': 2, 'text': '2000-5000元'},
                        {'value': 3, 'text': '5000-10000元'},
                        {'value': 4, 'text': '10000元以上'}
                    ]
                },
                {
                    'id': 'fp3',
                    'question': '您是否有应急基金？',
                    'type': 'single_choice',
                    'options': [
                        {'value': 1, 'text': '没有，月光族'},
                        {'value': 2, 'text': '有1-3个月的生活费'},
                        {'value': 3, 'text': '有3-6个月的生活费'},
                        {'value': 4, 'text': '有6个月以上的生活费'}
                    ]
                },
                {
                    'id': 'fp4',
                    'question': '您目前有哪些负债？',
                    'type': 'multiple_choice',
                    'options': [
                        {'value': 'none', 'text': '无负债'},
                        {'value': 'mortgage', 'text': '房贷'},
                        {'value': 'car_loan', 'text': '车贷'},
                        {'value': 'credit_card', 'text': '信用卡债务'},
                        {'value': 'student_loan', 'text': '学生贷款'},
                        {'value': 'other', 'text': '其他负债'}
                    ]
                },
                {
                    'id': 'fp5',
                    'question': '您的理财目标是什么？',
                    'type': 'multiple_choice',
                    'options': [
                        {'value': 'emergency_fund', 'text': '建立应急基金'},
                        {'value': 'house', 'text': '购买房产'},
                        {'value': 'car', 'text': '购买汽车'},
                        {'value': 'education', 'text': '教育储蓄'},
                        {'value': 'retirement', 'text': '退休规划'},
                        {'value': 'vacation', 'text': '旅游基金'},
                        {'value': 'investment', 'text': '投资理财'}
                    ]
                }
            ]
        }
    }
    
    # 理财产品配置
    DEFAULT_PRODUCTS = [
        {
            'name': '余额宝',
            'description': '支付宝旗下的货币基金产品，随存随取，适合短期资金管理',
            'productType': 'fund',
            'riskLevel': 'low',
            'expectedReturn': 2.5,
            'minInvestment': 1,
            'investmentPeriod': '随存随取',
            'features': {
                'liquidity': '高',
                'risk': '极低',
                'min_amount': '1元起投',
                'withdrawal': 'T+0到账'
            },
            'tags': ['货币基金', '低风险', '流动性高']
        },
        {
            'name': '招商银行朝朝盈',
            'description': '招商银行推出的现金管理类产品，收益稳定，风险较低',
            'productType': 'deposit',
            'riskLevel': 'low',
            'expectedReturn': 3.2,
            'minInvestment': 100,
            'investmentPeriod': '随存随取',
            'features': {
                'liquidity': '高',
                'risk': '极低',
                'min_amount': '100元起投',
                'withdrawal': '实时到账'
            },
            'tags': ['银行存款', '低风险', '收益稳定']
        },
        {
            'name': '易方达沪深300ETF',
            'description': '跟踪沪深300指数的ETF基金，分散投资，适合长期投资',
            'productType': 'fund',
            'riskLevel': 'medium',
            'expectedReturn': 8.5,
            'minInvestment': 100,
            'investmentPeriod': '建议3年以上',
            'features': {
                'liquidity': '中',
                'risk': '中等',
                'min_amount': '100元起投',
                'tracking': '沪深300指数'
            },
            'tags': ['指数基金', '分散投资', '长期持有']
        },
        {
            'name': '中国平安重疾险',
            'description': '提供重大疾病保障，保障范围广泛，理赔快速',
            'productType': 'insurance',
            'riskLevel': 'low',
            'expectedReturn': 0,
            'minInvestment': 3000,
            'investmentPeriod': '长期保障',
            'features': {
                'coverage': '重疾保障',
                'diseases': '100种重疾',
                'payment': '年缴',
                'benefit': '确诊即赔'
            },
            'tags': ['健康保障', '重疾保险', '家庭保障']
        },
        {
            'name': '国债逆回购',
            'description': '以国债为抵押的资金借贷，安全性高，收益稳定',
            'productType': 'bond',
            'riskLevel': 'low',
            'expectedReturn': 3.8,
            'minInvestment': 1000,
            'investmentPeriod': '1-182天可选',
            'features': {
                'liquidity': '中',
                'risk': '极低',
                'collateral': '国债抵押',
                'market': '交易所交易'
            },
            'tags': ['国债', '逆回购', '安全性高']
        },
        {
            'name': '贵州茅台股票',
            'description': 'A股优质蓝筹股，业绩稳定，适合价值投资',
            'productType': 'stock',
            'riskLevel': 'high',
            'expectedReturn': 15.0,
            'minInvestment': 180000,  # 按当前股价估算
            'investmentPeriod': '建议5年以上',
            'features': {
                'liquidity': '高',
                'risk': '较高',
                'market': 'A股',
                'sector': '白酒行业'
            },
            'tags': ['蓝筹股', '价值投资', '高分红']
        }
    ]
    
    # 分类配置
    CATEGORIES = {
        'income': {
            'salary': '工资收入',
            'bonus': '奖金收入',
            'investment': '投资收益',
            'part_time': '兼职收入',
            'other': '其他收入'
        },
        'expense': {
            'food': '餐饮美食',
            'transport': '交通出行',
            'shopping': '购物消费',
            'entertainment': '娱乐休闲',
            'health': '医疗健康',
            'education': '教育培训',
            'housing': '住房开销',
            'utilities': '水电煤气',
            'communication': '通讯费用',
            'insurance': '保险费用',
            'other': '其他支出'
        }
    }
    
    # 储蓄目标类型
    SAVINGS_GOAL_TYPES = {
        'emergency': '应急基金',
        'vacation': '旅游基金',
        'house': '购房基金',
        'car': '购车基金',
        'education': '教育基金',
        'retirement': '退休基金',
        'investment': '投资本金',
        'other': '其他目标'
    }
    
    # 风险等级配置
    RISK_LEVELS = {
        'low': {'name': '低风险', 'color': '#10B981'},
        'medium': {'name': '中等风险', 'color': '#F59E0B'},
        'high': {'name': '高风险', 'color': '#EF4444'}
    }
    
    # 产品类型配置
    PRODUCT_TYPES = {
        'fund': {'name': '基金', 'icon': '📊'},
        'insurance': {'name': '保险', 'icon': '🛡️'},
        'deposit': {'name': '存款', 'icon': '🏦'},
        'bond': {'name': '债券', 'icon': '📜'},
        'stock': {'name': '股票', 'icon': '📈'}
    }


"""
智能金融助手 - 配置文件
包含Qwen API相关配置信息
"""

# Qwen API配置
QWEN_API_KEY = "your-api-key"  # Qwen API Key
QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"  # Qwen API endpoint
QWEN_MODEL = "qwen3-max"  # 使用的模型

# Flask配置
FLASK_HOST = "127.0.0.1"  # Flask服务器地址
FLASK_PORT = 5001  # Flask服务器端口
FLASK_DEBUG = True  # 调试模式

# 日志配置
LOG_FILE = "backend/system.log"  # 日志文件路径
LOG_LEVEL = "INFO"  # 日志级别

# MPT算法配置
MIN_PORTFOLIO_WEIGHT = 0.0  # 最小投资组合权重
MAX_PORTFOLIO_WEIGHT = 1.0  # 最大投资组合权重
WEIGHT_SUM_TOLERANCE = 1e-6  # 权重和的容差

# 风险评分映射配置
RISK_SCENARIO_MAPPING = {
    "a) 卖出止损": 2,      # 保守型
    "b) 继续持有": 5,      # 稳健型
    "c) 加仓买入": 8       # 激进型
}

RISK_FOCUS_MAPPING = {
    "a) 本金绝对安全": 1,       # 极度保守
    "b) 跑赢通胀": 4,           # 稳健保守
    "c) 获得远超市场的收益，哪怕风险很高": 9  # 激进
}

KNOWLEDGE_LEVEL_MAPPING = {
    "a) 小白": 2,          # 投资新手，风险承受能力较低
    "b) 略有了解": 5,      # 有一定投资经验
    "c) 经验丰富": 8       # 投资专家，风险承受能力较高
}