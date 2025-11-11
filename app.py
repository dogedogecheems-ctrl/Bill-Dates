from flask import Flask, jsonify, request, send_from_directory, g, stream_with_context, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, Bill, SavingsGoal, FinancialProfile, RiskProfile, Questionnaire, FinancialProduct, UserPreference, AIAdvice
from services import FinancialService, AIAdviceService, ProductService
from config import Config
from datetime import datetime, date
import json
import time

# --- App Initialization ---
app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(Config)
service = AIAdviceService()
db.init_app(app)
CORS(app)

# --- Database Creation ---
def init_db(app):
    """初始化数据库并创建默认数据"""
    with app.app_context():
        db.create_all()
        
        # 检查是否已有默认用户数据
        user_id = 'default_user'
        
        # 创建默认财务画像
        if not FinancialProfile.query.filter_by(userId=user_id).first():
            profile = FinancialProfile(userId=user_id)
            db.session.add(profile)
        
        # 创建默认风险画像
        if not RiskProfile.query.filter_by(userId=user_id).first():
            risk_profile = RiskProfile(userId=user_id)
            db.session.add(risk_profile)
        
        # 创建默认问卷
        if not Questionnaire.query.first():
            for key, questionnaire_data in Config.QUESTIONNAIRES.items():
                questionnaire = Questionnaire(
                    name=questionnaire_data['name'],
                    description=questionnaire_data['description'],
                    questions=questionnaire_data['questions'],
                    type=key
                )
                db.session.add(questionnaire)
        
        # 创建默认理财产品
        if not FinancialProduct.query.first():
            for product_data in Config.DEFAULT_PRODUCTS:
                product = FinancialProduct(**product_data)
                db.session.add(product)
        
        db.session.commit()

# --- Helper Functions ---
def get_user_id():
    """获取当前用户ID（实际项目中应该从认证系统获取）"""
    return 'default_user'

# --- API Routes ---

# 账单相关API
@app.route('/api/bills', methods=['GET'])
def get_bills():
    """获取账单列表"""
    try:
        query = Bill.query
        
        # 搜索
        search_term = request.args.get('q')
        if search_term:
            query = query.filter(
                Bill.note.ilike(f'%{search_term}%') | 
                Bill.category.ilike(f'%{search_term}%')
            )
        
        # 类型过滤
        bill_type = request.args.get('type')
        if bill_type and bill_type != 'all':
            query = query.filter_by(type=bill_type)
        
        # 日期范围过滤
        date_gte = request.args.get('date_gte')
        if date_gte:
            query = query.filter(Bill.date >= datetime.strptime(date_gte, '%Y-%m-%d').date())
        
        date_lte = request.args.get('date_lte')
        if date_lte:
            query = query.filter(Bill.date <= datetime.strptime(date_lte, '%Y-%m-%d').date())
        
        # 排序和分页
        sort = request.args.get('sort', 'date')
        order = request.args.get('order', 'desc')
        limit = request.args.get('limit', type=int)
        
        if order == 'desc':
            query = query.order_by(getattr(Bill, sort).desc())
        else:
            query = query.order_by(getattr(Bill, sort).asc())
        
        if limit:
            query = query.limit(limit)
        
        bills = query.all()
        return jsonify([bill.to_dict() for bill in bills])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bills', methods=['POST'])
