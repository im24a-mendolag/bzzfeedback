import os
import sys
import mysql.connector

# Ensure project root is on sys.path for 'config' import when running as a script
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import DB_CONFIG


def get_mysql_connection_without_db():
    """Get MySQL connection without specifying a database"""
    config_without_db = DB_CONFIG.copy()
    if 'database' in config_without_db:
        del config_without_db['database']

    try:
        connection = mysql.connector.connect(**config_without_db)
        return connection
    except Exception as e:
        print(f"❌ Failed to connect to MySQL: {str(e)}")
        print("Please check your MySQL credentials in .env file")
        return None


def execute_change_query_with_connection(connection, query):
    """Execute a change query using the provided connection"""
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")
        print(f"Query: {query}")
        connection.rollback()
        return False


def get_sql_files(path):
    """Scan directory for SQL files and extract their dependencies"""
    sql_files = {}

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.sql'):
                full_path = os.path.join(root, file)

                # Read the first line to check for dependencies
                with open(full_path, "r") as f:
                    first_line = f.readline().strip()

                # Extract dependencies if present
                dependencies = []
                if first_line.startswith('-- dependencies:'):
                    # Format: -- dependencies: file1, file2, file3
                    deps_str = first_line.replace('-- dependencies:', '').strip()
                    if deps_str:
                        dependencies = [dep.strip() for dep in deps_str.split(',')]

                sql_files[full_path] = {
                    'dependencies': dependencies,
                    'executed': False
                }

    return sql_files


def find_file_by_name(files_dict, target_name):
    """Find a file path by its base name (without extension)"""
    for file_path in files_dict:
        base_name = os.path.basename(file_path).replace('.sql', '')
        if base_name == target_name:
            return file_path
    return None


def execute_sql_file(file_path, connection, executed_files, files_dict):
    """Execute a SQL file and handle its dependencies recursively"""
    # Check if already executed
    if file_path in executed_files:
        return True

    # Get dependencies for this file
    dependencies = files_dict[file_path]['dependencies']

    # First execute all dependencies
    for dep_name in dependencies:
        # Find the actual file path for this dependency
        dep_path = find_file_by_name(files_dict, dep_name)

        if not dep_path:
            print(f"❌ Error: Dependency '{dep_name}' not found for {os.path.basename(file_path)}")
            return False

        if dep_path not in executed_files:
            print(f"  📋 Executing dependency: {dep_name}")
            if not execute_sql_file(dep_path, connection, executed_files, files_dict):
                print(f"❌ Failed to execute dependency: {dep_name}")
                return False

    # Now execute the current file
    try:
        with open(file_path, "r") as f:
            sql_content = f.read()

        # Skip the dependencies line when executing
        if sql_content.startswith('-- dependencies:'):
            lines = sql_content.split('\n', 1)
            if len(lines) > 1:
                sql_content = lines[1]
            else:
                sql_content = ""

        # Execute the SQL using the connection
        if sql_content.strip():
            # Remove SQL single-line comments to avoid semicolons inside comments
            filtered_lines = []
            for raw_line in sql_content.split('\n'):
                line = raw_line.strip()
                if not line or line.startswith('--'):
                    continue
                filtered_lines.append(raw_line)
            cleaned_sql = '\n'.join(filtered_lines)

            # Split multiple SQL statements and execute them separately
            statements = [stmt.strip() for stmt in cleaned_sql.split(';') if stmt.strip()]
            for statement in statements:
                if statement:
                    ok = execute_change_query_with_connection(connection, statement)
                    if not ok:
                        return False

        print(f"✓ Successfully executed: {os.path.basename(file_path)}")
        executed_files.add(file_path)
        files_dict[file_path]['executed'] = True
        return True

    except Exception as e:
        print(f"✗ Error executing {file_path}: {str(e)}")
        return False


def execute_all_sql_files(path, connection):
    """Main function to execute all SQL files in correct order based on dependencies"""
    # Get all SQL files and their dependencies
    files_dict = get_sql_files(path)

    if not files_dict:
        print("No SQL files found!")
        return False

    print("Found SQL files:")
    for file_path, info in files_dict.items():
        print(f"  {os.path.basename(file_path)} (dependencies: {info['dependencies']})")

    executed_files = set()

    print("\nExecuting files in order:")
    # First execute files with no dependencies
    for file_path, info in files_dict.items():
        if not info['dependencies'] and not info['executed']:
            execute_sql_file(file_path, connection, executed_files, files_dict)

    # Then execute files with dependencies
    for file_path, info in files_dict.items():
        if not info['executed']:
            execute_sql_file(file_path, connection, executed_files, files_dict)

    # Verify all files were executed
    all_executed = all(info['executed'] for info in files_dict.values())
    if all_executed:
        print("\n✓ All files executed successfully!")
    else:
        print("\n✗ Some files failed to execute")

    return all_executed


def main():
    print("🔌 Connecting to MySQL...")
    connection = get_mysql_connection_without_db()

    if not connection:
        print("❌ Cannot proceed without MySQL connection")
        return

    print("🧨 Dropping and recreating database...")

    # Drop database if exists
    if not execute_change_query_with_connection(connection, "DROP DATABASE IF EXISTS bzzfeedbackdb"):
        print("❌ Failed to drop database")
        connection.close()
        return

    # Create database
    if not execute_change_query_with_connection(connection, "CREATE DATABASE bzzfeedbackdb"):
        print("❌ Failed to create database")
        connection.close()
        return

    print("✅ Database 'bzzfeedbackdb' created successfully!")

    # Close the connection without database
    connection.close()

    # Now connect to the specific database
    print("🔌 Connecting to bzzfeedbackdb...")
    try:
        cfg = DB_CONFIG.copy()
        cfg['database'] = 'bzzfeedbackdb'
        db_connection = mysql.connector.connect(**cfg)
        print("✅ Connected to bzzfeedbackdb successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to bzzfeedbackdb: {str(e)}")
        return

    print("\n📁 Setting up database schema...")
    # Path to SQL files in your project
    sql_files_path = os.path.join(os.path.dirname(__file__), "..", "sql")

    # Execute all SQL files in correct order
    success = execute_all_sql_files(sql_files_path, db_connection)

    db_connection.close()

    if success:
        print("\n🎉 Database setup completed successfully!")
        print("You can now start your Flask application!")
    else:
        print("\n❌ Database setup failed!")


if __name__ == "__main__":
    main()

