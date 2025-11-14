from datetime import datetime, date, timedelta
from sqlalchemy import func, extract, and_
from models import db, Bill, SavingsGoal, FinancialProfile, RiskProfile, FinancialProduct, AIAdvice
from config import Config
from openai import OpenAI
import json

class FinancialService:
    
    @staticmethod
    def get_current_month_range():
        """获取当前月份的起始和结束日期"""
        today = date.today()
        start_date = today.replace(day=1)
        
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
        return start_date, end_date
    
    @staticmethod
    def get_dashboard_summary(user_id='default_user'):
        """获取仪表盘摘要数据"""
        start_date, end_date = FinancialService.get_current_month_range()
        
        # 计算总收入
        total_income = db.session.query(func.sum(Bill.amount)).filter(
            Bill.type == 'income',
            Bill.date >= start_date,
            Bill.date <= end_date
        ).scalar() or 0
        
        # 计算总支出
        total_expense = db.session.query(func.sum(Bill.amount)).filter(
            Bill.type == 'expense',
            Bill.date >= start_date,
            Bill.date <= end_date
        ).scalar() or 0
        balance = total_income - total_expense
        
        # 计算财务健康分数
        health_score = FinancialService.calculate_health_score(total_income, total_expense, balance)
        
        return {
            'totalIncome': total_income,
            'totalExpense': total_expense,
            'balance': balance,
            'healthScore': health_score
        }
    
    @staticmethod
    def calculate_health_score(total_income, total_expense, balance):
        """计算财务健康分数"""
        if total_income == 0:
            return 0
        
        score = 50
        
        # 储蓄率评分
        savings_rate = (balance / total_income) * 100 if total_income > 0 else 0
        if savings_rate > 20:
            score += 30
        elif savings_rate > 10:
            score += 20
        elif savings_rate > 5:
            score += 10
        
        # 支出比例评分
        expense_ratio = total_expense / total_income if total_income > 0 else 0
        if expense_ratio > 0.9:
            score -= 20
        elif expense_ratio > 0.8:
            score -= 10
        print(f"Calculated health score: {score}")
        return max(0, min(100, score))
    
    @staticmethod
    def get_analysis_trends(period='month', user_id='default_user'):
        """获取分析趋势数据"""
        today = date.today()
        
        if period == 'year':
            start_date = today.replace(day=1, month=1)
            end_date = today.replace(day=31, month=12)
            group_by = extract('month', Bill.date)
            dates = [f'{i}月' for i in range(1, 13)]
        else:  # 默认 'month'
            start_date = today.replace(day=1)
            # 获取当月最后一天作为结束日期
            next_month = today.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
            group_by = extract('day', Bill.date)
            # 生成整个月的日期，不只是到今天
            days_in_month = end_date.day
            dates = [f'{i}日' for i in range(1, days_in_month + 1)]
        
        # 收入查询
        income_q = db.session.query(
            group_by.label('period'), func.sum(Bill.amount).label('total')
        ).filter(
            Bill.type == 'income',
            Bill.date >= start_date,
            Bill.date <= end_date
        ).group_by('period').all()
        
        # 支出查询
        expense_q = db.session.query(
            group_by.label('period'), func.sum(Bill.amount).label('total')
        ).filter(
            Bill.type == 'expense',
            Bill.date >= start_date,
            Bill.date <= end_date
        ).group_by('period').all()
        
        income_map = {int(item.period): float(item.total) for item in income_q}
        expense_map = {int(item.period): float(item.total) for item in expense_q}
        
        income_data = [income_map.get(i+1, 0.0) for i in range(len(dates))]
        expense_data = [expense_map.get(i+1, 0.0) for i in range(len(dates))]
        
        return {
            'dates': dates,
            'incomeData': income_data,
            'expenseData': expense_data
        }
    
    @staticmethod
    def get_expense_pie(user_id='default_user'):
        """获取支出饼图数据"""
        start_date, end_date = FinancialService.get_current_month_range()
        
        expense_data = db.session.query(
            Bill.category, func.sum(Bill.amount).label('total')
        ).filter(
            Bill.type == 'expense',
            Bill.date >= start_date,
            Bill.date <= end_date
        ).group_by(Bill.category).all()
        
        category_names = Config.CATEGORIES['expense']
        
        data = [
            {
                'value': item.total, 
                'name': category_names.get(item.category, item.category)
            } for item in expense_data
        ]
        
        return data
    
    @staticmethod
    def get_savings_stats(user_id='default_user'):
        """获取储蓄统计"""
        goals = SavingsGoal.query.all()
        total_savings = sum(g.currentAmount for g in goals)
        active_goals = sum(1 for g in goals if g.currentAmount < g.targetAmount)
        completed_goals = sum(1 for g in goals if g.currentAmount >= g.targetAmount)
        
        # 计算本月储蓄（基于最近30天的结余）
        thirty_days_ago = date.today() - timedelta(days=30)
        monthly_income = db.session.query(func.sum(Bill.amount)).filter(
            Bill.type == 'income',
            Bill.date >= thirty_days_ago
        ).scalar() or 0
        
        monthly_expense = db.session.query(func.sum(Bill.amount)).filter(
            Bill.type == 'expense',
            Bill.date >= thirty_days_ago
        ).scalar() or 0
        
        monthly_savings = monthly_income - monthly_expense
        
        return {
            'totalSavings': total_savings,
            'activeGoals': active_goals,
            'completedGoals': completed_goals,
            'monthlySavings': monthly_savings
        }

