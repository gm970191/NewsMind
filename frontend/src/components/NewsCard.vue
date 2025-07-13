<template>
  <el-card 
    class="news-card" 
    :body-style="{ padding: '0px' }"
    @click="handleClick"
    :class="{ 'translated': article.is_translated }"
  >
    <!-- 卡片头部 -->
    <div class="card-header">
      <div class="source-info">
        <span class="source-name">{{ article.source_name }}</span>
        <span class="category-tag" v-if="article.category">{{ article.category }}</span>
      </div>
      <div class="time-info">
        {{ formatTime(article.created_at) }}
      </div>
    </div>

    <!-- 卡片内容 -->
    <div class="card-content">
      <!-- 标题 -->
      <h3 class="article-title">
        {{ displayTitle }}
      </h3>

      <!-- 概要 -->
      <p class="article-summary">
        {{ displaySummary }}
      </p>

      <!-- 翻译状态指示器 -->
      <div class="translation-status" v-if="article.is_translated">
        <el-tag type="success" size="small">
          <el-icon><Check /></el-icon>
          已翻译
        </el-tag>
      </div>
    </div>

    <!-- 卡片底部 -->
    <div class="card-footer">
      <el-button 
        type="primary" 
        size="small" 
        @click.stop="handleDetailClick"
        plain
      >
        查看详情
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'

const props = defineProps({
  article: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'refresh'])
const router = useRouter()

// 计算属性
const displayTitle = computed(() => {
  return props.article.translated_title || props.article.original_title
})

const displaySummary = computed(() => {
  return props.article.translated_summary || props.article.original_summary
})

// 方法
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  
  // 小于1小时
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  }
  
  // 小于24小时
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  
  // 小于7天
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}天前`
  }
  
  // 超过7天显示具体日期
  return date.toLocaleDateString('zh-CN')
}

const handleClick = () => {
  emit('click', props.article)
}

const handleDetailClick = () => {
  if (!props.article.id || props.article.id <= 0) {
    ElMessage.error('文章ID无效')
    return
  }
  router.push(`/article/${props.article.id}`)
}
</script>

<style scoped>
.news-card {
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.news-card.translated {
  border-color: #67c23a;
}

.card-header {
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.source-info {
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
  background: #409eff;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
}

.time-info {
  font-size: 11px;
  color: #999;
}

.card-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: #303133;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-summary {
  margin: 0 0 12px 0;
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.translation-status {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
}

.card-footer {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  background: #fafafa;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    padding: 8px 12px;
  }
  
  .card-content {
    padding: 12px;
  }
  
  .card-footer {
    padding: 8px 12px;
  }
  
  .article-title {
    font-size: 14px;
  }
  
  .article-summary {
    font-size: 13px;
  }
}
</style> 