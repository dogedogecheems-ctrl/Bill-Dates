"""
智能金融助手 - Qwen大模型服务
封装Qwen API调用逻辑，生成投资组合专业解释
"""

import requests
import json
import logging
import re
from typing import Dict, Any, Optional
from config import QWEN_API_KEY, QWEN_API_URL, QWEN_MODEL
from utils import logger, format_percentage, format_currency

class QwenService:
    """Qwen大模型服务类"""

    def __init__(self):
        self.api_key = QWEN_API_KEY
        self.api_url = QWEN_API_URL
        self.model = QWEN_MODEL

        logger.info(f"Qwen服务初始化完成，使用模型: {self.model}")

    def clean_qwen_output(self, text: str) -> str:
        """
        清理Qwen输出的文本，移除Markdown格式标记

        Args:
            text: 原始文本

        Returns:
            str: 清理后的纯文本
        """
        if not text:
            return text

        # 移除 Markdown 标题标记 (##, ###, # 等)
        text = re.sub(r'^\s*#+\s*', '', text, flags=re.MULTILINE)

        # 移除 Markdown 粗体标记 (**粗体**)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)

        # 移除 Markdown 下划线粗体 (__粗体__)
        text = re.sub(r'__(.*?)__', r'\1', text)

        # 移除 Markdown 斜体标记 (*斜体*)
        text = re.sub(r'\*(.*?)\*', r'\1', text)

        # 移除 Markdown 行内代码标记 (`代码`)
        text = re.sub(r'`(.*?)`', r'\1', text)

        # 移除多余的空行
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        # 清理首尾空白字符
        text = text.strip()

        return text

    def _make_api_request(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        发起Qwen API请求

        Args:
            prompt: 提示词
            max_tokens: 最大生成token数

        Returns:
            Optional[str]: API响应文本，失败时返回None
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """你是一位专业的金融投资顾问，擅长基于现代投资组合理论为用户提供投资建议。请用专业、易懂的语言解释投资组合配置的原理。

重要格式要求：
1. 严格禁止使用任何Markdown格式标记，包括但不限于：
   - 标题标记：#, ##, ### 等
   - 粗体标记：**, __
   - 斜体标记：*, _
   - 行内代码标记：`
   - 列表标记：-, *, + 等
2. 所有标题和段落仅使用纯文本和换行符分隔
3. 如果需要分段，请直接使用换行符
4. 使用简洁、清晰的纯文本格式输出"""
                },
                {
                    "role": "user",
                    "content": prompt + "\n\n请严格遵循上述格式要求，输出纯文本内容，禁止使用任何Markdown标记。"
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.8
        }

        try:
            logger.info(f"正在调用Qwen API，模型: {self.model}")
            logger.info(f"请求输入长度: {len(prompt)} 字符")

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                logger.info(f"Qwen API调用成功，生成文本长度: {len(generated_text)} 字符")
                return generated_text
            else:
                logger.error(f"Qwen API调用失败，状态码: {response.status_code}")
                logger.error(f"错误响应: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error("Qwen API请求超时")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Qwen API请求异常: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Qwen API调用发生未知错误: {str(e)}")
            return None

    def generate_explanation(self, portfolio_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """
        生成投资组合的专业解释说明

        Args:
            portfolio_data: 投资组合数据
            user_profile: 用户画像数据

        Returns:
            str: 生成的专业解释文本
        """
        logger.info("开始生成投资组合专业解释")

        # 提取关键信息
        expected_return = portfolio_data.get('expected_return', 0)
        volatility = portfolio_data.get('expected_volatility', 0)
        max_drawdown = portfolio_data.get('max_drawdown_estimate', 0)
        risk_score = user_profile.get('risk_score', 5)
        age = user_profile.get('age', 30)
        investment_amount = user_profile.get('annual_investment_amount', 0)
        liquidity_demand = user_profile.get('liquidity_demand', '未提供')
        investment_horizon = user_profile.get('investment_horizon', '未提供')

        # 获取主要配置的基金信息
        plan_list = portfolio_data.get('plan_list', [])
        top_funds = plan_list[:5]  # 取前5个主要配置的基金

        # 构建基金配置描述
        fund_description = ""
        for i, fund in enumerate(top_funds, 1):
            fund_name = fund.get('fund_name', '')
            weight = fund.get('weight_percentage', 0)
            amount = fund.get('investment_amount', 0)
            fund_description += f"{i}. {fund_name}：{weight:.1f}%，约{format_currency(amount)}\n"

        # 风险特征描述
        risk_level = "保守型" if risk_score <= 3 else ("稳健型" if risk_score <= 7 else "积极型")

        # 构建提示词
        prompt = f"""请根据以下用户画像和投资组合数据，生成一份专业的投资配置说明。

**重要人称指令：在生成的全部内容中，请始终使用“您”、“您的”等第二人称尊称来指代用户，禁止使用“用户”、“投资者”等第三人称名词。**

用户基本情况：
年龄：{age}岁
年度投资金额：{format_currency(investment_amount)}
风险偏好评分：{risk_score}/10分 ({risk_level})
流动性需求：{liquidity_demand}
投资期限：{investment_horizon}

投资组合配置：
{fund_description}

投资组合关键指标：
预期年化收益率：{format_percentage(expected_return)}
预期年化波动率：{format_percentage(volatility)}
预期最大回撤：{format_percentage(max_drawdown)}

请按以下纯文本格式生成解释说明，不要使用任何Markdown标记：

投资组合概述
简要总结这个投资组合的核心特征和适合的人群。

理论基础
明确说明推荐是基于现代投资组合理论(MPT)的均值-方差模型。
解释有效边界的概念和如何找到最优配置点。

个性化匹配分析
根据您的风险偏好评分({risk_score}分)说明配置选择。
结合您的年龄、投资期限等因素解释方案的合理性。

配置原理详解
详细解释主要配置基金的作用：
- 低风险基金（货币基金、债券基金）如何提供稳定性。
- 中等风险基金（混合基金、指数基金）如何平衡收益风险。
- 高风险基金（股票基金、成长基金）如何争取高收益。
解释各基金之间的相关性分散风险的作用。

风险提示与预期
客观说明预期收益率、波动率和最大回撤的含义。
提醒市场风险和实际收益可能偏离您的预期的可能性。

投资建议
给出您后续管理和调整的建议。

请用专业但易懂的语言，让普通投资者能够理解。避免过于技术化的术语，必要时进行通俗解释。
"""

        # 尝试调用API生成解释
        generated_explanation = self._make_api_request(prompt)

        if generated_explanation:
            logger.info("成功使用Qwen生成投资组合解释")
            # 清理Markdown标记，确保纯文本输出
            cleaned_explanation = self.clean_qwen_output(generated_explanation)
            logger.info(f"Qwen输出清理完成，原始长度: {len(generated_explanation)}，清理后长度: {len(cleaned_explanation)}")
            return cleaned_explanation
        else:
            logger.warning("Qwen API调用失败，使用备用解释模板")
            return self._generate_fallback_explanation(portfolio_data, user_profile)

    def _generate_fallback_explanation(self, portfolio_data: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """
        生成备用解释（当API调用失败时使用）

        Args:
            portfolio_data: 投资组合数据
            user_profile: 用户画像数据

        Returns:
            str: 备用解释文本
        """
        expected_return = portfolio_data.get('expected_return', 0)
        volatility = portfolio_data.get('expected_volatility', 0)
        risk_score = user_profile.get('risk_score', 5)
        age = user_profile.get('age', 30)

        risk_level = "保守型" if risk_score <= 3 else ("稳健型" if risk_score <= 7 else "积极型")

        explanation = f"""投资组合配置说明

理论基础
您的投资组合基于现代投资组合理论(MPT)的均值-方差模型构建。该理论通过数学优化方法，在给定风险水平下最大化收益，或在给定收益目标下最小化风险，从而找到投资组合的有效边界。

个性化配置原理
根据您{risk_score}分的风险偏好评分和{age}岁的年龄特征，我们为您定制了{risk_level}投资组合：

核心配置逻辑：
- 通过量化模型分析了{len(portfolio_data.get('plan_list', []))}类基金的历史收益特征和相关性
- 在有效边界上选择了与您风险承受能力最匹配的最优点
- 采用分散化投资降低单一资产风险

投资组合特征：
- 预期年化收益率：{format_percentage(expected_return)}
- 预期年化波动率：{format_percentage(volatility)}
- 该配置在风险可控范围内追求合理收益

风险提示
投资有风险，入市需谨慎。过往业绩不代表未来表现，实际收益可能偏离预期。建议您定期关注投资组合表现，根据市场变化和个人情况进行适当调整。

重要声明
本投资建议仅供参考，不构成投资要约。请您根据自身情况谨慎决策，必要时咨询专业投资顾问。"""

        return explanation

# 创建全局Qwen服务实例
qwen_service = QwenService()