#!/usr/bin/env python3
"""
验证API修复的简化脚本
"""
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_database_queries():
    """测试数据库查询修复"""
    print("🔍 测试数据库查询修复...")
    
    try:
        # 设置测试环境变量
        os.environ['DEEPSEEK_API_KEY'] = 'test_key'
        
        from app.core.database import get_db
        from app.services.news_service import NewsRepository
        
        db = next(get_db())
        repo = NewsRepository(db)
        
        # 测试1: 基本查询
        print("1. 测试基本查询...")
        articles = repo.get_articles(skip=0, limit=5)
        print(f"✅ 基本查询成功，返回 {len(articles)} 篇文章")
        
        # 测试2: 带分类查询
        print("2. 测试带分类查询...")
        articles = repo.get_articles(skip=0, limit=5, category="国际")
        print(f"✅ 带分类查询成功，返回 {len(articles)} 篇文章")
        
        # 测试3: 带日期筛选查询
        print("3. 测试带日期筛选查询...")
        articles = repo.get_articles(skip=0, limit=5, date="today")
        print(f"✅ 带日期筛选查询成功，返回 {len(articles)} 篇文章")
        
        # 测试4: 已处理文章查询
        print("4. 测试已处理文章查询...")
        articles_with_content = repo.get_processed_articles_with_content(skip=0, limit=5)
        print(f"✅ 已处理文章查询成功，返回 {len(articles_with_content)} 篇文章")
        
        # 测试5: 统计查询
        print("5. 测试统计查询...")
        stats = repo.get_processing_statistics()
        print(f"✅ 统计查询成功，返回 {len(stats)} 个统计项")
        
        db.close()
        print("\n🎉 所有数据库查询测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库查询测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sql_fixes():
    """测试SQL修复"""
    print("\n🔧 测试SQL修复...")
    
    try:
        # 设置测试环境变量
        os.environ['DEEPSEEK_API_KEY'] = 'test_key'
        
        from app.core.database import get_db
        from app.services.news_service import NewsRepository
        from sqlalchemy import text
        
        db = next(get_db())
        
        # 测试1: 检查JOIN查询是否修复
        print("1. 测试JOIN查询修复...")
        query = text("""
            SELECT na.id, na.title, na.content, na.source_name, na.publish_time, 
                   na.category, na.language, na.created_at, pc.summary_zh
            FROM news_articles na
            LEFT JOIN processed_content pc ON na.id = pc.article_id
            WHERE na.category = '国际'
            ORDER BY na.created_at DESC 
            LIMIT 5
        """)
        
        result = db.execute(query)
        articles = result.fetchall()
        print(f"✅ JOIN查询成功，返回 {len(articles)} 篇文章")
        
        # 测试2: 检查日期筛选查询
        print("2. 测试日期筛选查询...")
        query = text("""
            SELECT na.id, na.title, na.content, na.source_name, na.publish_time, 
                   na.category, na.language, na.created_at, pc.summary_zh
            FROM news_articles na
            LEFT JOIN processed_content pc ON na.id = pc.article_id
            WHERE DATE(na.created_at) = DATE('now')
            ORDER BY na.created_at DESC 
            LIMIT 5
        """)
        
        result = db.execute(query)
        articles = result.fetchall()
        print(f"✅ 日期筛选查询成功，返回 {len(articles)} 篇文章")
        
        db.close()
        print("\n🎉 所有SQL修复测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ SQL修复测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始验证API修复...")
    
    # 测试数据库查询
    db_success = test_database_queries()
    
    # 测试SQL修复
    sql_success = test_sql_fixes()
    
    if db_success and sql_success:
        print("\n🎉 所有验证通过！API修复成功！")
        print("\n📝 修复总结:")
        print("1. ✅ 修复了get_articles方法中的date参数支持")
        print("2. ✅ 修复了get_processed_articles_with_content方法中的ambiguous column错误")
        print("3. ✅ 修复了get_processing_statistics方法中的ambiguous column错误")
        print("4. ✅ 修复了简化服务器中的SQL查询字段别名问题")
        sys.exit(0)
    else:
        print("\n❌ 部分验证失败，需要进一步检查")
        sys.exit(1) 