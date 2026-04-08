"""
Data Logging System
Comprehensive operation logging and analysis for drifter operations
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

dataclass
class OperationLog:
    """Single operation log entry"""
    operation_id: str
    timestamp: datetime
    event_type: str
    data: Dict[str, Any]
    session_id: str
    driver_id: str
    metadata: Dict[str, Any]

class DataLogger:
    """Comprehensive data logging system"""
    
    def __init__(self, config: Any):
        self.config = config
        self.retention_days = config.DATA_RETENTION_DAYS
        self.backup_enabled = config.BACKUP_ENABLED
        self.backup_interval = config.BACKUP_INTERVAL
        
        self.session_logs: Dict[str, List[OperationLog]] = {}
        self.current_session_id: Optional[str] = None
        
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
    def start_session(self, session_id: str, driver_id: str) -> None:
        """Start new logging session"""
        self.current_session_id = session_id
        self.session_logs[session_id] = []
        logger.info(f"Session started: {session_id} (Driver: {driver_id})")
    
    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        driver_id: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Log operation event"""
        if not self.current_session_id:
            logger.warning("No active session for logging")
            return
        
        log_entry = OperationLog(
            operation_id=self._generate_log_id(),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            data=data,
            session_id=self.current_session_id,
            driver_id=driver_id,
            metadata=metadata or {}
        )
        
        self.session_logs[self.current_session_id].append(log_entry)
        
        # Write to file
        self._write_to_file(log_entry)
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End logging session and generate summary"""
        if session_id not in self.session_logs:
            logger.warning(f"Session not found: {session_id}")
            return {}
        
        logs = self.session_logs[session_id]
        
        summary = {
            "session_id": session_id,
            "total_events": len(logs),
            "duration": self._calculate_duration(logs),
            "events_by_type": self._count_events_by_type(logs),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Session ended: {session_id} - {summary['total_events']} events logged")
        
        if self.backup_enabled:
            self._backup_session(session_id)
        
        return summary
    
    def get_session_logs(self, session_id: str) -> List[OperationLog]:
        """Retrieve logs for a session"""
        return self.session_logs.get(session_id, [])
    
    def query_logs(
        self,
        event_type: Optional[str] = None,
        session_id: Optional[str] = None,
        driver_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[OperationLog]:
        """Query logs with filters"""
        results = []
        
        for session, logs in self.session_logs.items():
            if session_id and session != session_id:
                continue
            
            for log in logs:
                if event_type and log.event_type != event_type:
                    continue
                if driver_id and log.driver_id != driver_id:
                    continue
                if start_time and log.timestamp < start_time:
                    continue
                if end_time and log.timestamp > end_time:
                    continue
                
                results.append(log)
        
        return results
    
    def cleanup_old_logs(self) -> int:
        """Remove logs older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        deleted_count = 0
        
        for session_id, logs in list(self.session_logs.items()):
            filtered = [l for l in logs if l.timestamp > cutoff_date]
            
            deleted_count += len(logs) - len(filtered)
            
            if filtered:
                self.session_logs[session_id] = filtered
            else:
                del self.session_logs[session_id]
        
        logger.info(f"Cleaned up {deleted_count} old log entries")
        return deleted_count
    
    def _write_to_file(self, log_entry: OperationLog) -> None:
        """Write log entry to file"""
        try:
            date_str = log_entry.timestamp.strftime("%Y-%m-%d")
            file_path = self.log_dir / f"operations_{date_str}.jsonl"
            
            with open(file_path, "a") as f:
                f.write(json.dumps(asdict(log_entry), default=str) + "\n")
        except Exception as e:
            logger.error(f"Failed to write log to file: {e}")
    
    def _backup_session(self, session_id: str) -> None:
        """Backup session data"""
        try:
            logs = self.session_logs[session_id]
            backup_path = self.log_dir / f"backup_{session_id}.json"
            
            with open(backup_path, "w") as f:
                json.dump([asdict(l, default=str) for l in logs], f, indent=2)
            
            logger.info(f"Session backed up: {backup_path}")
        except Exception as e:
            logger.error(f"Backup failed: {e}")
    
    def _calculate_duration(self, logs: List[OperationLog]) -> str:
        """Calculate session duration"""
        if len(logs) < 2:
            return "0s"
        
        duration = logs[-1].timestamp - logs[0].timestamp
        return str(duration).split(".")[0]
    
    def _count_events_by_type(self, logs: List[OperationLog]) -> Dict[str, int]:
        """Count events by type"""
        counts = {}
        for log in logs:
            counts[log.event_type] = counts.get(log.event_type, 0) + 1
        return counts
    
    def _generate_log_id(self) -> str:
        """Generate unique log ID"""
        import uuid
        return str(uuid.uuid4())[:8]