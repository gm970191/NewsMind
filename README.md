# NewsMind 新闻聚智系统

> 一个智能的新闻聚合与AI分析平台，支持多语言新闻采集、智能摘要生成和实时翻译

[![Version](https://img.shields.io/badge/version-v0.5-blue.svg)](https://github.com/your-username/NewsMind)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/vue-3.0+-green.svg)](https://vuejs.org)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 🚀 最新更新 (V0.5)

### ✨ 新功能
- **AI自动化处理**：每10分钟自动处理新抓取的新闻，无需人工干预
- **新闻源优化**：删除重复的BBC新闻源，提升内容质量
- **智能调度系统**：完善的定时任务调度器，支持新闻采集、AI处理和数据清理

### 🔧 技术改进
- 新增`get_unprocessed_articles`方法，支持批量获取未处理新闻
- 实现`_ai_process_job`定时任务，自动处理未处理新闻
- 完善的错误处理和日志记录机制

## 📖 项目简介

NewsMind是一个基于AI的新闻聚合系统，能够自动采集、分析和翻译多语言新闻内容。系统采用现代化的技术栈，提供直观的Web界面和强大的后端API。

### 🌟 核心特性

- **🔍 智能新闻采集**：支持RSS和网页抓取，自动去重和内容清洗
- **🤖 AI智能处理**：自动生成中文摘要、翻译标题和内容、质量评分
- **🌍 多语言支持**：支持中英文新闻，自动语言检测和翻译
- **⚡ 实时处理**：每10分钟自动处理新抓取新闻，确保内容及时更新
- **📊 数据统计**：详细的处理统计和质量分析
- **🎨 现代化UI**：基于Vue 3的响应式界面设计

## 🏗️ 系统架构

```
NewsMind/
├── backend/                 # 后端服务 (FastAPI + SQLAlchemy)
│   ├── app/
│   │   ├── api/            # API接口
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务服务
│   └── scripts/            # 管理脚本
├── frontend/               # 前端应用 (Vue 3 + Vite)
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   └── stores/         # 状态管理
└── docs/                   # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- SQLite 3

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/NewsMind.git
cd NewsMind
```

2. **后端设置**
```bash
cd backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 DEEPSEEK_API_KEY

# 初始化数据库
python scripts/init_db.py

# 启动后端服务
python start_server.py
```

3. **前端设置**
```bash
cd frontend
npm install
npm run dev
```

4. **访问应用**
- 前端界面：http://localhost:3000
- API文档：http://localhost:8000/docs
- 后端服务：http://localhost:8000

## 🔧 配置说明

### 环境变量配置

在 `backend/.env` 文件中配置：

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 数据库配置
DATABASE_URL=sqlite:///./newsmind.db

# 应用配置
DEBUG=true
LOG_LEVEL=INFO

# 新闻采集配置
MAX_ARTICLES_PER_SOURCE=20
CONTENT_RETENTION_DAYS=30

# AI处理配置
MAX_PROCESSING_BATCH_SIZE=10
PROCESSING_DELAY_SECONDS=1
```

### 定时任务配置

系统内置以下定时任务：

- **新闻采集**：每6小时自动采集最新新闻
- **AI处理**：每10分钟自动处理未处理新闻
- **数据清理**：每天凌晨2点清理过期内容

## 📊 功能特性

### 新闻采集
- 支持RSS和网页抓取
- 自动去重和内容清洗
- 多语言新闻源支持
- 智能内容提取

### AI处理
- 自动生成中文摘要
- 智能标题翻译
- 内容质量评分
- 批量处理优化

### 用户界面
- 响应式设计
- 实时数据更新
- 分类筛选功能
- 搜索和排序

### 数据管理
- 完整的CRUD操作
- 数据统计和分析
- 自动备份和清理
- 性能监控

## 🔌 API接口

### 新闻相关
- `GET /api/v1/news/articles` - 获取新闻列表
- `GET /api/v1/news/articles/{id}` - 获取新闻详情
- `GET /api/v1/news/sources` - 获取新闻源列表
- `GET /api/v1/news/statistics` - 获取统计信息

### AI处理
- `POST /api/v1/ai/process` - 批量处理新闻
- `POST /api/v1/ai/process/{id}` - 处理单篇新闻
- `GET /api/v1/ai/statistics` - 获取AI处理统计
- `GET /api/v1/ai/unprocessed-count` - 获取未处理数量

## 📈 性能指标

### 处理能力
- 每10分钟处理10篇新闻
- 每天可处理约1440篇新闻
- 支持多语言内容处理

### 系统资源
- 轻量级定时任务
- 优化的数据库查询
- 稳定的内存使用

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 更新日志

### V0.5 (2025-07-11)
- ✨ 新增AI自动化处理功能
- 🔧 优化新闻源管理
- 🚀 实现智能定时任务调度
- 📊 完善错误处理和日志记录

### V0.4 (2025-07-10)
- 🔧 修复中文显示问题
- 🧹 清理无效API和过时脚本
- 📈 优化前端用户体验

### V0.3 (2025-07-09)
- 🗑️ 删除processed_content表
- 🔄 重构AI处理逻辑
- 📊 完善数据统计功能

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目主页：https://github.com/your-username/NewsMind
- 问题反馈：https://github.com/your-username/NewsMind/issues
- 邮箱：your-email@example.com

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！ 

# 数据库路径说明

**所有数据库操作、配置、脚本均应指向 `backend/newsmind.db`。根目录下不应有 `newsmind.db`，如有请删除，避免混淆。**

--- 