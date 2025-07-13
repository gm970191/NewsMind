# NewsMind 简化版 - 智能新闻聚合系统

一个简化的新闻聚合系统，支持RSS新闻抓取、本地AI翻译和中文优先显示。

## 功能特性

### 🎯 核心功能
- **新闻抓取**: 从RSS源自动抓取新闻标题和概要
- **AI翻译**: 使用本地LM Studio进行中英文翻译
- **中文优先**: 新闻卡片和详情页优先显示中文内容
- **简洁界面**: 现代化的Vue3 + Element Plus界面

### 📰 新闻源
- BBC News (国际新闻)
- Reuters (国际新闻)
- TechCrunch (科技新闻)
- Ars Technica (科技新闻)
- Wired (科技新闻)

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.8+
- Node.js 16+
- LM Studio (本地AI服务)

### 2. 安装依赖

```bash
# 后端依赖
cd backend
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 3. 初始化数据库

```bash
python scripts/init_simple_db.py
```

### 4. 启动LM Studio

确保LM Studio运行在 `http://127.0.0.1:1234`

### 5. 启动服务

```bash
# 启动后端 (新终端)
python backend/start_server.py --mode dev

# 启动前端 (新终端)
npm run dev --prefix frontend
```

### 6. 访问系统

- 前端页面: http://localhost:5173
- API文档: http://localhost:8000/docs

## 使用说明

### 抓取新闻
点击主页的"抓取新闻"按钮，系统会自动从配置的RSS源获取最新新闻。

### AI翻译
点击"AI翻译"按钮，系统会使用本地LM Studio翻译未翻译的新闻标题和概要。

### 查看新闻
- 新闻卡片优先显示中文翻译内容
- 点击"查看详情"可查看完整的中文和原文内容
- 点击"原文链接"可跳转到原始新闻页面

## 系统架构

### 后端 (FastAPI)
```
backend/
├── app/
│   ├── api/           # API接口
│   ├── core/          # 核心配置
│   ├── models/        # 数据模型
│   └── services/      # 业务服务
├── start_server.py    # 服务启动
└── requirements.txt   # 依赖列表
```

### 前端 (Vue3)
```
frontend/
├── src/
│   ├── components/    # 组件
│   ├── views/         # 页面
│   ├── stores/        # 状态管理
│   └── router/        # 路由
├── package.json       # 依赖配置
└── vite.config.js     # 构建配置
```

## 数据库结构

### 新闻源表 (news_sources)
- `id`: 主键
- `name`: 新闻源名称
- `url`: RSS地址
- `type`: 类型 (rss/web)
- `category`: 分类
- `is_active`: 是否活跃

### 新闻文章表 (news_articles)
- `id`: 主键
- `original_title`: 原始标题
- `original_summary`: 原始概要
- `translated_title`: 翻译标题
- `translated_summary`: 翻译概要
- `source_url`: 原文链接
- `source_name`: 新闻源名称
- `category`: 分类
- `is_translated`: 是否已翻译
- `created_at`: 创建时间

## API接口

### 新闻相关
- `GET /api/v1/news/articles` - 获取新闻列表
- `GET /api/v1/news/articles/{id}` - 获取新闻详情
- `POST /api/v1/news/crawl` - 抓取新闻
- `GET /api/v1/news/statistics` - 获取统计信息

### AI翻译
- `POST /api/v1/ai/translate` - 批量翻译
- `POST /api/v1/ai/translate/{id}` - 翻译单篇文章
- `GET /api/v1/ai/statistics` - 获取翻译统计
- `GET /api/v1/ai/untranslated-count` - 获取未翻译数量

## 开发脚本

### 数据库管理
```bash
# 初始化数据库
python scripts/init_simple_db.py

# 检查数据库状态
python scripts/check_db.py
```

### 新闻抓取
```bash
# 手动抓取新闻
python scripts/simple_news_crawler.py
```

### 系统测试
```bash
# 端到端测试
python scripts/simple_e2e_test.py
```

## 配置说明

### LM Studio配置
- 默认地址: `http://127.0.0.1:1234`
- 支持模型: 任意兼容OpenAI格式的模型
- 推荐模型: Qwen2.5-7B-Instruct, Llama3.1-8B-Instruct

### 新闻源配置
在 `scripts/init_simple_db.py` 中修改新闻源列表：
```python
sources = [
    {
        'name': '新闻源名称',
        'url': 'RSS地址',
        'type': 'rss',
        'category': '分类'
    }
]
```

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查端口8000是否被占用
   - 确认数据库文件权限

2. **新闻抓取失败**
   - 检查网络连接
   - 确认RSS地址有效
   - 查看后端日志

3. **AI翻译失败**
   - 确认LM Studio已启动
   - 检查端口1234是否可访问
   - 确认模型已加载

4. **前端无法访问后端**
   - 检查后端服务状态
   - 确认API地址配置
   - 检查CORS设置

### 日志查看
```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
# 在浏览器开发者工具中查看
```

## 技术栈

- **后端**: FastAPI, SQLAlchemy, SQLite
- **前端**: Vue3, Element Plus, Pinia
- **AI**: LM Studio (本地部署)
- **数据库**: SQLite
- **构建工具**: Vite

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

---

**NewsMind 简化版** - 让新闻阅读更简单、更智能！ 