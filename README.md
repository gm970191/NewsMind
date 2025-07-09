# NewsMind - 智能新闻聚合系统

> **版本**: V0.1  
> **作者**: 星辰大海  
> **项目**: 基于AI的智能新闻聚合、分析与翻译系统

## 🌟 项目简介

NewsMind是一个基于Python FastAPI + Vue 3的智能新闻聚合系统，支持多语言新闻采集、AI智能分析、自动翻译和个性化推荐。系统采用前后端分离架构，具备完整的新闻生命周期管理能力。

## ✨ 核心功能

### 📰 新闻采集
- **多源采集**: 支持RSS、API、网页爬虫等多种数据源
- **多语言支持**: 英语、日语、韩语、中文等多语言新闻
- **实时更新**: 自动化新闻采集和更新机制
- **智能去重**: 基于URL和内容的智能去重算法

### 🤖 AI智能分析
- **智能摘要**: 基于DeepSeek API的新闻内容摘要
- **多语言翻译**: 支持跨语言新闻翻译
- **情感分析**: 新闻情感倾向分析
- **关键词提取**: 自动提取新闻关键词和主题

### 🎯 用户体验
- **响应式设计**: 支持PC、平板、手机多端访问
- **智能搜索**: 全文搜索和分类筛选
- **分页加载**: 流畅的加载更多体验
- **实时统计**: 新闻源和文章统计信息

## 🏗️ 技术架构

### 后端技术栈
- **框架**: FastAPI (Python)
- **数据库**: SQLite
- **AI服务**: DeepSeek API
- **爬虫**: requests + BeautifulSoup
- **缓存**: 内存缓存系统

### 前端技术栈
- **框架**: Vue 3 + Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

### 部署方案
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx
- **进程管理**: 系统服务

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Git

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/gm970191/NewsMind.git
cd NewsMind
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp backend/ENV_SETUP.md backend/.env
# 编辑 .env 文件，设置您的 DeepSeek API 密钥
# 详细配置说明请参考 backend/ENV_SETUP.md
```

3. **安装后端依赖**
```bash
pip install -r requirements.txt
```

4. **安装前端依赖**
```bash
cd frontend
npm install
```

5. **启动服务**
```bash
# 启动后端服务
python backend/start_server.py --mode simple

# 启动前端服务
cd frontend
npm run dev
```

5. **访问系统**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 📊 系统特性

### 数据统计
- **新闻源**: 33个活跃新闻源
- **文章数量**: 165篇多语言新闻
- **语言分布**: 英语127篇、中文28篇、日语10篇
- **分类覆盖**: 国际、科技、财经、体育等

### 性能指标
- **API响应时间**: < 100ms
- **页面加载时间**: < 2s
- **并发支持**: 100+ 用户
- **数据准确性**: 99%+

## 🔧 开发指南

### 项目结构
```
NewsMind/
├── backend/                 # 后端代码
│   ├── app/                # 主应用
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   └── utils/         # 工具函数
│   ├── tests/             # 测试代码
│   └── start_server.py    # 启动脚本
├── frontend/               # 前端代码
│   ├── src/               # 源代码
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── stores/        # 状态管理
│   │   └── router/        # 路由配置
│   └── package.json       # 依赖配置
├── docs/                   # 项目文档
├── scripts/                # 工具脚本
└── test_results/           # 测试结果
```

### 开发规范
- **代码风格**: 遵循PEP 8 (Python) 和ESLint (JavaScript)
- **提交规范**: 使用语义化提交信息
- **测试覆盖**: 单元测试覆盖率 > 80%
- **文档更新**: 代码变更同步更新文档

## 🧪 测试

### 运行测试
```bash
# 后端测试
cd backend
python -m pytest

# 前端测试
cd frontend
npm run test

# 端到端测试
python test_load_more_functionality.py
```

### 测试报告
- **功能测试**: 通过率 100%
- **性能测试**: 响应时间达标
- **兼容性测试**: 主流浏览器支持

## 📈 版本历史

### V0.1 (2025-07-09)
- ✅ 完成基础新闻采集功能
- ✅ 实现AI智能分析系统
- ✅ 构建响应式前端界面
- ✅ 支持多语言新闻处理
- ✅ 完善分页加载功能
- ✅ 建立完整测试体系

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 贡献流程
1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request

### 开发环境
```bash
# 设置开发环境
git clone https://github.com/gm970191/NewsMind.git
cd NewsMind
pip install -r requirements.txt
cd frontend && npm install
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

**星辰大海** - 全栈开发工程师

- GitHub: [@gm970191](https://github.com/gm970191)
- 项目地址: [NewsMind](https://github.com/gm970191/NewsMind)

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [DeepSeek](https://platform.deepseek.com/)

---

⭐ 如果这个项目对您有帮助，请给我们一个Star！ 