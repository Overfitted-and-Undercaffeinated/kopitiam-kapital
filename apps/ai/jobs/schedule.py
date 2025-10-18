"""Job scheduling configuration"""

def setup_schedule():
    """Configure scheduled jobs"""
    # TODO: Set up Celery Beat schedule
    # - Morning briefs at 7 AM SGT
    # - EOD reports at 6 PM SGT
    # - Market monitoring every 5 minutes during trading hours
    
    schedule = {
        'morning-brief': {
            'task': 'jobs.tasks.send_morning_briefs',
            'schedule': '0 7 * * 1-5',  # 7 AM weekdays
        },
        'eod-report': {
            'task': 'jobs.tasks.send_eod_reports',
            'schedule': '0 18 * * 1-5',  # 6 PM weekdays
        },
        'position-monitor': {
            'task': 'jobs.tasks.monitor_all_positions',
            'schedule': 60,  # Every 60 seconds
        },
    }
    
    return schedule

