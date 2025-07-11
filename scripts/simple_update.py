#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("backend/newsmind.db")
cursor = conn.cursor()

# 更新原始内容
new_content = """中文翻译内容

特朗普在与以色列总理内塔尼亚胡会面后表示，加沙停火在几天内实现的可能性很大。

---

Original Content

Donald Trump says there's a "very good chance" of a Gaza ceasefire within days after meeting Israeli PM Netanyahu.

Trump made the statement on social media, saying: "Just had a great meeting with Prime Minister Netanyahu. We discussed the Gaza situation, and I think there's a very good chance of a ceasefire this week or next."

This statement has drawn widespread attention from the international community. Analysts believe Trump's statement may mark an important turning point in the Middle East situation."""

cursor.execute("""
    UPDATE processed_content 
    SET original_content_zh = ?, original_content_length = ?
    WHERE article_id = 62
""", (new_content, len(new_content)))

conn.commit()
print(f"更新完成，内容长度: {len(new_content)} 字符")
conn.close() 