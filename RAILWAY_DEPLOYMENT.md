# Railway Deployment Guide

## MySQL URL Configuration for Railway

Your app has been updated to handle Railway's MySQL connection format automatically.

### What was changed:

1. **config.py**: Updated to parse `MYSQL_URL` environment variable (Railway specific)
2. **app/db.py**: Added SSL configuration for Railway's MySQL service

### Railway Environment Variables

Railway provides a `MYSQL_URL` variable when you add a MySQL service:

```
MYSQL_URL=mysql://user:password@host:port/database
```

**To set this up in Railway:**

1. Go to your Railway project dashboard
2. Select your **web service** (not the MySQL service)
3. Go to the **Variables** tab
4. Click **New Variable**
5. Set:
   - **Name**: `MYSQL_URL`
   - **Value**: `${{ MySQL.MYSQL_URL }}`
6. Click **Add**

This will connect your web service to the MySQL database service.

### Required Environment Variables to Set:

```
FLASK_SECRET_KEY=your-super-secret-key-change-this
LOG_LEVEL=WARNING
```

### Deployment Commands:

```bash
# 1. Login to Railway
railway login

# 2. Initialize project
railway init

# 3. Add MySQL database
railway add mysql

# 4. Set environment variables
railway variables set FLASK_SECRET_KEY="your-secret-key-here"
railway variables set LOG_LEVEL="WARNING"

# 5. Deploy
railway up

# 6. Initialize database
railway run python scripts/init_db.py

# 7. Seed demo data (optional)
railway run python scripts/seed_demo.py

# 8. Open your app
railway open
```

### Database Connection Details:

- **Local Development**: Uses individual MYSQL_* environment variables
- **Railway Production**: Automatically uses DATABASE_URL or individual variables
- **SSL**: Automatically configured for Railway's MySQL service
- **Connection Pooling**: Configured for production use

### Troubleshooting:

If you encounter connection issues:

1. Check Railway logs: `railway logs`
2. Verify environment variables: `railway variables`
3. Test database connection: `railway connect mysql`

Your app will automatically adapt to Railway's MySQL configuration!
