# 环境变量配置说明

## 🔐 API密钥安全配置

为了保护您的API密钥安全，请按照以下步骤配置环境变量：

### 1. 创建.env文件

在 `backend/` 目录下创建 `.env` 文件，内容如下：

```bash
# DeepSeek API配置
# 请从 https://platform.deepseek.com/ 获取您的API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 数据库配置
DATABASE_URL=sqlite:///./newsmind.db

# 应用配置
DEBUG=true
LOG_LEVEL=INFO

# CORS配置 - 允许的前端域名
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# 新闻采集配置
MAX_ARTICLES_PER_SOURCE=20
CONTENT_RETENTION_DAYS=30

# AI处理配置
MAX_PROCESSING_BATCH_SIZE=10
PROCESSING_DELAY_SECONDS=1
```

### 2. 获取DeepSeek API密钥

1. 访问 [DeepSeek Platform](https://platform.deepseek.com/)
2. 注册或登录您的账户
3. 在控制台中创建新的API密钥
4. 将API密钥复制到 `.env` 文件的 `DEEPSEEK_API_KEY` 字段

### 3. 安全注意事项

- ✅ `.env` 文件已添加到 `.gitignore`，不会被提交到Git
- ✅ 不要在代码中硬编码API密钥
- ✅ 不要将 `.env` 文件分享给他人
- ✅ 定期轮换您的API密钥

### 4. 验证配置

启动服务器时，如果API密钥未正确配置，会显示错误信息：

```
ValueError: DEEPSEEK_API_KEY 环境变量未设置。请在 .env 文件中设置您的 API 密钥。
```

### 5. 生产环境部署

在生产环境中，请：

1. 使用环境变量而不是文件
2. 设置 `DEBUG=false`
3. 配置适当的 `CORS_ORIGINS`
4. 使用生产级数据库

## 🚀 快速开始

1. 复制上述配置到 `backend/.env` 文件
2. 替换 `your_deepseek_api_key_here` 为您的实际API密钥
3. 启动服务器：`python start_server.py --mode simple`

## 📝 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | 必需 |
| `DATABASE_URL` | 数据库连接URL | sqlite:///./newsmind.db |
| `DEBUG` | 调试模式 | true |
| `LOG_LEVEL` | 日志级别 | INFO |
| `CORS_ORIGINS` | 允许的跨域来源 | ["http://localhost:3000"] |
| `MAX_ARTICLES_PER_SOURCE` | 每个源的最大文章数 | 20 |
| `CONTENT_RETENTION_DAYS` | 内容保留天数 | 30 |
| `MAX_PROCESSING_BATCH_SIZE` | AI处理批次大小 | 10 |
| `PROCESSING_DELAY_SECONDS` | 处理延迟秒数 | 1 | 