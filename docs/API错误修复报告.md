# API错误修复报告

## 🚨 问题描述

用户反馈前端页面出现500错误：
```
GET http://localhost:3000/api/v1/news/articles?skip=0&limit=20&category=%E5%9B%BD%E9%99%85%E6%96%B0%E9%97%BB&date=today 500 (INTERNAL SERVER ERROR)
```

错误信息：`{"error":"ambiguous column name: created_at"}`

## 🔍 问题分析

### 根本原因
1. **JOIN查询中的字段冲突**：`news_articles`和`processed_content`两个表都有`created_at`字段
2. **缺少表别名**：在JOIN查询中没有明确指定字段来源的表
3. **前端传递了后端未处理的参数**：前端传递了`date`参数，但后端API没有处理

### 影响范围
- `/api/v1/news/articles` - 新闻列表API
- `/api/v1/ai/processed-articles` - 已处理文章API
- 所有涉及JOIN查询的数据库操作

## 🛠️ 修复方案

### 1. 修复后端API参数支持

**文件**: `backend/app/api/news.py`
```python
@router.get("/articles")
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    source_id: Optional[int] = None,
    language: Optional[str] = None,
    is_processed: Optional[bool] = None,
    date: Optional[str] = None,  # 新增日期参数
    order_by: str = Query("created_at", regex="^(created_at|publish_time|title)$"),
    order_desc: bool = Query(True)
):
```

### 2. 修复NewsRepository中的日期筛选

**文件**: `backend/app/services/news_service.py`
```python
def get_articles(
    self,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    source_id: Optional[int] = None,
    language: Optional[str] = None,
    is_processed: Optional[bool] = None,
    date: Optional[str] = None,  # 新增日期参数
    order_by: str = "created_at",
    order_desc: bool = True
) -> List[NewsArticle]:
    
    # 添加日期筛选逻辑
    if date:
        from datetime import datetime, timedelta
        from sqlalchemy import func
        today = datetime.utcnow().date()
        if date == "today":
            query = query.filter(func.date(NewsArticle.created_at) == today)
        elif date == "yesterday":
            yesterday = today - timedelta(days=1)
            query = query.filter(func.date(NewsArticle.created_at) == yesterday)
        elif date == "week":
            week_ago = today - timedelta(days=7)
            query = query.filter(NewsArticle.created_at >= week_ago)
        elif date == "month":
            month_ago = today - timedelta(days=30)
            query = query.filter(NewsArticle.created_at >= month_ago)
```

### 3. 修复JOIN查询中的ambiguous column错误

**文件**: `backend/app/services/news_service.py`

#### 修复get_processed_articles_with_content方法
```python
def get_processed_articles_with_content(
    self,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    min_quality: Optional[float] = None
) -> List[Dict[str, Any]]:
    """获取已处理且包含处理结果的文章"""
    query = self.db.query(NewsArticle, ProcessedContent).join(
        ProcessedContent, NewsArticle.id == ProcessedContent.article_id
    )
    
    if category:
        query = query.filter(NewsArticle.category == category)
    if min_quality:
        query = query.filter(ProcessedContent.quality_score >= min_quality)
    
    # 明确指定排序字段，避免ambiguous column错误
    results = query.order_by(desc(NewsArticle.created_at)).offset(skip).limit(limit).all()
    
    return [
        {
            'article': article,
            'processed_content': content
        }
        for article, content in results
    ]
```

#### 修复get_processing_statistics方法
```python
def get_processing_statistics(self) -> Dict[str, Any]:
    """获取AI处理统计信息"""
    # ... 其他代码 ...
    
    # 按分类统计 - 明确指定字段避免ambiguous column错误
    category_stats = self.db.query(
        NewsArticle.category,
        func.count(ProcessedContent.id).label('processed_count')
    ).join(ProcessedContent, NewsArticle.id == ProcessedContent.article_id).group_by(
        NewsArticle.category
    ).all()
```

### 4. 修复简化服务器中的SQL查询

**文件**: `backend/start_server.py`

#### 修复where_conditions中的字段别名
```python
# 构建查询条件
where_conditions = []
params = []

if category:
    where_conditions.append("na.category = ?")  # 添加表别名
    params.append(category)

if language:
    where_conditions.append("na.language = ?")  # 添加表别名
    params.append(language)

# 添加日期筛选
if date_filter:
    if date_filter == 'today':
        where_conditions.append("DATE(na.created_at) = DATE('now')")  # 添加表别名
    elif date_filter == 'yesterday':
        where_conditions.append("DATE(na.created_at) = DATE('now', '-1 day')")  # 添加表别名
    elif date_filter == 'week':
        where_conditions.append("DATE(na.created_at) >= DATE('now', '-7 days')")  # 添加表别名
    elif date_filter == 'month':
        where_conditions.append("DATE(na.created_at) >= DATE('now', '-30 days')")  # 添加表别名
    else:
        try:
            from datetime import datetime
            datetime.strptime(date_filter, '%Y-%m-%d')
            where_conditions.append("DATE(na.created_at) = ?")  # 添加表别名
            params.append(date_filter)
        except ValueError:
            pass
```

## ✅ 验证结果

### 测试项目
1. ✅ 基本查询 - 成功返回5篇文章
2. ✅ 带分类查询 - 成功返回5篇文章
3. ✅ 带日期筛选查询 - 成功返回0篇文章（今日无新文章）
4. ✅ 已处理文章查询 - 成功返回0篇文章
5. ✅ 统计查询 - 成功返回5个统计项
6. ✅ JOIN查询修复 - 成功返回5篇文章
7. ✅ 日期筛选查询 - 成功返回0篇文章

### 修复效果
- **消除了ambiguous column错误**
- **支持了前端传递的date参数**
- **所有JOIN查询正常工作**
- **数据库查询性能正常**

## 📋 修复清单

- [x] 修复`get_articles`方法中的date参数支持
- [x] 修复`get_processed_articles_with_content`方法中的ambiguous column错误
- [x] 修复`get_processing_statistics`方法中的ambiguous column错误
- [x] 修复简化服务器中的SQL查询字段别名问题
- [x] 添加完整的测试验证
- [x] 创建修复报告文档

## 🎯 总结

本次修复解决了前端页面500错误的核心问题：
1. **数据库层面**：修复了JOIN查询中的字段冲突问题
2. **API层面**：增加了对前端传递参数的完整支持
3. **兼容性**：保持了与现有功能的完全兼容

修复后，前端页面可以正常使用分类筛选和日期筛选功能，不再出现500错误。

## 📅 修复时间
2025-07-10 