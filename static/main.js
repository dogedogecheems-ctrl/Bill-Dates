// 财务保障应用主要JavaScript文件

// 全局 API 基础 URL
const API_BASE_URL = '/api';

// 配置对象
let APP_CONFIG = {
    categories: {},
    savingsGoalTypes: {},
    riskLevels: {},
    productTypes: {}
};

// 数据管理类
class FinanceManager {
    constructor() {
        // 本地缓存，用于减少不必要的API调用
        this.bills = [];
        this.savingsGoals = [];
        this.financialProfile = null;
        this.riskProfile = null;
        this.financialProducts = [];
        this.aiAdvice = [];
        
        this.loadConfig();
    }
    
    // 加载应用配置
    async loadConfig() {
        try {
            const response = await this.request('/config');
            APP_CONFIG = response;
            
            // 更新分类名称映射
            this.categoryNames = {
                ...APP_CONFIG.categories.income,
                ...APP_CONFIG.categories.expense
            };
        } catch (error) {
            console.error('Failed to load config:', error);
            // 使用默认配置
            this.categoryNames = {
                'salary': '工资收入',
                'bonus': '奖金收入',
                'investment': '投资收益',
                'food': '餐饮美食',
                'transport': '交通出行',
                'shopping': '购物消费',
                'entertainment': '娱乐休闲',
                'health': '医疗健康',
                'education': '教育培训',
                'other': '其他'
            };
        }
    }