def add_bill():
    """添加账单"""
    try:
        data = request.json
        
        new_bill = Bill(
            type=data['type'],
            amount=float(data['amount']),
            category=data['category'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            note=data.get('note', '')
        )
        
        db.session.add(new_bill)
        db.session.commit()
        
        return jsonify(new_bill.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/bills/<int:id>', methods=['PUT'])
def update_bill(id):
    """更新账单"""
    try:
        bill = Bill.query.get_or_404(id)
        data = request.json
        
        bill.type = data['type']
        bill.amount = float(data['amount'])
        bill.category = data['category']
        bill.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        bill.note = data.get('note', '')
        
        db.session.commit()
        return jsonify(bill.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/bills/<int:id>', methods=['DELETE'])
def delete_bill(id):
    """删除账单"""
    try:
        bill = Bill.query.get_or_404(id)
        db.session.delete(bill)
        db.session.commit()
        return jsonify({'message': 'Bill deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 储蓄目标相关API
@app.route('/api/savings-goals', methods=['GET'])
def get_savings_goals():
    """获取储蓄目标列表"""
    try:
        limit = request.args.get('limit', type=int)
        query = SavingsGoal.query.order_by(SavingsGoal.createdAt.desc())
        
        if limit:
            query = query.limit(limit)
        
        goals = query.all()
        return jsonify([goal.to_dict() for goal in goals])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/savings-goals', methods=['POST'])
def add_savings_goal():
    """添加储蓄目标"""
    try:
        data = request.json
        
        new_goal = SavingsGoal(
            name=data['name'],
            targetAmount=float(data['targetAmount']),
            currentAmount=float(data.get('currentAmount', 0)),
            targetDate=datetime.strptime(data['targetDate'], '%Y-%m-%d').date() if data.get('targetDate') else None,
            type=data['type']
        )
        
        db.session.add(new_goal)
        db.session.commit()
        
        return jsonify(new_goal.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/savings-goals/<int:id>', methods=['DELETE'])
def delete_savings_goal(id):
    """删除储蓄目标"""
    try:
        goal = SavingsGoal.query.get_or_404(id)
        db.session.delete(goal)
        db.session.commit()
        return jsonify({'message': 'Goal deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/savings-goals/<int:id>/add-savings', methods=['POST'])
def add_savings_to_goal(id):
    """向储蓄目标添加金额"""
    try:
        goal = SavingsGoal.query.get_or_404(id)
        data = request.json
        amount = float(data.get('amount', 0))
        
        if amount > 0:
            goal.currentAmount = min(goal.currentAmount + amount, goal.targetAmount)
            db.session.commit()
        
        return jsonify(goal.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# 仪表盘和分析API
@app.route('/api/dashboard-summary', methods=['GET'])
def get_dashboard_summary():
    """获取仪表盘摘要"""
    try:
        user_id = get_user_id()
        data = FinancialService.get_dashboard_summary(user_id)
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/trends', methods=['GET'])
def get_analysis_trends():
    """获取分析趋势数据"""
    try:
        period = request.args.get('period', 'month')
        user_id = get_user_id()
        data = FinancialService.get_analysis_trends(period, user_id)
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/expense-pie', methods=['GET'])
def get_expense_pie():
    """获取支出饼图数据"""
    try:
        user_id = get_user_id()
        data = FinancialService.get_expense_pie(user_id)
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/savings-stats', methods=['GET'])
def get_savings_stats():
    """获取储蓄统计"""
    try:
        user_id = get_user_id()
        data = FinancialService.get_savings_stats(user_id)
        return jsonify(data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 用户画像相关API
@app.route('/api/financial-profile', methods=['GET'])
def get_financial_profile():
    """获取财务画像"""
    try:
        user_id = get_user_id()
        profile = FinancialProfile.query.filter_by(userId=user_id).first()
        
        if not profile:
            profile = FinancialProfile(userId=user_id)
            db.session.add(profile)
            db.session.commit()
        
        return jsonify(profile.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-profile', methods=['POST'])
def update_financial_profile():
    """更新财务画像"""
    try:
        user_id = get_user_id()
        profile = FinancialProfile.query.filter_by(userId=user_id).first()
        
        if not profile:
            profile = FinancialProfile(userId=user_id)
            db.session.add(profile)
        
        data = request.json
        profile.assetLiabilityRatio = data.get('assetLiabilityRatio', profile.assetLiabilityRatio)
        profile.debtIncomeRatio = data.get('debtIncomeRatio', profile.debtIncomeRatio)
        profile.surplusRatio = data.get('surplusRatio', profile.surplusRatio)
        profile.liquidityRatio = data.get('liquidityRatio', profile.liquidityRatio)
        profile.type = data.get('type', profile.type)
        
        db.session.commit()
        return jsonify(profile.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/risk-profile', methods=['GET'])
def get_risk_profile():
    """获取风险画像"""
    try:
        user_id = get_user_id()
        profile = RiskProfile.query.filter_by(userId=user_id).first()
        
        if not profile:
            profile = RiskProfile(userId=user_id)
            db.session.add(profile)
            db.session.commit()
        
        return jsonify(profile.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/risk-profile', methods=['POST'])
def update_risk_profile():
    """更新风险画像"""
    try:
        user_id = get_user_id()
        profile = RiskProfile.query.filter_by(userId=user_id).first()
        
        if not profile:
            profile = RiskProfile(userId=user_id)
            db.session.add(profile)
        
        data = request.json
        profile.score = data.get('score', profile.score)
        profile.answers = data.get('answers', profile.answers)
        profile.riskLevel = data.get('riskLevel', profile.riskLevel)
        profile.timestamp = datetime.now()
        
        db.session.commit()
        return jsonify(profile.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# 问卷相关API
@app.route('/api/questionnaires', methods=['GET'])
def get_questionnaires():
    """获取问卷列表"""
    try:
        questionnaires = Questionnaire.query.filter_by(isActive=True).all()
        return jsonify([q.to_dict() for q in questionnaires])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questionnaires/<int:id>', methods=['GET'])
def get_questionnaire(id):
    """获取单个问卷详情"""
    try:
        questionnaire = Questionnaire.query.get_or_404(id)
        return jsonify(questionnaire.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 理财产品相关API
@app.route('/api/financial-products', methods=['GET'])
def get_financial_products():
    """获取理财产品列表"""
    try:
        user_id = get_user_id()
        products = ProductService.get_recommended_products(user_id)
        return jsonify(products)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-products/search', methods=['GET'])
def search_financial_products():
    """搜索理财产品"""
    try:
        query = request.args.get('q', '')
        product_type = request.args.get('type')
        risk_level = request.args.get('risk')
        limit = request.args.get('limit', 20, type=int)
        
        products = ProductService.search_products(query, product_type, risk_level, limit)
        return jsonify(products)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/financial-products', methods=['POST'])
def add_financial_product():
    """添加理财产品（管理员功能）"""
    try:
        data = request.json
        
        product = FinancialProduct(
            name=data['name'],
            description=data.get('description', ''),
            productType=data['productType'],
            riskLevel=data.get('riskLevel', 'low'),
            expectedReturn=float(data.get('expectedReturn', 0)),
            minInvestment=float(data.get('minInvestment', 0)),
            investmentPeriod=data.get('investmentPeriod', ''),
            features=data.get('features', {}),
            tags=data.get('tags', [])
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/financial-products/<int:id>', methods=['PUT'])
def update_financial_product(id):
    """更新理财产品（管理员功能）"""
    try:
        product = FinancialProduct.query.get_or_404(id)
        data = request.json
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.productType = data.get('productType', product.productType)
        product.riskLevel = data.get('riskLevel', product.riskLevel)
        product.expectedReturn = float(data.get('expectedReturn', product.expectedReturn))
        product.minInvestment = float(data.get('minInvestment', product.minInvestment))
        product.investmentPeriod = data.get('investmentPeriod', product.investmentPeriod)
        product.features = data.get('features', product.features)
        product.tags = data.get('tags', product.tags)
        product.isActive = data.get('isActive', product.isActive)
        
        db.session.commit()
        return jsonify(product.to_dict())
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/ai-advice/financial', methods=['GET'])
def get_financial_advice_stream():
    """获取财务建议（流式传输）"""
    try:
        user_id = get_user_id()
        service = AIAdviceService()
        
        def generate():
            try:
                for chunk in service.generate_financial_advice_stream(user_id):
                    # 发送数据块
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                
                # 发送结束信号
                yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
                
            except Exception as e:
                # 发送错误信号
                yield f"data: {json.dumps({'type': 'error', 'content': f'生成失败: {str(e)}'})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-advice/investment', methods=['GET'])
def get_investment_advice_stream():
    """获取投资建议（流式传输）"""
    try:
        user_id = get_user_id()
        service = AIAdviceService()
        
        def generate():
            try:
                for chunk in service.generate_financial_advice_stream(user_id):
                    # 发送数据块
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                
                # 发送结束信号
                yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"
                
            except Exception as e:
                # 发送错误信号
                yield f"data: {json.dumps({'type': 'error', 'content': f'生成失败: {str(e)}'})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-advice', methods=['GET'])
def get_ai_advice_history():
    """获取AI建议历史"""
    try:
        user_id = get_user_id()
        limit = request.args.get('limit', 10, type=int)
        
        advice_list = AIAdvice.query.filter_by(userId=user_id)\
            .order_by(AIAdvice.createdAt.desc())\
            .limit(limit).all()
        
        return jsonify([advice.to_dict() for advice in advice_list])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 配置相关API
@app.route('/api/config', methods=['GET'])
def get_config():
    """获取应用配置"""
    try:
        return jsonify({
            'categories': Config.CATEGORIES,
            'savingsGoalTypes': Config.SAVINGS_GOAL_TYPES,
            'riskLevels': Config.RISK_LEVELS,
            'productTypes': Config.PRODUCT_TYPES
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 静态文件服务
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if path.endswith('.html') or path.endswith('.js') or path.startswith('resources/'):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# --- Main Runner ---
if __name__ == '__main__':
    init_db(app)
    app.run(debug=Config.DEBUG, port=5000, host='0.0.0.0')