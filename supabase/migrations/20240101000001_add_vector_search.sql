-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to notes table
ALTER TABLE notes ADD COLUMN embedding vector(1536);

-- Create index for vector similarity search
CREATE INDEX ON notes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Function to search notes by similarity
CREATE OR REPLACE FUNCTION search_notes(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 10,
  filter_user_id uuid DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  chunk text,
  source text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    notes.id,
    notes.chunk,
    notes.source,
    1 - (notes.embedding <=> query_embedding) AS similarity
  FROM notes
  WHERE 
    (filter_user_id IS NULL OR notes.user_id = filter_user_id)
    AND 1 - (notes.embedding <=> query_embedding) > match_threshold
  ORDER BY notes.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

