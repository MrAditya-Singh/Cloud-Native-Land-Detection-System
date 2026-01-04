"""Cron-based scheduler for automated data ingestion."""

import logging
import schedule
import time
from typing import Callable, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CronScheduler:
    """
    Cron-style scheduler for automated satellite data downloads.
    
    Uses the schedule library to run ingestion tasks at specified intervals.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize cron scheduler.
        
        Args:
            config: Scheduler configuration
        """
        self.config = config or {}
        self.jobs = []
        self.running = False
        logger.info("Cron scheduler initialized")
    
    def schedule_daily(
        self,
        task: Callable,
        time_str: str = "02:00",
        task_name: str = "ingestion_task"
    ) -> None:
        """
        Schedule a task to run daily at a specific time.
        
        Args:
            task: Callable to execute
            time_str: Time in HH:MM format (24-hour)
            task_name: Name for the task
        """
        job = schedule.every().day.at(time_str).do(
            self._wrapped_task, task, task_name
        )
        self.jobs.append({
            'job': job,
            'name': task_name,
            'schedule': f"Daily at {time_str}"
        })
        logger.info(f"Scheduled task '{task_name}' to run daily at {time_str}")
    
    def schedule_hourly(
        self,
        task: Callable,
        task_name: str = "ingestion_task"
    ) -> None:
        """
        Schedule a task to run every hour.
        
        Args:
            task: Callable to execute
            task_name: Name for the task
        """
        job = schedule.every().hour.do(
            self._wrapped_task, task, task_name
        )
        self.jobs.append({
            'job': job,
            'name': task_name,
            'schedule': "Hourly"
        })
        logger.info(f"Scheduled task '{task_name}' to run hourly")
    
    def schedule_interval(
        self,
        task: Callable,
        interval_minutes: int,
        task_name: str = "ingestion_task"
    ) -> None:
        """
        Schedule a task to run at a specific interval.
        
        Args:
            task: Callable to execute
            interval_minutes: Interval in minutes
            task_name: Name for the task
        """
        job = schedule.every(interval_minutes).minutes.do(
            self._wrapped_task, task, task_name
        )
        self.jobs.append({
            'job': job,
            'name': task_name,
            'schedule': f"Every {interval_minutes} minutes"
        })
        logger.info(f"Scheduled task '{task_name}' to run every {interval_minutes} minutes")
    
    def schedule_from_cron(
        self,
        task: Callable,
        cron_expr: str,
        task_name: str = "ingestion_task"
    ) -> None:
        """
        Schedule a task using cron expression.
        
        Args:
            task: Callable to execute
            cron_expr: Cron expression (simplified parsing)
            task_name: Name for the task
            
        Note:
            This is a simplified cron parser. For full cron support,
            consider using python-crontab library.
        """
        # Parse simple cron expressions like "0 2 * * *"
        parts = cron_expr.split()
        
        if len(parts) >= 5:
            minute, hour, day, month, weekday = parts[:5]
            
            if minute != '*' and hour != '*':
                # Daily at specific time
                time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
                self.schedule_daily(task, time_str, task_name)
            elif minute == '0' and hour == '*':
                # Every hour
                self.schedule_hourly(task, task_name)
            else:
                logger.warning(f"Unsupported cron expression: {cron_expr}")
        else:
            logger.warning(f"Invalid cron expression: {cron_expr}")
    
    def _wrapped_task(self, task: Callable, task_name: str) -> None:
        """
        Wrapper for scheduled tasks with error handling and logging.
        
        Args:
            task: Task to execute
            task_name: Name of the task
        """
        logger.info(f"Starting scheduled task: {task_name}")
        start_time = datetime.now()
        
        try:
            task()
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Task '{task_name}' completed successfully in {duration:.2f}s")
        except Exception as e:
            logger.error(f"Task '{task_name}' failed with error: {e}", exc_info=True)
    
    def run(self, run_once: bool = False) -> None:
        """
        Start the scheduler.
        
        Args:
            run_once: If True, run all pending jobs once and exit
        """
        if not self.jobs:
            logger.warning("No jobs scheduled")
            return
        
        self.running = True
        logger.info(f"Starting cron scheduler with {len(self.jobs)} jobs")
        
        try:
            if run_once:
                schedule.run_all()
                logger.info("All jobs executed once")
            else:
                while self.running:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Scheduler error: {e}", exc_info=True)
            self.running = False
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        logger.info("Stopping cron scheduler")
    
    def clear_all(self) -> None:
        """Clear all scheduled jobs."""
        schedule.clear()
        self.jobs = []
        logger.info("Cleared all scheduled jobs")
    
    def list_jobs(self) -> list:
        """
        List all scheduled jobs.
        
        Returns:
            List of job information
        """
        return [
            {
                'name': job['name'],
                'schedule': job['schedule'],
                'next_run': str(job['job'].next_run) if hasattr(job['job'], 'next_run') else None
            }
            for job in self.jobs
        ]
