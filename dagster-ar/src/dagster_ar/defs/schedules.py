import dagster as dg
from dagster_ar.defs.jobs import daily_update_job

# Schedule to run daily update job every midnight UTC
daily_update_schedule = dg.ScheduleDefinition(
    job=daily_update_job,
    cron_schedule="0 0 * * *",  # Every day at midnight UTC
    name="daily_update_schedule",
    description="Runs daily update job every midnight to fetch new data from the last 24 hours"
)
