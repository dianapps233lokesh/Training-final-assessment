from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "analytics"

    def ready(self):
        import logging
        from datetime import timedelta  # Import timedelta

        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from django.conf import settings
        from django_apscheduler.jobstores import DjangoJobStore
        from django_apscheduler.models import DjangoJobExecution

        from analytics.jobs import (
            daily_sales_aggregation_job,
            low_stock_alert_job,
            pending_order_reminder_job,
        )

        logger = logging.getLogger(__name__)

        def start_scheduler():
            scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
            scheduler.add_jobstore(DjangoJobStore(), "default")

            # Clear old job executions
            DjangoJobExecution.objects.delete_old_job_executions(
                max_age=int(timedelta(days=7).total_seconds())
            )

            # Job 1: Daily Sales Aggregation
            # Schedule: Every day at 11:59 PM (for testing: every 2 minutes)
            scheduler.add_job(
                daily_sales_aggregation_job,
                trigger=CronTrigger(hour="23", minute="59"),  # Production schedule
                # trigger=CronTrigger(minute="*/2"), # Testing schedule
                id="daily_sales_aggregation",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added job 'daily_sales_aggregation'.")

            # Job 2: Low Stock Alert
            # Schedule: Every day at 9:00 AM (for testing: every 1 minute)
            scheduler.add_job(
                low_stock_alert_job,
                trigger=CronTrigger(hour="9", minute="0"),  # Production schedule
                # trigger=CronTrigger(minute="*/1"), # Testing schedule
                id="low_stock_alert",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added job 'low_stock_alert'.")

            # Job 3: Pending Order Reminder
            # Schedule: Every 6 hours (for testing: every 3 minutes)
            scheduler.add_job(
                pending_order_reminder_job,
                trigger=CronTrigger(hour="*/6"),  # Production schedule
                # trigger=CronTrigger(minute="*/3"), # Testing schedule
                id="pending_order_reminder",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added job 'pending_order_reminder'.")

            try:
                logger.info("Starting scheduler...")
                scheduler.start()
            except KeyboardInterrupt:
                logger.info("Scheduler stopped.")
                scheduler.shutdown()
            except Exception as e:
                logger.error(f"Scheduler failed to start: {e}")

        # Ensure scheduler starts only once
        if settings.DEBUG:
            # In development, run once to avoid duplicate jobs on reloads
            import os

            if os.environ.get("RUN_MAIN", None) != "true":
                start_scheduler()
        else:
            start_scheduler()
