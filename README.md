# BZZ Feedback System

A comprehensive web-based feedback management system built with Flask and MySQL, designed for educational institutions to facilitate anonymous feedback between students and teachers.

## 🎯 Overview

BZZ Feedback is a secure, role-based feedback platform that allows students to submit anonymous feedback to their teachers across different subjects and categories. Teachers can view, manage, and respond to feedback while maintaining student privacy through optional anonymity features.

## ✨ Key Features

### For Students
- **Anonymous Feedback Submission**: Submit feedback with optional anonymity
- **Class-Based Teacher Filtering**: Only see teachers that teach your specific class
- **Subject-Based Organization**: Choose from 16+ subjects and teachers
- **Categorized Feedback**: Use predefined categories or create custom feedback
- **Thread-Based Discussions**: Engage in follow-up conversations with teachers
- **Modern Dashboard**: Beautiful, responsive interface with teacher avatars
- **Enhanced Forms**: Intuitive feedback submission with helpful guidance

### For Teachers
- **Feedback Management**: View and organize feedback by subject
- **Read Status Tracking**: Mark feedback as read/unread
- **Subject Assignment**: Manage assigned subjects
- **Class Assignment**: Manage which classes you teach
- **Response System**: Reply to student feedback in threaded conversations
- **Analytics Dashboard**: Track feedback statistics and trends

### For Administrators
- **User Management**: Create and manage student/teacher accounts
- **Subject Administration**: Add, edit, and assign subjects
- **Class Management**: Assign teachers to specific classes
- **Feedback Moderation**: Approve, reject, or moderate feedback submissions
- **System Analytics**: Monitor platform usage and feedback patterns

## 🛠️ Technology Stack

- **Backend**: Flask 3.0.0 (Python web framework)
- **Database**: MySQL 8.0+ with connection pooling
- **Authentication**: Flask-Login with secure password hashing
- **Frontend**: Modern CSS with CSS Grid/Flexbox, responsive design
- **UI/UX**: Clean, accessible interface with smooth animations
- **Typography**: Inter font family for optimal readability
- **Logging**: Rotating file handlers with configurable levels
- **Testing**: pytest with comprehensive test coverage
- **Deployment**: Gunicorn WSGI server ready

## 📋 Prerequisites

- Python 3.8+
- MySQL 8.0+
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd bzzfeedback

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt


### 2. Database Configuration

### 2. Database Configuration

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here

# MySQL Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=bzzfeedbackdb

# Optional: Logging Configuration
LOG_DIR=logs
LOG_LEVEL=INFO
```

### 3. Initialize Database

```bash
# This will create the database and all required tables
python scripts/init_db.py
```

### 4. Seed Demo Data (Optional)

```bash
# Populate with sample data for testing
python scripts/seed_demo.py
```

### 5. Run the Application

```bash
# Development server
python run.py


The application will be available at `http://localhost:5000`

## 👥 User Management

### Setting User Passwords

Use the password management script to set or reset user passwords:

```bash
python scripts/set_password.py <username> <new_password>

**Examples:**
```bash
# Set password for teacher 'alice'
python scripts/set_password.py alice Password123!

# Set password for student 'john'
python scripts/set_password.py john MyNewPass!
```

### Default Demo Accounts

After running the seed script, you can use these demo accounts:

- **Students**: 
  - `student1` / `password123` (Grade 10A)
  - `student3` / `password123` (Grade 11B)
- **Teachers** (15 teachers with diverse subject specializations): 
  - `alice` / `password123` (Mathematics, Physics) - teaches Grade 9A, Grade 10A, Grade 12A
  - `bob` / `password123` (English, Literature) - teaches Grade 9B, Grade 10B, Grade 12B
  - `charlie` / `password123` (Chemistry, Biology) - teaches Grade 9A, Grade 11A
  - `diana` / `password123` (History, Geography) - teaches Grade 9B, Grade 11B
  - `eve` / `password123` (Mathematics, Computer Science) - teaches Grade 10A, Grade 12A
  - `frank` / `password123` (Art, Music) - teaches Grade 10B, Grade 12B
  - `grace` / `password123` (Physical Education, Psychology) - teaches Grade 11A
  - `henry` / `password123` (Economics, Foreign Language) - teaches Grade 11B
  - `isabel` / `password123` (Science, Biology) - teaches Grade 9A, Grade 12B
  - `jack` / `password123` (Mathematics, Physics) - teaches Grade 9B
  - `kate` / `password123` (English, Foreign Language) - teaches Grade 10A
  - `liam` / `password123` (History, Economics) - teaches Grade 10B
  - `maya` / `password123` (Art, Literature) - teaches Grade 11A
  - `noah` / `password123` (Computer Science, Mathematics) - teaches Grade 11B
  - `olivia` / `password123` (Music, Psychology) - teaches Grade 12A
- **Admin**: `admin` / `password123`

**Note**: Each class has 3+ teachers assigned with diverse subject coverage. Students will only see teachers that teach their specific class. The system now includes 16 different subjects across all academic areas.

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install test dependencies (already in requirements.txt)
pip install -r requirements.txt

# Run all tests
pytest -q

# Run with verbose output
pytest -v

# Run specific test files
pytest tests/test_auth.py
pytest tests/test_student_flow.py
```

