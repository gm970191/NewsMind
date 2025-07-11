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
        <!-- 分类按钮组 -->
        <el-col :span="24" class="category-section">
          <div class="category-buttons">
            <el-button 
              :type="selectedCategory === '' ? 'primary' : 'default'"
              @click="handleCategorySelect('')"
              size="large"
            >
              全部
            </el-button>
            <el-button 
              :type="selectedCategory === '科技' ? 'primary' : 'default'"
              @click="handleCategorySelect('科技')"
              size="large"
            >
              科技
            </el-button>
            <el-button 
              :type="selectedCategory === '财经' ? 'primary' : 'default'"
              @click="handleCategorySelect('财经')"
              size="large"
            >
              财经
            </el-button>
            <el-button 
              :type="selectedCategory === '军事' ? 'primary' : 'default'"
              @click="handleCategorySelect('军事')"
              size="large"
            >
              军事
            </el-button>
            <el-button 
              :type="selectedCategory === '政治' ? 'primary' : 'default'"
              @click="handleCategorySelect('政治')"
              size="large"
            >
              政治
            </el-button>
            <el-button 
              :type="selectedCategory === '国际' ? 'primary' : 'default'"
              @click="handleCategorySelect('国际')"
              size="large"
            >
              国际
            </el-button>
            <el-button 
              :type="selectedCategory === '其他' ? 'primary' : 'default'"
              @click="handleCategorySelect('其他')"
              size="large"
            >
              其他
            </el-button>
          </div>
        </el-col>
      </el-row>

      <!-- 其他筛选选项 -->
      <el-row :gutter="20" class="filter-row">
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
            <el-option label="未处理文章" value="unprocessed" />
          </el-select>
        </el-col>
        <el-col :span="12">
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
  // 根据显示类型返回对应的文章列表
  if (showType.value === 'processed') {
    return newsStore.processedArticles
  } else if (showType.value === 'unprocessed') {
    // 显示未处理的文章（在articles中但不在processedArticles中的）
    const processedIds = new Set(newsStore.processedArticles.map(a => a.id))
    return newsStore.articles.filter(a => !processedIds.has(a.id))
  } else {
    // 显示所有文章
    return newsStore.articles
  }
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

const handleCategorySelect = async (category) => {
  selectedCategory.value = category
  currentPage.value = 1
  await fetchArticles()
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
  // 重新获取数据以更新显示
  await refreshData()
}

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    await refreshData()
    return
  }
  
  try {
    const result = await newsStore.searchArticles(searchKeyword.value)
    if (showType.value === 'processed') {
      newsStore.processedArticles = result.articles
    } else if (showType.value === 'unprocessed') {
      // 对于未处理文章，需要过滤搜索结果
      const processedIds = new Set(newsStore.processedArticles.map(a => a.id))
      newsStore.articles = result.articles.filter(a => !processedIds.has(a.id))
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
      // 对于全部文章和未处理文章，都获取所有文章
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

.category-section {
  margin-bottom: 15px;
}

.category-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 15px 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.category-buttons .el-button {
  min-width: 100px;
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.category-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.category-buttons .el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.category-buttons .el-button--primary:hover {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
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