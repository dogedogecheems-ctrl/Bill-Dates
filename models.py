from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime
import json

db = SQLAlchemy()

class Bill(db.Model):
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # 'income' or 'expense'
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    note = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.isoformat(),
            'note': self.note,
            'timestamp': self.timestamp.isoformat()
        }

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    targetAmount = db.Column(db.Float, nullable=False)
    currentAmount = db.Column(db.Float, default=0.0)
    targetDate = db.Column(db.Date, nullable=True)
    type = db.Column(db.String(50), nullable=False)
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'targetAmount': self.targetAmount,
            'currentAmount': self.currentAmount,
            'targetDate': self.targetDate.isoformat() if self.targetDate else None,
            'type': self.type,
            'createdAt': self.createdAt.isoformat(),
            'progress': (self.currentAmount / self.targetAmount * 100) if self.targetAmount > 0 else 0
        }

class FinancialProfile(db.Model):
    __tablename__ = 'financial_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(100), unique=True, nullable=False, default='default_user')
    assetLiabilityRatio = db.Column(db.Float, default=0)
    debtIncomeRatio = db.Column(db.Float, default=0)
    surplusRatio = db.Column(db.Float, default=0)
    liquidityRatio = db.Column(db.Float, default=0)
    type = db.Column(db.String(50), default='健康稳健型')
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updatedAt = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'assetLiabilityRatio': self.assetLiabilityRatio,
            'debtIncomeRatio': self.debtIncomeRatio,
            'surplusRatio': self.surplusRatio,
            'liquidityRatio': self.liquidityRatio,
            'type': self.type,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None
        }

class RiskProfile(db.Model):
    __tablename__ = 'risk_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(100), unique=True, nullable=False, default='default_user')
    score = db.Column(db.Integer, default=0)
    answers = db.Column(db.JSON, default={})
    riskLevel = db.Column(db.String(20), default='保守型')
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'score': self.score,
            'answers': self.answers,
            'riskLevel': self.riskLevel,
            'timestamp': self.timestamp.isoformat()
        }

class Questionnaire(db.Model):
    __tablename__ = 'questionnaires'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    questions = db.Column(db.JSON, nullable=False)
    type = db.Column(db.String(50), default='risk_assessment')  # risk_assessment, financial_profile
    isActive = db.Column(db.Boolean, default=True)
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updatedAt = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'questions': self.questions,
            'type': self.type,
            'isActive': self.isActive,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None
        }

class FinancialProduct(db.Model):
    __tablename__ = 'financial_products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    productType = db.Column(db.String(50), nullable=False)  # fund, insurance, deposit, bond, stock
    riskLevel = db.Column(db.String(20), default='low')  # low, medium, high
    expectedReturn = db.Column(db.Float, default=0)  # 预期年化收益率
    minInvestment = db.Column(db.Float, default=0)  # 最低投资额
    investmentPeriod = db.Column(db.String(50))  # 投资期限
    features = db.Column(db.JSON, default={})
    tags = db.Column(db.JSON, default=[])
    isActive = db.Column(db.Boolean, default=True)
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updatedAt = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'productType': self.productType,
            'riskLevel': self.riskLevel,
            'expectedReturn': self.expectedReturn,
            'minInvestment': self.minInvestment,
            'investmentPeriod': self.investmentPeriod,
            'features': self.features,
            'tags': self.tags,
            'isActive': self.isActive,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None
        }

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(100), nullable=False, default='default_user')
    preferenceType = db.Column(db.String(50), nullable=False)  # notification, theme, language
    preferenceValue = db.Column(db.JSON, nullable=False)
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updatedAt = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'preferenceType': self.preferenceType,
            'preferenceValue': self.preferenceValue,
            'createdAt': self.createdAt.isoformat(),
            'updatedAt': self.updatedAt.isoformat() if self.updatedAt else None
        }

class AIAdvice(db.Model):
    __tablename__ = 'ai_advice'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(100), nullable=False, default='default_user')
    adviceType = db.Column(db.String(50), nullable=False)  # financial_planning, investment, savings
    content = db.Column(db.Text, nullable=False)
    context = db.Column(db.JSON, default={})  # 生成建议的上下文信息
    isRead = db.Column(db.Boolean, default=False)
    createdAt = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.userId,
            'adviceType': self.adviceType,
            'content': self.content,
            'context': self.context,
            'isRead': self.isRead,
            'createdAt': self.createdAt.isoformat()
        }