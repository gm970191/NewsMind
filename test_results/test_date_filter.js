// 测试日期筛选功能
async function testDateFilter() {
    console.log('🧪 测试日期筛选功能...');
    
    const testCases = [
        { date: 'today', description: '今日新闻' },
        { date: 'yesterday', description: '昨日新闻' },
        { date: 'week', description: '本周新闻' },
        { date: 'month', description: '本月新闻' },
        { date: '', description: '全部新闻' }
    ];
    
    for (const testCase of testCases) {
        console.log(`\n📋 测试: ${testCase.description}`);
        
        try {
            const url = testCase.date 
                ? `http://localhost:8000/api/v1/news/articles?date=${testCase.date}&limit=3`
                : 'http://localhost:8000/api/v1/news/articles?limit=3';
            
            const response = await fetch(url);
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ 成功: 获取到 ${data.articles.length} 条新闻`);
                
                // 显示前几条新闻的日期信息
                data.articles.slice(0, 2).forEach((article, index) => {
                    const collectDate = new Date(article.created_at).toLocaleDateString();
                    const publishDate = article.publish_time 
                        ? new Date(article.publish_time).toLocaleDateString()
                        : '无';
                    console.log(`   ${index + 1}. ${article.title}`);
                    console.log(`      收集: ${collectDate}, 发布: ${publishDate}`);
                });
            } else {
                console.log(`❌ 错误: 状态码 ${response.status}`);
            }
        } catch (error) {
            console.log(`💥 请求失败: ${error.message}`);
        }
    }
    
    console.log('\n🎯 日期筛选功能测试完成！');
    console.log('\n📝 功能说明:');
    console.log('- today: 筛选今日收集的新闻');
    console.log('- yesterday: 筛选昨日收集的新闻');
    console.log('- week: 筛选本周收集的新闻');
    console.log('- month: 筛选本月收集的新闻');
    console.log('- 空值: 显示全部新闻');
}

// 运行测试
if (typeof fetch !== 'undefined') {
    testDateFilter();
} else {
    console.log('❌ 需要支持fetch的环境来运行此测试');
} 