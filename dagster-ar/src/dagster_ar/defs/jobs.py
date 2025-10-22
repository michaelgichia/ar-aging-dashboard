import dagster as dg
from dagster_ar.defs.daily_partitions import daily_partition
from dagster_ar.defs.partitions import aging_bucket_partitions

# Asset selections for different job types
daily_update_assets = dg.AssetSelection.assets(
    "extract_customers",
    "transform_customers",
    "load_customers",
    "extract_invoices",
    "extract_payments",
    "transform_invoices",
    "load_invoices",
    "transform_payments",
    "load_payments"
)

aging_bucket_assets = dg.AssetSelection.assets(
    "extract_customers_partitioned",
    "transform_customers_partitioned",
    "load_customers_partitioned",
    "extract_invoices_partitioned",
    "extract_payments_partitioned",
    "transform_invoices_partitioned",
    "load_invoices_partitioned",
    "transform_payments_partitioned",
    "load_payments_partitioned"
)

# Daily update job - runs every midnight to fetch last 24 hours of data
daily_update_job = dg.define_asset_job(
    name="daily_update_job",
    partitions_def=daily_partition,
    selection=daily_update_assets,
    description="Daily job to fetch new invoices, customers, and payments from the last 24 hours"
)

# Aging bucket backfill job - for backfilling historical data by aging buckets
aging_bucket_backfill_job = dg.define_asset_job(
    name="aging_bucket_backfill_job",
    partitions_def=aging_bucket_partitions,
    selection=aging_bucket_assets,
    description="Job to backfill historical data by aging buckets (Current, 1-30 days, 31-60 days, etc.)"
)

# Combined job for running all assets (both daily and partitioned)
all_assets_job = dg.define_asset_job(
    name="all_assets_job",
    selection=dg.AssetSelection.all(),
    description="Job to run all assets (both daily and partitioned)"
)
