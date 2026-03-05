import os
import requests
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Absolute path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "blog", "src", "content", "patents")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", DEFAULT_OUTPUT)

# Configure Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
# Strategy: Use Gemini with Google Search grounding to find
# and summarize the latest patents. This is more reliable than
# trying to scrape patent databases directly.
# ============================================================

PATENT_TOPICS = [
    {"topic": "Apple latest patent 2025 2026", "category": "スマートフォン", "company": "Apple"},
    {"topic": "Google latest AI patent 2025 2026", "category": "AI", "company": "Google"},
    {"topic": "Sony latest patent technology 2025 2026", "category": "VR/AR", "company": "Sony"},
    {"topic": "Tesla latest patent electric vehicle 2025 2026", "category": "EV・バッテリー", "company": "Tesla"},
    {"topic": "Samsung latest patent display 2025 2026", "category": "ディスプレイ", "company": "Samsung"},
    {"topic": "Toyota latest patent robot autonomous 2025 2026", "category": "ロボティクス", "company": "Toyota"},
    {"topic": "Meta latest patent VR AR headset 2025 2026", "category": "VR/AR", "company": "Meta"},
    {"topic": "Microsoft latest patent AI computing 2025 2026", "category": "AI", "company": "Microsoft"},
    {"topic": "NVIDIA latest patent GPU AI chip 2025 2026", "category": "コンピューティング", "company": "NVIDIA"},
]


def generate_patent_articles(num_articles=3):
    """Use Gemini to find and create articles about real recent patents."""
    print(f"  --> Generating {num_articles} patent articles using Gemini...")
    
    # Get list of existing article titles to avoid duplicates
    existing_titles = set()
    if os.path.exists(OUTPUT_DIR):
        for fname in os.listdir(OUTPUT_DIR):
            if fname.endswith(".md"):
                fpath = os.path.join(OUTPUT_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as ef:
                        for line in ef:
                            if line.startswith("original_title:"):
                                title = line.split(":", 1)[1].strip().strip('"').strip("'")
                                existing_titles.add(title.lower().strip())
                                break
                except:
                    pass
    
    existing_list = "\n".join(existing_titles) if existing_titles else "なし"
    
    # Select topics based on rotation to get variety
    day_offset = int(datetime.now().strftime("%j")) % len(PATENT_TOPICS)
    selected_topics = []
    for i in range(num_articles + 2):  # Extra in case some fail
        idx = (day_offset + i) % len(PATENT_TOPICS)
        selected_topics.append(PATENT_TOPICS[idx])
    
    topics_text = "\n".join([f"- {t['company']}: {t['topic']} (カテゴリ: {t['category']})" for t in selected_topics[:num_articles]])
    
    prompt = f"""
あなたは特許専門の記者です。以下の企業の最新の特許について、実在する特許情報を基に記事を作成してください。

【対象企業と分野】
{topics_text}

【重要なルール】
1. 実際に存在する特許、または既に報道されている特許出願に基づいて書いてください
2. 特許番号が分かる場合は含めてください
3. 以下のタイトルは既に記事にしているので、絶対に重複しないでください：
{existing_list}

【各記事のフォーマット】
各記事は以下の区切り文字で区切ってください：
===ARTICLE_START===

[ORIGINAL_TITLE] 英語の元タイトル（できるだけ実際の特許タイトルに近いもの）
[JP_TITLE] 読者が思わずクリックしたくなる日本語タイトル（20〜35文字）。専門用語は使わない。
[CATEGORY] カテゴリ（AI, VR/AR, ロボティクス, EV・バッテリー, スマートフォン, ヘルスケア, コンピューティング, 通信, ディスプレイ, その他 から1つ）
[KEYWORD] 英語キーワード1つ（例: robot, vr, battery）
[APPLICANT] 出願企業名
[PATENT_LINK] Google Patentsのリンク（分かる場合。分からなければ空欄）

[CONTENT]

## 🎯 ざっくり言うとこういう発明！

（3行で、小学生にも分かるように箇条書き。絵文字を使って楽しく！）

## 🔍 もうちょっと詳しく！

（技術的な内容を、身近な例えを使って分かりやすく解説。200〜300文字程度。）

## 🌍 もしこれが実現したら？

（この発明が商品化されたとき、私たちの日常がどう変わるかを具体的にイメージさせる。150〜250文字程度。）

## 💡 ちょっと豆知識

（この特許に関連する面白いトリビアを1つ。）

## 🏷️ 関連キーワード

（関連する日本語キーワードをカンマ区切りで5つ程度）

===ARTICLE_END===

{num_articles}記事を生成してください。
"""
    
    models_to_try = ["gemini-2.5-flash", "gemini-3-flash"]
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response.text:
                return parse_articles(response.text)
        except Exception as e:
            msg = str(e)[:100]
            print(f"    - Gemini Error with {model_name}: {msg}...")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"    - Rate limited. Waiting 30 seconds...")
                time.sleep(30)
            continue
    
    print("    - All AI models failed.")
    return []


