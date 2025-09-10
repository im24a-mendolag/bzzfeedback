-- dependencies: 01_users, 02_teachers, 03_subjects, 04_teacher_subjects, 05_feedback_categories

-- Default subjects
INSERT IGNORE INTO subjects (name) VALUES
('Mathematics'),
('English'),
('Science'),
('History');

-- Default teachers as users (set real password hashes later via app or script)
INSERT IGNORE INTO users (username, password_hash, role) VALUES
('alice', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('bob',   '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('admin', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'admin');

-- Ensure teachers table rows exist for these users
INSERT IGNORE INTO teachers (user_id)
SELECT u.id FROM users u WHERE u.username IN ('alice', 'bob');

-- Link teachers to subjects
INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Mathematics', 'English', 'Science')
WHERE u.username = 'alice';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('English', 'History')
WHERE u.username = 'bob';

-- Global feedback categories (subject_id NULL)
INSERT IGNORE INTO feedback_categories (subject_id, name) VALUES
(NULL, 'Homework'),
(NULL, 'Exams'),
(NULL, 'Pace'),
(NULL, 'Clarity');

