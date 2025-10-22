import math
from sqlalchemy import text
import dagster as dg
import pandas as pd
from uuid import UUID
from datetime import datetime, timedelta

from common.db.invoices import invoice_columns
from common.db.payments import payments_columns
from dagster_ar.defs.resources.database import DatabaseResource
from dagster_ar.defs.resources.unified import UnifiedAccountingResource
from common.db.customers import customers_columns
from dagster_ar.defs.partitions import (
    aging_bucket_partitions,
    get_days_range_for_partition,
)


def categorize(days):
    """Categorize days overdue into aging buckets."""
    if pd.isna(days):
        return 0
    elif days <= 0:
        return 0
    elif days <= 30:
        return 1
    elif days <= 60:
        return 2
    elif days <= 90:
        return 3
    elif days <= 120:
        return 4
    else:
        return 5


def get_aging_bucket_filter(partition_key: str) -> dict:
    """Get filter parameters for a specific aging bucket partition."""
    min_days, max_days = get_days_range_for_partition(partition_key)

    # Calculate date range for the aging bucket
    today = datetime.now()

    if partition_key == "0":  # Current
        # Current: due date is today or in the future
        return {
            "due_date_from": today.strftime("%Y-%m-%d"),
            "due_date_to": (today + timedelta(days=365)).strftime(
                "%Y-%m-%d"
            ),  # Future invoices
            "min_days": 0,
            "max_days": 0,
        }
    elif partition_key == "5":  # 120+ days
        # 120+ days: due date is more than 120 days ago
        due_date_cutoff = today - timedelta(days=120)
        return {
            "due_date_from": "1900-01-01",  # Very old date
            "due_date_to": due_date_cutoff.strftime("%Y-%m-%d"),
            "min_days": 121,
            "max_days": None,
        }
    else:
        # Specific day ranges
        due_date_from = today - timedelta(days=max_days)
        due_date_to = today - timedelta(days=min_days)
        return {
            "due_date_from": due_date_from.strftime("%Y-%m-%d"),
            "due_date_to": due_date_to.strftime("%Y-%m-%d"),
            "min_days": min_days,
            "max_days": max_days,
        }


@dg.asset(partitions_def=aging_bucket_partitions)
def extract_customers_partitioned(context, unified_api: UnifiedAccountingResource):
    """
    Fetches customers for a specific aging bucket partition.
    """
    partition_key = context.partition_key

    data = unified_api.get_customers(params={"env": "Sandbox", "limit": 50})

    context.log.info(f"Extracted {len(data)} customers for partition {partition_key}")
    return data


@dg.asset(
    partitions_def=aging_bucket_partitions,
    ins={"customers": dg.AssetIn("extract_customers_partitioned")},
)
def transform_customers_partitioned(context, customers: list) -> pd.DataFrame:
    """
    Transforms raw customer data for a specific aging bucket partition.
    """
    df = pd.DataFrame(customers)
    customer_copy = df.copy()
    customers_df = customer_copy[customers_columns]

    context.log.info(
        f"Transformed {len(customers_df)} customers for partition {context.partition_key}"
    )
    return customers_df


@dg.asset(
    partitions_def=aging_bucket_partitions,
    ins={"customers": dg.AssetIn("transform_customers_partitioned")},
)
def load_customers_partitioned(
    context, database: DatabaseResource, customers: pd.DataFrame
) -> None:
    """
    Loads customers for a specific aging bucket partition.
    """
    if customers.empty:
        context.log.info(f"No customers to load for partition {context.partition_key}")
        return

    with database.get_transaction() as conn:
        # UPSERT each customer
        insert_sql = text("""
          INSERT INTO customers (
              id, name, company_name, is_active, is_supplier, created_at, updated_at
          ) VALUES (
              :id, :name, :company_name, :is_active, :is_supplier, NOW(), NOW()
          )
          ON CONFLICT (id) DO UPDATE
          SET
              name = EXCLUDED.name,
              company_name = EXCLUDED.company_name,
              is_active = EXCLUDED.is_active,
              is_supplier = EXCLUDED.is_supplier,
              updated_at = NOW()
          WHERE customers.name = '[Unknown Customer]'
            OR customers.company_name = '[Unknown Company]';
      """)

        for _, row in customers.iterrows():
            # Safely convert is_supplier to boolean
            is_supplier = row.get("is_supplier", False)
            if is_supplier is None or (
                isinstance(is_supplier, float) and math.isnan(is_supplier)
            ):
                is_supplier = False
            else:
                is_supplier = bool(is_supplier)

            conn.execute(
                insert_sql,
                {
                    "id": UUID(str(row["id"])),
                    "name": row["name"],
                    "company_name": row.get("company_name", ""),
                    "is_active": bool(row.get("is_active", True)),
                    "is_supplier": is_supplier,
                },
            )

    context.log.info(
        f"Loaded {len(customers)} customers for partition {context.partition_key}"
    )


