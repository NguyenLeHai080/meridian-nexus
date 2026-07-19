ALTER TABLE users ADD COLUMN mfa_secret VARCHAR(512) NULL;
-- statement
ALTER TABLE users ADD COLUMN mfa_enabled_at DATETIME NULL;
-- statement
ALTER TABLE users ADD COLUMN mfa_last_used_step INTEGER NULL;
-- statement
CREATE TABLE IF NOT EXISTS mfa_recovery_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code_hash VARCHAR(64) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- statement
CREATE INDEX IF NOT EXISTS mfa_recovery_codes_user_id_index ON mfa_recovery_codes(user_id);