    // --- 通用 API Fetcher ---
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'API 请求失败');
            }
            
            if (response.status === 204) {
                return null;
            }
            
            return response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            showToast(`操作失败: ${error.message}`, 'error');
            throw error;
        }
    }

    // --- 账单 (Bills) ---
    async getBills(params = {}) {
        const query = new URLSearchParams(params).toString();
        this.bills = await this.request(`/bills?${query}`);
        return this.bills;
    }

    async addBill(bill) {
        const newBill = await this.request('/bills', {
            method: 'POST',
            body: JSON.stringify(bill),
        });
        this.bills.unshift(newBill);
        return newBill;
    }

    async updateBill(id, bill) {
        const updatedBill = await this.request(`/bills/${id}`, {
            method: 'PUT',
            body: JSON.stringify(bill),
        });
        
        const index = this.bills.findIndex(b => b.id === id);
        if (index !== -1) {
            this.bills[index] = updatedBill;
        }
        return updatedBill;
    }

    async deleteBill(id) {
        await this.request(`/bills/${id}`, { method: 'DELETE' });
        this.bills = this.bills.filter(bill => bill.id !== id);
    }

    // --- 储蓄 (Savings) ---
    async getSavingsGoals(params = {}) {
        const query = new URLSearchParams(params).toString();
        this.savingsGoals = await this.request(`/savings-goals?${query}`);
        return this.savingsGoals;
    }

    async addSavingsGoal(goal) {
        const newGoal = await this.request('/savings-goals', {
            method: 'POST',
            body: JSON.stringify(goal),
        });
        this.savingsGoals.unshift(newGoal);
        return newGoal;
    }

    async deleteSavingsGoal(id) {
        await this.request(`/savings-goals/${id}`, { method: 'DELETE' });
        this.savingsGoals = this.savingsGoals.filter(g => g.id !== id);
    }

    async updateSavingsGoal(id, amount) {
        const updatedGoal = await this.request(`/savings-goals/${id}/add-savings`, {
            method: 'POST',
            body: JSON.stringify({ amount }),
        });
        
        const index = this.savingsGoals.findIndex(g => g.id === id);
        if (index !== -1) {
            this.savingsGoals[index] = updatedGoal;
        }
        return updatedGoal;
    }

    async getSavingsStats() {
        return await this.request('/savings-stats');
    }

    // --- 画像 (Profiles) ---
    async getFinancialProfile() {
        this.financialProfile = await this.request('/financial-profile');
        return this.financialProfile;
    }

    async updateFinancialProfile(profileData) {
        this.financialProfile = await this.request('/financial-profile', {
            method: 'POST',
            body: JSON.stringify(profileData),
        });
        return this.financialProfile;
    }

    async getRiskProfile() {
        this.riskProfile = await this.request('/risk-profile');
        return this.riskProfile;
    }

    async updateRiskProfile(profileData) {
        this.riskProfile = await this.request('/risk-profile', {
            method: 'POST',
            body: JSON.stringify(profileData),
        });
        return this.riskProfile;
    }

    // --- 仪表盘 ---
    async getDashboardSummary() {
        return await this.request('/dashboard-summary');
    }

    // --- 分析 ---
    async getAnalysisTrends(period = 'month') {
        return await this.request(`/analysis/trends?period=${period}`);
    }

    async getAnalysisExpensePie() {
        return await this.request('/analysis/expense-pie');
    }

    // --- 理财产品 ---
    async getFinancialProducts() {
        this.financialProducts = await this.request('/financial-products');
        return this.financialProducts;
    }

    async searchFinancialProducts(query, type = null, risk = null) {
        const params = new URLSearchParams({ q: query });
        if (type) params.append('type', type);
        if (risk) params.append('risk', risk);
        
        return await this.request(`/financial-products/search?${params}`);
    }

    // --- 问卷 ---
    async getQuestionnaires() {
        return await this.request('/questionnaires');
    }

    async getQuestionnaire(id) {
        return await this.request(`/questionnaires/${id}`);
    }

    // --- AI建议 ---
    async getFinancialAdviceStream(callback) {
        try {
            const eventSource = new EventSource(`${API_BASE_URL}/ai-advice/financial`);
            
            return new Promise((resolve, reject) => {
                eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        
                        switch(data.type) {
                            case 'content':
                                callback(data.content);
                                break;
                            case 'done':
                                eventSource.close();
                                resolve();
                                break;
                            case 'error':
                                eventSource.close();
                                reject(new Error(data.content));
                                break;
                        }
                    } catch (error) {
                        console.error('Parse error:', error);
                    }
                };
                
                eventSource.onerror = (error) => {
                    console.error('SSE error:', error);
                    eventSource.close();
                    reject(new Error('连接失败，请检查网络连接'));
                };
                
                // 设置超时
                setTimeout(() => {
                    eventSource.close();
                    reject(new Error('请求超时'));
                }, 120000); // 2分钟超时
            });
            
        } catch (error) {
            console.error('Stream error:', error);
            callback('获取建议失败，请稍后重试。');
            throw error;
        }
    }

    async getInvestmentAdviceStream(callback) {
        try {
            const eventSource = new EventSource(`${API_BASE_URL}/ai-advice/investment`);
            
            return new Promise((resolve, reject) => {
                eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        
                        switch(data.type) {
                            case 'content':
                                callback(data.content);
                                break;
                            case 'done':
                                eventSource.close();
                                resolve();
                                break;
                            case 'error':
                                eventSource.close();
                                reject(new Error(data.content));
                                break;
                        }
                    } catch (error) {
                        console.error('Parse error:', error);
                    }
                };
                
                eventSource.onerror = (error) => {
                    console.error('SSE error:', error);
                    eventSource.close();
                    reject(new Error('连接失败，请检查网络连接'));
                };
                
                // 设置超时
                setTimeout(() => {
                    eventSource.close();
                    reject(new Error('请求超时'));
                }, 120000); // 2分钟超时
            });
            
        } catch (error) {
            console.error('Stream error:', error);
            callback('获取建议失败，请稍后重试。');
            throw error;
        }
    }
    // --- 助手函数 ---

    // 获取分类名称
    getCategoryName(category) {
        return this.categoryNames[category] || category;
    }

    // 数字动画
    animateNumber(elementId, targetValue, prefix = '¥', toFixed = 2) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = parseFloat(element.textContent.replace(prefix, '').replace(/,/g, '')) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            let progress = Math.min(elapsed / duration, 1);
            
            // 添加 easeOutQuad 缓动
            progress = progress * (2 - progress);

            const currentValue = startValue + (targetValue - startValue) * progress;
            
            if (toFixed === 0) {
                element.textContent = prefix + Math.round(currentValue);
            } else {
                element.textContent = prefix + currentValue.toFixed(toFixed);
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = prefix + targetValue.toFixed(toFixed);
            }
        };

        requestAnimationFrame(animate);
    }

    // 数字动画
    animateScore(elementId, targetValue, toFixed = 0) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = parseFloat(element.textContent.replace(/,/g, '')) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            let progress = Math.min(elapsed / duration, 1);
            
            // 添加 easeOutQuad 缓动
            progress = progress * (2 - progress);

            const currentValue = startValue + (targetValue - startValue) * progress;
            
            if (toFixed === 0) {
                element.textContent = Math.round(currentValue);
            } else {
                element.textContent = currentValue.toFixed(toFixed);
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = targetValue.toFixed(toFixed);
            }
        };

        requestAnimationFrame(animate);
    }

    // 格式化日期
    formatDate(dateString) {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // 格式化货币
    formatCurrency(amount) {
        return '¥' + parseFloat(amount).toFixed(2);
    }

    // 计算进度百分比
    calculateProgress(current, target) {
        if (target <= 0) return 0;
        return Math.min((current / target) * 100, 100);
    }

    // 获取风险等级颜色
    getRiskLevelColor(riskLevel) {
        const colors = {
            'low': '#10B981',
            'medium': '#F59E0B', 
            'high': '#EF4444'
        };
        return colors[riskLevel] || '#6B7280';
    }

    // 获取产品类型图标
    getProductTypeIcon(productType) {
        const icons = {
            'fund': '📊',
            'insurance': '🛡️',
            'deposit': '🏦',
            'bond': '📜',
            'stock': '📈'
        };
        return icons[productType] || '💰';
    }
}

