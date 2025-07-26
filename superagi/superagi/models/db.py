from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from superagi.config.config import get_config
from urllib.parse import urlparse
from superagi.lib.logger import logger

engine = None


def connect_db():
    """
    Connects to the PostgreSQL database using SQLAlchemy.

    Returns:
        engine: The SQLAlchemy engine object representing the database connection.
    """
    global engine
    if engine is not None:
        return engine

    # Create the connection URL
    db_host = get_config('DB_HOST', 'super__postgres')
    db_username = get_config('DB_USERNAME')
    db_password = get_config('DB_PASSWORD')
    db_name = get_config('DB_NAME')
    db_url = get_config('DB_URL', None)

    if db_url is None:
        if db_username is None:
            db_url = f'postgresql://{db_host}/{db_name}'
        else:
            db_url = f'postgresql://{db_username}:{db_password}@{db_host}/{db_name}'
    else:
        db_url = urlparse(db_url)
        db_url = db_url.scheme + "://" + db_url.netloc + db_url.path

    # Create the SQLAlchemy engine
    engine = create_engine(
        db_url,
        pool_size=20,
        max_overflow=50,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=False,
    )

    # Test the connection
    try:
        connection = engine.connect()
        logger.info("Connected to the database! @ " + db_url)
        connection.close()
    except Exception as e:
        logger.error(f"Unable to connect to the database:{e}")

    return engine


# ? NOVO: função DBSession para uso nos controllers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connect_db())

def DBSession():
    return SessionLocal()
