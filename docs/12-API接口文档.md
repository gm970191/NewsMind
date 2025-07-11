# NewsMind API接口文档

## 📋 接口概述

NewsMind提供RESTful API接口，支持新闻数据的增删改查、AI处理、统计分析等功能。

## 🔗 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **认证方式**: 暂无需认证

## 📰 新闻相关接口

### 1. 获取新闻列表

**接口地址**: `GET /news/articles`

**请求参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| skip | integer | 否 | 0 | 跳过数量 |
| limit | integer | 否 | 20 | 返回数量 (1-100) |
| category | string | 否 | - | 分类筛选 |
| language | string | 否 | - | 语言筛选 (zh/en) |
| is_processed | boolean | 否 | - | 处理状态筛选 |
| date | string | 否 | - | 日期筛选 (today/yesterday/week/month) |
| order_by | string | 否 | created_at | 排序字段 |
| order_desc | boolean | 否 | true | 是否降序 |

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/news/articles?limit=10&category=科技&language=zh"
```

**响应示例**:
```json
{
  "articles": [
    {
      "id": 1,
      "original_title": "AI Breakthrough in Natural Language Processing",
      "translated_title": "自然语言处理领域的AI突破",
      "original_content": "Scientists have made significant progress...",
      "translated_content": "科学家们在自然语言处理领域取得了重大进展...",
      "summary_zh": "研究人员开发出新的AI模型，在自然语言理解方面表现优异。",
      "detailed_summary_zh": "最新研究显示，新型AI模型在多个NLP基准测试中超越了现有最佳模型...",
      "original_language": "en",
      "source_url": "https://example.com/article1",
      "source_id": 1,
      "source_name": "TechNews",
      "category": "科技",
      "quality_score": 8.5,
      "is_processed": true,
      "created_at": "2025-07-11T10:30:00Z",
      "updated_at": "2025-07-11T10:35:00Z"
    }
  ],
  "total": 100,
  "skip": 0,
  "limit": 10
}
```

### 2. 获取新闻详情

**接口地址**: `GET /news/articles/{id}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 新闻文章ID |

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/news/articles/123"
```

**响应示例**:
```json
{
  "id": 123,
  "original_title": "Global Economic Trends 2025",
  "translated_title": "2025年全球经济趋势",
  "original_content": "The global economy is experiencing...",
  "translated_content": "全球经济正在经历...",
  "summary_zh": "2025年全球经济面临多重挑战，但新兴市场展现活力。",
  "detailed_summary_zh": "根据最新经济数据，2025年全球经济将呈现复杂态势...",
  "original_language": "en",
  "source_url": "https://example.com/article123",
  "source_id": 2,
  "source_name": "EconomicDaily",
  "publish_time": "2025-07-11T08:00:00Z",
  "category": "财经",
  "quality_score": 9.0,
  "translation_quality_score": 8.8,
  "is_processed": true,
  "is_title_translated": true,
  "is_content_translated": true,
  "created_at": "2025-07-11T10:30:00Z",
  "updated_at": "2025-07-11T10:35:00Z"
}
```

### 3. 获取新闻源列表

**接口地址**: `GET /news/sources`

**请求参数**: 无

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/news/sources"
```

**响应示例**:
```json
{
  "sources": [
    {
      "id": 1,
      "name": "CNN",
      "url": "http://rss.cnn.com/rss/edition.rss",
      "type": "rss",
      "category": "国际",
      "weight": 1.0,
      "is_active": true,
      "created_at": "2025-07-01T00:00:00Z",
      "updated_at": "2025-07-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "TechCrunch",
      "url": "http://feeds.feedburner.com/TechCrunch/",
      "type": "rss",
      "category": "科技",
      "weight": 1.0,
      "is_active": true,
      "created_at": "2025-07-01T00:00:00Z",
      "updated_at": "2025-07-01T00:00:00Z"
    }
  ],
  "total": 2
}
```

### 4. 获取统计信息

**接口地址**: `GET /news/statistics`

**请求参数**: 无

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/news/statistics"
```

**响应示例**:
```json
{
  "total_articles": 100,
  "processed_articles": 80,
  "unprocessed_articles": 20,
  "total_sources": 10,
  "processing_rate": 80.0
}
```

## 🤖 AI处理相关接口

### 1. 批量处理新闻

**接口地址**: `POST /ai/process`

**请求参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| limit | integer | 否 | 10 | 处理数量 (1-50) |

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/ai/process" \
  -H "Content-Type: application/json" \
  -d '{"limit": 5}'
```

**响应示例**:
```json
{
  "message": "AI processing completed",
  "results": {
    "total_articles": 5,
    "success_count": 4,
    "error_count": 1,
    "api_calls": 12
  }
}
```

### 2. 处理单篇新闻

**接口地址**: `POST /ai/process/{id}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 新闻文章ID |

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/ai/process/123"
```

**响应示例**:
```json
{
  "message": "Article 123 processed successfully"
}
```

### 3. 获取AI处理统计

**接口地址**: `GET /ai/statistics`

