# 🎓 Harvard DASH → Azure AI → Supabase Pipeline

## 📋 Overview

This pipeline automatically fetches research papers from Harvard DASH, analyzes them using Azure AI (OpenAI), and stores the structured results in Supabase.

**Pipeline runs:**
- 🕐 Daily at 3 AM UTC
- 🔄 On every push to main branch
- 🎯 Manually via GitHub Actions

---

## 🚀 Quick Setup

### 1️⃣ Set up Supabase Database

Run this SQL in your Supabase SQL Editor:

```sql
-- Copy contents from supabase_harvard_schema.sql
```

Or use the SQL file:
```bash
cat supabase_harvard_schema.sql | supabase db execute
```

### 2️⃣ Configure GitHub Secrets

Go to your GitHub repository:
- **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 4 secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `AZURE_AI_ENDPOINT` | Azure OpenAI endpoint | `https://api.openai.com` |
| `AZURE_AI_KEY` | Azure OpenAI API key | `sk-proj-...` |
| `SUPABASE_URL` | Your Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase service role key | `eyJhbGc...` |

### 3️⃣ Push to GitHub

```bash
git add .
git commit -m "🎓 Add Harvard DASH pipeline with AI analysis"
git push origin main
```

### 4️⃣ Verify Workflow

1. Go to **Actions** tab in GitHub
2. You should see "Harvard DASH → Azure AI → Supabase Pipeline"
3. Click on the latest run
4. Check logs for:
   - ✅ Papers fetched
   - ✅ Azure AI analysis completed
   - ✅ Supabase insert successful

---

## 📁 Files Created

```
harvard-brainstem/
├── .github/
│   └── workflows/
│       └── harvard-pipeline.yml    # GitHub Actions workflow
├── ingest_harvard.py               # Main pipeline script
├── requirements.txt                # Python dependencies
├── supabase_harvard_schema.sql    # Database schema
└── PIPELINE_SETUP.md              # This file
```

---

## 🔧 Configuration

### Pipeline Settings

Edit `ingest_harvard.py` to customize:

```python
MAX_PAPERS_PER_RUN = 10  # Papers to process per run
MAX_TEXT_LENGTH = 8000   # Max chars sent to AI
```

### Schedule

Edit `.github/workflows/harvard-pipeline.yml`:

```yaml
schedule:
  - cron: '0 3 * * *'  # Daily at 3 AM UTC
```

Cron examples:
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1` - Every Monday at midnight
- `0 12 * * *` - Daily at noon

---

## 📊 Pipeline Flow

```
┌─────────────────────┐
│  Harvard DASH RSS   │
│  (Research Papers)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Fetch Papers       │
│  (feedparser)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Azure AI Analysis  │
│  (GPT-3.5-turbo)   │
│  • Topic            │
│  • Findings         │
│  • Methodology      │
│  • Significance     │
│  • Keywords         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Supabase Storage   │
│  (harvard_papers)   │
└─────────────────────┘
```

---

## 🧪 Testing Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables
```bash
export AZURE_AI_ENDPOINT="https://api.openai.com"
export AZURE_AI_KEY="sk-proj-..."
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="eyJhbGc..."
```

### 3. Run the script
```bash
python ingest_harvard.py
```

### Expected output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 HARVARD DASH → AZURE AI → SUPABASE PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ Started: 2025-01-19 15:30:00 UTC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All environment variables validated

📥 Fetching papers from Harvard DASH...
   Feed URL: https://dash.harvard.edu/feed/rss_1.0/site
✅ Fetched 10 papers from DASH

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Processing paper 1/10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 Analyzing: Legal Implications of AI in Healthcare...
   ✅ AI Analysis completed
   📊 Topic: Healthcare Law & AI Ethics

💾 Storing in Supabase...
   ✅ Supabase insert successful
   📊 Record ID: https://dash.harvard.edu/handle/1/...

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PIPELINE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Papers fetched:     10
   Successfully stored: 10
   Failed:             0
   Success rate:       100.0%
⏰ Completed: 2025-01-19 15:32:45 UTC
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Pipeline execution complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📊 Supabase Data Structure

### Table: `harvard_papers`

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Auto-incrementing ID |
| `paper_id` | TEXT | Unique paper identifier (from DASH) |
| `title` | TEXT | Paper title |
| `authors` | TEXT | Author names |
| `published_date` | TEXT | Publication date |
| `link` | TEXT | Link to paper |
| `summary` | TEXT | Paper abstract/summary |
| `ai_topic` | TEXT | AI-identified main topic |
| `ai_findings` | TEXT | JSON array of key findings |
| `ai_methodology` | TEXT | Research methodology |
| `ai_significance` | TEXT | Significance/impact |
| `ai_keywords` | TEXT | JSON array of keywords |
| `processed_at` | TIMESTAMPTZ | Processing timestamp |
| `source` | TEXT | Source (Harvard DASH) |
| `metadata` | JSONB | Additional metadata |

### Query Examples

```sql
-- Get all papers
SELECT * FROM harvard_papers ORDER BY processed_at DESC LIMIT 10;

