<template>
  <el-card 
    class="news-card" 
    :body-style="{ padding: '0px' }"
    @click="$emit('click')"
    hover
  >
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="source-info">
        <span class="source-name">{{ article.source_name }}</span>
        <el-tag 
          :type="getCategoryType(article.category)" 
          size="small"
          class="category-tag"
        >
          {{ article.category }}
        </el-tag>
      </div>
      <div class="time-info">
        {{ formatTime(article.created_at) }}
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <h3 class="article-title">{{ article.title }}</h3>
      
      <!-- 摘要内容 -->
      <div v-if="article.ai_processing" class="summary-section">
        <div class="summary-tabs">
          <el-tabs v-model="activeTab" size="small">
            <el-tab-pane label="中文摘要" name="zh">
              <div class="summary-content">
                {{ article.ai_processing.summary_zh }}
              </div>
            </el-tab-pane>
            <el-tab-pane label="英文摘要" name="en">
              <div class="summary-content">
                {{ article.ai_processing.summary_en }}
              </div>
            </el-tab-pane>
            <el-tab-pane label="原文" name="original">
              <div class="summary-content">
                {{ truncateContent(article.content) }}
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <!-- 质量评分 -->
        <div class="quality-score">
          <el-rate 
            v-model="qualityScore" 
            disabled 
            show-score 
            text-color="#ff9900"
            score-template="{value}"
          />
        </div>
      </div>
      
      <!-- 未处理状态 -->
      <div v-else class="unprocessed-content">
        <p class="content-preview">{{ truncateContent(article.content) }}</p>
        <el-tag type="warning" size="small">待AI处理</el-tag>
      </div>
    </div>

    <!-- 卡片底部 -->
    <div class="card-footer">
      <div class="footer-left">
        <el-button 
          link
          size="small" 
          @click.stop="handleViewDetail"
        >
          查看详情
        </el-button>
        <el-button 
          v-if="article.source_url" 
          link
          size="small" 
          @click.stop="handleViewOriginal"
        >
          原文链接
        </el-button>
      </div>
      <div class="footer-right">
        <el-button 
          v-if="!article.ai_processing" 
          type="primary" 
          size="small" 
          @click.stop="handleProcess"
          :loading="processing"
        >
          立即处理
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useNewsStore } from '../stores/news'

const props = defineProps({
  article: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])

const router = useRouter()
const newsStore = useNewsStore()

// 响应式数据
const activeTab = ref('zh')
const processing = ref(false)

// 计算属性
const qualityScore = computed(() => {
  if (props.article.ai_processing?.quality_score) {
    return props.article.ai_processing.quality_score / 2 // 转换为5分制
  }
  return 0
})

// 方法
const getCategoryType = (category) => {
  const typeMap = {
    '国际新闻': 'primary',
    '科技': 'success',
    '财经': 'warning',
    '体育': 'info'
  }
  return typeMap[category] || 'info'
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}

const truncateContent = (content, maxLength = 150) => {
  if (!content) return ''
  return content.length > maxLength 
    ? content.substring(0, maxLength) + '...' 
    : content
}

const handleViewDetail = () => {
  router.push(`/article/${props.article.id}`)
}

const handleViewOriginal = () => {
  if (props.article.source_url) {
    window.open(props.article.source_url, '_blank')
  }
}

const handleProcess = async () => {
  processing.value = true
  try {
    await newsStore.processArticles(1)
    ElMessage.success('AI处理完成')
    // 刷新数据
    await newsStore.fetchArticles()
  } catch (error) {
    ElMessage.error('AI处理失败')
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.news-card {
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.news-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  background-color: #fafafa;
}

.source-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.source-name {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.category-tag {
  font-size: 10px;
}

.time-info {
  font-size: 11px;
  color: #999;
}

.card-content {
  padding: 16px;
  flex: 1;
}

.article-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.summary-section {
  margin-top: 12px;
}

.summary-tabs {
  margin-bottom: 12px;
}

.summary-content {
  font-size: 13px;
  line-height: 1.5;
  color: #666;
  max-height: 80px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.quality-score {
  text-align: center;
  margin-top: 8px;
}

.unprocessed-content {
  margin-top: 12px;
}

.content-preview {
  font-size: 13px;
  line-height: 1.5;
  color: #666;
  margin-bottom: 8px;
  max-height: 60px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-footer {
  padding: 12px 16px;
  border-top: 1px solid #f0f0f0;
  background-color: #fafafa;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  gap: 8px;
}

.footer-right {
  display: flex;
  gap: 8px;
}

:deep(.el-tabs__header) {
  margin-bottom: 8px;
}

:deep(.el-tabs__nav-wrap) {
  padding: 0;
}

:deep(.el-tabs__item) {
  font-size: 12px;
  padding: 0 8px;
}

:deep(.el-tabs__content) {
  padding: 0;
}
</style> 