class AIAdviceService:
    
    def __init__(self):
        """初始化 OpenAI 客户端"""
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=getattr(Config, 'OPENAI_BASE_URL', None)  # 可选的自定义 base_url
        )
        
    def generate_financial_advice_stream(self, user_id='default_user'):
        """生成财务建议（流式传输）"""
        try:
            # 获取用户数据
            dashboard_data = FinancialService.get_dashboard_summary(user_id)
            profile = FinancialProfile.query.filter_by(userId=user_id).first()
            risk_profile = RiskProfile.query.filter_by(userId=user_id).first()
            
            # 构建提示
            prompt = f"""
            基于以下用户信息，请提供个性化的财务建议：
            
            当前财务状况：
            - 本月收入：¥{dashboard_data['totalIncome']:.2f}
            - 本月支出：¥{dashboard_data['totalExpense']:.2f}
            - 本月结余：¥{dashboard_data['balance']:.2f}
            - 财务健康分数：{dashboard_data['healthScore']}分
            
            用户画像：
            - 财务类型：{profile.type if profile else '未评估'}
            - 风险等级：{risk_profile.riskLevel if risk_profile else '未评估'}
            
            请提供：
            1. 财务管理建议
            2. 储蓄建议
            3. 投资建议
            4. 需要改进的地方
            
            请以清晰、实用的方式回答，适合普通用户理解。
            """
            
            if not Config.OPENAI_API_KEY:
                yield "AI建议功能暂时不可用，请配置API密钥。"
                return
            
            # 收集完整的响应内容用于保存
            full_content = []
            
            # 使用流式传输调用 OpenAI API
            stream = self.client.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的理财顾问，请为用户提供实用、安全的财务建议。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                stream=True  # 启用流式传输
            )
            
            # 处理流式响应
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_content.append(content)
                    yield content
            
            # 保存完整的建议到数据库
            complete_advice = ''.join(full_content)
            self._save_financial_advice(user_id, complete_advice, dashboard_data, profile, risk_profile)
            
        except Exception as e:
            yield f"生成建议时出现错误：{str(e)}"
    
    def generate_investment_advice_stream(self, user_id='default_user'):
        """生成投资建议（流式传输）"""
        try:
            # 获取用户风险画像
            risk_profile = RiskProfile.query.filter_by(userId=user_id).first()
            dashboard_data = FinancialService.get_dashboard_summary(user_id)
            
            if not risk_profile:
                yield "请先完成风险评估问卷，以便为您提供合适的投资建议。"
                return
            
            # 根据风险等级推荐产品
            if risk_profile.riskLevel == '保守型':
                recommended_products = ['deposit', 'bond', '货币基金']
                investment_style = '保守稳健'
            elif risk_profile.riskLevel == '平衡型':
                recommended_products = ['fund', 'bond', '部分股票基金']
                investment_style = '平衡配置'
            else:
                recommended_products = ['fund', 'stock', '混合投资']
                investment_style = '积极进取'
            
            prompt = f"""
            为用户生成投资建议：
            
            用户风险等级：{risk_profile.riskLevel}
            投资风格：{investment_style}
            推荐产品类型：{', '.join(recommended_products)}
            
            当前财务状况：
            - 月收入：¥{dashboard_data['totalIncome']:.2f}
            - 月结余：¥{dashboard_data['balance']:.2f}
            
            请提供：
            1. 资产配置建议
            2. 具体产品推荐
            3. 投资时机建议
            4. 风险控制措施
            5. 投资金额建议
            
            投资建议应该具体、实用，适合{investment_style}的投资者。
            """
            
            if not Config.OPENAI_API_KEY:
                yield "AI投资建议功能暂时不可用。"
                return
            
            # 收集完整的响应内容用于保存
            full_content = []
            
            # 使用流式传输调用 OpenAI API
            stream = self.client.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的投资顾问，请根据用户的风险承受能力提供合适的投资建议。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.6,
                stream=True  # 启用流式传输
            )
            
            # 处理流式响应
            for chunk in stream:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_content.append(content)
                    yield content
            
            # 保存完整的建议到数据库
            complete_advice = ''.join(full_content)
            self._save_investment_advice(user_id, complete_advice, risk_profile, dashboard_data, recommended_products)
            
        except Exception as e:
            yield f"生成投资建议时出现错误：{str(e)}"
    
    def _save_financial_advice(self, user_id, advice, dashboard_data, profile, risk_profile):
        """保存财务建议到数据库"""
        try:
            ai_advice = AIAdvice(
                userId=user_id,
                adviceType='financial_planning',
                content=advice,
                context={
                    'dashboard_data': dashboard_data,
                    'profile_type': profile.type if profile else None,
                    'risk_level': risk_profile.riskLevel if risk_profile else None
                }
            )
            db.session.add(ai_advice)
            db.session.commit()
        except Exception as e:
            print(f"保存财务建议失败: {str(e)}")
    
    def _save_investment_advice(self, user_id, advice, risk_profile, dashboard_data, recommended_products):
        """保存投资建议到数据库"""
        try:
            ai_advice = AIAdvice(
                userId=user_id,
                adviceType='investment',
                content=advice,
                context={
                    'risk_level': risk_profile.riskLevel,
                    'recommended_products': recommended_products,
                    'dashboard_data': dashboard_data
                }
            )
            db.session.add(ai_advice)
            db.session.commit()
        except Exception as e:
            print(f"保存投资建议失败: {str(e)}")
    
    def generate_financial_advice(self, user_id='default_user'):
        """生成财务建议"""
        try:
            # 获取用户数据
            dashboard_data = FinancialService.get_dashboard_summary(user_id)
            profile = FinancialProfile.query.filter_by(userId=user_id).first()
            risk_profile = RiskProfile.query.filter_by(userId=user_id).first()
            
            # 构建提示
            prompt = f"""
            基于以下用户信息，请提供个性化的财务建议：
            
            当前财务状况：
            - 本月收入：¥{dashboard_data['totalIncome']:.2f}
            - 本月支出：¥{dashboard_data['totalExpense']:.2f}
            - 本月结余：¥{dashboard_data['balance']:.2f}
            - 财务健康分数：{dashboard_data['healthScore']}分
            
            用户画像：
            - 财务类型：{profile.type if profile else '未评估'}
            - 风险等级：{risk_profile.riskLevel if risk_profile else '未评估'}
            
            请提供：
            1. 财务管理建议
            2. 储蓄建议
            3. 投资建议
            4. 需要改进的地方
            
            请以清晰、实用的方式回答，适合普通用户理解。
            """
            
            if not Config.OPENAI_API_KEY:
                return "AI建议功能暂时不可用，请配置API密钥。"
            service = AIAdviceService()
            response = self.client.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": """你是一位专业的个人金融顾问，擅长基于现代投资组合理论为用户提供财务健康建议。

