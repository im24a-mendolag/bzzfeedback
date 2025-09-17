-- dependencies: 02_teachers
CREATE TABLE IF NOT EXISTS teacher_classes (
    teacher_id INT NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (teacher_id, class_name),
    CONSTRAINT fk_tc_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
