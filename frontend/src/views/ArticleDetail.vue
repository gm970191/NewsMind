<template>
  <div class="article-detail">
    <el-card class="article-card">
      <div class="header">
        <h2>{{ getDisplayTitle() }}</h2>
        <div v-if="article.original_language !== 'zh' && article.original_title" class="original-title">
          <span>原文：{{ article.original_title }}</span>
        </div>
        <div class="meta">
          <span>来源：{{ article.source_name }}</span>
          <span>分类：{{ article.category }}</span>
          <span>发布时间：{{ formatDate(article.publish_time || article.created_at) }}</span>
        </div>
      </div>
      <el-divider></el-divider>
      <div v-if="article.processed_content">
        <div class="section">
          <h3>中文概要</h3>
          <p class="summary">{{ article.processed_content.summary_zh }}</p>
        </div>
        <el-divider></el-divider>
        <div class="section">
          <h3>正文总结（最多10000字）</h3>
          <div class="detailed-summary">
            <div class="content-text markdown-content" v-html="renderMarkdown(article.processed_content.detailed_summary_zh)"></div>
          </div>
        </div>
      </div>
      <div v-else>
        <el-alert title="该新闻尚未AI处理，暂无AI摘要和详细总结。" type="info" show-icon></el-alert>
      </div>
      <el-divider></el-divider>
      <div v-if="article.translated_content" class="section">
        <h3>中文翻译</h3>
        <div class="translation-content">
          <div class="content-text">
            {{ article.translated_content }}
          </div>
        </div>
      </div>
      
      <div class="section">
        <h3>原始正文</h3>
        <div class="origin-content">
          <div class="content-text">
            {{ article.original_content }}
          </div>
        </div>
      </div>
      <div class="footer">
        <el-button type="primary" @click="goBack">返回</el-button>
        <el-button v-if="!article.is_processed" type="success" @click="processArticle">立即AI处理</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import MarkdownIt from 'markdown-it';

export default {
  name: 'ArticleDetail',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const article = ref({});
    const loading = ref(false);

    const fetchArticle = async () => {
      loading.value = true;
      try {
        const { data } = await axios.get(`/api/v1/news/articles/${route.params.id}`);
        article.value = data;
      } catch (e) {
        ElMessage.error('获取文章详情失败');
      } finally {
        loading.value = false;
      }
    };

    const processArticle = async () => {
      try {
        ElMessage.info('正在AI处理中，请稍候...');
        const response = await axios.post(`/api/v1/ai/process-button/${route.params.id}`);
        console.log('AI处理响应:', response.data);
        ElMessage.success(response.data.message || 'AI处理已完成！');
        await fetchArticle(); // 重新获取文章数据
      } catch (e) {
        console.error('AI处理失败:', e);
        const errorMsg = e.response?.data?.detail || e.response?.data?.message || e.message;
        ElMessage.error('AI处理失败: ' + errorMsg);
      }
    };

    const goBack = () => {
      router.back();
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleString('zh-CN');
    };

    const renderMarkdown = (text) => {
      if (!text) return '';
      const md = new MarkdownIt();
      return md.render(text);
    };

    const getDisplayTitle = () => {
      // 优先显示翻译后的标题，如果没有则显示原文标题
      if (article.value.translated_title) {
        return article.value.translated_title;
      }
      return article.value.original_title;
    };

    onMounted(fetchArticle);

    return {
      article,
      loading,
      processArticle,
      goBack,
      formatDate,
      renderMarkdown,
      getDisplayTitle
    };
  }
};
</script>

<style scoped>
.article-detail {
  max-width: 900px;
  margin: 32px auto;
  padding: 0 16px;
}
.article-card {
  box-shadow: 0 2px 12px #f0f1f2;
  border-radius: 12px;
  padding: 32px 24px;
}
.header {
  margin-bottom: 12px;
}
.header h2 {
  margin: 0 0 8px 0;
  font-size: 2rem;
  font-weight: bold;
}
.meta {
  color: #888;
  font-size: 0.95rem;
  display: flex;
  gap: 24px;
}
.section {
  margin-bottom: 18px;
}
.summary {
  font-size: 1.1rem;
  color: #333;
  background: #f8f8fa;
  padding: 12px 16px;
  border-radius: 6px;
  line-height: 1.7;
}
.detailed-summary {
  background: #f6f8ff;
  padding: 14px 16px;
  border-radius: 6px;
  font-size: 1rem;
  color: #222;
}
.original-content {
  background: #f9f9f9;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 1rem;
  color: #444;
}
.origin-content {
  background: #f4f4f4;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 0.98rem;
  color: #666;
}

.translation-content {
  background: #f0f8ff;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 0.98rem;
  color: #333;
}
.original-title {
  margin: 8px 0;
}
.original-title span {
  font-size: 0.9rem;
  color: #888;
  font-weight: normal;
  margin: 0;
  font-style: italic;
}
.content-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
}

.markdown-content {
  white-space: normal;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin: 16px 0 8px 0;
  font-weight: bold;
  color: #333;
}

.markdown-content h1 {
  font-size: 1.8rem;
  border-bottom: 2px solid #e1e4e8;
  padding-bottom: 8px;
}

.markdown-content h2 {
  font-size: 1.5rem;
  border-bottom: 1px solid #e1e4e8;
  padding-bottom: 6px;
}

.markdown-content h3 {
  font-size: 1.3rem;
}

.markdown-content p {
  margin: 8px 0;
  line-height: 1.6;
}

.markdown-content ul,
.markdown-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.markdown-content li {
  margin: 4px 0;
  line-height: 1.6;
}

.markdown-content strong {
  font-weight: bold;
  color: #333;
}

.markdown-content em {
  font-style: italic;
}

.markdown-content blockquote {
  border-left: 4px solid #e1e4e8;
  padding-left: 16px;
  margin: 16px 0;
  color: #666;
  font-style: italic;
}
.footer {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}
</style> 