# NewsMind 自动更新设置

## 自动更新方案

### 方案1: 使用启动脚本（推荐）
```bash
python start_news_system.py
```
这个脚本会自动启动：
- 后端服务 (http://localhost:8000)
- 前端服务 (http://localhost:3000)
- 新闻采集调度器（每6小时执行一次）

### 方案2: 手动运行新闻采集
```bash
python scripts/simple_news_crawler.py
```

### 方案3: 使用Windows计划任务
1. 运行 `python scripts/setup_auto_update.py` 创建计划任务
2. 系统会自动每6小时执行一次新闻采集

## 服务地址
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- 健康检查: http://localhost:8000/health

## 新闻采集频率
- 默认: 每6小时执行一次
- 可手动执行: `python scripts/simple_news_crawler.py`

## 故障排除
1. 如果新闻采集失败，系统会自动创建测试数据
2. 检查日志文件了解详细错误信息
3. 确保网络连接正常

## 停止服务
- 按 Ctrl+C 停止所有服务
- 或分别停止各个进程
