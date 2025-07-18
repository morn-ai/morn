import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.config.agent_config import config

logger = logging.getLogger(__name__)


class BruteForceProtection:
    """Brute force protection system"""

    def __init__(self):
        # Configuration from config
        self.max_failed_attempts = config.max_failed_attempts
        self.lockout_duration = config.lockout_duration
        self.max_attempts_per_minute = config.max_attempts_per_minute
        self.failed_attempt_delay = config.failed_attempt_delay

        # Storage for tracking attempts
        self.failed_attempts: Dict[str, int] = defaultdict(int)  # IP -> failed count
        self.lockout_until: Dict[str, datetime] = {}  # IP -> lockout until time
        self.attempt_timestamps: Dict[str, list[datetime]] = defaultdict(list)  # IP -> list of attempt timestamps

        # Thread lock for thread safety
        self._lock = threading.Lock()

        # Cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_old_records, daemon=True)
        self._cleanup_thread.start()

    def is_ip_locked(self, ip_address: str) -> bool:
        """Check if an IP address is currently locked out"""
        with self._lock:
            if ip_address in self.lockout_until:
                if datetime.now() < self.lockout_until[ip_address]:
                    return True
                else:
                    # Lockout expired, remove it
                    del self.lockout_until[ip_address]
                    self.failed_attempts[ip_address] = 0
            return False

    def is_rate_limited(self, ip_address: str) -> bool:
        """Check if an IP address is rate limited"""
        with self._lock:
            now = datetime.now()
            cutoff_time = now - timedelta(minutes=1)

            # Remove old timestamps
            self.attempt_timestamps[ip_address] = [
                ts for ts in self.attempt_timestamps[ip_address]
                if ts > cutoff_time
            ]

            # Check if too many attempts in the last minute
            return len(self.attempt_timestamps[ip_address]) >= self.max_attempts_per_minute

    def record_attempt(self, ip_address: str, success: bool) -> None:
        """Record a login attempt"""
        with self._lock:
            now = datetime.now()
            self.attempt_timestamps[ip_address].append(now)

            if not success:
                self.failed_attempts[ip_address] += 1
                logger.warning(f"Failed login attempt from IP {ip_address}. "
                               f"Total failures: {self.failed_attempts[ip_address]}")

                # Check if should lockout
                if self.failed_attempts[ip_address] >= self.max_failed_attempts:
                    lockout_until = now + timedelta(seconds=self.lockout_duration)
                    self.lockout_until[ip_address] = lockout_until
                    logger.warning(f"IP {ip_address} locked out until {lockout_until}")
            else:
                # Reset failed attempts on successful login
                self.failed_attempts[ip_address] = 0
                if ip_address in self.lockout_until:
                    del self.lockout_until[ip_address]
                logger.info(f"Successful login from IP {ip_address}, resetting failed attempts")

    def get_remaining_attempts(self, ip_address: str) -> int:
        """Get remaining attempts before lockout"""
        with self._lock:
            return max(0, self.max_failed_attempts - self.failed_attempts[ip_address])

    def get_lockout_remaining(self, ip_address: str) -> Optional[int]:
        """Get remaining lockout time in seconds, or None if not locked"""
        with self._lock:
            if ip_address in self.lockout_until:
                remaining = (self.lockout_until[ip_address] - datetime.now()).total_seconds()
                return max(0, int(remaining))
            return None

    def _cleanup_old_records(self) -> None:
        """Clean up old records periodically"""
        while True:
            try:
                time.sleep(300)  # Clean up every 5 minutes
                with self._lock:
                    now = datetime.now()

                    # Clean up expired lockouts
                    expired_ips = [
                        ip for ip, lockout_time in self.lockout_until.items()
                        if now >= lockout_time
                    ]
                    for ip in expired_ips:
                        del self.lockout_until[ip]
                        self.failed_attempts[ip] = 0

                    # Clean up old attempt timestamps (older than 1 hour)
                    cutoff_time = now - timedelta(hours=1)
                    for ip in list(self.attempt_timestamps.keys()):
                        self.attempt_timestamps[ip] = [
                            ts for ts in self.attempt_timestamps[ip]
                            if ts > cutoff_time
                        ]
                        if not self.attempt_timestamps[ip]:
                            del self.attempt_timestamps[ip]

                    # Clean up failed attempts for IPs that haven't been active
                    inactive_ips = [
                        ip for ip in self.failed_attempts.keys()
                        if ip not in self.lockout_until and ip not in self.attempt_timestamps
                    ]
                    for ip in inactive_ips:
                        del self.failed_attempts[ip]

            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")


# Global instance
brute_force_protection = BruteForceProtection()
