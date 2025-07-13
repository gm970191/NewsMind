import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNewsStore = defineStore('news', () => {
  // 状态
  const articles = ref([])
  const statistics = ref({})
  const loading = ref(false)

  // 获取文章列表
  const fetchArticles = async (params = {}) => {
    loading.value = true
    try {
      const queryParams = new URLSearchParams()
      
      if (params.limit) queryParams.append('limit', params.limit)
      if (params.skip) queryParams.append('skip', params.skip)
      
      const response = await fetch(`/api/v1/news/articles?${queryParams}`)
      
      if (response.ok) {
        const data = await response.json()
        
        if (params.append) {
          // 追加模式
          articles.value.push(...data.articles)
        } else {
          // 替换模式
          articles.value = data.articles
        }
      } else {
        throw new Error('获取文章失败')
      }
    } catch (error) {
      console.error('获取文章失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取统计信息
  const fetchStatistics = async () => {
    try {
      const response = await fetch('/api/v1/news/statistics')
      
      if (response.ok) {
        statistics.value = await response.json()
      } else {
        throw new Error('获取统计信息失败')
      }
    } catch (error) {
      console.error('获取统计信息失败:', error)
      throw error
    }
  }

  // 搜索文章
  const searchArticles = async (keyword) => {
    loading.value = true
    try {
      const response = await fetch(`/api/v1/news/search?keyword=${encodeURIComponent(keyword)}`)
      
      if (response.ok) {
        const data = await response.json()
        return data
      } else {
        throw new Error('搜索失败')
      }
    } catch (error) {
      console.error('搜索失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 重置状态
  const reset = () => {
    articles.value = []
    statistics.value = {}
    loading.value = false
  }

  return {
    // 状态
    articles,
    statistics,
    loading,
    
    // 方法
    fetchArticles,
    fetchStatistics,
    searchArticles,
    reset
  }
}) 