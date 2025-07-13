# NewsMind - 智能新闻聚合系统

## 项目简介

NewsMind 是一个基于 Vue.js + FastAPI 的智能新闻聚合系统，支持多源新闻抓取、AI智能翻译和分类浏览。

## 核心功能

### 🗞️ 新闻聚合
- **多源抓取**: 支持 RSS 和网页新闻源
- **定时更新**: 自动定时抓取最新新闻
- **去重处理**: 智能识别重复新闻

### 🤖 AI 智能处理
- **自动翻译**: 英文新闻自动翻译为中文
- **本地AI**: 基于 LM Studio 本地大模型
- **异步处理**: 后台自动翻译，无需人工干预

### 🏷️ 分类浏览
- **智能分类**: 军事、科技、政治等分类
- **标签筛选**: 点击标签快速筛选新闻
- **响应式设计**: 支持桌面和移动端

## 技术架构

### 前端 (Vue.js 3)
- **框架**: Vue 3 + Composition API
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4

### 后端 (FastAPI)
- **框架**: FastAPI + SQLAlchemy
- **数据库**: SQLite
- **AI服务**: LM Studio 本地模型
- **定时任务**: APScheduler

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- LM Studio (本地AI服务)

### 1. 克隆项目
```bash
git clone <repository-url>
cd NewsMind
```

### 2. 后端设置
```bash
cd backend
pip install -r requirements.txt
```

### 3. 启动LM Studio
- 下载并安装 [LM Studio](https://lmstudio.ai/)
- 启动本地服务 (默认端口: 1234)
- 加载模型: `qwen2-0.5b-instruct`

### 4. 启动后端服务
```bash
python start_server.py --mode dev
```

### 5. 前端设置
```bash
cd frontend
npm install
npm run dev
```

### 6. 访问应用
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
NewsMind/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API接口
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   └── services/       # 业务服务
│   ├── start_server.py     # 启动脚本
│   └── requirements.txt    # 依赖列表
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   └── router/         # 路由配置
│   └── package.json
└── docs/                   # 项目文档
```

## API 接口

### 新闻相关
- `GET /api/v1/news/articles` - 获取新闻列表
- `GET /api/v1/news/articles/{id}` - 获取新闻详情
- `GET /api/v1/news/statistics` - 获取统计信息
- `POST /api/v1/news/crawl` - 手动抓取新闻

### AI 处理
- `POST /api/v1/ai/translate` - 批量翻译
- `POST /api/v1/ai/translate/{id}` - 翻译单篇
- `GET /api/v1/ai/untranslated-count` - 未翻译数量
- `POST /api/v1/ai/trigger-translation` - 手动触发翻译

## 配置说明

### 环境变量
```bash
# 数据库配置
DATABASE_URL=sqlite:///./newsmind.db

# 开发模式
DEBUG=true
```

### LM Studio 配置
- **服务地址**: http://127.0.0.1:1234
- **模型名称**: qwen2-0.5b-instruct
- **超时设置**: 30秒

## 定时任务

系统自动运行以下定时任务：
- **新闻抓取**: 每6小时自动抓取
- **AI翻译**: 每10分钟处理未翻译新闻
- **数据清理**: 每天凌晨2点清理旧数据

## 开发指南

### 添加新闻源
1. 在数据库中添加新闻源记录
2. 配置 RSS URL 或网页地址
3. 设置分类和状态

### 自定义AI模型
1. 在 LM Studio 中加载新模型
2. 修改 `ai_processor.py` 中的模型名称
3. 重启后端服务

### 前端开发
```bash
cd frontend
npm run dev          # 开发模式
npm run build        # 构建生产版本
npm run preview      # 预览构建结果
```

## 部署

### Docker 部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 生产环境
1. 设置 `DEBUG=false`
2. 配置生产数据库
3. 使用 nginx 反向代理
4. 配置 SSL 证书

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。 