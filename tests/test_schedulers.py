"""Tests for scheduler functionality."""

import pytest
from unittest.mock import Mock

from data_ingestion.schedulers.cron_scheduler import CronScheduler


def test_cron_scheduler_initialization():
    """Test CronScheduler initialization."""
    scheduler = CronScheduler()
    
    assert scheduler.jobs == []
    assert scheduler.running is False


def test_schedule_daily():
    """Test daily scheduling."""
    scheduler = CronScheduler()
    
    mock_task = Mock()
    scheduler.schedule_daily(mock_task, "02:00", "test_task")
    
    assert len(scheduler.jobs) == 1
    assert scheduler.jobs[0]['name'] == 'test_task'
    assert 'Daily at 02:00' in scheduler.jobs[0]['schedule']


def test_schedule_hourly():
    """Test hourly scheduling."""
    scheduler = CronScheduler()
    
    mock_task = Mock()
    scheduler.schedule_hourly(mock_task, "test_task")
    
    assert len(scheduler.jobs) == 1
    assert scheduler.jobs[0]['schedule'] == 'Hourly'


def test_schedule_interval():
    """Test interval scheduling."""
    scheduler = CronScheduler()
    
    mock_task = Mock()
    scheduler.schedule_interval(mock_task, 30, "test_task")
    
    assert len(scheduler.jobs) == 1
    assert 'Every 30 minutes' in scheduler.jobs[0]['schedule']


def test_list_jobs():
    """Test listing scheduled jobs."""
    scheduler = CronScheduler()
    
    mock_task = Mock()
    scheduler.schedule_daily(mock_task, "02:00", "task1")
    scheduler.schedule_hourly(mock_task, "task2")
    
    jobs = scheduler.list_jobs()
    
    assert len(jobs) == 2
    assert jobs[0]['name'] == 'task1'
    assert jobs[1]['name'] == 'task2'


def test_clear_all():
    """Test clearing all jobs."""
    scheduler = CronScheduler()
    
    mock_task = Mock()
    scheduler.schedule_daily(mock_task, "02:00", "task1")
    
    assert len(scheduler.jobs) == 1
    
    scheduler.clear_all()
    
    assert len(scheduler.jobs) == 0
