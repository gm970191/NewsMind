# NewsMind API 接口文档

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API前缀**: `/api/v1`
- **内容类型**: `application/json`

## 认证

当前版本无需认证，所有接口均可直接访问。

## 新闻相关接口

### 1. 获取新闻列表

**接口**: `GET /api/v1/news/articles`

**参数**:
- `limit` (可选): 每页数量，默认20，最大100
- `skip` (可选): 跳过数量，默认0

**响应示例**:
```json
{
  "articles": [
    {
      "id": 1,
      "original_title": "Original Title",
      "original_summary": "Original summary...",
      "translated_title": "翻译标题",
      "translated_summary": "翻译摘要...",
      "source_name": "Wired",
      "source_url": "https://example.com/article",
      "category": "科技",
      "is_translated": true,
      "created_at": "2025-07-13T10:00:00"
    }
  ]
}
```

### 2. 获取新闻详情

**接口**: `GET /api/v1/news/articles/{id}`

**参数**:
- `id` (路径参数): 新闻ID

**响应示例**:
```json
{
  "id": 1,
  "original_title": "Original Title",
  "original_summary": "Original summary...",
  "translated_title": "翻译标题",
  "translated_summary": "翻译摘要...",
  "source_name": "Wired",
  "source_url": "https://example.com/article",
  "category": "科技",
  "is_translated": true,
  "created_at": "2025-07-13T10:00:00"
}
```

### 3. 获取统计信息

**接口**: `GET /api/v1/news/statistics`

**响应示例**:
```json
{
  "total_articles": 100,
  "translated_articles": 80,
  "untranslated_articles": 20,
  "total_sources": 5
}
```

### 4. 手动抓取新闻

**接口**: `POST /api/v1/news/crawl`

**响应示例**:
```json
{
  "message": "News crawling completed",
  "new_articles": 15
}
```

## AI 处理接口

### 1. 批量翻译

**接口**: `POST /api/v1/ai/translate`

**参数**:
- `limit` (可选): 翻译数量限制，默认10，最大50

**响应示例**:
```json
{
  "message": "AI translation completed",
  "results": {
    "total_articles": 10,
    "success_count": 8,
    "error_count": 2
  }
}
```

### 2. 翻译单篇新闻

**接口**: `POST /api/v1/ai/translate/{id}`

**参数**:
- `id` (路径参数): 新闻ID

**响应示例**:
```json
{
  "message": "Article 1 translated successfully"
}
```

### 3. 获取未翻译数量

**接口**: `GET /api/v1/ai/untranslated-count`

**响应示例**:
```json
{
  "untranslated_count": 25
}
```

### 4. 手动触发翻译

**接口**: `POST /api/v1/ai/trigger-translation`

**响应示例**:
```json
{
  "message": "AI translation triggered successfully",
  "note": "Check logs for detailed results"
}
```

## 错误响应

### 400 Bad Request
```json
{
  "detail": "Invalid parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Article not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Translation failed: Connection timeout"
}
```

## 状态码说明

- `200`: 请求成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 使用示例

### JavaScript (Fetch API)
```javascript
// 获取新闻列表
const response = await fetch('/api/v1/news/articles?limit=10');
const data = await response.json();

// 翻译新闻
const translateResponse = await fetch('/api/v1/ai/translate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ limit: 5 })
});
```

### Python (requests)
```python
import requests

# 获取新闻列表
response = requests.get('http://localhost:8000/api/v1/news/articles')
articles = response.json()

# 翻译新闻
response = requests.post('http://localhost:8000/api/v1/ai/translate', 
                        json={'limit': 5})
result = response.json()
```

### cURL
```bash
# 获取新闻列表
curl -X GET "http://localhost:8000/api/v1/news/articles?limit=10"

# 翻译新闻
curl -X POST "http://localhost:8000/api/v1/ai/translate" \
     -H "Content-Type: application/json" \
     -d '{"limit": 5}'
```

## 注意事项

1. **AI翻译依赖**: 需要本地 LM Studio 服务运行在 `http://127.0.0.1:1234`
2. **超时设置**: AI翻译接口超时时间为30秒
3. **并发限制**: 建议同时翻译数量不超过10篇
4. **数据格式**: 所有时间字段使用 ISO 8601 格式

## 更新日志

### v1.0.0 (2025-07-13)
- 移除 DeepSeek API 依赖
- 仅支持本地 LM Studio AI 服务
- 简化配置和部署流程 