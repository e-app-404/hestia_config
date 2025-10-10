PRAGMA journal_mode=WAL;
PRAGMA synchronous = NORMAL;

CREATE TABLE IF NOT EXISTS room_configs (
  room_id        TEXT NOT NULL,
  config_domain  TEXT NOT NULL,
  config_data    TEXT NOT NULL,
  version        INTEGER DEFAULT 1,
  created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (room_id, config_domain)
);

CREATE INDEX IF NOT EXISTS idx_room_configs_domain_room
  ON room_configs (config_domain, room_id);

CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);
INSERT OR IGNORE INTO schema_version(version) VALUES(1);
