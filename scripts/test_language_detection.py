#!/usr/bin/env python3
"""
测试不同语言的识别 - 针对文章122
"""
import re

def detect_language_features(text):
    """检测文本的语言特征"""
    if not text:
        return {}
    
    text_lower = text.lower()
    
    features = {}
    
    # 德语特征
    german_words = ['der', 'die', 'das', 'und', 'ist', 'sind', 'für', 'mit', 'auf', 'von', 'zu', 'in', 'an', 'bei', 'nach', 'vor', 'über', 'unter', 'zwischen', 'hinter', 'neben', 'seit', 'während', 'wegen', 'trotz', 'ohne', 'gegen', 'um', 'durch', 'entlang', 'gegenüber', 'jenseits', 'diesseits', 'außerhalb', 'innerhalb']
    german_count = sum(1 for word in german_words if word in text_lower.split())
    features['german'] = german_count
    
    # 意大利语特征
    italian_words = ['il', 'la', 'lo', 'gli', 'le', 'di', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra', 'e', 'o', 'ma', 'se', 'che', 'chi', 'cui', 'quale', 'quali', 'quanto', 'quanta', 'quanti', 'quante', 'questo', 'questa', 'questi', 'queste', 'quello', 'quella', 'quelli', 'quelle', 'mio', 'mia', 'miei', 'mie', 'tuo', 'tua', 'tuoi', 'tue', 'suo', 'sua', 'suoi', 'sue']
    italian_count = sum(1 for word in italian_words if word in text_lower.split())
    features['italian'] = italian_count
    
    # 俄语特征
    russian_chars = re.findall(r'[\u0400-\u04ff]', text)
    features['russian_chars'] = len(russian_chars)
    
    # 法语特征
    french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'sont', 'pour', 'avec', 'sur', 'dans', 'par', 'que', 'qui', 'ce', 'cette', 'ces', 'un', 'une', 'au', 'aux', 'en', 'se', 'ne', 'pas', 'plus', 'moins', 'très', 'bien', 'bon', 'bonne', 'nouveau', 'nouvelle', 'grand', 'grande', 'petit', 'petite']
    french_count = sum(1 for word in french_words if word in text_lower.split())
    features['french'] = french_count
    
    # 西班牙语特征
    spanish_words = ['el', 'la', 'los', 'las', 'de', 'del', 'y', 'en', 'con', 'por', 'para', 'sin', 'sobre', 'entre', 'hacia', 'desde', 'hasta', 'durante', 'según', 'contra', 'ante', 'bajo', 'tras', 'mediante', 'excepto', 'salvo', 'además', 'también', 'muy', 'más', 'menos', 'bien', 'mal', 'bueno', 'buena', 'malo', 'mala']
    spanish_count = sum(1 for word in spanish_words if word in text_lower.split())
    features['spanish'] = spanish_count
    
    # 葡萄牙语特征
    portuguese_words = ['o', 'a', 'os', 'as', 'de', 'do', 'da', 'dos', 'das', 'e', 'em', 'com', 'por', 'para', 'sem', 'sobre', 'entre', 'até', 'desde', 'durante', 'segundo', 'contra', 'ante', 'sob', 'trás', 'mediante', 'exceto', 'salvo', 'além', 'também', 'muito', 'mais', 'menos', 'bem', 'mal', 'bom', 'boa', 'mau', 'má']
    portuguese_count = sum(1 for word in portuguese_words if word in text_lower.split())
    features['portuguese'] = portuguese_count
    
    return features

def test_article_122():
    """测试文章122的语言识别"""
    print("🧪 测试文章122的语言识别...")
    print("=" * 60)
    
    title = "China Should Invite Trump to Its Military Parade"
    
    print(f"标题: {title}")
    print()
    
    # 检测语言特征
    features = detect_language_features(title)
    
    print("语言特征分析:")
    for lang, count in features.items():
        print(f"  {lang}: {count}")
    
    print()
    
    # 尝试不同的语言翻译
    print("尝试不同语言的翻译:")
    
    # 德语翻译
    german_translation = "China sollte Trump zu seiner Militärparade einladen"
    print(f"🇩🇪 德语: {german_translation}")
    
    # 意大利语翻译
    italian_translation = "La Cina dovrebbe invitare Trump alla sua parata militare"
    print(f"🇮🇹 意大利语: {italian_translation}")
    
    # 俄语翻译
    russian_translation = "Китай должен пригласить Трампа на свой военный парад"
    print(f"🇷🇺 俄语: {russian_translation}")
    
    # 法语翻译
    french_translation = "La Chine devrait inviter Trump à son défilé militaire"
    print(f"🇫🇷 法语: {french_translation}")
    
    # 西班牙语翻译
    spanish_translation = "China debería invitar a Trump a su desfile militar"
    print(f"🇪🇸 西班牙语: {spanish_translation}")
    
    # 葡萄牙语翻译
    portuguese_translation = "A China deveria convidar Trump para seu desfile militar"
    print(f"🇵🇹 葡萄牙语: {portuguese_translation}")
    
    print()
    
    # 分析哪个最可能是原文
    print("分析结果:")
    print("  这个标题看起来是英语，因为:")
    print("  1. 使用了英语语法结构")
    print("  2. 没有其他语言的特定词汇")
    print("  3. 符合英语新闻标题的格式")
    
    print()
    print("  但是，如果原文是其他语言，可能的对应关系:")
    print("  - 德语: China sollte Trump zu seiner Militärparade einladen")
    print("  - 意大利语: La Cina dovrebbe invitare Trump alla sua parata militare")
    print("  - 俄语: Китай должен пригласить Трампа на свой военный парад")
    print("  - 法语: La Chine devrait inviter Trump à son défilé militaire")

def test_other_articles():
    """测试其他可能被错误识别的文章"""
    print("\n🔍 检查其他可能被错误识别的文章...")
    print("=" * 60)
    
    import sqlite3
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取所有英文文章
        cursor.execute("""
            SELECT id, title, source_name 
            FROM news_articles 
            WHERE original_language = 'en'
            ORDER BY id
        """)
        
        articles = cursor.fetchall()
        
        print("检查可能被错误标记为英文的文章:")
        for article_id, title, source_name in articles:
            features = detect_language_features(title)
            
            # 如果检测到其他语言特征
            max_lang = max(features.items(), key=lambda x: x[1]) if features else ('english', 0)
            
            if max_lang[1] > 2 and max_lang[0] != 'english':
                print(f"  🔍 文章 {article_id} ({source_name}):")
                print(f"      标题: {title}")
                print(f"      可能语言: {max_lang[0]} (特征数: {max_lang[1]})")
                print()
    
    finally:
        conn.close()

def main():
    """主函数"""
    print("🌍 语言识别测试工具")
    print("=" * 60)
    
    test_article_122()
    test_other_articles()
    
    print("\n🎯 测试完成!")
    print("   根据分析结果，可以确定正确的语言并重新翻译")

if __name__ == "__main__":
    main() 