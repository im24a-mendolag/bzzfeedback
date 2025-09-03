-- dependencies: 03_subjects
CREATE TABLE IF NOT EXISTS feedback_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NULL,
    name VARCHAR(255) NOT NULL,
    CONSTRAINT fk_fc_subject FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
    UNIQUE KEY uniq_subject_name (subject_id, name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