## 📊 Logging

The application includes comprehensive logging:

- **Info Logs**: `logs/info.log` - General application activity
- **Error Logs**: `logs/error.log` - Errors and exceptions only
- **Automatic Rotation**: Logs rotate at 1MB with 5 backup files
- **Request Tracking**: All HTTP requests are logged with timing information

## 🏗️ Project Structure

```
bzzfeedback/
├── app/                    # Main application package
│   ├── templates/         # Jinja2 HTML templates
│   ├── auth.py           # Authentication logic
│   ├── db.py             # Database connection and queries
│   ├── main.py           # Flask app factory
│   └── routes.py         # Application routes
├── scripts/              # Utility scripts
│   ├── init_db.py       # Database initialization
│   ├── seed_demo.py     # Demo data seeding
│   └── set_password.py  # Password management
├── sql/                  # Database schema files
├── tests/                # Test suite
├── logs/                 # Application logs
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## 🔄 User Workflows

### Student Workflow
1. **Register/Login** → Create account with class selection or login
2. **Choose Teacher** → Select from teachers that teach your class
3. **Select Subject** → Pick from teacher's assigned subjects
4. **Submit Feedback** → Choose category and provide detailed feedback
5. **Track Status** → Monitor feedback status and teacher responses

### Teacher Workflow
1. **Login** → Access teacher dashboard
2. **View Feedback** → Browse feedback by subject
3. **Read & Respond** → Mark as read and reply to students
4. **Manage Subjects** → View assigned subjects and statistics
5. **Class Management** → View assigned classes and student feedback

### Admin Workflow
1. **Login** → Access admin dashboard
2. **User Management** → Create/edit student and teacher accounts
3. **Subject Administration** → Manage subjects and assignments
4. **Class Management** → Assign teachers to classes
5. **Feedback Moderation** → Review and moderate feedback submissions

## 🚀 Deployment

### Production Deployment with Gunicorn

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Environment Variables for Production

```env
FLASK_SECRET_KEY=your-production-secret-key
MYSQL_HOST=your-production-db-host
MYSQL_USER=your-production-db-user
MYSQL_PASSWORD=your-production-db-password
MYSQL_DATABASE=bzzfeedbackdb
LOG_LEVEL=WARNING
```

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for secure session handling
- **SQL Injection Protection**: Parameterized queries throughout
- **Role-Based Access**: Strict role separation (student/teacher/admin)
- **Optional Anonymity**: Students can submit anonymous feedback
- **Input Validation**: Form validation and sanitization

## 📈 Database Schema

The application uses a well-structured MySQL database with the following key tables:

- **users**: User accounts with role-based access and class assignments
- **teachers**: Teacher profiles and information
- **subjects**: Available subjects for feedback
- **teacher_subjects**: Many-to-many relationship between teachers and subjects
- **teacher_classes**: Many-to-many relationship between teachers and classes
- **feedback**: Main feedback submissions
- **feedback_messages**: Threaded conversations on feedback
- **feedback_categories**: Predefined feedback categories

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the logs in the `logs/` directory
- Review the test files for usage examples
- Ensure your MySQL database is properly configured
- Verify all environment variables are set correctly

---

**Built with ❤️ using Flask and MySQL**