import dagster as dg

from dagster_ar.defs.assets import invoices
from dagster_ar.defs.assets import partitioned_invoices
from dagster_ar.defs.jobs import daily_update_job, aging_bucket_backfill_job, all_assets_job
from dagster_ar.defs.schedules import daily_update_schedule
from dagster_ar.defs.resources.database import DatabaseResource
from dagster_ar.defs.resources.unified import UnifiedAccountingResource

postgres_resource_instance = DatabaseResource(
    user=dg.EnvVar("POSTGRES_USER"),
    password=dg.EnvVar("POSTGRES_PASSWORD"),
    host=dg.EnvVar("POSTGRES_HOST"),
    port=5432,
    database=dg.EnvVar("POSTGRES_DB"),
)

unified_api_instance = UnifiedAccountingResource(
    base_url=dg.EnvVar("UNIFIED_BASE_URL"),
    conn_id=dg.EnvVar("UNIFIED_CONN_ID"),
    api_key=dg.EnvVar("UNIFIED_API_KEY"),
)

all_assets = dg.load_assets_from_modules(modules=[invoices, partitioned_invoices])


@dg.definitions
def defs():
    return dg.Definitions(
        assets=all_assets,
        jobs=[daily_update_job, aging_bucket_backfill_job, all_assets_job],
        schedules=[daily_update_schedule],
        resources={
            "database": postgres_resource_instance,
            "unified_api": unified_api_instance,
        },
    )
