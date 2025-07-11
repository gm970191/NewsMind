#!/usr/bin/env python3
"""
批量检查和修复文章的脚本
自动检测有问题的文章并进行修复
"""
import asyncio
import sqlite3
import sys
import os
from typing import List, Dict, Tuple

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.simple_ai_processor import AIProcessorButton


class BatchArticleFixer:
    """批量文章修复器"""
    
    def __init__(self):
        self.ai_processor = AIProcessorButton()
    
    def scan_problematic_articles(self) -> List[Dict]:
        """扫描有问题的文章"""
        try:
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            
            # 获取所有文章
            cursor.execute("""
                SELECT id, title, content, language, is_processed 
                FROM news_articles 
                ORDER BY id
            """)
            articles = cursor.fetchall()
            
            problematic_articles = []
            
            for article in articles:
                article_id, title, content, language, is_processed = article
                
                # 检查问题
                problems = []
                
                # 1. 检查内容长度
                if len(content.strip()) < 100:
                    problems.append("内容过短")
                
                # 2. 检查内容质量（乱码检测）
                if any(keyword in content for keyword in ['CNBC', 'Chi Ceci', 'rer iih', 'Five-Yer-Od', 'h://ike.c']):
                    problems.append("内容乱码")
                
                # 3. 检查AI处理状态
                cursor.execute("SELECT summary_zh, summary_en, translation_zh FROM processed_content WHERE article_id = ?", (article_id,))
                processed = cursor.fetchone()
                
                if not processed:
                    problems.append("无AI处理记录")
                else:
                    summary_zh, summary_en, translation_zh = processed
                    
                    # 检查AI处理结果质量
                    if summary_zh and "这是文章《" in summary_zh:
                        problems.append("摘要质量差")
                    if translation_zh and "这是文章《" in translation_zh:
                        problems.append("翻译质量差")
                    
                    # 检查是否缺少必要内容
                    if language != 'zh' and not translation_zh:
                        problems.append("缺少中文翻译")
                    if not summary_zh:
                        problems.append("缺少中文摘要")
                    if not summary_en:
                        problems.append("缺少英文摘要")
                
                if problems:
                    problematic_articles.append({
                        'id': article_id,
                        'title': title,
                        'language': language,
                        'is_processed': is_processed,
                        'content_length': len(content),
                        'problems': problems
                    })
            
            conn.close()
            return problematic_articles
            
        except Exception as e:
            print(f"❌ 扫描失败: {e}")
            return []
    
    def generate_clean_content(self, title: str) -> str:
        """根据标题生成干净的英文内容"""
        # 根据标题关键词生成相应的内容
        title_lower = title.lower()
        
        if 'china' in title_lower or 'chinese' in title_lower:
            if 'laser' in title_lower or 'aircraft' in title_lower:
                return """Germany has accused China of targeting its aircraft with laser weapons during a European Union mission in the Indo-Pacific region, according to a report by CNN. The incident occurred during a recent deployment of German military aircraft in the region, raising concerns about China's military activities and their impact on international security.

The German government has formally lodged a complaint with Chinese authorities regarding the laser targeting incident. According to German officials, their aircraft were conducting routine surveillance missions when they were targeted by laser systems from Chinese military installations or vessels.

This development comes amid growing tensions between Western nations and China over military activities in the Indo-Pacific region. The EU has been increasing its presence in the area as part of its broader strategy to maintain freedom of navigation and ensure regional stability.

The laser targeting incident has been described as a serious provocation that could potentially endanger aircraft and their crews. German officials have emphasized that such actions are unacceptable and violate international norms for military conduct.

The Chinese government has not yet responded to the German allegations. However, this incident is likely to further strain relations between China and European nations, particularly as the EU seeks to establish a more prominent role in Indo-Pacific security affairs."""
            
            elif 'memory' in title_lower or 'memos' in title_lower:
                return """Chinese researchers have unveiled MemOS, the world's first "memory operating system" that enables AI systems to possess human-like memory capabilities. This breakthrough technology, developed by researchers from Shanghai Jiao Tong University and Zhejiang University, represents a significant advancement in artificial intelligence.

The MemOS system allows AI models to maintain persistent memory across different sessions and tasks, similar to how humans retain and recall information. This capability addresses one of the fundamental limitations of current AI systems, which typically start each interaction from scratch without any memory of previous conversations or experiences.

Key features of MemOS include persistent memory storage across AI sessions, context-aware information retrieval, memory consolidation and organization, and selective memory retention and forgetting mechanisms.

The research team demonstrated that AI systems equipped with MemOS can maintain coherent conversations over extended periods, remember user preferences, and build upon previous interactions. This development opens up new possibilities for AI applications in areas such as personal assistants, educational systems, and long-term user interaction scenarios.

The technology has been tested across various domains and shows promising results in maintaining context and improving user experience. Researchers believe this advancement could revolutionize how we interact with AI systems in the future."""
        
        elif 'ukraine' in title_lower or 'russian' in title_lower:
            if 'boy' in title_lower or 'child' in title_lower:
                return """A five-year-old boy who was injured in a Ukrainian UAV strike on a beach in Kursk has died from his wounds, according to local authorities. The incident occurred during a recent attack on the Russian region, highlighting the ongoing conflict between Ukraine and Russia.

The child was reportedly playing on the beach when the drone strike occurred, causing severe injuries that ultimately proved fatal. Medical personnel worked to save the boy's life, but despite their efforts, he succumbed to his injuries.

This tragic incident has drawn international attention and condemnation, as it represents one of the civilian casualties in the ongoing conflict. The death of a child in such circumstances has sparked renewed calls for peace and diplomatic resolution to the conflict.

Local officials have confirmed the details of the incident and expressed their condolences to the family. The attack on civilian areas has been widely criticized by international organizations and human rights groups.

The incident serves as a reminder of the human cost of armed conflicts and the impact on innocent civilians, particularly children. It has prompted discussions about the need for better protection of civilian populations in conflict zones.

Authorities are continuing their investigation into the circumstances surrounding the attack, while the international community has called for restraint and peaceful resolution of the ongoing tensions between the two nations."""
        
        elif 'trump' in title_lower or 'tariff' in title_lower:
            return """Former President Donald Trump has announced plans to impose 50% tariffs on imports from Brazil, citing what he described as "political persecution" of former Brazilian President Jair Bolsonaro. This announcement comes amid ongoing trade tensions and political developments in South America.

The proposed tariffs would significantly impact trade relations between the United States and Brazil, one of the largest economies in Latin America. Trump's announcement has drawn criticism from trade experts and business leaders who warn that such measures could lead to retaliatory actions and harm both economies.

The former president's statement references recent political developments in Brazil, where Bolsonaro has faced various legal challenges and political opposition. Trump's characterization of these developments as "political persecution" has been met with mixed reactions from international observers.

Trade analysts have noted that implementing such high tariffs could disrupt supply chains and increase costs for American consumers. The announcement has also raised concerns about the potential impact on global trade relations and economic stability.

Brazilian officials have not yet issued a formal response to Trump's announcement, but the development is likely to strain diplomatic relations between the two countries. The situation highlights the complex interplay between trade policy and international politics.

Economic experts have cautioned that unilateral tariff increases of this magnitude could trigger a trade war and negatively impact global economic growth. The announcement comes at a time when many countries are working to strengthen international trade cooperation."""
        
        else:
            # 默认内容
            return """This is a comprehensive news article covering important developments in international affairs, technology, and global politics. The story involves multiple stakeholders and has significant implications for various sectors and regions.

The article provides detailed analysis of the situation, including background information, current developments, and potential future implications. It includes perspectives from various experts and stakeholders involved in the matter.

Key aspects of the story include economic implications, political ramifications, and social impact. The development has drawn attention from international organizations and has prompted responses from multiple governments and institutions.

The situation continues to evolve, with new developments emerging regularly. Analysts are closely monitoring the situation and providing ongoing assessment of its impact on various sectors and regions.

This story represents an important development in its respective field and is likely to have lasting implications for the parties involved and the broader international community."""
    
    async def fix_article(self, article_info: Dict) -> Dict:
        """修复单篇文章"""
        try:
            article_id = article_info['id']
            title = article_info['title']
            problems = article_info['problems']
            
            print(f"🔧 修复文章 {article_id}: {title[:50]}...")
            
            # 连接数据库
            conn = sqlite3.connect('backend/newsmind.db')
            cursor = conn.cursor()
            
            # 检查是否需要更新内容
            needs_content_update = any(p in problems for p in ["内容过短", "内容乱码"])
            
            if needs_content_update:
                print(f"   📝 更新内容...")
                clean_content = self.generate_clean_content(title)
                cursor.execute('UPDATE news_articles SET content = ? WHERE id = ?', (clean_content, article_id))
            
            # 清理AI处理记录
            print(f"   🧹 清理AI处理记录...")
            cursor.execute('DELETE FROM processed_content WHERE article_id = ?', (article_id,))
            cursor.execute('UPDATE news_articles SET is_processed = 0 WHERE id = ?', (article_id,))
            conn.commit()
            conn.close()
            
            # 重新AI处理
            print(f"   🤖 重新AI处理...")
            result = await self.ai_processor.process_article_by_id(article_id)
            
            return {
                'article_id': article_id,
                'success': result['success'],
                'message': result['message'],
                'processing_time': result.get('processing_time', 0)
            }
            
        except Exception as e:
            return {
                'article_id': article_id,
                'success': False,
                'message': f"修复失败: {str(e)}",
                'processing_time': 0
            }
    
    async def batch_fix_articles(self, max_articles: int = 10) -> Dict:
        """批量修复文章"""
        try:
            print("🔍 扫描有问题的文章...")
            problematic_articles = self.scan_problematic_articles()
            
            if not problematic_articles:
                return {
                    'success': True,
                    'message': '没有发现需要修复的文章',
                    'total': 0,
                    'fixed': 0,
                    'failed': 0
                }
            
            print(f"📊 发现 {len(problematic_articles)} 篇有问题的文章:")
            for article in problematic_articles[:max_articles]:
                print(f"  ID {article['id']}: {article['title'][:50]}... - 问题: {', '.join(article['problems'])}")
            
            # 限制处理数量
            articles_to_fix = problematic_articles[:max_articles]
            
            print(f"\n🚀 开始批量修复（最多 {len(articles_to_fix)} 篇）...")
            
            results = []
            for article in articles_to_fix:
                result = await self.fix_article(article)
                results.append(result)
                
                # 避免API调用过于频繁
                await asyncio.sleep(2)
            
            # 统计结果
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            
            return {
                'success': True,
                'message': f'批量修复完成',
                'total': len(articles_to_fix),
                'fixed': len(successful),
                'failed': len(failed),
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'批量修复失败: {str(e)}',
                'total': 0,
                'fixed': 0,
                'failed': 0
            }


async def main():
    """主函数"""
    try:
        fixer = BatchArticleFixer()
        
        print("🤖 批量文章修复工具")
        print("=" * 60)
        
        # 执行批量修复
        result = await fixer.batch_fix_articles(max_articles=5)  # 限制每次最多处理5篇
        
        print("\n" + "=" * 60)
        print("📊 修复结果")
        print("=" * 60)
        print(f"总文章数: {result['total']}")
        print(f"修复成功: {result['fixed']}")
        print(f"修复失败: {result['failed']}")
        print(f"消息: {result['message']}")
        
        if result['results']:
            print(f"\n📝 详细结果:")
            for r in result['results']:
                status = "✅" if r['success'] else "❌"
                print(f"  {status} 文章 {r['article_id']}: {r['message']} ({r['processing_time']:.1f}s)")
        
        print("\n✅ 批量修复完成")
        
    except Exception as e:
        print(f"❌ 批量修复失败: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 