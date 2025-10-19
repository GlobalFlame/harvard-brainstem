-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- 🎓 HARVARD PAPERS DATABASE SCHEMA
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- Table for storing Harvard DASH papers with AI analysis results
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- Drop table if exists (for clean setup)
DROP TABLE IF EXISTS harvard_papers;

-- Create harvard_papers table
CREATE TABLE harvard_papers (
    -- Primary identification
    id BIGSERIAL PRIMARY KEY,
    paper_id TEXT UNIQUE NOT NULL,
    
    -- Paper metadata
    title TEXT NOT NULL,
    authors TEXT,
    published_date TEXT,
    link TEXT,
    summary TEXT,
    
    -- AI analysis results
    ai_topic TEXT,
    ai_findings TEXT,  -- JSON array as text
    ai_methodology TEXT,
    ai_significance TEXT,
    ai_keywords TEXT,  -- JSON array as text
    
    -- Processing metadata
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source TEXT DEFAULT 'Harvard DASH',
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_harvard_papers_paper_id ON harvard_papers(paper_id);
CREATE INDEX idx_harvard_papers_title ON harvard_papers(title);
CREATE INDEX idx_harvard_papers_processed_at ON harvard_papers(processed_at DESC);
CREATE INDEX idx_harvard_papers_ai_topic ON harvard_papers(ai_topic);

-- Enable Row Level Security (optional)
ALTER TABLE harvard_papers ENABLE ROW LEVEL SECURITY;

-- Create policy for authenticated users (adjust as needed)
CREATE POLICY "Enable read access for all users" ON harvard_papers
    FOR SELECT
    USING (true);

CREATE POLICY "Enable insert for service role" ON harvard_papers
    FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Enable update for service role" ON harvard_papers
    FOR UPDATE
    USING (true);

-- Create trigger to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_harvard_papers_updated_at
    BEFORE UPDATE ON harvard_papers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- ✅ SCHEMA CREATED SUCCESSFULLY
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- Next steps:
-- 1. Run this SQL in your Supabase SQL Editor
-- 2. Verify table exists: SELECT * FROM harvard_papers LIMIT 1;
-- 3. Run the GitHub Actions pipeline
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

