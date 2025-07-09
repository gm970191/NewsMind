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
            :loading="loading" 
            @click="handleProcessArticles"
            :icon="Refresh"
          >
            AI处理 ({{ unprocessedCount }})
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
              <div class="stat-number">{{ statistics.processed_articles || 0 }}</div>
              <div class="stat-label">已处理</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-number">{{ statistics.unprocessed_articles || 0 }}</div>
              <div class="stat-label">待处理</div>
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

      <!-- 筛选和搜索 -->
      <el-row :gutter="20" class="filter-row">
        <el-col :span="6">
          <el-select v-model="selectedCategory" placeholder="选择分类" clearable @change="handleCategoryChange">
            <el-option label="全部" value="" />
            <el-option label="国际新闻" value="国际新闻" />
            <el-option label="科技" value="科技" />
            <el-option label="财经" value="财经" />
            <el-option label="体育" value="体育" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="selectedDate" placeholder="选择日期" @change="handleDateChange">
            <el-option label="今日" value="today" />
            <el-option label="昨日" value="yesterday" />
            <el-option label="本周" value="week" />
            <el-option label="本月" value="month" />
            <el-option label="全部" value="" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="showType" placeholder="显示类型" @change="handleShowTypeChange">
            <el-option label="全部文章" value="all" />
            <el-option label="已处理文章" value="processed" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索文章..."
            :prefix-icon="Search"
            @keyup.enter="handleSearch"
            clearable
          />
        </el-col>
      </el-row>

      <!-- 新闻卡片列表 -->
      <div class="articles-container">
        <el-row :gutter="20">
          <el-col 
            v-for="article in displayArticles" 
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
          v-if="!loading && displayArticles.length === 0" 
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
import { Refresh, Search } from '@element-plus/icons-vue'
import { useNewsStore } from '../stores/news'
import NewsCard from '../components/NewsCard.vue'

const router = useRouter()
const newsStore = useNewsStore()

// 响应式数据
const selectedCategory = ref('')
const selectedDate = ref('today')  // 默认显示今日新闻
const showType = ref('all')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const displayArticles = computed(() => {
  if (showType.value === 'processed') {
    return newsStore.processedArticles
  }
  return newsStore.articles
})

const statistics = computed(() => newsStore.statistics)
const loading = computed(() => newsStore.loading)
const unprocessedCount = computed(() => statistics.value.unprocessed_articles || 0)
const hasMore = computed(() => {
  // 基于当前显示的文章数量判断是否还有更多数据
  const currentCount = displayArticles.value.length
  const totalCount = statistics.value.total_articles || 0
  
  // 如果当前显示数量小于总数，说明还有更多数据
  return currentCount < totalCount
})

// 方法
const refreshData = async () => {
  try {
    await Promise.all([
      newsStore.fetchStatistics(),
      newsStore.fetchArticles({ limit: pageSize.value }),
      newsStore.fetchProcessedArticles({ limit: pageSize.value })
    ])
    ElMessage.success('数据刷新成功')
  } catch (error) {
    ElMessage.error('数据刷新失败')
  }
}

const handleProcessArticles = async () => {
  try {
    const result = await newsStore.processArticles(5)
    ElMessage.success(`AI处理完成: ${result.results.success_count} 篇成功`)
    await refreshData()
  } catch (error) {
    ElMessage.error('AI处理失败')
  }
}

const handleCategoryChange = async () => {
  currentPage.value = 1
  await fetchArticles()
}

const handleDateChange = async () => {
  currentPage.value = 1
  await fetchArticles()
}

const handleShowTypeChange = async () => {
  currentPage.value = 1
  await fetchArticles()
}

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    await fetchArticles()
    return
  }
  
  try {
    const result = await newsStore.searchArticles(searchKeyword.value)
    if (showType.value === 'processed') {
      newsStore.processedArticles = result.articles
    } else {
      newsStore.articles = result.articles
    }
  } catch (error) {
    ElMessage.error('搜索失败')
  }
}

const handleArticleClick = (article) => {
  // 验证文章ID是否有效
  if (!article.id || article.id <= 0) {
    ElMessage.error('文章ID无效')
    return
  }
  router.push(`/article/${article.id}`)
}

const loadMore = async () => {
  currentPage.value++
  await fetchArticles(true) // 传递true表示追加模式
}

const fetchArticles = async (append = false) => {
  const params = {
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  }
  
  if (selectedCategory.value) {
    params.category = selectedCategory.value
  }

  if (selectedDate.value) {
    params.date = selectedDate.value
  }
  
  // 如果是追加模式，添加append参数
  if (append) {
    params.append = true
  }
  
  try {
    if (showType.value === 'processed') {
      await newsStore.fetchProcessedArticles(params)
    } else {
      await newsStore.fetchArticles(params)
    }
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

.filter-row {
  margin-bottom: 20px;
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