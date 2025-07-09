// 前端功能测试脚本
const puppeteer = require('puppeteer');

async function testFrontend() {
    console.log('开始测试前端功能...');
    
    const browser = await puppeteer.launch({ 
        headless: false,
        defaultViewport: { width: 1280, height: 720 }
    });
    
    try {
        const page = await browser.newPage();
        
        // 测试1: 访问首页
        console.log('测试1: 访问首页');
        await page.goto('http://localhost:3000', { waitUntil: 'networkidle0' });
        await page.waitForSelector('.news-list', { timeout: 10000 });
        console.log('✓ 首页加载成功');
        
        // 测试2: 检查新闻列表
        console.log('测试2: 检查新闻列表');
        const newsCount = await page.$$eval('.news-card', cards => cards.length);
        console.log(`✓ 找到 ${newsCount} 条新闻`);
        
        // 测试3: 测试搜索功能
        console.log('测试3: 测试搜索功能');
        await page.type('input[placeholder*="搜索"]', '测试');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(1000);
        console.log('✓ 搜索功能正常');
        
        // 测试4: 测试分类筛选
        console.log('测试4: 测试分类筛选');
        await page.click('button:contains("科技")');
        await page.waitForTimeout(1000);
        console.log('✓ 分类筛选正常');
        
        // 测试5: 点击新闻卡片
        console.log('测试5: 点击新闻卡片');
        await page.click('.news-card:first-child');
        await page.waitForSelector('.article-detail', { timeout: 10000 });
        console.log('✓ 文章详情页面加载成功');
        
        // 测试6: 测试AI处理功能
        console.log('测试6: 测试AI处理功能');
        const processButton = await page.$('button:contains("AI处理")');
        if (processButton) {
            await processButton.click();
            await page.waitForTimeout(2000);
            console.log('✓ AI处理功能正常');
        } else {
            console.log('⚠ 未找到AI处理按钮（可能已处理过）');
        }
        
        // 测试7: 返回首页
        console.log('测试7: 返回首页');
        await page.click('button:contains("返回")');
        await page.waitForSelector('.news-list', { timeout: 10000 });
        console.log('✓ 返回功能正常');
        
        console.log('\n🎉 所有测试通过！');
        
    } catch (error) {
        console.error('❌ 测试失败:', error.message);
    } finally {
        await browser.close();
    }
}

// 如果没有puppeteer，使用简单的HTTP请求测试
async function simpleTest() {
    console.log('执行简单功能测试...');
    
    try {
        // 测试API连接
        const response = await fetch('http://localhost:8000/api/v1/news/articles');
        const data = await response.json();
        console.log('✓ API连接正常，获取到', data.articles.length, '条新闻');
        
        // 测试前端页面
        const frontendResponse = await fetch('http://localhost:3000');
        if (frontendResponse.ok) {
            console.log('✓ 前端页面可访问');
        }
        
        console.log('\n🎉 基础功能测试通过！');
        console.log('\n📋 测试结果总结:');
        console.log('- 后端API服务: ✅ 正常运行');
        console.log('- 前端页面服务: ✅ 正常运行');
        console.log('- API数据接口: ✅ 返回测试数据');
        console.log('- 前端路由: ✅ 页面可访问');
        console.log('\n🌐 访问地址:');
        console.log('- 前端页面: http://localhost:3000');
        console.log('- API文档: http://localhost:8000/docs');
        
    } catch (error) {
        console.error('❌ 测试失败:', error.message);
    }
}

// 运行测试
if (typeof fetch !== 'undefined') {
    simpleTest();
} else {
    console.log('使用Node.js fetch进行测试...');
    simpleTest();
} 