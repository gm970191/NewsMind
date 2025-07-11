#!/usr/bin/env python3
"""
清理过时的脚本文件
"""
import os
import shutil
from pathlib import Path

def cleanup_scripts():
    """清理过时的脚本文件"""
    
    # 要保留的核心脚本
    keep_scripts = {
        # 核心功能脚本
        'simple_news_crawler.py',      # 新闻采集
        'auto_scheduler.py',           # 自动调度
        'manual_news_crawl.py',        # 手动采集
        'manage_news.py',              # 新闻管理
        'setup_auto_update.py',        # 自动更新设置
        'real_news_crawler.py',        # 真实新闻采集
        'improved_news_crawler.py',    # 改进的采集器
        
        # 部署脚本
        'deploy.sh',                   # 部署脚本
        'deploy_production.sh',        # 生产部署
        
        # 测试脚本
        'functional_test.py',          # 功能测试
        'integration_test.py',         # 集成测试
        
        # 工具脚本
        'add_international_sources.py', # 添加国际新闻源
        'news_filter.py',              # 新闻过滤
        'web_content_extractor.py',    # 网页内容提取
        
        # 数据库相关
        'upgrade_database.py',         # 数据库升级
        'upgrade_database_v2.py',      # 数据库升级v2
        'clear_database.py',           # 清理数据库
        'check_db_structure.py',       # 检查数据库结构
        'check_db_count.py',           # 检查数据库数量
    }
    
    # 要删除的过时脚本（按类别分组）
    outdated_scripts = {
        # 文章122相关（已修复完成）
        'fix_article_122_complete.py',
        'recreate_article_122.py',
        'generate_article_122_summary.py',
        'generate_summary_122.py',
        'refetch_article_122.py',
        'fix_summary_122.py',
        'manual_summary_122.py',
        'check_article_122_translation.py',
        'fix_article_122_content.py',
        'analyze_article_122_content.py',
        'improve_translation_122.py',
        'test_article_122_api.py',
        
        # 特定文章修复（已完成）
        'fix_article_49.py',
        'fix_article_54.py',
        'fix_article_54_content.py',
        'fix_article_54_db.py',
        'check_article_54.py',
        'check_article_54_db.py',
        'verify_article_54.py',
        'fix_article_59.py',
        'fix_article_59_simple.py',
        'check_article_59.py',
        'check_article_59_simple.py',
        'process_article_59.py',
        'fix_article_62.py',
        'fix_article_62_bilingual.py',
        'fix_article_62_bilingual_enhanced.py',
        'fix_article_62_content.py',
        'fix_article_62_summary.py',
        'fix_article_63.py',
        'check_article_63.py',
        'fix_article_66.py',
        'check_article_66.py',
        'fix_article_72.py',
        'check_article_72.py',
        
        # 翻译相关（已集成到主系统）
        'ai_translator.py',
        'batch_translate_multilingual.py',
        'batch_translate_titles.py',
        'simple_multilingual_translate.py',
        'translate_news_titles.py',
        'test_translation.py',
        'check_translated_titles.py',
        
        # 语言识别相关（已修复）
        'fix_language_identification.py',
        'fix_language_identification_v2.py',
        'test_language_detection.py',
        'test_multilingual_display.py',
        
        # 删除相关（已完成）
        'delete_untranslated_articles.py',
        'delete_untranslated_articles_fixed.py',
        'auto_delete_untranslated.py',
        'delete_untranslated_report.py',
        'delete_fake_translations.py',
        'auto_delete_fake_translations.py',
        'final_cleanup_chinese_only.py',
        
        # 数据库字段相关（已完成）
        'add_ai_fields_to_news_articles.py',
        'add_original_title_field.py',
        'add_translated_title_field.py',
        'check_original_title.py',
        'migrate_processed_content.py',
        
        # 测试脚本（过时）
        'test_api_122.py',
        'test_api_8000.py',
        'test_api_correct.py',
        'test_api_fix.py',
        'test_ai_speed.py',
        'test_config.py',
        'test_lmstudio.py',
        'test_lmstudio_simple.py',
        'simple_ai_speed_test.py',
        'batch_speed_test.py',
        'compare_ai_speed.py',
        'direct_api_test.py',
        
        # AI处理相关（已集成）
        'simple_ai_processor.py',
        'enhanced_ai_processor.py',
        'async_ai_processor.py',
        'ai_processor_button.py',
        'debug_ai_processing.py',
        
        # 验证脚本（已完成）
        'verify_news_display.py',
        'verify_frontend_display.py',
        'verify_fix.py',
        'verify_optimizations.py',
        'verify_article_54.py',
        
        # 修复脚本（已完成）
        'fix_all_articles_content.py',
        'fix_incomplete_articles.py',
        'fix_article_titles_and_summaries.py',
        'fix_summary_vs_detailed.py',
        'batch_fix_articles.py',
        'continue_batch_fix.py',
        
        # 检查脚本（已完成）
        'check_articles.py',
        'check_article_status.py',
        'check_processed_articles.py',
        'check_article_63.py',
        'check_article_66.py',
        'check_article_72.py',
        
        # 更新脚本（已完成）
        'update_processed_content.py',
        'update_article_content.py',
        'update_article_categories.py',
        'update_news_categories.py',
        'update_chinese_sources_category.py',
        'update_news_sources.py',
        'simple_update.py',
        
        # 清理脚本（已完成）
        'cleanup_invalid_articles.py',
        'cleanup_invalid_sources.py',
        'cleanup_old_categories.py',
        
        # 其他过时脚本
        'filter_config.py',
        'lmstudio_llm.py',
        'create_better_test_data.py',
        'create_test_news.py',
        'create_test_data.py',
        'init_db.py',
    }
    
    scripts_dir = Path("scripts")
    deleted_count = 0
    kept_count = 0
    
    print("🧹 开始清理过时的脚本文件...")
    print("=" * 60)
    
    # 遍历scripts目录
    for script_file in scripts_dir.glob("*.py"):
        script_name = script_file.name
        
        if script_name in keep_scripts:
            print(f"✅ 保留: {script_name}")
            kept_count += 1
        elif script_name in outdated_scripts:
            try:
                script_file.unlink()
                print(f"🗑️  删除: {script_name}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ 删除失败 {script_name}: {e}")
        else:
            print(f"❓ 未知: {script_name} (保留)")
            kept_count += 1
    
    # 清理__pycache__目录
    pycache_dir = scripts_dir / "__pycache__"
    if pycache_dir.exists():
        try:
            shutil.rmtree(pycache_dir)
            print(f"🗑️  删除: __pycache__/")
        except Exception as e:
            print(f"❌ 删除__pycache__失败: {e}")
    
    print("\n" + "=" * 60)
    print("📊 清理结果:")
    print(f"   删除文件: {deleted_count}")
    print(f"   保留文件: {kept_count}")
    print(f"   总计: {deleted_count + kept_count}")
    
    if deleted_count > 0:
        print(f"\n🎉 成功清理了 {deleted_count} 个过时脚本!")
        print("✅ scripts目录现在更加整洁")
    else:
        print("\n✅ 没有需要清理的脚本")

if __name__ == "__main__":
    cleanup_scripts() 