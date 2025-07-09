<template>
  <div class="article-detail">
    <div class="container mx-auto px-4 py-8">
      <!-- 返回按钮 -->
      <div class="mb-6">
        <button 
          @click="$router.go(-1)" 
          class="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          返回
        </button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">加载中...</p>
      </div>

      <!-- 文章内容 -->
      <div v-else-if="article" class="max-w-4xl mx-auto">
        <!-- 文章头部 -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ article.title }}</h1>
          <div class="flex items-center text-gray-600 text-sm mb-4">
            <span class="mr-4">来源: {{ article.source_name }}</span>
            <span class="mr-4">分类: {{ article.category }}</span>
            <span class="mr-4">语言: {{ article.language }}</span>
            <span v-if="article.quality_score" class="mr-4">
              质量评分: {{ article.quality_score.toFixed(1) }}
            </span>
            <span>{{ formatDate(article.publish_time) }}</span>
          </div>
          <div class="flex items-center space-x-4">
            <a 
              :href="article.source_url" 
              target="_blank" 
              class="text-blue-600 hover:text-blue-800 transition-colors"
            >
              查看原文
            </a>
            <button 
              v-if="!article.is_processed"
              @click="processArticle"
              :disabled="processing"
              class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {{ processing ? '处理中...' : 'AI处理' }}
            </button>
          </div>
        </div>

        <!-- 文章内容 -->
        <div class="prose prose-lg max-w-none mb-8">
          <div class="bg-white p-6 rounded-lg shadow-sm border">
            <h3 class="text-lg font-semibold mb-4">原文内容</h3>
            <div class="text-gray-700 leading-relaxed whitespace-pre-wrap">{{ article.content }}</div>
          </div>
        </div>

        <!-- AI处理结果 -->
        <div v-if="article.is_processed && processedContent" class="space-y-6">
          <!-- 摘要 -->
          <div class="bg-white p-6 rounded-lg shadow-sm border">
            <h3 class="text-lg font-semibold mb-4 text-gray-900">AI摘要</h3>
            <div class="grid md:grid-cols-2 gap-6">
              <div>
                <h4 class="font-medium text-gray-700 mb-2">中文摘要</h4>
                <p class="text-gray-600 leading-relaxed">{{ processedContent.summary_zh }}</p>
              </div>
              <div>
                <h4 class="font-medium text-gray-700 mb-2">English Summary</h4>
                <p class="text-gray-600 leading-relaxed">{{ processedContent.summary_en }}</p>
              </div>
            </div>
          </div>

          <!-- 翻译 -->
          <div v-if="processedContent.translation_zh" class="bg-white p-6 rounded-lg shadow-sm border">
            <h3 class="text-lg font-semibold mb-4 text-gray-900">中文翻译</h3>
            <div class="text-gray-600 leading-relaxed whitespace-pre-wrap">{{ processedContent.translation_zh }}</div>
          </div>

          <!-- 质量评估 -->
          <div v-if="processedContent.quality_score" class="bg-white p-6 rounded-lg shadow-sm border">
            <h3 class="text-lg font-semibold mb-4 text-gray-900">质量评估</h3>
            <div class="flex items-center">
              <div class="flex-1">
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700">内容质量</span>
                  <span class="text-sm text-gray-600">{{ processedContent.quality_score.toFixed(1) }}/10</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    :style="{ width: (processedContent.quality_score / 10 * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <div v-if="processedContent.processing_time" class="mt-4 text-sm text-gray-500">
              处理时间: {{ processedContent.processing_time }}秒
            </div>
          </div>
        </div>

        <!-- 处理中状态 -->
        <div v-else-if="processing" class="bg-white p-6 rounded-lg shadow-sm border text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600">AI正在处理文章内容...</p>
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else class="text-center py-12">
        <div class="text-red-600 mb-4">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">文章未找到</h3>
        <p class="text-gray-600">抱歉，无法找到指定的文章。</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useNewsStore } from '../stores/news'

export default {
  name: 'ArticleDetail',
  setup() {
    const route = useRoute()
    const newsStore = useNewsStore()
    
    const article = ref(null)
    const processedContent = ref(null)
    const loading = ref(true)
    const processing = ref(false)

    const loadArticle = async () => {
      try {
        loading.value = true
        const articleId = parseInt(route.params.id)
        const response = await fetch(`http://localhost:8000/api/v1/news/articles/${articleId}`)
        
        if (response.ok) {
          const data = await response.json()
          article.value = data
          processedContent.value = data.processed_content
        } else {
          console.error('Failed to load article')
        }
      } catch (error) {
        console.error('Error loading article:', error)
      } finally {
        loading.value = false
      }
    }

    const processArticle = async () => {
      try {
        processing.value = true
        const articleId = parseInt(route.params.id)
        const response = await fetch(`http://localhost:8000/api/v1/ai/process/${articleId}`, {
          method: 'POST'
        })
        
        if (response.ok) {
          // 重新加载文章以获取处理结果
          await loadArticle()
        } else {
          console.error('Failed to process article')
        }
      } catch (error) {
        console.error('Error processing article:', error)
      } finally {
        processing.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }

    onMounted(() => {
      loadArticle()
    })

    return {
      article,
      processedContent,
      loading,
      processing,
      processArticle,
      formatDate
    }
  }
}
</script>

<style scoped>
.article-detail {
  min-height: 100vh;
  background-color: #f8fafc;
}

.prose {
  max-width: none;
}

.prose h1, .prose h2, .prose h3, .prose h4, .prose h5, .prose h6 {
  color: #1f2937;
}

.prose p {
  color: #374151;
}
</style> 