**请求参数**: 无

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/ai/statistics"
```

**响应示例**:
```json
{
  "ai_processing_statistics": {
    "total_processed": 80,
    "average_quality_score": 7.8,
    "average_processing_time": 2.5,
    "quality_distribution": [
      {
        "score_range": 7,
        "count": 25
      },
      {
        "score_range": 8,
        "count": 30
      },
      {
        "score_range": 9,
        "count": 15
      }
    ],
    "category_statistics": [
      {
        "category": "科技",
        "processed_count": 30
      },
      {
        "category": "国际",
        "processed_count": 25
      },
      {
        "category": "财经",
        "processed_count": 15
      }
    ]
  }
}
```

### 4. 获取未处理数量

**接口地址**: `GET /ai/unprocessed-count`

**请求参数**: 无

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/ai/unprocessed-count"
```

**响应示例**:
```json
{
  "unprocessed_count": 20
}
```

### 5. 获取文章处理状态

**接口地址**: `GET /ai/article-status/{id}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 新闻文章ID |

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/ai/article-status/123"
```

**响应示例**:
```json
{
  "article_id": 123,
  "original_title": "Global Economic Trends 2025",
  "translated_title": "2025年全球经济趋势",
  "display_title": "2025年全球经济趋势",
  "original_language": "en",
  "is_processed": true,
  "has_summary_zh": true,
  "has_detailed_summary_zh": true,
  "has_translation": true,
  "needs_summary": false,
  "needs_translation": false,
  "needs_processing": false
}
```

## 🔍 搜索接口

### 搜索新闻

**接口地址**: `GET /news/search`

**请求参数**:
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| keyword | string | 是 | - | 搜索关键词 |
| limit | integer | 否 | 50 | 返回数量 |

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/news/search?keyword=AI&limit=10"
```

**响应示例**:
```json
{
  "articles": [
    {
      "id": 1,
      "original_title": "AI Breakthrough in Natural Language Processing",
      "translated_title": "自然语言处理领域的AI突破",
      "summary_zh": "研究人员开发出新的AI模型...",
      "category": "科技",
      "created_at": "2025-07-11T10:30:00Z"
    }
  ],
  "total": 5,
  "keyword": "AI"
}
```

## 📊 高级统计接口

### 获取处理统计详情

**接口地址**: `GET /news/processing-statistics`

**请求参数**: 无

**请求示例**:
```bash
curl "http://localhost:8000/api/v1/news/processing-statistics"
```

**响应示例**:
```json
{
  "total_processed": 80,
  "average_quality_score": 7.8,
  "average_processing_time": 2.5,
  "quality_distribution": [
    {
      "score_range": 7,
      "count": 25
    },
    {
      "score_range": 8,
      "count": 30
    },
    {
      "score_range": 9,
      "count": 15
    }
  ],
  "category_statistics": [
    {
      "category": "科技",
      "processed_count": 30
    },
    {
      "category": "国际",
      "processed_count": 25
    },
    {
      "category": "财经",
      "processed_count": 15
    }
  ],
  "language_statistics": [
    {
      "language": "en",
      "count": 60
    },
    {
      "language": "zh",
      "count": 20
    }
  ]
}
```

## ⚠️ 错误处理

### 错误响应格式
```json
{
  "detail": "错误描述信息",
  "status_code": 400,
  "timestamp": "2025-07-11T10:30:00Z"
}
```

### 常见错误码
| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 参数验证失败 |
| 500 | 服务器内部错误 |

### 错误响应示例
```json
{
  "detail": "Article with id 999 not found",
  "status_code": 404,
  "timestamp": "2025-07-11T10:30:00Z"
}
```

## 🔧 使用示例

### JavaScript/Node.js
```javascript
const axios = require('axios');

// 获取新闻列表
async function getArticles() {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/news/articles', {
      params: {
        limit: 10,
        category: '科技',
        language: 'zh'
      }
    });
    console.log(response.data);
  } catch (error) {
    console.error('获取新闻失败:', error.response.data);
  }
}

// 处理单篇新闻
async function processArticle(id) {
  try {
    const response = await axios.post(`http://localhost:8000/api/v1/ai/process/${id}`);
    console.log(response.data);
  } catch (error) {
    console.error('处理新闻失败:', error.response.data);
  }
}
```

### Python
```python
import requests

# 获取新闻列表
def get_articles():
    try:
        response = requests.get('http://localhost:8000/api/v1/news/articles', params={
            'limit': 10,
            'category': '科技',
            'language': 'zh'
        })
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'获取新闻失败: {e}')
        return None

# 处理单篇新闻
def process_article(article_id):
    try:
        response = requests.post(f'http://localhost:8000/api/v1/ai/process/{article_id}')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'处理新闻失败: {e}')
        return None
```

### cURL
```bash
# 获取新闻列表
curl "http://localhost:8000/api/v1/news/articles?limit=10&category=科技"

# 获取单篇新闻
curl "http://localhost:8000/api/v1/news/articles/123"

# 处理新闻
curl -X POST "http://localhost:8000/api/v1/ai/process/123"

# 获取统计信息
curl "http://localhost:8000/api/v1/news/statistics"
```

## 📝 注意事项

1. **请求频率限制**: 建议控制请求频率，避免对服务器造成过大压力
2. **参数验证**: 请确保请求参数符合接口要求
3. **错误处理**: 请妥善处理各种错误情况
4. **数据格式**: 所有请求和响应均使用JSON格式
5. **时区**: 时间字段使用UTC时区

## 🔄 版本更新

- **v0.5.0**: 新增AI处理相关接口，优化新闻查询接口
- **v0.4.0**: 修复中文显示问题，完善错误处理
- **v0.3.0**: 重构数据模型，删除processed_content表

---

如有疑问或需要技术支持，请提交Issue或联系开发团队。 