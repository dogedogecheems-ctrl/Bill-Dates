"""
智能金融助手 - 工具函数
包含日志配置、数据清洗等辅助功能
"""

import logging
import os
import re
from typing import Union, Any, Dict
from config import LOG_FILE, LOG_LEVEL

def setup_logging():
    """
    配置日志系统
    创建日志目录并设置日志格式
    """
    # 确保日志目录存在
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # 配置日志格式
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )

    return logging.getLogger(__name__)

def clean_numeric_input(value: Union[str, int, float]) -> float:
    """
    清洗数字输入，移除常见的非数字字符

    Args:
        value: 输入值（字符串、整数或浮点数）

    Returns:
        float: 清洗后的数字

    Examples:
        clean_numeric_input("25岁") -> 25.0
        clean_numeric_input("10,0000万元") -> 1000000.0
        clean_numeric_input("1,000,000") -> 1000000.0
    """
    if isinstance(value, (int, float)):
        return float(value)

    if not isinstance(value, str):
        raise ValueError(f"无法处理的输入类型: {type(value)}")

    # 移除中文字符（岁、年、万元、千元、元等）
    cleaned = re.sub(r'[岁年万千元]', '', value)

    # 移除英文字符（years、$、comma等）
    cleaned = re.sub(r'[years$]', '', cleaned, flags=re.IGNORECASE)

    # 移除逗号和空格
    cleaned = re.sub(r'[,\s]', '', cleaned)

    # 处理特殊单位转换
    if '万' in value and cleaned:
        # 如果原字符串包含"万"，则乘以10000
        numeric_value = float(cleaned) * 10000
    elif '千' in value and cleaned:
        # 如果原字符串包含"千"，则乘以1000
        numeric_value = float(cleaned) * 1000
    elif cleaned:
        numeric_value = float(cleaned)
    else:
        raise ValueError(f"无法从输入 '{value}' 中提取有效数字")

    return numeric_value

def calculate_risk_score(risk_scenario: str, risk_focus: str, knowledge_level: str) -> float:
    """
    根据用户的三个风险偏好问题回答计算综合风险评分

    Args:
        risk_scenario: 风险场景选择 (a/b/c)
        risk_focus: 风险关注点选择 (a/b/c)
        knowledge_level: 投资知识水平 (a/b/c)

    Returns:
        float: 综合风险评分 (1-10分)
    """
    from config import RISK_SCENARIO_MAPPING, RISK_FOCUS_MAPPING, KNOWLEDGE_LEVEL_MAPPING

    # 获取各维度评分
    scenario_score = RISK_SCENARIO_MAPPING.get(risk_scenario, 5)
    focus_score = RISK_FOCUS_MAPPING.get(risk_focus, 5)
    knowledge_score = KNOWLEDGE_LEVEL_MAPPING.get(knowledge_level, 5)

    # 加权计算综合评分（风险场景权重最高，投资知识次之，风险关注点最低）
    risk_score = (scenario_score * 0.5 + focus_score * 0.2 + knowledge_score * 0.3)

    # 确保评分在1-10范围内
    risk_score = max(1.0, min(10.0, risk_score))

    return round(risk_score, 2)

def validate_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证和清洗用户输入数据

    Args:
        user_data: 原始用户数据字典

    Returns:
        Dict[str, Any]: 清洗和验证后的用户数据

    Raises:
        ValueError: 当必填字段缺失或数据格式不正确时
    """
    required_fields = [
        'age', 'annual_investment_amount', 'liquidity_demand',
        'target_return_description', 'investment_horizon',
        'risk_scenario_choice', 'risk_focus_choice', 'investment_knowledge_level'
    ]

    # 检查必填字段
    missing_fields = [field for field in required_fields if field not in user_data]
    if missing_fields:
        raise ValueError(f"缺少必填字段: {missing_fields}")

    try:
        # 清洗数字字段
        age = clean_numeric_input(user_data['age'])
        annual_investment_amount = clean_numeric_input(user_data['annual_investment_amount'])

        # 验证年龄范围
        if age < 18 or age > 100:
            raise ValueError("年龄必须在18-100岁之间")

        # 验证投资金额
        if annual_investment_amount <= 0:
            raise ValueError("年度投资金额必须大于0")

        # 计算风险评分
        risk_score = calculate_risk_score(
            user_data['risk_scenario_choice'],
            user_data['risk_focus_choice'],
            user_data['investment_knowledge_level']
        )

        return {
            'age': int(age),
            'annual_investment_amount': float(annual_investment_amount),
            'liquidity_demand': user_data['liquidity_demand'],
            'target_return_description': user_data['target_return_description'],
            'investment_horizon': user_data['investment_horizon'],
            'risk_scenario_choice': user_data['risk_scenario_choice'],
            'risk_focus_choice': user_data['risk_focus_choice'],
            'investment_knowledge_level': user_data['investment_knowledge_level'],
            'risk_score': risk_score
        }

    except (ValueError, KeyError) as e:
        raise ValueError(f"数据验证失败: {str(e)}")

def format_currency(amount: float, currency: str = "元") -> str:
    """
    格式化货币显示

    Args:
        amount: 金额
        currency: 货币单位

    Returns:
        str: 格式化后的货币字符串
    """
    if amount >= 100000000:
        return f"{amount/100000000:.2f}亿{currency}"
    elif amount >= 10000:
        return f"{amount/10000:.2f}万{currency}"
    else:
        return f"{amount:.2f}{currency}"

def format_percentage(percentage: float, decimal_places: int = 2) -> str:
    """
    格式化百分比显示

    Args:
        percentage: 百分比数值 (例如 0.15 表示 15%)
        decimal_places: 小数位数

    Returns:
        str: 格式化后的百分比字符串
    """
    return f"{percentage * 100:.{decimal_places}f}%"

# 初始化日志系统
logger = setup_logging()