@dg.asset(partitions_def=aging_bucket_partitions, deps=["load_customers_partitioned"])
def extract_invoices_partitioned(context, unified_api: UnifiedAccountingResource):
    """
    Fetches invoices for a specific aging bucket partition based on due date range.
    """
    partition_key = context.partition_key
    aging_filter = get_aging_bucket_filter(partition_key)

    # Build params for the API call
    params = {
        "env": "Sandbox",
        "limit": 50,
        "due_date_from": aging_filter["due_date_from"],
        "due_date_to": aging_filter["due_date_to"],
    }

    data = unified_api.get_invoices(params=params)

    context.log.info(
        f"Extracted {len(data)} invoices for partition {partition_key} "
        f"(due_date: {aging_filter['due_date_from']} to {aging_filter['due_date_to']})"
    )
    return data


@dg.asset(partitions_def=aging_bucket_partitions)
def extract_payments_partitioned(context, unified_api: UnifiedAccountingResource):
    """
    Fetches payments for a specific aging bucket partition.
    """
    partition_key = context.partition_key
    aging_filter = get_aging_bucket_filter(partition_key)

    # Build params for the API call
    params = {
        "env": "Sandbox",
        "limit": 50,
        "due_date_from": aging_filter["due_date_from"],
        "due_date_to": aging_filter["due_date_to"],
    }

    data = unified_api.get_payments(params=params)

    context.log.info(f"Extracted {len(data)} payments for partition {partition_key}")
    return data


@dg.asset(
    partitions_def=aging_bucket_partitions,
    ins={
        "invoices": dg.AssetIn("extract_invoices_partitioned"),
        "payments": dg.AssetIn("extract_payments_partitioned"),
    },
)
def transform_invoices_partitioned(
    context, invoices: list, payments: list
) -> pd.DataFrame:
    """
    Transforms invoices and payments for a specific aging bucket partition.
    """
    partition_key = context.partition_key

    if not invoices:
        context.log.info(f"No invoices to transform for partition {partition_key}")
        return pd.DataFrame()

    invoices_df = pd.DataFrame(invoices)
    invoices_df["invoice_at"] = pd.to_datetime(
        invoices_df["invoice_at"], errors="coerce", utc=True
    )

    payments_df = pd.DataFrame(payments)
    payments_summary = (
        payments_df.groupby("invoice_id")["total_amount"]
        .sum()
        .reset_index(name="total_paid")
    )

    merged = invoices_df.merge(
        payments_summary, how="left", left_on="id", right_on="invoice_id"
    )

    merged = merged.drop(columns=["invoice_id"])
    merged["total_paid"] = merged["total_paid"].fillna(0)
    merged["balance_amount"] = merged["total_amount"] - merged["total_paid"]
    merged["due_at"] = pd.to_datetime(merged["due_at"], errors="coerce", utc=True)
    today = pd.Timestamp.now(tz="UTC")
    merged["days_overdue"] = (today - merged["due_at"]).dt.days
    merged["days_overdue"] = merged["days_overdue"].fillna(0).clip(lower=0)
    merged["aging_bucket"] = merged["days_overdue"].apply(categorize)

    # Filter to only include records that match this partition's aging bucket
    aging_filter = get_aging_bucket_filter(partition_key)
    min_days, max_days = aging_filter["min_days"], aging_filter["max_days"]

    if partition_key == "0":  # Current
        # Current: days_overdue should be 0 or negative
        filtered_merged = merged[merged["days_overdue"] <= 0]
    elif partition_key == "5":  # 120+ days
        # 120+ days: days_overdue should be > 120
        filtered_merged = merged[merged["days_overdue"] > 120]
    else:
        # Specific ranges: days_overdue should be within the range
        if max_days is not None:
            filtered_merged = merged[
                (merged["days_overdue"] >= min_days)
                & (merged["days_overdue"] <= max_days)
            ]
        else:
            filtered_merged = merged[merged["days_overdue"] >= min_days]

    ar_aging_df = filtered_merged.rename(
        columns={
            "id": "invoice_id",
            "contact_id": "customer_id",
        }
    )

    result_df = ar_aging_df[invoice_columns]
    context.log.info(
        f"Transformed {len(result_df)} invoices for partition {partition_key}"
    )
    return result_df


