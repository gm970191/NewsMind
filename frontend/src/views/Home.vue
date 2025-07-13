<template>
  <div class="home">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <h1>NewsMind</h1>
          <span class="subtitle">智能新闻聚合</span>
        </div>
        <div class="header-actions">
          <el-button 
            type="primary" 
            :loading="crawling" 
            @click="handleCrawlNews"
            :icon="Refresh"
          >
            抓取新闻
          </el-button>
          <el-button 
            type="success" 
            :loading="translating" 
            @click="handleTranslateNews"
            :icon="Refresh"
          >
            AI翻译 ({{ untranslatedCount }})
          </el-button>
          <el-button @click="refreshData" :icon="Refresh" :loading="loading">
            刷新
          </el-button>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="main-content">
      <!-- 统计信息 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-number">{{ statistics.total_articles || 0 }}</div>
              <div class="stat-label">总文章数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-number">{{ statistics.translated_articles || 0 }}</div>
              <div class="stat-label">已翻译</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-number">{{ statistics.untranslated_articles || 0 }}</div>
              <div class="stat-label">待翻译</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-number">{{ statistics.total_sources || 0 }}</div>
              <div class="stat-label">新闻源</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分类标签 -->
      <div class="category-bar">
        <el-tag
          v-for="cat in simpleCategories"
          :key="cat"
          :type="selectedCategory === cat ? 'primary' : 'info'"
          @click="selectedCategory = cat"
          class="category-tag"
        >
          {{ cat }}
        </el-tag>
      </div>

      <!-- 新闻卡片列表 -->
      <div class="articles-container">
        <el-row :gutter="20">
          <el-col 
            v-for="article in filteredArticles" 
            :key="article.id" 
            :xs="24" 
            :sm="12" 
            :md="8" 
            :lg="6"
            class="article-col"
          >
            <NewsCard 
              :article="article" 
              @click="handleArticleClick(article)"
              @refresh="refreshData"
            />
          </el-col>
        </el-row>

        <!-- 加载更多 -->
        <div v-if="hasMore" class="load-more">
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="loadMore"
            plain
          >
            加载更多
          </el-button>
        </div>

        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && articles.length === 0" 
          description="暂无新闻数据"
        />
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useNewsStore } from '../stores/news'
import NewsCard from '../components/NewsCard.vue'

const router = useRouter()
const newsStore = useNewsStore()

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(20)
const crawling = ref(false)
const translating = ref(false)

// 计算属性
const articles = computed(() => newsStore.articles)
const statistics = computed(() => newsStore.statistics)
const loading = computed(() => newsStore.loading)
const untranslatedCount = computed(() => statistics.value.untranslated_articles || 0)
const hasMore = computed(() => {
  const currentCount = articles.value.length
  const totalCount = statistics.value.total_articles || 0
  return currentCount < totalCount
})

const selectedCategory = ref('全部')
const simpleCategories = ['全部', '军事', '科技', '政治']

// 只保留三类的筛选
const filteredArticles = computed(() => {
  if (selectedCategory.value === '全部') return articles.value
  return articles.value.filter(a => a.category === selectedCategory.value)
})

// 方法
const refreshData = async () => {
  try {
    await Promise.all([
      newsStore.fetchStatistics(),
      newsStore.fetchArticles({ limit: pageSize.value })
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  }
}

const handleCrawlNews = async () => {
  crawling.value = true
  try {
    const response = await fetch('/api/v1/news/crawl', {
      method: 'POST'
    })
    
    if (response.ok) {
      const result = await response.json()
      ElMessage.success(`抓取完成: ${result.new_articles} 篇新文章`)
      await refreshData()
    } else {
      ElMessage.error('抓取失败')
    }
  } catch (error) {
    ElMessage.error('抓取失败')
  } finally {
    crawling.value = false
  }
}

const handleTranslateNews = async () => {
  translating.value = true
  try {
    const response = await fetch('/api/v1/ai/translate', {
      method: 'POST'
    })
    
    if (response.ok) {
      const result = await response.json()
      ElMessage.success(`翻译完成: ${result.results.success_count} 篇成功`)
      await refreshData()
    } else {
      ElMessage.error('翻译失败')
    }
  } catch (error) {
    ElMessage.error('翻译失败')
  } finally {
    translating.value = false
  }
}

const handleArticleClick = (article) => {
  if (!article.id || article.id <= 0) {
    ElMessage.error('文章ID无效')
    return
  }
  router.push(`/article/${article.id}`)
}

const loadMore = async () => {
  currentPage.value++
  await fetchArticles(true)
}

const fetchArticles = async (append = false) => {
  const params = {
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  }
  
  if (append) {
    params.append = true
  }
  
  try {
    await newsStore.fetchArticles(params)
  } catch (error) {
    ElMessage.error('获取文章失败')
  }
}

// 生命周期
onMounted(async () => {
  await refreshData()
})
</script>

<style scoped>
.home {
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

.logo h1 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.subtitle {
  font-size: 14px;
  opacity: 0.8;
  margin-left: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-item {
  padding: 10px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.category-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
.category-tag {
  cursor: pointer;
  user-select: none;
}

.articles-container {
  margin-top: 20px;
}

.article-col {
  margin-bottom: 20px;
}

.load-more {
  text-align: center;
  margin-top: 30px;
}
</style> 