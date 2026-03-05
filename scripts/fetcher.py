import os
import requests
import feedparser
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Absolute path handling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "blog", "src", "content", "patents")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", DEFAULT_OUTPUT)
BLOG_BASE_URL = "https://patent-summary-blog.vercel.app/patents"

# Configure Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
# Patent Sources
# ============================================================
# USPTO RSS feeds for newly published patent applications
# Google Patents also provides some RSS endpoints
SOURCES = [
    # USPTO - Latest Published Patent Applications (various tech categories)
    {
        "name": "USPTO - Computing",
        "url": "https://www.uspto.gov/rss/feeds/patapp/latest-computing.xml",
        "type": "rss",
    },
    {
        "name": "USPTO - Communications",
        "url": "https://www.uspto.gov/rss/feeds/patapp/latest-communications.xml",
        "type": "rss",
    },
    {
        "name": "USPTO - Electrical",
        "url": "https://www.uspto.gov/rss/feeds/patapp/latest-electrical.xml",
        "type": "rss",
    },
    # Google Patents RSS (search-based)
    {
        "name": "Google Patents - AI",
        "url": "https://patents.google.com/rss/search?q=artificial+intelligence&num=5&oq=artificial+intelligence",
        "type": "rss",
    },
    {
        "name": "Google Patents - VR/AR",
        "url": "https://patents.google.com/rss/search?q=virtual+reality+augmented+reality&num=5",
        "type": "rss",
    },
    {
        "name": "Google Patents - Robotics",
        "url": "https://patents.google.com/rss/search?q=robotics+automation&num=5",
        "type": "rss",
    },
    {
        "name": "Google Patents - EV Battery",
        "url": "https://patents.google.com/rss/search?q=electric+vehicle+battery&num=5",
        "type": "rss",
    },
]

# Fallback: scrape Google Patents search results if RSS fails
FALLBACK_SEARCHES = [
    {"name": "AI & Machine Learning", "query": "artificial+intelligence+machine+learning", "category": "AI"},
    {"name": "VR / AR", "query": "virtual+reality+augmented+reality+headset", "category": "VR/AR"},
    {"name": "Robotics", "query": "robotics+humanoid+automation", "category": "ロボティクス"},
    {"name": "EV & Battery", "query": "electric+vehicle+battery+charging", "category": "EV・バッテリー"},
    {"name": "Smartphone", "query": "smartphone+foldable+display", "category": "スマートフォン"},
    {"name": "Healthcare", "query": "medical+device+wearable+health", "category": "ヘルスケア"},
]


