"""Failure simulation for testing drone resilience to component failures."""

import random
from datetime import datetime, timedelta


class FailureSimulator:
    def __init__(self):
        self.active_failures = {}
        self.failure_log = []
    
    def inject_failure(self, failure_type, drone_id=None, duration=None, severity=0.5):
        """Inject a failure into a drone or system component."""
        if drone_id is None:
            drone_id = "system"
        
        if drone_id not in self.active_failures:
            self.active_failures[drone_id] = []
        
        failure = {
            "type": failure_type,
            "drone_id": drone_id,
            "severity": severity,
            "injected_at": datetime.now(),
            "duration": duration,
            "active": True,
        }
        
        self.active_failures[drone_id].append(failure)
        self.failure_log.append(failure)
        
        return failure
    
    def get_active_failures(self, drone_id=None):
        """Get list of active failures for a drone."""
        if drone_id is None:
            all_failures = []
            for failures in self.active_failures.values():
                all_failures.extend([f for f in failures if f["active"]])
            return all_failures
        
        if drone_id not in self.active_failures:
            return []
        
        return [f for f in self.active_failures[drone_id] if f["active"]]
    
    def clear_failure(self, drone_id, failure_type):
        """Manually clear a specific failure."""
        if drone_id in self.active_failures:
            for failure in self.active_failures[drone_id]:
                if failure["type"] == failure_type and failure["active"]:
                    failure["active"] = False
                    return True
        return False
    
    def update_failures(self):
        """Update failure states based on elapsed time."""
        for drone_id, failures in self.active_failures.items():
            for failure in failures:
                if failure["active"] and failure["duration"] is not None:
                    elapsed = (datetime.now() - failure["injected_at"]).total_seconds()
                    if elapsed >= failure["duration"]:
                        failure["active"] = False
    
    def get_failure_statistics(self):
        """Return statistics on failures injected."""
        total_failures = len(self.failure_log)
        active_count = sum(len(self.get_active_failures(did)) for did in self.active_failures)
        
        failure_types = {}
        for failure in self.failure_log:
            ftype = failure["type"]
            failure_types[ftype] = failure_types.get(ftype, 0) + 1
        
        return {
            "total_injected": total_failures,
            "currently_active": active_count,
            "failure_types": failure_types,
        }
