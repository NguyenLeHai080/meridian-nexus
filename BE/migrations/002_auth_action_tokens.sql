CREATE TABLE IF NOT EXISTS auth_action_tokens (
    token_hash VARCHAR(64) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    purpose VARCHAR(30) NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- statement
CREATE INDEX IF NOT EXISTS auth_action_tokens_user_purpose_index
ON auth_action_tokens(user_id, purpose);
-- statement
CREATE INDEX IF NOT EXISTS auth_action_tokens_expires_at_index
ON auth_action_tokens(expires_at);