def fetch_rss(source):
    """Fetch patents from RSS feed."""
    print(f"  --> Fetching RSS: {source['name']}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(source["url"], timeout=15, headers=headers)
        feed = feedparser.parse(response.content)
        patents = []
        for entry in feed.entries[:5]:  # Limit to 5 per source
            patents.append({
                "title": entry.get("title", "No Title").strip(),
                "link": entry.get("link", ""),
                "source": source["name"],
                "published": entry.get("published", datetime.now().strftime("%Y-%m-%d")),
                "summary": entry.get("summary", entry.get("description", "No Summary")),
                "applicant": extract_applicant(entry),
            })
        print(f"  --> Found {len(patents)} entries.")
        return patents
    except Exception as e:
        print(f"  --> RSS Error for {source['name']}: {e}")
        return []


def extract_applicant(entry):
    """Try to extract applicant/assignee from feed entry."""
    # Different feeds store this in different fields
    for field in ["author", "dc_creator", "assignee"]:
        val = entry.get(field, "")
        if val:
            return val
    # Try to extract from summary/description
    summary = entry.get("summary", "")
    if "Applicant:" in summary:
        match = re.search(r"Applicant:\s*(.+?)(?:\n|<|$)", summary)
        if match:
            return match.group(1).strip()
    return "Unknown"


def fetch_google_patents_fallback():
    """Fallback: scrape Google Patents search results."""
    print("  --> Using Google Patents search fallback...")
    all_patents = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for search in FALLBACK_SEARCHES:
        try:
            url = f"https://patents.google.com/?q={search['query']}&oq={search['query']}&num=3&sort=new"
            response = requests.get(url, timeout=15, headers=headers)
            soup = BeautifulSoup(response.text, "lxml")
            
            # Extract patent entries from search results
            results = soup.select("search-result-item, article, .result")
            for result in results[:3]:
                title_el = result.select_one("h3, .result-title, span.style-scope")
                link_el = result.select_one("a[href]")
                
                title = title_el.get_text(strip=True) if title_el else "Unknown Patent"
                link = ""
                if link_el:
                    href = link_el.get("href", "")
                    if href.startswith("/patent/"):
                        link = f"https://patents.google.com{href}"
                    else:
                        link = href
                
                if title and title != "Unknown Patent":
                    all_patents.append({
                        "title": title,
                        "link": link,
                        "source": f"Google Patents - {search['name']}",
                        "published": datetime.now().strftime("%Y-%m-%d"),
                        "summary": f"Category: {search['category']}",
                        "applicant": "Unknown",
                    })
            
            time.sleep(2)  # Be polite
        except Exception as e:
            print(f"  --> Fallback error for {search['name']}: {e}")
    
    print(f"  --> Fallback found {len(all_patents)} patents total.")
    return all_patents


def get_patent_detail(link):
    """Try to fetch more details about a patent from its page."""
    if not link:
        return ""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(link, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        
        # Try to get abstract
        abstract = soup.select_one(".abstract, #abstract, .patent-abstract")
        if abstract:
            return abstract.get_text(strip=True)[:1000]
        
        # Try meta description
        meta = soup.select_one('meta[name="description"]')
        if meta:
            return meta.get("content", "")[:1000]
        
        return ""
    except Exception:
        return ""


def summarize_patent(patent):
    """Summarize patent using Gemini API - made for complete beginners!"""
    print(f"    - Summarizing: {patent['title'][:60]}...")
    
    # Try to get more detail if we only have a short summary
    extra_detail = ""
    if len(patent["summary"]) < 100 and patent["link"]:
        extra_detail = get_patent_detail(patent["link"])
    
    full_info = patent["summary"]
    if extra_detail:
        full_info += f"\n\n追加詳細: {extra_detail}"
    
    prompt = f"""
あなたは「難しい特許を、まるでテレビの面白ニュースのように楽しく伝える天才ライター」です。
読者はテクノロジーの専門家ではなく、普通の一般人です。小学生でも理解できるレベルで書いてください。

以下の特許情報を、とにかく面白く・分かりやすく日本語で紹介してください。
「この発明が実現したら、私たちの生活がどう変わるか？」を中心に書いてください。

【特許情報】
タイトル: {patent['title']}
出願者/企業: {patent['applicant']}
ソース: {patent['source']}
内容: {full_info}

【記事の構成 (必ずこの順番で書いてください)】

[JP_TITLE] 読者が思わずクリックしたくなる、ワクワクする日本語タイトル（20〜35文字程度）。
専門用語は使わず、「えっ、そんなことできるの！？」と思わせる書き方で。

[CATEGORY] 以下のうち最も適切なカテゴリを1つ:
AI, VR/AR, ロボティクス, EV・バッテリー, スマートフォン, ヘルスケア, コンピューティング, 通信, ディスプレイ, その他

[KEYWORD] 内容を象徴する英語キーワードを1つ（例: robot, vr, battery, phone）。画像検索に使います。

[APPLICANT] 出願企業名（分かる場合。分からなければ "不明"）

[SUMMARY]

## 🎯 ざっくり言うとこういう発明！

（3行で、小学生にも分かるように箇条書き。絵文字を使って楽しく！）

## 🔍 もうちょっと詳しく！

（技術的な内容を、身近な例えを使って解説。例えば「スマホのカメラが、まるで医者の目になるような技術です」のように。200〜300文字程度。）

## 🌍 もしこれが実現したら？

（この発明が商品化されたとき、私たちの日常がどう変わるかを具体的にイメージさせる。「朝起きたらロボットが朝食を作ってくれて…」のような書き方で。150〜250文字程度。）

## 💡 ちょっと豆知識

（この特許に関連する豆知識やトリビアを1つ。「実はAppleはこの分野で年間○○件の特許を出していて…」のような。）

## 🏷️ 関連キーワード

（関連する日本語キーワードをカンマ区切りで5つ程度）

【出力形式】
[JP_TITLE]、[CATEGORY]、[KEYWORD]、[APPLICANT] は必ず最初の数行に含めてください。
その後、Markdown形式で要約を出力してください。
"""
    
    models_to_try = ["gemini-2.5-flash", "gemini-3-flash"]
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response.text:
                if model_name != models_to_try[0]:
                    print(f"    - Success using fallback AI: {model_name}!")
                
                text = response.text
                jp_title = "最新の特許"
                category = "その他"
                keyword = "technology"
                applicant = "不明"
                
                lines = text.split("\n")
                for line in lines[:15]:
                    if "[JP_TITLE]" in line:
                        jp_title = line.replace("[JP_TITLE]", "").strip()
                    elif "[CATEGORY]" in line:
                        category = line.replace("[CATEGORY]", "").strip()
                    elif "[KEYWORD]" in line:
                        raw_keyword = line.replace("[KEYWORD]", "").strip().lower()
                        eng_match = re.match(r"([a-z]+)", raw_keyword)
                        keyword = eng_match.group(1) if eng_match else "technology"
                    elif "[APPLICANT]" in line:
                        applicant = line.replace("[APPLICANT]", "").strip()
                
                # Clean up the markdown content
                clean_content = text
                for tag in ["[JP_TITLE]", "[CATEGORY]", "[KEYWORD]", "[APPLICANT]"]:
                    clean_content = "\n".join(
                        [l for l in clean_content.split("\n") if tag not in l]
                    ).strip()
                
                return {
                    "jp_title": jp_title,
                    "category": category,
                    "keyword": keyword,
                    "applicant": applicant,
                    "content": clean_content,
                }
        except Exception as e:
            msg = str(e)[:100]
            print(f"    - Gemini Error with {model_name}: {msg}...")
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"    - Rate limited. Waiting 30 seconds...")
                time.sleep(30)
            continue
    
    print("    - All AI models failed. Skipping this patent.")
    return None


def save_to_markdown(patent, summary_data):
    """Save patent summary to markdown file."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    sanitized_name = "".join(
        [c for c in patent["title"][:40] if c.isalnum() or c == " "]
    ).rstrip().replace(" ", "-")
    filename = f"{date_str}-{sanitized_name}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    keyword = summary_data.get("keyword", "technology")
    slug = filename.replace(".md", "")
    image_url = f"https://picsum.photos/seed/{keyword}-{slug}/800/450"
    
    content = f"""---
title: "{summary_data['jp_title'].replace('"', "'")}"
original_title: "{patent['title'].replace('"', "'")}"
date: "{date_str}"
category: "{summary_data['category']}"
image: "{image_url}"
original_link: "{patent['link']}"
source: "{patent['source']}"
applicant: "{summary_data.get('applicant', '不明')}"
---

{summary_data['content']}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  --> Saved to Blog: {filepath}")
    return filepath


def main():
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        print("Error: GEMINI_API_KEY not found in .env")
        return
    
    print("=" * 60)
    print("  Patent Summary Blog - Auto Fetcher")
    print("=" * 60)
    
    # Fetch from all RSS sources
    all_patents = []
    for source in SOURCES:
        all_patents.extend(fetch_rss(source))
        time.sleep(1)
    
    # If RSS didn't return enough, use fallback
    if len(all_patents) < 3:
        print("  --> RSS returned few results, trying fallback...")
        all_patents.extend(fetch_google_patents_fallback())
    
    # Deduplicate
    unique_patents = []
    seen = set()
    for p in all_patents:
        key = p["link"] if p["link"] else p["title"]
        if key not in seen:
            seen.add(key)
            unique_patents.append(p)
    
    # Skip already-saved patents
    existing_links = set()
    existing_titles = set()
    if os.path.exists(OUTPUT_DIR):
        for fname in os.listdir(OUTPUT_DIR):
            if fname.endswith(".md"):
                fpath = os.path.join(OUTPUT_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as ef:
                        for line in ef:
                            if line.startswith("original_link:"):
                                link = line.split(":", 1)[1].strip().strip('"').strip("'")
                                existing_links.add(link)
                            if line.startswith("original_title:"):
                                title = line.split(":", 1)[1].strip().strip('"').strip("'")
                                existing_titles.add(title)
                except:
                    pass
    
    new_patents = [
        p for p in unique_patents
        if p["link"] not in existing_links and p["title"] not in existing_titles
    ]
    print(f"\nFound {len(unique_patents)} unique patents, {len(new_patents)} are new.")
    
    # Process top 3
    count = 0
    consecutive_failures = 0
    for patent in new_patents:
        if count >= 3:
            break
        if consecutive_failures >= 5:
            print("    - Too many consecutive failures. Stopping.")
            break
        
        summary_data = summarize_patent(patent)
        if summary_data:
            consecutive_failures = 0
            save_to_markdown(patent, summary_data)
            count += 1
            time.sleep(2)
        else:
            consecutive_failures += 1
    
    print(f"\nExecution complete! {count} patents summarized.")


if __name__ == "__main__":
    main()
