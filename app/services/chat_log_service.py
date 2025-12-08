"""
Chat Log Service - Database persistence for chat conversations
"""

import os
import logging
import hashlib
from typing import Optional
import asyncpg

logger = logging.getLogger(__name__)
_pool: Optional[asyncpg.Pool] = None
CLIENT_ID = "dv-aviation"


async def get_db_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        db_host = os.getenv("DB_HOST", "/cloudsql/n8n-agent-451019:us-east4:addressable-audience-curation-demographics")
        db_name = os.getenv("DB_NAME", "demographics")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "Rvgx51cwEYPnK86V2wu7hUuOwsj5F23u")

        try:
            if db_host.startswith("/cloudsql/"):
                _pool = await asyncpg.create_pool(database=db_name, user=db_user, password=db_password, host=db_host, min_size=1, max_size=5)
            else:
                db_port = int(os.getenv("DB_PORT", "5432"))
                _pool = await asyncpg.create_pool(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port, min_size=1, max_size=5)
            logger.info(f"Database pool created for chat logging")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    return _pool


def hash_ip(ip: str) -> str:
    if not ip:
        return ""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


async def log_chat_message(
    session_id: str, user_message: str, ai_response: Optional[str] = None,
    language: str = "en", intent: Optional[str] = None, model_used: Optional[str] = None,
    tokens_in: Optional[int] = None, tokens_out: Optional[int] = None,
    latency_ms: Optional[int] = None, client_ip: Optional[str] = None, user_agent: Optional[str] = None
) -> Optional[int]:
    try:
        pool = await get_db_pool()
        ip_hash = hash_ip(client_ip) if client_ip else None
        if user_agent and len(user_agent) > 500:
            user_agent = user_agent[:500]

        query = """
            INSERT INTO chat_logs (client_id, session_id, user_message, ai_response, language, intent, model_used, tokens_in, tokens_out, latency_ms, client_ip_hash, user_agent)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) RETURNING id
        """
        async with pool.acquire() as conn:
            result = await conn.fetchval(query, CLIENT_ID, session_id, user_message, ai_response, language, intent, model_used, tokens_in, tokens_out, latency_ms, ip_hash, user_agent)
        logger.debug(f"Logged chat message for {CLIENT_ID}: id={result}")
        return result
    except Exception as e:
        logger.error(f"Failed to log chat message: {e}")
        return None


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