-- Search by topic
SELECT title, ai_topic, ai_significance 
FROM harvard_papers 
WHERE ai_topic ILIKE '%AI%' 
ORDER BY processed_at DESC;

-- Get papers by author
SELECT title, authors, ai_keywords 
FROM harvard_papers 
WHERE authors ILIKE '%Smith%';

-- Count papers by topic
SELECT ai_topic, COUNT(*) 
FROM harvard_papers 
GROUP BY ai_topic 
ORDER BY COUNT(*) DESC;
```

---

## 🔍 Monitoring

### GitHub Actions Logs

View detailed logs:
1. Go to **Actions** tab
2. Click on workflow run
3. Expand "Run Harvard ingestion pipeline"
4. Look for:
   - ✅ Papers fetched: X
   - ✅ AI analysis completed
   - ✅ Supabase insert successful

### Supabase Dashboard

Monitor database:
1. Go to Supabase Dashboard
2. **Table Editor** → `harvard_papers`
3. Check latest entries
4. Verify `processed_at` timestamps

---

## ❓ Troubleshooting

### Pipeline fails with "Missing environment variables"

**Solution:** Add all 4 GitHub Secrets:
- `AZURE_AI_ENDPOINT`
- `AZURE_AI_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

### "No papers to process"

**Possible causes:**
- Harvard DASH RSS feed is down
- Feed format changed
- Network connectivity issues

**Solution:** Check feed manually:
```bash
curl https://dash.harvard.edu/feed/rss_1.0/site
```

### "AI Analysis failed"

**Possible causes:**
- Invalid OpenAI API key
- Rate limit exceeded
- Model unavailable

**Solution:**
- Verify API key is correct
- Check OpenAI billing
- Try switching model in `ingest_harvard.py`

### "Supabase insert failed"

**Possible causes:**
- Table doesn't exist
- Invalid credentials
- Schema mismatch

**Solution:**
1. Run `supabase_harvard_schema.sql`
2. Verify `SUPABASE_KEY` is service role key
3. Check table exists: `SELECT * FROM harvard_papers LIMIT 1;`

---

## 🎯 Advanced Features

### Custom AI Analysis

Edit the prompt in `ingest_harvard.py`:

```python
prompt = """Your custom analysis instructions here..."""
```

### Additional Data Sources

Add more RSS feeds:

```python
FEEDS = [
    "https://dash.harvard.edu/feed/rss_1.0/site",
    "https://example.edu/papers.rss",
]
```

### Email Notifications

Add to workflow:

```yaml
- name: Send notification
  if: success()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.MAIL_USERNAME }}
    password: ${{ secrets.MAIL_PASSWORD }}
    subject: ✅ Harvard Pipeline Success
    body: Pipeline processed ${{ env.PAPERS_COUNT }} papers
    to: you@example.com
```

---

## 📄 License

© 2025 AI-15 Neural Systems. All rights reserved.

---

## 🆘 Support

**Issues?**
- Check GitHub Actions logs
- Verify all secrets are set
- Test locally first
- Check Supabase table exists

**Questions?**
- Review this documentation
- Check Harvard DASH API docs
- Consult OpenAI API documentation
- Review Supabase Python client docs

---

<div align="center">

**🎓 Harvard Research Pipeline**

Powered by Azure AI + Supabase  
Automated via GitHub Actions

**Ready to process academic papers! 📚🧠💾**

</div>