def parse_articles(text):
    """Parse multiple articles from Gemini response."""
    articles = []
    
    # Split by article delimiter
    raw_articles = text.split("===ARTICLE_START===")
    
    for raw in raw_articles:
        if "===ARTICLE_END===" not in raw:
            continue
        
        article_text = raw.split("===ARTICLE_END===")[0].strip()
        
        if not article_text:
            continue
        
        article = {
            "original_title": "",
            "jp_title": "最新の特許",
            "category": "その他",
            "keyword": "technology",
            "applicant": "不明",
            "patent_link": "",
            "content": "",
        }
        
        lines = article_text.split("\n")
        content_started = False
        content_lines = []
        
        for line in lines:
            if "[ORIGINAL_TITLE]" in line:
                article["original_title"] = line.replace("[ORIGINAL_TITLE]", "").strip()
            elif "[JP_TITLE]" in line:
                article["jp_title"] = line.replace("[JP_TITLE]", "").strip()
            elif "[CATEGORY]" in line:
                article["category"] = line.replace("[CATEGORY]", "").strip()
            elif "[KEYWORD]" in line:
                raw_kw = line.replace("[KEYWORD]", "").strip().lower()
                eng_match = re.match(r"([a-z]+)", raw_kw)
                article["keyword"] = eng_match.group(1) if eng_match else "technology"
            elif "[APPLICANT]" in line:
                article["applicant"] = line.replace("[APPLICANT]", "").strip()
            elif "[PATENT_LINK]" in line:
                article["patent_link"] = line.replace("[PATENT_LINK]", "").strip()
            elif "[CONTENT]" in line:
                content_started = True
            elif content_started:
                content_lines.append(line)
            elif line.startswith("## "):
                # Content started without explicit [CONTENT] marker
                content_started = True
                content_lines.append(line)
        
        article["content"] = "\n".join(content_lines).strip()
        
        if article["content"] and article["jp_title"] != "最新の特許":
            articles.append(article)
            print(f"    - Parsed: {article['jp_title'][:40]}...")
    
    return articles


def save_article(article):
    """Save a single article to markdown."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    sanitized_name = "".join(
        [c for c in article["original_title"][:40] if c.isalnum() or c == " "]
    ).rstrip().replace(" ", "-")
    
    if not sanitized_name:
        sanitized_name = "".join(
            [c for c in article["jp_title"][:20] if c.isalnum() or c == " " or ord(c) > 127]
        ).rstrip().replace(" ", "-")
    
    filename = f"{date_str}-{sanitized_name}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    keyword = article.get("keyword", "technology")
    slug = filename.replace(".md", "")
    image_url = f"https://picsum.photos/seed/{keyword}-{slug}/800/450"
    
    link = article.get("patent_link", "")
    if not link or link == "空欄":
        link = ""
    
    content = f"""---
title: "{article['jp_title'].replace('"', "'")}"
original_title: "{article['original_title'].replace('"', "'")}"
date: "{date_str}"
category: "{article['category']}"
image: "{image_url}"
original_link: "{link}"
source: "Patent Research"
applicant: "{article.get('applicant', '不明')}"
---

{article['content']}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  --> Saved: {filepath}")
    return filepath


def main():
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        print("Error: GEMINI_API_KEY not found in .env")
        return
    
    print("=" * 60)
    print("  Patent Insider - Auto Fetcher")
    print("=" * 60)
    
    articles = generate_patent_articles(num_articles=3)
    
    if not articles:
        print("\nNo articles generated. Check API status.")
        return
    
    count = 0
    for article in articles:
        filepath = save_article(article)
        count += 1
    
    print(f"\nExecution complete! {count} patent articles created.")


if __name__ == "__main__":
    main()
