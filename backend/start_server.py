#!/usr/bin/env python3
"""
NewsMind 后端服务启动脚本
支持开发环境和生产环境
"""
import os
import sys
import argparse
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def setup_environment():
    """设置环境变量"""
    # 禁用playwright（如果环境不支持）
    if os.environ.get('DISABLE_PLAYWRIGHT'):
        print("⚠️  Playwright已禁用，使用简化模式")
    
    # 设置日志级别
    os.environ.setdefault('LOG_LEVEL', 'INFO')

def start_development_server():
    """启动开发服务器"""
    try:
        from app.main import app
        import uvicorn
        
        print("🚀 启动NewsMind开发服务器")
        print("📍 访问地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保已安装所需依赖:")
        print("   pip install fastapi uvicorn sqlalchemy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def start_production_server():
    """启动生产服务器"""
    try:
        from app.main import app
        import uvicorn
        
        print("🚀 启动NewsMind生产服务器")
        print("📍 访问地址: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="warning"
        )
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保已安装所需依赖:")
        print("   pip install fastapi uvicorn sqlalchemy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def start_simple_server():
    """启动简化服务器（用于测试）"""
    try:
        from flask import Flask, jsonify
        import sqlite3
        
        app = Flask(__name__)
        DB_PATH = "newsmind.db"
        
        @app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected" if os.path.exists(DB_PATH) else "not_found"
            })
        
        @app.route('/api/v1/news/articles')
        def get_articles():
            try:
                from flask import request
                
                # 获取分页参数
                skip = request.args.get('skip', 0, type=int)
                limit = request.args.get('limit', 20, type=int)
                category = request.args.get('category', None)
                language = request.args.get('language', None)
                date_filter = request.args.get('date', None)  # 新增日期筛选参数
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # 构建查询条件
                where_conditions = []
                params = []
                
                if category:
                    where_conditions.append("category = ?")
                    params.append(category)
                
                if language:
                    where_conditions.append("language = ?")
                    params.append(language)
                
                # 添加日期筛选
                if date_filter:
                    if date_filter == 'today':
                        # 筛选今日新闻
                        where_conditions.append("DATE(created_at) = DATE('now')")
                    elif date_filter == 'yesterday':
                        # 筛选昨日新闻
                        where_conditions.append("DATE(created_at) = DATE('now', '-1 day')")
                    elif date_filter == 'week':
                        # 筛选本周新闻
                        where_conditions.append("DATE(created_at) >= DATE('now', '-7 days')")
                    elif date_filter == 'month':
                        # 筛选本月新闻
                        where_conditions.append("DATE(created_at) >= DATE('now', '-30 days')")
                    else:
                        # 自定义日期格式 YYYY-MM-DD
                        try:
                            from datetime import datetime
                            datetime.strptime(date_filter, '%Y-%m-%d')
                            where_conditions.append("DATE(created_at) = ?")
                            params.append(date_filter)
                        except ValueError:
                            pass  # 忽略无效日期格式
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # 执行查询
                query = f"""
                    SELECT id, title, content, source_name, publish_time, category, language, created_at
                    FROM news_articles 
                    {where_clause}
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """
                params.extend([limit, skip])
                
                cursor.execute(query, params)
                articles = []
                for row in cursor.fetchall():
                    articles.append({
                        "id": row[0],
                        "title": row[1],
                        "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                        "source_name": row[3],
                        "publish_time": row[4],
                        "category": row[5],
                        "language": row[6],
                        "created_at": row[7]
                    })
                conn.close()
                return jsonify({"articles": articles, "total": len(articles)})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/v1/news/statistics')
        def get_statistics():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM news_articles")
                total_articles = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_processed = 1")
                processed_articles = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM news_sources WHERE is_active = 1")
                active_sources = cursor.fetchone()[0]
                
                conn.close()
                
                return jsonify({
                    "total_articles": total_articles,
                    "processed_articles": processed_articles,
                    "active_sources": active_sources
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/v1/ai/processed-articles')
        def get_processed_articles():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, content, source_name, publish_time, category, language
                    FROM news_articles 
                    WHERE is_processed = 1
                    ORDER BY created_at DESC 
                    LIMIT 20
                """)
                articles = []
                for row in cursor.fetchall():
                    articles.append({
                        "id": row[0],
                        "title": row[1],
                        "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                        "source_name": row[3],
                        "publish_time": row[4],
                        "category": row[5],
                        "language": row[6]
                    })
                conn.close()
                return jsonify({"articles": articles, "total": len(articles)})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/v1/news/articles/<int:article_id>')
        def get_article(article_id):
            """获取单篇文章详情"""
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, title, content, source_url, source_name, publish_time, 
                           category, language, quality_score, is_processed, created_at
                    FROM news_articles 
                    WHERE id = ?
                """, (article_id,))
                
                row = cursor.fetchone()
                if not row:
                    conn.close()
                    return jsonify({"error": "Article not found"}), 404
                
                article = {
                    "id": row[0],
                    "title": row[1],
                    "content": row[2],
                    "source_url": row[3],
                    "source_name": row[4],
                    "publish_time": row[5],
                    "category": row[6],
                    "language": row[7],
                    "quality_score": row[8],
                    "is_processed": bool(row[9]),
                    "created_at": row[10]
                }
                
                # 获取处理结果（如果存在）
                cursor.execute("""
                    SELECT summary_zh, summary_en, translation_zh, quality_score, processing_time
                    FROM processed_content 
                    WHERE article_id = ?
                """, (article_id,))
                
                processed_row = cursor.fetchone()
                if processed_row:
                    article["processed_content"] = {
                        "summary_zh": processed_row[0],
                        "summary_en": processed_row[1],
                        "translation_zh": processed_row[2],
                        "quality_score": processed_row[3],
                        "processing_time": processed_row[4]
                    }
                else:
                    article["processed_content"] = None
                
                conn.close()
                return jsonify(article)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/v1/ai/process/<int:article_id>', methods=['POST'])
        def process_article(article_id):
            """处理单篇文章"""
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # 检查文章是否存在
                cursor.execute("SELECT id, title, content, language FROM news_articles WHERE id = ?", (article_id,))
                row = cursor.fetchone()
                if not row:
                    conn.close()
                    return jsonify({"error": "Article not found"}), 404
                
                # 模拟AI处理（简化模式）
                article_id, title, content, language = row
                
                # 生成简单的摘要和翻译
                summary_zh = f"这是文章《{title}》的中文摘要。"
                summary_en = f"This is the English summary of article '{title}'."
                translation_zh = None
                if language == 'en':
                    translation_zh = f"这是文章《{title}》的中文翻译。"
                
                # 保存处理结果
                cursor.execute("""
                    INSERT OR REPLACE INTO processed_content 
                    (article_id, summary_zh, summary_en, translation_zh, quality_score, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (article_id, summary_zh, summary_en, translation_zh, 7.5, 2.0))
                
                # 更新文章处理状态
                cursor.execute("UPDATE news_articles SET is_processed = 1 WHERE id = ?", (article_id,))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    "message": f"Article {article_id} processed successfully",
                    "results": {
                        "success_count": 1,
                        "error_count": 0
                    }
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @app.route('/api/v1/ai/process', methods=['POST'])
        def process_articles():
            """批量处理文章"""
            try:
                from flask import request
                limit = request.args.get('limit', 5, type=int)
                
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # 获取未处理的文章
                cursor.execute("""
                    SELECT id, title, content, language 
                    FROM news_articles 
                    WHERE is_processed = 0 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                articles = cursor.fetchall()
                success_count = 0
                error_count = 0
                
                for article_id, title, content, language in articles:
                    try:
                        # 模拟AI处理
                        summary_zh = f"这是文章《{title}》的中文摘要。"
                        summary_en = f"This is the English summary of article '{title}'."
                        translation_zh = None
                        if language == 'en':
                            translation_zh = f"这是文章《{title}》的中文翻译。"
                        
                        # 保存处理结果
                        cursor.execute("""
                            INSERT OR REPLACE INTO processed_content 
                            (article_id, summary_zh, summary_en, translation_zh, quality_score, processing_time)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (article_id, summary_zh, summary_en, translation_zh, 7.5, 2.0))
                        
                        # 更新文章处理状态
                        cursor.execute("UPDATE news_articles SET is_processed = 1 WHERE id = ?", (article_id,))
                        
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        print(f"Error processing article {article_id}: {e}")
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    "message": "AI processing completed",
                    "results": {
                        "total_articles": len(articles),
                        "success_count": success_count,
                        "error_count": error_count
                    }
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        print("🚀 启动NewsMind简化测试服务器")
        print("📍 访问地址: http://localhost:8000")
        print("📚 健康检查: http://localhost:8000/health")
        print("📰 新闻列表: http://localhost:8000/api/v1/news/articles")
        print("📊 统计信息: http://localhost:8000/api/v1/news/statistics")
        print("🤖 AI处理: http://localhost:8000/api/v1/ai/processed-articles")
        print("⏹️  按 Ctrl+C 停止服务")
        print("-" * 50)
        
        app.run(host='0.0.0.0', port=8000, debug=False)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请安装Flask:")
        print("   pip install flask")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='NewsMind 后端服务启动脚本')
    parser.add_argument('--mode', choices=['dev', 'prod', 'simple'], 
                       default='dev', help='启动模式 (默认: dev)')
    parser.add_argument('--disable-playwright', action='store_true',
                       help='禁用playwright')
    
    args = parser.parse_args()
    
    # 设置环境
    if args.disable_playwright:
        os.environ['DISABLE_PLAYWRIGHT'] = '1'
    
    setup_environment()
    
    # 根据模式启动服务
    if args.mode == 'dev':
        start_development_server()
    elif args.mode == 'prod':
        start_production_server()
    elif args.mode == 'simple':
        start_simple_server()

if __name__ == '__main__':
    main() 