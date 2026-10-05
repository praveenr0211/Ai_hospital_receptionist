import sys
import psycopg
from psycopg import sql
from alembic.config import Config
from alembic import command
from app.config import settings

def ensure_database_exists():
    """Connect to postgres administrative database and ensure the target database exists."""
    print(f"Checking if database '{settings.POSTGRES_DB}' exists on {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}...")
    
    # Connect to default 'postgres' database
    conn_str = (
        f"host={settings.POSTGRES_HOST} "
        f"port={settings.POSTGRES_PORT} "
        f"user={settings.POSTGRES_USER} "
        f"password={settings.POSTGRES_PASSWORD} "
        f"dbname=postgres"
    )
    
    try:
        with psycopg.connect(conn_str, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s;",
                    (settings.POSTGRES_DB,)
                )
                exists = cur.fetchone()
                if not exists:
                    print(f"Database '{settings.POSTGRES_DB}' does not exist. Creating it now...")
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings.POSTGRES_DB)))
                    print(f"Database '{settings.POSTGRES_DB}' created successfully.")
                else:
                    print(f"Database '{settings.POSTGRES_DB}' already exists.")
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        print("\nPlease check your PostgreSQL credentials in .env (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT).")
        raise

def run_migrations():
    """Run alembic upgrade head programmatically."""
    print("Applying Alembic migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Alembic migrations applied successfully.")

def main():
    try:
        ensure_database_exists()
        run_migrations()
        print("\nDatabase initialization complete!")
    except Exception as e:
        print(f"\nInitialization aborted: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