重要格式要求：
1. 严格禁止使用任何Markdown格式标记，包括但不限于：
   - 标题标记：#, ##, ### 等
   - 粗体标记：**, __
   - 斜体标记：*, _
   - 行内代码标记：`
   - 列表标记：-, *, + 等
2. 所有标题和段落仅使用纯文本和换行符分隔
3. 如果需要分段，请直接使用换行符
4. 使用简洁、清晰的纯文本格式输出"""},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            advice = response.choices[0].message.content
            
            # 保存建议到数据库
            ai_advice = AIAdvice(
                userId=user_id,
                adviceType='financial_planning',
                content=advice,
                context={
                    'dashboard_data': dashboard_data,
                    'profile_type': profile.type if profile else None,
                    'risk_level': risk_profile.riskLevel if risk_profile else None
                }
            )
            db.session.add(ai_advice)
            db.session.commit()
            
            return advice
            
        except Exception as e:
            return f"生成建议时出现错误：{str(e)}"
    
    def generate_investment_advice(self, user_id='default_user'):
        """生成投资建议"""
        try:
            # 获取用户风险画像
            risk_profile = RiskProfile.query.filter_by(userId=user_id).first()
            dashboard_data = FinancialService.get_dashboard_summary(user_id)
            
            if not risk_profile:
                return "请先完成风险评估问卷，以便为您提供合适的投资建议。"
            
            # 根据风险等级推荐产品
            if risk_profile.riskLevel == '保守型':
                recommended_products = ['deposit', 'bond', '货币基金']
                investment_style = '保守稳健'
            elif risk_profile.riskLevel == '平衡型':
                recommended_products = ['fund', 'bond', '部分股票基金']
                investment_style = '平衡配置'
            else:
                recommended_products = ['fund', 'stock', '混合投资']
                investment_style = '积极进取'
            
            prompt = f"""
            为用户生成投资建议：
            
            用户风险等级：{risk_profile.riskLevel}
            投资风格：{investment_style}
            推荐产品类型：{', '.join(recommended_products)}
            
            当前财务状况：
            - 月收入：¥{dashboard_data['totalIncome']:.2f}
            - 月结余：¥{dashboard_data['balance']:.2f}
            
            请提供：
            1. 资产配置建议
            2. 具体产品推荐
            3. 投资时机建议
            4. 风险控制措施
            5. 投资金额建议
            
            投资建议应该具体、实用，适合{investment_style}的投资者。
            """
            
            if not Config.OPENAI_API_KEY:
                return "AI投资建议功能暂时不可用。"
            
            response = self.client.chat.completions.create(
                model=Config.AI_MODEL,
                messages=[
                    {"role": "system", "content": """你是一位专业的金融投资顾问，擅长基于现代投资组合理论为用户提供投资建议。请用专业、易懂的语言解释投资组合配置的原理。

重要格式要求：
1. 严格禁止使用任何Markdown格式标记，包括但不限于：
   - 标题标记：#, ##, ### 等
   - 粗体标记：**, __
   - 斜体标记：*, _
   - 行内代码标记：`
   - 列表标记：-, *, + 等
