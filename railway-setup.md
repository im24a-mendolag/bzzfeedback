# Railway Setup Instructions

## The Problem
Your app is trying to connect to `localhost:3306` instead of the Railway MySQL service. This means the `MYSQL_URL` environment variable is not set correctly.

## Solution Steps

### 1. Check Your Railway Project Structure
Make sure you have:
- ✅ A **Web Service** (your Flask app)
- ✅ A **MySQL Service** (database)

### 2. Set the MYSQL_URL Variable

**In Railway Dashboard:**

1. Go to your Railway project
2. Click on your **Web Service** (not the MySQL service)
3. Go to the **Variables** tab
4. Click **New Variable**
5. Set:
   - **Name**: `MYSQL_URL`
   - **Value**: `${{ MySQL.MYSQL_URL }}`
6. Click **Add**

### 3. Verify the Variable is Set

After setting the variable, you should see:
```
MYSQL_URL = mysql://user:password@host:port/database
```

### 4. Redeploy

```bash
# Redeploy your app
railway up
```

### 5. Check the Logs

```bash
# Check the deployment logs
railway logs
```

You should see debug output like:
```
DEBUG: MYSQL_URL = mysql://user:password@host:port/database
DEBUG: Using MYSQL_URL: mysql://user:password@host:port/database
DEBUG: Parsed config: {'host': 'hostname', 'port': 3306, ...}
```

## Alternative: Use Individual Variables

If `MYSQL_URL` doesn't work, try setting individual variables:

1. In your Web Service Variables, add:
   - `MYSQL_HOST` = `${{ MySQL.MYSQL_HOST }}`
   - `MYSQL_PORT` = `${{ MySQL.MYSQL_PORT }}`
   - `MYSQL_USER` = `${{ MySQL.MYSQL_USER }}`
   - `MYSQL_PASSWORD` = `${{ MySQL.MYSQL_PASSWORD }}`
   - `MYSQL_DATABASE` = `${{ MySQL.MYSQL_DATABASE }}`

## Troubleshooting

### Check if MySQL Service is Running
```bash
# Connect to your MySQL service
railway connect mysql
```

### Test Database Connection
```bash
# Test the connection
railway run python test_db_connection.py
```

### Common Issues

1. **Variable not set**: Make sure you're setting the variable on the **Web Service**, not the MySQL service
2. **Wrong service**: Make sure you're clicking on your Flask app service, not the database service
3. **Variable name**: Make sure it's exactly `MYSQL_URL` (case sensitive)
4. **Value format**: Make sure the value is exactly `${{ MySQL.MYSQL_URL }}`

## Expected Debug Output

When working correctly, you should see:
```
DEBUG: MYSQL_URL = mysql://user:password@host:port/database
DEBUG: Using MYSQL_URL: mysql://user:password@host:port/database
DEBUG: Parsed config: {'host': 'hostname', 'port': 3306, 'user': 'username', 'password': 'password', 'database': 'database_name'}
DEBUG: Initializing MySQL pool with config: {...}
DEBUG: Added SSL configuration for cloud deployment
DEBUG: MySQL pool initialized successfully
```
