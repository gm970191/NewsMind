<template>
  <div class="article-detail">
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-content">
        <el-button @click="goBack" :icon="ArrowLeft" plain>
          返回
        </el-button>
        <h1 class="page-title">文章详情</h1>
        <div class="header-actions">
          <el-button 
            v-if="article && article.source_url" 
            type="primary" 
            @click="openOriginal"
            :icon="Link"
          >
            原文链接
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容 -->
    <el-main class="main-content" v-loading="loading">
      <div v-if="article" class="article-container">
        <!-- 文章头部信息 -->
        <div class="article-header">
          <div class="article-meta">
            <span class="source-name">{{ article.source_name }}</span>
            <span class="category-tag" v-if="article.category">{{ article.category }}</span>
            <span class="publish-time">{{ formatTime(article.created_at) }}</span>
          </div>
          
          <!-- 翻译状态 -->
          <div class="translation-status" v-if="article.is_translated">
            <el-tag type="success">
              <el-icon><Check /></el-icon>
              已翻译
            </el-tag>
          </div>
        </div>

        <!-- 文章内容 -->
        <div class="article-content">
          <!-- 中文内容 -->
          <div v-if="article.translated_title || article.translated_summary" class="content-section chinese-content">
            <h2 class="section-title">
              <el-icon><ChatDotRound /></el-icon>
              中文内容
            </h2>
            
            <h1 class="article-title">{{ article.translated_title }}</h1>
            <div class="article-summary">{{ article.translated_summary }}</div>
          </div>

          <!-- 原文内容 -->
          <div class="content-section original-content">
            <h2 class="section-title">
              <el-icon><Document /></el-icon>
              原文内容
            </h2>
            
            <h1 class="article-title">{{ article.original_title }}</h1>
            <div class="article-summary">{{ article.original_summary }}</div>
          </div>
        </div>
      </div>

      <!-- 加载失败 -->
      <el-empty 
        v-else-if="!loading" 
        description="文章不存在或已被删除"
      >
        <el-button type="primary" @click="goBack">返回首页</el-button>
      </el-empty>
    </el-main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Link, Check, ChatDotRound, Document } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const article = ref(null)
const loading = ref(true)

// 方法
const fetchArticle = async () => {
  const articleId = route.params.id
  
  if (!articleId) {
    ElMessage.error('文章ID无效')
    goBack()
    return
  }

  loading.value = true
  try {
    const response = await fetch(`/api/v1/news/articles/${articleId}`)
    
    if (response.ok) {
      article.value = await response.json()
    } else if (response.status === 404) {
      article.value = {} // 兜底，防止为 null
      ElMessage.error('文章不存在')
    } else {
      article.value = {} // 兜底，防止为 null
      ElMessage.error('获取文章失败')
    }
  } catch (error) {
    article.value = {} // 兜底，防止为 null
    ElMessage.error('获取文章失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

const goBack = () => {
  router.push('/')
}

const openOriginal = () => {
  if (article.value?.source_url) {
    window.open(article.value.source_url, '_blank')
  }
}

// 生命周期
onMounted(() => {
  fetchArticle()
})
</script>

<style scoped>
.article-detail {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.article-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.article-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.source-name {
  font-weight: 600;
  color: #409eff;
}

.category-tag {
  background: #409eff;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.publish-time {
  color: #666;
  font-size: 14px;
}

.translation-status {
  display: flex;
  align-items: center;
}

.article-content {
  padding: 0;
}

.content-section {
  padding: 30px;
  border-bottom: 1px solid #e4e7ed;
}

.content-section:last-child {
  border-bottom: none;
}

.chinese-content {
  background: #f8fff8;
}

.original-content {
  background: #f8f9fa;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.chinese-content .section-title {
  color: #67c23a;
  border-bottom-color: #67c23a;
}

.article-title {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.3;
  color: #303133;
  margin: 0 0 20px 0;
}

.article-summary {
  font-size: 16px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 10px;
  }
  
  .article-header {
    padding: 15px;
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .content-section {
    padding: 20px;
  }
  
  .article-title {
    font-size: 20px;
  }
  
  .article-summary {
    font-size: 14px;
  }
}
</style> 