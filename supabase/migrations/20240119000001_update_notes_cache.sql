-- Add caching fields to notes table
ALTER TABLE notes
ADD COLUMN content_type TEXT CHECK (content_type IN ('news', 'filing', 'research')),
ADD COLUMN query_hash TEXT,
ADD COLUMN metadata JSONB;

CREATE INDEX idx_notes_query_hash ON notes(query_hash, content_type);
CREATE INDEX idx_notes_content_type_ts ON notes(content_type, ts DESC);

COMMENT ON COLUMN notes.content_type IS 'Type of cached content for TTL management';
COMMENT ON COLUMN notes.query_hash IS 'SHA256 hash of query for cache key';
COMMENT ON COLUMN notes.metadata IS 'Additional context (title, rank, published date)';

