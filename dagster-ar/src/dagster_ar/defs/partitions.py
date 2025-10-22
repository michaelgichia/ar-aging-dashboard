import dagster as dg


# Define the aging bucket partition keys
AGING_BUCKET_KEYS = ["0", "1", "2", "3", "4", "5"]

# Create the static partition definition
aging_bucket_partitions = dg.StaticPartitionsDefinition(AGING_BUCKET_KEYS)


def get_aging_bucket_info():
    """
    Get aging bucket information mapping partition keys to day ranges.
    Returns a dictionary mapping partition key to (min_days, max_days).
    """
    return {
        "0": (0, 0),      # Current
        "1": (1, 30),     # 1-30 days
        "2": (31, 60),    # 31-60 days
        "3": (61, 90),    # 61-90 days
        "4": (91, 120),   # 91-120 days
        "5": (121, None), # 120+ days (None means no upper limit)
    }


def get_days_range_for_partition(partition_key: str):
    """Get the min and max days for a given partition key."""
    aging_info = get_aging_bucket_info()
    return aging_info.get(partition_key, (0, 0))


def get_partition_key_for_record(record) -> str:
    """Determine which aging bucket a record belongs to based on days_overdue."""
    if hasattr(record, 'days_overdue'):
        days_overdue = record.days_overdue
    elif isinstance(record, dict) and 'days_overdue' in record:
        days_overdue = record['days_overdue']
    else:
        return "0"

    # Use the same logic as the categorize function
    if days_overdue is None or days_overdue <= 0:
        return "0"
    elif days_overdue <= 30:
        return "1"
    elif days_overdue <= 60:
        return "2"
    elif days_overdue <= 90:
        return "3"
    elif days_overdue <= 120:
        return "4"
    else:
        return "5"
