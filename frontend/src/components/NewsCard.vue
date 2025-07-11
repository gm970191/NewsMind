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
        <div class="source-left">
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
          <span class="collect-date">收集: {{ formatDate(article.created_at) }}</span>
          <span v-if="article.publish_time" class="publish-date">发布: {{ formatDate(article.publish_time) }}</span>
        </div>
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <h3 class="article-title">
        {{ getDisplayTitle() }}
        <span v-if="article.original_language !== 'zh' && article.original_title && article.translated_title" class="origin-title" style="font-size:13px;color:#888;margin-left:6px;">（{{ article.original_title }}）</span>
      </h3>
      <!-- 显示中文概要或原文预览 -->
      <div v-if="article.processed_content && article.processed_content.summary_zh" class="summary-section">
        <div class="summary-content">
          {{ article.processed_content.summary_zh }}
        </div>
      </div>
      <!-- 未处理文章显示原文预览 -->
      <div v-else-if="article.translated_content || article.original_content" class="unprocessed-content">
        <div class="content-preview">
          {{ truncateContent(article.translated_content || article.original_content, 200) }}
        </div>
      </div>
      
      <!-- 质量评分 -->
      <div v-if="(article.processed_content && article.processed_content.quality_score) || article.translation_quality_score" class="quality-score">
        <el-rate 
          :model-value="qualityScore" 
          disabled 
          show-score 
          text-color="#ff9900"
          score-template="{value}"
        />
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
          v-if="!article.is_processed" 
          type="primary" 
          size="small" 
          @click.stop="handleProcess"
          :loading="processing"
        >
          AI总结
        </el-button>
        <el-button 
          v-else
          type="info" 
          size="small" 
          disabled
        >
          AI总结
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useNewsStore } from '../stores/news'

const props = defineProps({
  article: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'refresh'])

const router = useRouter()
const newsStore = useNewsStore()

// 响应式数据
const activeTab = ref('zh')
const processing = ref(false)

// 监听文章变化，设置默认标签页
watch(() => props.article, (newArticle) => {
  if (newArticle) {
    // 如果是非中文新闻且有翻译，默认显示翻译
    if (newArticle.original_language !== 'zh' && newArticle.translated_content) {
      activeTab.value = 'translation'
    } else {
      activeTab.value = 'zh'
    }
  }
}, { immediate: true })

// 计算属性
const qualityScore = computed(() => {
  if (props.article.processed_content?.quality_score) {
    return props.article.processed_content.quality_score / 2 // 转换为5分制
  }
  if (props.article.translation_quality_score) {
    return props.article.translation_quality_score / 2 // 转换为5分制
  }
  return 0
})

// 方法
const getCategoryType = (category) => {
  const typeMap = {
    '科技': 'success',
    '财经': 'warning',
    '军事': 'danger',
    '政治': 'primary',
    '国际': 'info',
    '其他': 'info'
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

const formatDate = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleDateString()
}

const truncateContent = (content, maxLength = 300) => {
  if (!content) return ''
  return content.length > maxLength 
    ? content.substring(0, maxLength) + '...' 
    : content
}

const getDisplayTitle = () => {
  // 优先显示中文翻译标题，如果没有则显示原文
  if (props.article.translated_title) {
    return props.article.translated_title
  }
  return props.article.original_title
}

const handleViewDetail = () => {
  // 验证文章ID是否有效
  if (!props.article.id || props.article.id <= 0) {
    ElMessage.error('文章ID无效')
    return
  }
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
    // 调用单篇文章处理API
    const response = await fetch(`/api/v1/ai/process/${props.article.id}`, {
      method: 'POST'
    })
    
    if (response.ok) {
      ElMessage.success('AI处理完成')
      // 触发父组件刷新数据
      emit('refresh')
    } else {
      ElMessage.error('AI处理失败')
    }
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

.source-left {
  display: flex;
  align-items: center;
  gap: 8px;
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
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #999;
}

.collect-date, .publish-date {
  font-size: 10px;
  color: #666;
}

.collect-date {
  color: #409eff;
  font-weight: 500;
}

.publish-date {
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
  line-height: 1.6;
  color: #666;
  max-height: 200px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 8;
  -webkit-box-orient: vertical;
  margin-bottom: 8px;
  white-space: pre-wrap;
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
  line-height: 1.6;
  color: #666;
  margin-bottom: 8px;
  max-height: 150px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 5;
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

.footer-right .el-button--info.is-disabled {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #c0c4cc;
  cursor: not-allowed;
}

.footer-right .el-button--info.is-disabled:hover {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #c0c4cc;
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