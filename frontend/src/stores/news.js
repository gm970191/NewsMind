import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useNewsStore = defineStore('news', () => {
  // 状态
  const articles = ref([])
  const processedArticles = ref([])
  const loading = ref(false)
  const currentArticle = ref(null)
  const statistics = ref({})

  // 计算属性
  const totalArticles = computed(() => articles.value.length)
  const processedCount = computed(() => processedArticles.value.length)

  // 获取新闻列表
  const fetchArticles = async (params = {}) => {
    loading.value = true
    try {
      const response = await axios.get('/api/v1/news/articles', { params })
      
      // 如果是追加模式，则追加到现有数据
      if (params.append) {
        articles.value = [...articles.value, ...response.data.articles]
      } else {
        // 否则覆盖现有数据
        articles.value = response.data.articles
      }
      
      return response.data
    } catch (error) {
      console.error('获取新闻列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取已处理的文章
  const fetchProcessedArticles = async (params = {}) => {
    loading.value = true
    try {
      // 使用现有的news/articles接口，添加is_processed=true参数
      const response = await axios.get('/api/v1/news/articles', { 
        params: { ...params, is_processed: true }
      })
      
      // 如果是追加模式，则追加到现有数据
      if (params.append) {
        processedArticles.value = [...processedArticles.value, ...response.data.articles]
      } else {
        // 否则覆盖现有数据
        processedArticles.value = response.data.articles
      }
      
      return response.data
    } catch (error) {
      console.error('获取已处理文章失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取文章详情
  const fetchArticleDetail = async (id) => {
    loading.value = true
    try {
      const response = await axios.get(`/api/v1/news/articles/${id}`)
      currentArticle.value = response.data
      return response.data
    } catch (error) {
      console.error('获取文章详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 触发AI处理
  const processArticles = async (limit = 10) => {
    loading.value = true
    try {
      const response = await axios.post(`/api/v1/ai/process?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('AI处理失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取统计信息
  const fetchStatistics = async () => {
    try {
      const response = await axios.get('/api/v1/news/statistics')
      statistics.value = response.data
      return response.data
    } catch (error) {
      console.error('获取统计信息失败:', error)
      throw error
    }
  }

  // 搜索文章
  const searchArticles = async (keyword) => {
    loading.value = true
    try {
      const response = await axios.get('/api/v1/news/search', {
        params: { keyword }
      })
      return response.data
    } catch (error) {
      console.error('搜索文章失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    articles,
    processedArticles,
    loading,
    currentArticle,
    statistics,
    
    // 计算属性
    totalArticles,
    processedCount,
    
    // 方法
    fetchArticles,
    fetchProcessedArticles,
    fetchArticleDetail,
    processArticles,
    fetchStatistics,
    searchArticles
  }
}) 