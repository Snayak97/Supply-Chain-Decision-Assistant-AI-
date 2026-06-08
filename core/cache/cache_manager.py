"""
Memory & Caching Layer for result caching and scenario state persistence.
Layer 5 - Memory & Caching Layer

For MVP, uses SQLite instead of Redis for simplicity and local execution.
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from core.database.session import SessionLocal
from core.database.models import ToolResultCache, ScenarioSession


class CacheManager:
    """Manages tool result caching and scenario session persistence."""
    
    @staticmethod
    def generate_cache_key(tool_name: str, **kwargs) -> str:
        """Generate a unique cache key from tool name and arguments."""
        # Create a deterministic string from arguments
        args_str = json.dumps(kwargs, sort_keys=True)
        key_string = f"{tool_name}:{args_str}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    @staticmethod
    def get_cached_result(tool_name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result if available and not expired.
        
        Keyed on hash(tool_name + normalized_arguments). TTL aligned to
        warehouse refresh cadence (default 4 hours).
        """
        cache_key = CacheManager.generate_cache_key(tool_name, **kwargs)
        
        db: Session = SessionLocal()
        try:
            cached = db.query(ToolResultCache).filter(
                ToolResultCache.cache_key == cache_key,
                ToolResultCache.is_valid == True
            ).first()
            
            if cached and cached.expires_at > datetime.utcnow():
                return json.loads(cached.result)
            
            # Mark as invalid if expired
            if cached:
                cached.is_valid = False
                db.commit()
            
            return None
        finally:
            db.close()
    
    @staticmethod
    def cache_result(tool_name: str, result: Dict[str, Any], ttl_hours: int = 4, **kwargs) -> None:
        """Cache a tool result with specified TTL."""
        cache_key = CacheManager.generate_cache_key(tool_name, **kwargs)
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        db: Session = SessionLocal()
        try:
            # Check if cache entry exists
            cached = db.query(ToolResultCache).filter(
                ToolResultCache.cache_key == cache_key
            ).first()
            
            if cached:
                # Update existing entry
                cached.result = json.dumps(result)
                cached.expires_at = expires_at
                cached.is_valid = True
            else:
                # Create new entry
                cache_entry = ToolResultCache(
                    cache_key=cache_key,
                    tool_name=tool_name,
                    result=json.dumps(result),
                    expires_at=expires_at,
                    is_valid=True
                )
                db.add(cache_entry)
            
            db.commit()
        finally:
            db.close()
    
    @staticmethod
    def invalidate_cache(tool_name: Optional[str] = None) -> None:
        """
        Invalidate cache entries.
        
        If tool_name specified, only invalidate that tool's cache.
        Otherwise, invalidate all cache (e.g., on warehouse refresh).
        """
        db: Session = SessionLocal()
        try:
            query = db.query(ToolResultCache)
            if tool_name:
                query = query.filter(ToolResultCache.tool_name == tool_name)
            
            query.update({"is_valid": False})
            db.commit()
        finally:
            db.close()
    
    @staticmethod
    def save_scenario_session(
        session_id: str,
        perturbations: List[Dict[str, Any]]
    ) -> None:
        """
        Save or update scenario session state.
        
        The accumulated perturbation list for the session is stored so that
        sessions survive process restarts.
        """
        db: Session = SessionLocal()
        try:
            session = db.query(ScenarioSession).filter(
                ScenarioSession.session_id == session_id
            ).first()
            
            if session:
                # Update existing session
                session.perturbations = perturbations
                session.updated_at = datetime.utcnow()
                session.is_active = True
            else:
                # Create new session
                session = ScenarioSession(
                    session_id=session_id,
                    perturbations=perturbations,
                    is_active=True
                )
                db.add(session)
            
            db.commit()
        finally:
            db.close()
    
    @staticmethod
    def get_scenario_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve scenario session state."""
        db: Session = SessionLocal()
        try:
            session = db.query(ScenarioSession).filter(
                ScenarioSession.session_id == session_id,
                ScenarioSession.is_active == True
            ).first()
            
            if session:
                return {
                    "session_id": session.session_id,
                    "perturbations": session.perturbations,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat()
                }
            
            return None
        finally:
            db.close()
    
    @staticmethod
    def clear_scenario_session(session_id: str) -> None:
        """Clear scenario session (reset perturbations)."""
        db: Session = SessionLocal()
        try:
            session = db.query(ScenarioSession).filter(
                ScenarioSession.session_id == session_id
            ).first()
            
            if session:
                session.perturbations = []
                session.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def cleanup_expired_cache() -> int:
        """Remove expired cache entries. Returns count of entries cleaned up."""
        db: Session = SessionLocal()
        try:
            expired = db.query(ToolResultCache).filter(
                ToolResultCache.expires_at < datetime.utcnow()
            ).all()
            
            count = len(expired)
            for entry in expired:
                db.delete(entry)
            
            db.commit()
            return count
        finally:
            db.close()
