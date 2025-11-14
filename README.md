# Bill Dates - 个人财务管理应用

一个现代化的个人财务管理应用，提供账单记录、储蓄目标管理、财务分析和AI理财建议等功能。

## 功能特性

### 🏠 首页仪表盘
- 实时财务概览（收入、支出、结余）
- 财务健康度评分
- 最近账单展示
- 储蓄目标预览
- AI个性化理财建议

### 📝 账单管理
- 快速记录收入和支出
- 智能分类管理
- 账单搜索和筛选
- 账单编辑和删除
- 月度财务统计

### 🎯 储蓄目标
- 创建多个储蓄目标
- 目标进度追踪
- 储蓄统计和分析
- 目标完成提醒

### 📊 财务分析
- 收支趋势分析
- 支出分类统计
- 财务健康度评估
- 关键财务指标
- AI财务洞察

### 📈 理财管理
- 风险评估问卷
- 个性化产品推荐
- 理财产品搜索
- 投资组合建议

### 🤖 AI智能助手
- 个性化理财建议
- 投资建议分析
- 财务健康诊断
- 流式响应体验

## 技术架构

### 后端技术栈
- **Flask**: Web框架
- **SQLAlchemy**: ORM数据库工具
- **SQLite**: 轻量级数据库
- **OpenAI API**: AI智能建议
- **Flask-CORS**: 跨域支持

### 前端技术栈
- **HTML5 + CSS3**: 页面结构和样式
- **Tailwind CSS**: 原子化CSS框架
- **JavaScript ES6+**: 交互逻辑
- **ECharts.js**: 数据可视化
- **Anime.js**: 动画效果

### 数据库设计
- **账单表 (bills)**: 记录收入和支出
- **储蓄目标表 (savings_goals)**: 管理储蓄目标
- **财务画像表 (financial_profiles)**: 用户财务画像
- **风险画像表 (risk_profiles)**: 风险评估结果
- **理财产品表 (financial_products)**: 理财产品信息
- **问卷表 (questionnaires)**: 风险评估问卷
- **AI建议表 (ai_advice)**: AI生成的建议
- **用户偏好表 (user_preferences)**: 用户设置

## 安装和运行

### 环境要求
- Python 3.8+
- Node.js 16+ (可选，用于前端开发)
- OpenAI API Key (可选，用于AI功能)

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd finance-app
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，添加 OpenAI API Key
```

5. 初始化数据库
```bash
python init_db.py
```

6. 运行应用
```bash
python app.py
```

### 访问应用
- 前端页面: http://localhost:5000
- API文档: http://localhost:5000/api (需要实现)

## 项目结构

```
finance-app/
├── app.py                 # 主应用文件
├── models.py              # 数据模型定义
├── services.py            # 业务逻辑服务
├── config.py              # 配置文件
├── init_db.py             # 数据库初始化脚本
├── utils                  # 辅助工具
├── mpt_solver.py          # MPT算法
├── qwen_service.py        # AI算法工具
├── requirements.txt       # Python依赖
├── README.md              # 项目说明
├── static/                # 静态文件目录
│   ├── index.html         # 首页
│   ├── bills.html         # 账单页面
│   ├── savings.html       # 储蓄页面
│   ├── analysis.html      # 分析页面
│   ├── insurance.html     # 保障页面
│   ├── main.js            # 主要JavaScript文件
│   └── resources/         # 资源文件
└── instance/
    └── finance.db         # SQLite数据库文件
```

## API接口

### 账单相关
- `GET /api/bills` - 获取账单列表
- `POST /api/bills` - 创建账单
- `PUT /api/bills/<id>` - 更新账单
- `DELETE /api/bills/<id>` - 删除账单

### 储蓄目标
- `GET /api/savings-goals` - 获取储蓄目标
- `POST /api/savings-goals` - 创建储蓄目标
- `DELETE /api/savings-goals/<id>` - 删除储蓄目标
- `POST /api/savings-goals/<id>/add-savings` - 添加储蓄

### 财务分析
- `GET /api/dashboard-summary` - 仪表盘摘要
- `GET /api/analysis/trends` - 收支趋势
- `GET /api/analysis/expense-pie` - 支出分类
- `GET /api/savings-stats` - 储蓄统计

### 用户画像
- `GET /api/financial-profile` - 获取财务画像
- `POST /api/financial-profile` - 更新财务画像
- `GET /api/risk-profile` - 获取风险画像
- `POST /api/risk-profile` - 更新风险画像

### 理财产品
- `GET /api/financial-products` - 获取理财产品
- `GET /api/financial-products/search` - 搜索理财产品
- `POST /api/financial-products` - 添加理财产品
- `PUT /api/financial-products/<id>` - 更新理财产品
- `DELETE /api/financial-products/<id>` - 删除理财产品

### AI建议
- `GET /api/ai-advice/financial` - 获取财务建议（流式）
- `GET /api/ai-advice/investment` - 获取投资建议（流式）
- `GET /api/ai-advice` - 获取AI建议历史

### 配置
- `GET /api/config` - 获取应用配置

## 开发指南

### 添加新功能
1. 在 `models.py` 中定义数据模型
2. 在 `services.py` 中添加业务逻辑
3. 在 `app.py` 中添加API接口
4. 在前端页面中添加对应功能

### 前端开发
- 使用 Tailwind CSS 进行样式设计
- 使用 ECharts.js 进行数据可视化
- 使用 Anime.js 添加动画效果
- 确保移动端适配

### 后端开发
- 遵循 RESTful API 设计规范
- 使用 SQLAlchemy 进行数据库操作
- 添加适当的错误处理和验证
- 考虑性能和安全性

## 部署指南

### 测试环境部署
1. windows平台点击start.bat进行自动化部署
2. Linux/Mac平台点击run.sh进行自动化部署

### 生产环境部署
1. 设置环境变量
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key
export OPENAI_API_KEY=your-openai-api-key
```

2. 使用生产级Web服务器
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 许可证

本项目采用 GPL-v3 许可证 - 查看 [LICENSE](./LICENSE) 文件了解详情。

## 更新日志

### v1.0.0 (2025-11-10)
- 初始版本发布
- 基础财务管理功能
- AI智能建议功能
- 移动端适配
- 数据可视化分析

---

**注意**: 这是一个教育和个人使用的项目，请根据实际情况调整配置和功能。理财有风险，投资需谨慎。