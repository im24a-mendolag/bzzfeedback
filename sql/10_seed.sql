-- dependencies: 01_users, 02_teachers, 03_subjects, 04_teacher_subjects, 05_feedback_categories, 08_teacher_classes

-- Default subjects
INSERT IGNORE INTO subjects (name) VALUES
('Mathematics'),
('English'),
('Science'),
('History'),
('Physics'),
('Chemistry'),
('Biology'),
('Geography'),
('Art'),
('Music'),
('Physical Education'),
('Computer Science'),
('Economics'),
('Psychology'),
('Literature'),
('Foreign Language');

-- Default teachers as users (set real password hashes later via app or script)
INSERT IGNORE INTO users (username, password_hash, role) VALUES
('alice', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('bob',   '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('charlie', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('diana', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('eve', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('frank', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('grace', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('henry', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('isabel', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('jack', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('kate', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('liam', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('maya', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('noah', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('olivia', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'teacher'),
('admin', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'admin');

-- Demo students with classes
INSERT IGNORE INTO users (username, password_hash, role, class_name) VALUES
('student1', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'student', 'Grade 10A'),
('student2', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'student', 'Grade 10A'),
('student3', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'student', 'Grade 11B'),
('student4', '$2b$12$R2p8Q9u7l7wJpQw9xQw9xO3cT9K0wQw9xQw9xO3cT9K0wQw9xQw9xO', 'student', 'Grade 11B');

-- Ensure teachers table rows exist for these users
INSERT IGNORE INTO teachers (user_id)
SELECT u.id FROM users u WHERE u.username IN ('alice', 'bob', 'charlie', 'diana', 'eve', 'frank', 'grace', 'henry', 'isabel', 'jack', 'kate', 'liam', 'maya', 'noah', 'olivia');

-- Link teachers to subjects (diverse subject assignments)
INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Mathematics', 'Physics')
WHERE u.username = 'alice';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('English', 'Literature')
WHERE u.username = 'bob';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Chemistry', 'Biology')
WHERE u.username = 'charlie';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('History', 'Geography')
WHERE u.username = 'diana';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Mathematics', 'Computer Science')
WHERE u.username = 'eve';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Art', 'Music')
WHERE u.username = 'frank';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Physical Education', 'Psychology')
WHERE u.username = 'grace';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Economics', 'Foreign Language')
WHERE u.username = 'henry';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Science', 'Biology')
WHERE u.username = 'isabel';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Mathematics', 'Physics')
WHERE u.username = 'jack';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('English', 'Foreign Language')
WHERE u.username = 'kate';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('History', 'Economics')
WHERE u.username = 'liam';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Art', 'Literature')
WHERE u.username = 'maya';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Computer Science', 'Mathematics')
WHERE u.username = 'noah';

INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
SELECT t.id, s.id
FROM teachers t
JOIN users u ON u.id = t.user_id
JOIN subjects s ON s.name IN ('Music', 'Psychology')
WHERE u.username = 'olivia';

-- Link teachers to classes they teach (ensuring each class has 3+ teachers)
-- Grade 9A: alice, charlie, isabel
INSERT IGNORE INTO teacher_classes (teacher_id, class_name)
SELECT t.id, 'Grade 9A'
FROM teachers t
JOIN users u ON u.id = t.user_id
WHERE u.username IN ('alice', 'charlie', 'isabel');

-- Grade 9B: bob, diana, jack
INSERT IGNORE INTO teacher_classes (teacher_id, class_name)
SELECT t.id, 'Grade 9B'
FROM teachers t
JOIN users u ON u.id = t.user_id
WHERE u.username IN ('bob', 'diana', 'jack');

-- Grade 10A: alice, eve, kate
INSERT IGNORE INTO teacher_classes (teacher_id, class_name)
SELECT t.id, 'Grade 10A'
FROM teachers t
JOIN users u ON u.id = t.user_id
WHERE u.username IN ('alice', 'eve', 'kate');

-- Grade 10B: bob, frank, liam
INSERT IGNORE INTO teacher_classes (teacher_id, class_name)
SELECT t.id, 'Grade 10B'
FROM teachers t
JOIN users u ON u.id = t.user_id
WHERE u.username IN ('bob', 'frank', 'liam');

-- Grade 11A: charlie, grace, maya
INSERT IGNORE INTO teacher_classes (teacher_id, class_name)
SELECT t.id, 'Grade 11A'
FROM teachers t
JOIN users u ON u.id = t.user_id
WHERE u.username IN ('charlie', 'grace', 'maya');

-- Grade 11B: diana, henry, noah
INSERT IGNORE INTO teacher_classes (teacher_id, class_name)
SELECT t.id, 'Grade 11B'
FROM teachers t
JOIN users u ON u.id = t.user_id
WHERE u.username IN ('diana', 'henry', 'noah');

-- Grade 12A: eve, alice, olivia
INSERT IGNORE INTO teacher_classes (teacher_id, class_name)
SELECT t.id, 'Grade 12A'
FROM teachers t
JOIN users u ON u.id = t.user_id
WHERE u.username IN ('eve', 'alice', 'olivia');

-- Grade 12B: frank, bob, isabel
INSERT IGNORE INTO teacher_classes (teacher_id, class_name)
SELECT t.id, 'Grade 12B'
FROM teachers t
JOIN users u ON u.id = t.user_id
WHERE u.username IN ('frank', 'bob', 'isabel');

-- Global feedback categories (subject_id NULL)
INSERT IGNORE INTO feedback_categories (subject_id, name) VALUES
(NULL, 'Homework'),
(NULL, 'Exams'),
(NULL, 'Pace'),
(NULL, 'Clarity');