@dg.asset(
    partitions_def=aging_bucket_partitions,
    ins={"aging_data": dg.AssetIn("transform_invoices_partitioned")},
)
def load_invoices_partitioned(
    context, database: DatabaseResource, aging_data: pd.DataFrame
) -> None:
    """
    Loads invoices for a specific aging bucket partition.
    """
    partition_key = context.partition_key

    if aging_data.empty:
        context.log.info(f"No invoice data to load for partition {partition_key}")
        return

    aging_data = aging_data.copy()
    staging_table_name = f"invoices_staging_bucket_{partition_key}"

    invoice_update_columns = [
        "customer_id",
        "invoice_number",
        "invoice_at",
        "due_at",
        "currency",
        "days_overdue",
        "aging_bucket",
    ]

    with database.get_transaction() as conn:
        aging_data.to_sql(
            staging_table_name,
            con=conn,
            if_exists="replace",
            index=False,
        )

        customer_ids = aging_data["customer_id"].dropna().unique().tolist()

        if customer_ids:
            params = {f"id_{i}": str(cid) for i, cid in enumerate(customer_ids)}
            placeholders = ", ".join(f":id_{i}" for i in range(len(customer_ids)))

            existing_query = text(f"""
                SELECT id
                FROM customers
                WHERE id IN ({placeholders})
            """)

            existing_ids = {
                row[0] for row in conn.execute(existing_query, params).fetchall()
            }
            missing_ids = [cid for cid in customer_ids if cid not in existing_ids]
        else:
            missing_ids = []

        if missing_ids:
            insert_sql = text("""
                INSERT INTO customers (
                    id, name, company_name, is_active, is_supplier, created_at, updated_at
                )
                VALUES (
                    :id, '[Unknown Customer]', '[Unknown Company]', TRUE, FALSE, NOW(), NOW()
                )
                ON CONFLICT (id) DO NOTHING;
            """)
            for cid in missing_ids:
                conn.execute(insert_sql, {"id": UUID(str(cid))})

        set_clause = ", ".join(
            [f"{col} = EXCLUDED.{col}" for col in invoice_update_columns]
        )

        upsert_sql = text(f"""
            INSERT INTO invoices (
                invoice_id, customer_id, invoice_number, currency,
                total_amount, balance_amount, tax_amount,
                invoice_at, due_at, days_overdue, aging_bucket,
                status, type, notes, posted_at, paid_amount,
                created_at, updated_at
            )
            SELECT
                invoice_id::uuid, customer_id::uuid, invoice_number, currency,
                total_amount, balance_amount, tax_amount,
                invoice_at::timestamptz, due_at::timestamptz, days_overdue,
                aging_bucket, status, type, notes, posted_at::timestamptz,
                paid_amount, NOW(), NOW()
            FROM {staging_table_name}
            ON CONFLICT (invoice_id) DO UPDATE SET
                {set_clause};
        """)

        conn.execute(upsert_sql)

    context.log.info(f"Loaded {len(aging_data)} invoices for partition {partition_key}")


@dg.asset(
    partitions_def=aging_bucket_partitions,
    ins={"payments": dg.AssetIn("extract_payments_partitioned")},
)
def transform_payments_partitioned(context, payments: list):
    """
    Transforms payment data for a specific aging bucket partition.
    """
    partition_key = context.partition_key

    df = pd.DataFrame(payments)
    payments_df_copy = df.copy()
    payments_df = payments_df_copy[payments_columns].rename(
        columns={"id": "payment_id", "contact_id": "customer_id"}
    )

    context.log.info(
        f"Transformed {len(payments_df)} payments for partition {partition_key}"
    )
    return payments_df


@dg.asset(
    partitions_def=aging_bucket_partitions,
    ins={"payments": dg.AssetIn("transform_payments_partitioned")},
)
def load_payments_partitioned(
    context, database: DatabaseResource, payments: pd.DataFrame
) -> None:
    """
    Loads payments for a specific aging bucket partition.
    """
    partition_key = context.partition_key

    if payments.empty:
        context.log.info(f"No payments to load for partition {partition_key}")
        return

    with database.get_connection() as conn:
        table_name = f"payments_bucket_{partition_key}"
        payments.to_sql(table_name, con=conn, if_exists="replace", index=False)

    context.log.info(f"Loaded {len(payments)} payments for partition {partition_key}")