// --- 全局实例和辅助函数 ---

// 创建一个全局唯一的 financeManager 实例
const financeManager = new FinanceManager();

// 显示提示消息
function showToast(message, type = 'info', duration = 3000) {
    // 移除现有的toast
    const existingToast = document.querySelector('.toast-notification');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = `fixed top-4 left-4 right-4 z-50 p-4 rounded-xl text-white text-center transform transition-all duration-300 translate-y-[-100px] opacity-0 toast-notification ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 
        type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
    }`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // 触发动画
    setTimeout(() => {
        toast.classList.remove('translate-y-[-100px]', 'opacity-0');
    }, 10);
    
    // 自动隐藏
    setTimeout(() => {
        toast.classList.add('translate-y-[-100px]', 'opacity-0');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
}

// 账单类型变化时更新分类选项
function updateCategoryOptions(type) {
    const categorySelect = document.getElementById('billCategory');
    if (!categorySelect) return;

    categorySelect.innerHTML = '';
    
    if (type === 'income') {
        const incomeCategories = APP_CONFIG.categories.income || {
            'salary': '工资收入',
            'bonus': '奖金收入',
            'investment': '投资收益',
            'other': '其他收入'
        };
        
        Object.entries(incomeCategories).forEach(([value, text]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = text;
            categorySelect.appendChild(option);
        });
    } else {
        const expenseCategories = APP_CONFIG.categories.expense || {
            'food': '餐饮美食',
            'transport': '交通出行',
            'shopping': '购物消费',
            'entertainment': '娱乐休闲',
            'health': '医疗健康',
            'education': '教育培训',
            'other': '其他支出'
        };
        
        Object.entries(expenseCategories).forEach(([value, text]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = text;
            categorySelect.appendChild(option);
        });
    }
}

// 获取储蓄目标类型名称
function getSavingsGoalTypeName(type) {
    const types = APP_CONFIG.savingsGoalTypes || {
        'emergency': '应急基金',
        'vacation': '旅游基金',
        'house': '购房基金',
        'car': '购车基金',
        'education': '教育基金',
        'retirement': '退休基金',
        'investment': '投资本金',
        'other': '其他目标'
    };
    return types[type] || type;
}

// 显示加载状态
function showLoading(elementId, text = '加载中...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <span class="ml-2 text-gray-600">${text}</span>
            </div>
        `;
    }
}

// 隐藏加载状态
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

// 格式化数字为千分位
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// 检查是否为移动设备
function isMobile() {
    return window.innerWidth <= 768;
}

// 适配移动端的模态框
function showMobileModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        const content = modal.querySelector('.modal-content');
        if (content) {
            setTimeout(() => {
                content.classList.remove('translate-y-full');
            }, 10);
        }
    }
}

function hideMobileModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const content = modal.querySelector('.modal-content');
        if (content) {
            content.classList.add('translate-y-full');
        }
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
    }
}

// 全局事件监听器
document.addEventListener('change', function(e) {
    if (e.target.id === 'billType') {
        updateCategoryOptions(e.target.value);
    }
});

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化配置
    financeManager.loadConfig();
    
    // 设置全局错误处理
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        showToast('页面出现错误，请刷新重试', 'error');
    });
    
    // 添加触摸反馈
    document.addEventListener('touchstart', function(e) {
        if (e.target.classList.contains('touch-feedback')) {
            e.target.style.transform = 'scale(0.98)';
        }
    });
    
    document.addEventListener('touchend', function(e) {
        if (e.target.classList.contains('touch-feedback')) {
            e.target.style.transform = 'scale(1)';
        }
    });
});

// 导出到全局作用域
window.financeManager = financeManager;
window.showToast = showToast;
window.updateCategoryOptions = updateCategoryOptions;
window.getSavingsGoalTypeName = getSavingsGoalTypeName;