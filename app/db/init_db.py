from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.base_class import Base
from app.db.session import engine
from app.models import *  # Import all models

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """
    Create database tables
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")