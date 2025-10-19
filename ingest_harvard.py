#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 HARVARD DASH → AZURE AI → SUPABASE PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Fetches Harvard DASH papers, analyzes with Azure AI (OpenAI),
and stores structured results in Supabase database.

© 2025 AI-15 Neural Systems
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import json
import feedparser
import requests
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI
from supabase import create_client, Client

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Harvard DASH RSS Feed
DASH_RSS_FEED = "https://dash.harvard.edu/feed/rss_1.0/site"

# Azure AI / OpenAI Configuration
AZURE_AI_ENDPOINT = os.environ.get("AZURE_AI_ENDPOINT")
AZURE_AI_KEY = os.environ.get("AZURE_AI_KEY")

# Supabase Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Processing limits
MAX_PAPERS_PER_RUN = 10  # Process up to 10 papers per run
MAX_TEXT_LENGTH = 8000   # Max characters to send to AI

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 VALIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def validate_environment() -> bool:
    """Validate all required environment variables are set."""
    required = {
        "AZURE_AI_ENDPOINT": AZURE_AI_ENDPOINT,
        "AZURE_AI_KEY": AZURE_AI_KEY,
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY,
    }
    
    missing = [name for name, value in required.items() if not value]
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        return False
    
    print("✅ All environment variables validated")
    return True

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📥 HARVARD DASH FETCHING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_harvard_papers() -> List[Dict]:
    """Fetch papers from Harvard DASH RSS feed."""
    print(f"\n📥 Fetching papers from Harvard DASH...")
    print(f"   Feed URL: {DASH_RSS_FEED}")
    
    try:
        feed = feedparser.parse(DASH_RSS_FEED)
        
        if not feed.entries:
            print("⚠️ No entries found in feed")
            return []
        
        papers = []
        for entry in feed.entries[:MAX_PAPERS_PER_RUN]:
            paper = {
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
                "authors": entry.get("author", "Unknown"),
                "id": entry.get("id", entry.get("link", "")),
            }
            papers.append(paper)
        
        print(f"✅ Fetched {len(papers)} papers from DASH")
        return papers
    
    except Exception as e:
        print(f"❌ Error fetching papers: {str(e)}")
        return []

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧠 AZURE AI ANALYSIS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_paper_with_ai(paper: Dict) -> Optional[Dict]:
    """Analyze paper using Azure AI (OpenAI)."""
    print(f"\n🧠 Analyzing: {paper['title'][:60]}...")
    
    try:
        # Initialize OpenAI client with Azure endpoint
        client = OpenAI(
            api_key=AZURE_AI_KEY,
            base_url=AZURE_AI_ENDPOINT if AZURE_AI_ENDPOINT.endswith('/v1') else f"{AZURE_AI_ENDPOINT}/v1"
        )
        
        # Prepare text for analysis
        text_to_analyze = f"""
Title: {paper['title']}
Authors: {paper['authors']}
Published: {paper['published']}

Summary:
{paper['summary'][:MAX_TEXT_LENGTH]}
"""
        
        # AI Analysis Prompt
        prompt = """You are an expert academic paper analyzer. Analyze this Harvard research paper and provide a structured response with:

1. Main Topic/Field (one phrase)
2. Key Findings (2-3 bullet points)
3. Methodology (brief description)
4. Significance (1-2 sentences)
5. Keywords (5-7 relevant terms)

Format your response as clean JSON with keys: topic, findings, methodology, significance, keywords"""
        
        # Call Azure AI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text_to_analyze}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        # Extract analysis
        analysis_text = response.choices[0].message.content.strip()
        
        # Try to parse as JSON
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # If not JSON, create structured format
            analysis = {
                "topic": "Academic Research",
                "findings": [analysis_text[:200]],
                "methodology": "See summary",
                "significance": analysis_text[:300],
                "keywords": ["research", "Harvard", "academic"]
            }
        
        print(f"   ✅ AI Analysis completed")
        print(f"   📊 Topic: {analysis.get('topic', 'N/A')}")
        
        return analysis
    
    except Exception as e:
        print(f"   ❌ AI Analysis failed: {str(e)}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💾 SUPABASE STORAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def store_in_supabase(paper: Dict, analysis: Dict) -> bool:
    """Store analyzed paper in Supabase."""
    print(f"\n💾 Storing in Supabase...")
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Prepare data for insertion
        data = {
            "paper_id": paper["id"],
            "title": paper["title"],
            "authors": paper["authors"],
            "published_date": paper["published"],
            "link": paper["link"],
            "summary": paper["summary"][:500],  # Truncate summary
            "ai_topic": analysis.get("topic", ""),
            "ai_findings": json.dumps(analysis.get("findings", [])),
            "ai_methodology": analysis.get("methodology", ""),
            "ai_significance": analysis.get("significance", ""),
            "ai_keywords": json.dumps(analysis.get("keywords", [])),
            "processed_at": datetime.utcnow().isoformat(),
            "source": "Harvard DASH",
            "metadata": json.dumps({
                "feed_url": DASH_RSS_FEED,
                "processed_by": "harvard-pipeline",
                "ai_model": "gpt-3.5-turbo"
            })
        }
        
        # Insert into harvard_papers table (upsert to avoid duplicates)
        result = supabase.table("harvard_papers").upsert(
            data,
            on_conflict="paper_id"
        ).execute()
        
        if result.data:
            print(f"   ✅ Supabase insert successful")
            print(f"   📊 Record ID: {paper['id'][:40]}...")
            return True
        else:
            print(f"   ⚠️ Insert returned no data")
            return False
    
    except Exception as e:
        print(f"   ❌ Supabase insert failed: {str(e)}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 MAIN PIPELINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Main pipeline execution."""
    print("\n" + "━" * 65)
    print("🎓 HARVARD DASH → AZURE AI → SUPABASE PIPELINE")
    print("━" * 65)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("━" * 65)
    
    # Step 1: Validate environment
    if not validate_environment():
        print("\n❌ Pipeline aborted due to configuration errors")
        sys.exit(1)
    
    # Step 2: Fetch papers
    papers = fetch_harvard_papers()
    if not papers:
        print("\n⚠️ No papers to process")
        print("━" * 65)
        return
    
    # Step 3: Process each paper
    successful = 0
    failed = 0
    
    for i, paper in enumerate(papers, 1):
        print(f"\n{'━' * 65}")
        print(f"📄 Processing paper {i}/{len(papers)}")
        print(f"{'━' * 65}")
        
        # Analyze with AI
        analysis = analyze_paper_with_ai(paper)
        if not analysis:
            failed += 1
            continue
        
        # Store in Supabase
        if store_in_supabase(paper, analysis):
            successful += 1
        else:
            failed += 1
    
    # Step 4: Summary
    print(f"\n{'━' * 65}")
    print("📊 PIPELINE SUMMARY")
    print(f"{'━' * 65}")
    print(f"   Papers fetched:     {len(papers)}")
    print(f"   Successfully stored: {successful}")
    print(f"   Failed:             {failed}")
    print(f"   Success rate:       {(successful/len(papers)*100):.1f}%")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("━" * 65)
    print("✅ Pipeline execution complete!")
    print("━" * 65 + "\n")

if __name__ == "__main__":
    main()

