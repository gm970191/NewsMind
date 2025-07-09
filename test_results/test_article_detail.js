// 测试文章详情页面的错误处理
async function testArticleDetailErrorHandling() {
    console.log('🧪 测试文章详情页面错误处理...');
    
    const testCases = [
        { id: 45, description: '不存在的文章ID' },
        { id: -1, description: '负数ID' },
        { id: 0, description: '零ID' },
        { id: 'abc', description: '非数字ID' },
        { id: 1, description: '存在的文章ID（应该成功）' }
    ];
    
    for (const testCase of testCases) {
        console.log(`\n📋 测试: ${testCase.description} (ID: ${testCase.id})`);
        
        try {
            const response = await fetch(`http://localhost:8000/api/v1/news/articles/${testCase.id}`);
            
            if (response.ok) {
                const article = await response.json();
                console.log(`✅ 成功: 文章 "${article.title}" 存在`);
            } else if (response.status === 404) {
                console.log(`❌ 404: 文章ID ${testCase.id} 不存在`);
            } else {
                console.log(`⚠️  其他错误: 状态码 ${response.status}`);
            }
        } catch (error) {
            console.log(`💥 请求失败: ${error.message}`);
        }
    }
    
    console.log('\n🎯 测试完成！');
    console.log('\n📝 预期结果:');
    console.log('- ID 45: 应该返回404');
    console.log('- ID -1, 0, "abc": 应该返回404或400');
    console.log('- ID 1: 应该成功返回文章数据');
}

// 运行测试
if (typeof fetch !== 'undefined') {
    testArticleDetailErrorHandling();
} else {
    console.log('❌ 需要支持fetch的环境来运行此测试');
} 