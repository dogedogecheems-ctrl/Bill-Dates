"""
智能金融助手 - MPT核心算法实现
基于现代投资组合理论的均值-方差模型
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Any
from scipy.optimize import minimize
from utils import logger, format_percentage

# 虚构基金数据配置
FUNDS_NAMES = [
    '货币基金A', '债券基金B', '混合基金C', '股票基金D',
    '指数基金E', 'QDII基金F', 'REITs基金G', '商品基金H',
    '稳健理财I', '成长精选J'
]

# 各基金的预期年化收益率（小数形式）
EXPECTED_RETURNS = np.array([
    0.025,  # 货币基金A - 2.5%
    0.045,  # 债券基金B - 4.5%
    0.085,  # 混合基金C - 8.5%
    0.155,  # 股票基金D - 15.5%
    0.125,  # 指数基金E - 12.5%
    0.105,  # QDII基金F - 10.5%
    0.095,  # REITs基金G - 9.5%
    0.135,  # 商品基金H - 13.5%
    0.035,  # 稳健理财I - 3.5%
    0.185   # 成长精选J - 18.5%
])

# 基金之间的协方差矩阵（模拟数据）
# 这个矩阵反映了不同基金收益之间的相关性
COVARIANCE_MATRIX = np.array([
    # A      B      C      D      E      F      G      H      I      J
    [0.0008, 0.0003, 0.0001, 0.0000, 0.0001, 0.0001, 0.0001, 0.0000, 0.0006, 0.0000],  # A
    [0.0003, 0.0015, 0.0005, 0.0001, 0.0003, 0.0002, 0.0002, 0.0001, 0.0008, 0.0001],  # B
    [0.0001, 0.0005, 0.0040, 0.0025, 0.0030, 0.0020, 0.0018, 0.0022, 0.0003, 0.0028],  # C
    [0.0000, 0.0001, 0.0025, 0.0225, 0.0150, 0.0100, 0.0080, 0.0120, 0.0001, 0.0180],  # D
    [0.0001, 0.0003, 0.0030, 0.0150, 0.0144, 0.0085, 0.0075, 0.0095, 0.0002, 0.0120],  # E
    [0.0001, 0.0002, 0.0020, 0.0100, 0.0085, 0.0090, 0.0065, 0.0078, 0.0001, 0.0085],  # F
    [0.0001, 0.0002, 0.0018, 0.0080, 0.0075, 0.0065, 0.0064, 0.0055, 0.0002, 0.0070],  # G
    [0.0000, 0.0001, 0.0022, 0.0120, 0.0095, 0.0078, 0.0055, 0.0169, 0.0001, 0.0105],  # H
    [0.0006, 0.0008, 0.0003, 0.0001, 0.0002, 0.0001, 0.0002, 0.0001, 0.0012, 0.0001],  # I
    [0.0000, 0.0001, 0.0028, 0.0180, 0.0120, 0.0085, 0.0070, 0.0105, 0.0001, 0.0256]   # J
])

class MPTSolver:
    """现代投资组合理论求解器"""

    def __init__(self):
        self.funds_names = FUNDS_NAMES
        self.expected_returns = EXPECTED_RETURNS
        self.covariance_matrix = COVARIANCE_MATRIX
        self.num_funds = len(FUNDS_NAMES)

        logger.info(f"MPT求解器初始化完成，包含{self.num_funds}个基金")
        logger.info(f"预期收益率范围: {format_percentage(np.min(self.expected_returns))} - {format_percentage(np.max(self.expected_returns))}")

    def calculate_portfolio_metrics(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        计算投资组合的预期收益率、波动率和最大回撤估算

        Args:
            weights: 投资组合权重数组

        Returns:
            Tuple[float, float, float]: (预期收益率, 波动率, 最大回撤估算)
        """
        # 计算预期收益率
        expected_return = np.dot(weights, self.expected_returns)

        # 计算波动率（标准差）
        portfolio_variance = np.dot(weights.T, np.dot(self.covariance_matrix, weights))
        volatility = np.sqrt(portfolio_variance)

        # 估算最大回撤（使用经验公式：最大回撤 ≈ 2-3倍波动率）
        # 这是一个简化的估算，实际最大回撤需要历史数据支持
        max_drawdown = volatility * 2.5  # 经验倍数

        return float(expected_return), float(volatility), float(max_drawdown)

    def optimize_portfolio(self, target_risk: float = None, target_return: float = None) -> Dict[str, Any]:
        """
        优化投资组合

        Args:
            target_risk: 目标风险水平（可选）
            target_return: 目标收益率（可选）

        Returns:
            Dict: 包含优化结果的字典
        """
        # 约束条件：权重和为1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

        # 边界条件：每个权重在0到1之间
        bounds = tuple([(0, 1) for _ in range(self.num_funds)])

        # 初始猜测：等权重
        initial_weights = np.array([1.0 / self.num_funds] * self.num_funds)

        if target_risk is not None:
            # 给定风险水平，最大化收益率
            def objective(weights):
                return -np.dot(weights, self.expected_returns)  # 最大化收益率

            # 添加风险约束
            risk_constraint = {
                'type': 'eq',
                'fun': lambda x: self.calculate_portfolio_metrics(x)[1] - target_risk
            }
            constraints_list = [constraints, risk_constraint]

        elif target_return is not None:
            # 给定收益率，最小化风险
            def objective(weights):
                portfolio_variance = np.dot(weights.T, np.dot(self.covariance_matrix, weights))
                return portfolio_variance  # 最小化方差

            # 添加收益约束
            return_constraint = {
                'type': 'eq',
                'fun': lambda x: np.dot(x, self.expected_returns) - target_return
            }
            constraints_list = [constraints, return_constraint]
        else:
            # 默认：最小化风险
            def objective(weights):
                portfolio_variance = np.dot(weights.T, np.dot(self.covariance_matrix, weights))
                return portfolio_variance

            constraints_list = [constraints]

        # 执行优化
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list,
            options={'ftol': 1e-9, 'disp': False}
        )

        if not result.success:
            logger.warning(f"投资组合优化未完全收敛: {result.message}")

        # 提取最优权重
        optimal_weights = result.x
        expected_return, volatility, max_drawdown = self.calculate_portfolio_metrics(optimal_weights)

        return {
            'weights': optimal_weights,
            'expected_return': expected_return,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'success': result.success,
            'message': result.message
        }

    def calculate_efficient_frontier(self, num_portfolios: int = 100) -> List[Dict[str, Any]]:
        """
        计算有效边界

        Args:
            num_portfolios: 生成投资组合的数量

        Returns:
            List[Dict]: 有效边界上的投资组合列表
        """
        logger.info(f"开始计算有效边界，生成{num_portfolios}个投资组合")

        # 计算最小风险投资组合
        min_variance_result = self.optimize_portfolio()
        min_volatility = min_variance_result['volatility']

        # 计算最大收益率投资组合（单一最高收益基金）
        max_return_idx = np.argmax(self.expected_returns)
        max_return = self.expected_returns[max_return_idx]
        max_return_weights = np.zeros(self.num_funds)
        max_return_weights[max_return_idx] = 1.0
        max_return_volatility = np.sqrt(self.covariance_matrix[max_return_idx, max_return_idx])

        # 在最小波动率和最大收益率之间生成目标收益率序列
        target_returns = np.linspace(min_variance_result['expected_return'], max_return * 0.9, num_portfolios)

        efficient_portfolios = []

        for i, target_return in enumerate(target_returns):
            try:
                result = self.optimize_portfolio(target_return=target_return)
                if result['success']:
                    efficient_portfolios.append({
                        'target_return': target_return,
                        'weights': result['weights'],
                        'expected_return': result['expected_return'],
                        'volatility': result['volatility'],
                        'max_drawdown': result['max_drawdown']
                    })

                if i % 20 == 0:
                    logger.info(f"有效边界计算进度: {i+1}/{num_portfolios}")

            except Exception as e:
                logger.warning(f"计算目标收益率{format_percentage(target_return)}的投资组合时出错: {str(e)}")
                continue

        logger.info(f"有效边界计算完成，成功生成{len(efficient_portfolios)}个有效投资组合")
        return efficient_portfolios

    def map_risk_to_portfolio(self, risk_score: float, efficient_frontier: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        将用户风险评分映射到有效边界上的最优投资组合

        Args:
            risk_score: 用户风险评分 (1-10分)
            efficient_frontier: 有效边界投资组合列表

        Returns:
            Dict: 最优投资组合信息
        """
        logger.info(f"开始为风险评分{risk_score}分映射最优投资组合")

        if not efficient_frontier:
            # 如果有效边界为空，返回等权重投资组合
            equal_weights = np.array([1.0 / self.num_funds] * self.num_funds)
            expected_return, volatility, max_drawdown = self.calculate_portfolio_metrics(equal_weights)
            logger.warning("有效边界为空，返回等权重投资组合")
            return {
                'weights': equal_weights,
                'expected_return': expected_return,
                'volatility': volatility,
                'max_drawdown': max_drawdown,
                'risk_score_used': risk_score
            }

        # 根据风险评分选择投资组合
        # 风险评分1-10分映射到有效边界上的不同风险水平
        # 低风险评分（1-3）选择低波动率组合
        # 中等风险评分（4-7）选择中等风险组合
        # 高风险评分（8-10）选择高收益组合

        # 将风险评分归一化到0-1范围
        normalized_risk = (risk_score - 1) / 9

        # 选择第百分位的投资组合
        portfolio_index = int(normalized_risk * (len(efficient_frontier) - 1))
        selected_portfolio = efficient_frontier[portfolio_index]

        # 格式化权重，确保小的权重被设为0
        weights = selected_portfolio['weights']
        weights[weights < 0.001] = 0  # 将小于0.1%的权重设为0
        weights = weights / np.sum(weights)  # 重新归一化

        logger.info(f"为风险评分{risk_score}分选择了第{portfolio_index+1}个投资组合")
        logger.info(f"投资组合预期收益率: {format_percentage(selected_portfolio['expected_return'])}")
        logger.info(f"投资组合波动率: {format_percentage(selected_portfolio['volatility'])}")

        return {
            'weights': weights,
            'expected_return': selected_portfolio['expected_return'],
            'volatility': selected_portfolio['volatility'],
            'max_drawdown': selected_portfolio['max_drawdown'],
            'risk_score_used': risk_score
        }

    def format_portfolio_result(self, portfolio_data: Dict[str, Any], investment_amount: float) -> Dict[str, Any]:
        """
        格式化投资组合结果，包含基金名称、权重、投资金额等

        Args:
            portfolio_data: 投资组合数据
            investment_amount: 投资金额

        Returns:
            Dict: 格式化后的投资组合结果
        """
        weights = portfolio_data['weights']

        # 创建投资组合列表
        portfolio_list = []
        for i, (fund_name, weight) in enumerate(zip(self.funds_names, weights)):
            if weight > 0.001:  # 只包含权重大于0.1%的基金
                amount = weight * investment_amount
                portfolio_list.append({
                    'fund_name': fund_name,
                    'weight': weight,
                    'weight_percentage': weight * 100,
                    'investment_amount': amount
                })

        # 按权重排序
        portfolio_list.sort(key=lambda x: x['weight'], reverse=True)

        return {
            'plan_list': portfolio_list,
            'expected_return': portfolio_data['expected_return'],
            'expected_volatility': portfolio_data['volatility'],
            'max_drawdown_estimate': portfolio_data['max_drawdown'],
            'risk_score_used': portfolio_data['risk_score_used']
        }