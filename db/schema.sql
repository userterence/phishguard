CREATE DATABASE IF NOT EXISTS phishguard CHARACTER SET utf8mb4;
USE phishguard;

CREATE TABLE users (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  email         VARCHAR(190) NOT NULL UNIQUE,
  full_name     VARCHAR(190) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('admin','student','teacher') NOT NULL,
  is_active     TINYINT(1) NOT NULL DEFAULT 1,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scans (
  id             BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id        BIGINT NULL,
  url            VARCHAR(2048) NOT NULL,
  domain         VARCHAR(255) NOT NULL,
  status         ENUM('safe','suspicious','phishing') NOT NULL,
  category       VARCHAR(40) NULL,   -- academic|scholarship|account|enrollment|none
  confidence     FLOAT NULL,
  reasons        JSON NULL,
  source         ENUM('extension','dashboard') DEFAULT 'extension',
  created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_scans_user (user_id),
  INDEX idx_scans_status (status),
  INDEX idx_scans_created (created_at),
  CONSTRAINT fk_scans_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE reports (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id      BIGINT NOT NULL,
  url          VARCHAR(2048) NOT NULL,
  category     VARCHAR(40) NOT NULL,
  description  TEXT NULL,
  status       ENUM('pending','verified','rejected','false_positive') NOT NULL DEFAULT 'pending',
  reviewer_id  BIGINT NULL,
  review_note  TEXT NULL,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_rep_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_rep_rev  FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE site_list (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,
  domain     VARCHAR(255) NOT NULL UNIQUE,
  list_type  ENUM('trusted','blocked') NOT NULL,
  added_by   BIGINT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifications (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id     BIGINT NULL,           -- NULL = broadcast
  title       VARCHAR(190) NOT NULL,
  body        TEXT NOT NULL,
  is_read     TINYINT(1) DEFAULT 0,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
