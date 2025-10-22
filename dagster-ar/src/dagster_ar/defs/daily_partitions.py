import dagster as dg
from datetime import datetime, date

# Create daily partition definition starting from 2025-01-01
daily_partition = dg.DailyPartitionsDefinition(
    start_date="2025-01-01",
    end_date=None,  # No end date - runs indefinitely
    timezone="UTC"
)
