## BZZ Feedback (Flask + MySQL)

### Setup

1) Create virtualenv and install deps

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

2) Configure environment

Copy `.env.example` to `.env` and set values for MySQL and `FLASK_SECRET_KEY`.

3) Initialize database (drops and recreates `bzzfeedbackdb`)

```bash
python scripts/init_db.py
```

4) Run app (development)

```bash
# Option A: simple entry point
python run.py

# Option B: Flask CLI
set FLASK_APP=wsgi:app
flask run --reload
```

### Logs

- Files are written to `logs/` (configurable via `LOG_DIR`).
- `info.log`: general app logs at `LOG_LEVEL` (default INFO).
- `error.log`: only errors and above.
- Rotate at ~1 MB, keep 5 backups.

### Tests

Install test deps (already listed in requirements.txt):

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

### Demo data

Populate the database with lots of sample feedback to visualize lists and counts:

```bash
python scripts/seed_demo.py
```


### Reset/set a user's password

Use the helper script to set a new password for any user (we use the `email` field as username):

```bash
python scripts/set_password.py <username> <new_password>
```

Examples:

```bash
# Set password for teacher 'alice'
python scripts/set_password.py alice Password123!

# Set password for student 'john'
python scripts/set_password.py john MyNewPass!
```

You should see "Password updated for '<username>'" if the user exists.

### Flows

- Students: Login → choose teacher → choose subject and category (or custom) → submit feedback (title + info). Feedback is stored with optional student_id (anonymity depends on how you provision accounts).
- Teachers: Login → view feedback per subject → mark as read.

### SQL files

Located under `sql/`. They include a simple dependency header parsed by `scripts/init_db.py`.