2. 所有标题和段落仅使用纯文本和换行符分隔
3. 如果需要分段，请直接使用换行符
4. 使用简洁、清晰的纯文本格式输出"""},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.6
            )
            
            advice = response.choices[0].message.content
            
            # 保存建议
            ai_advice = AIAdvice(
                userId=user_id,
                adviceType='investment',
                content=advice,
                context={
                    'risk_level': risk_profile.riskLevel,
                    'recommended_products': recommended_products,
                    'dashboard_data': dashboard_data
                }
            )
            db.session.add(ai_advice)
            db.session.commit()
            
            return advice
            
        except Exception as e:
            return f"生成投资建议时出现错误：{str(e)}"

    @staticmethod
    def generate_financial_advice_static(user_id='default_user'):
        """静态方法版本（保持向后兼容）"""
        service = AIAdviceService()
        return service.generate_financial_advice(user_id)
    
    @staticmethod
    def generate_investment_advice_static(user_id='default_user'):
        """静态方法版本（保持向后兼容）"""
        service = AIAdviceService()
        return service.generate_investment_advice(user_id)

class ProductService:
    
    @staticmethod
    def get_recommended_products(user_id='default_user', limit=10):
        """根据用户画像推荐理财产品"""
        try:
            risk_profile = RiskProfile.query.filter_by(userId=user_id).first()
            
            if not risk_profile:
                # 如果没有风险画像，返回低风险产品
                products = FinancialProduct.query.filter_by(
                    riskLevel='low',
                    isActive=True
                ).limit(limit).all()
            else:
                # 根据风险等级推荐产品
                if risk_profile.riskLevel == '保守型':
                    risk_levels = ['low']
                elif risk_profile.riskLevel == '平衡型':
                    risk_levels = ['low', 'medium']
                else:  # 积极型
                    risk_levels = ['low', 'medium', 'high']
                
                products = FinancialProduct.query.filter(
                    FinancialProduct.riskLevel.in_(risk_levels),
                    FinancialProduct.isActive == True
                ).order_by(FinancialProduct.expectedReturn.desc()).limit(limit).all()
            
            return [product.to_dict() for product in products]
            
        except Exception as e:
            return []
    
    @staticmethod
    def search_products(query, product_type=None, risk_level=None, limit=20):
        """搜索理财产品"""
        try:
            q = FinancialProduct.query.filter(
                FinancialProduct.isActive == True,
                FinancialProduct.name.ilike(f'%{query}%')
            )
            
            if product_type:
                q = q.filter(FinancialProduct.productType == product_type)
            
            if risk_level:
                q = q.filter(FinancialProduct.riskLevel == risk_level)
            
            products = q.order_by(FinancialProduct.expectedReturn.desc()).limit(limit).all()
            
            return [product.to_dict() for product in products]
            
        except Exception as e:
            return []