import math
from sqlalchemy import text
import dagster as dg
import pandas as pd
from uuid import UUID

from common.db.invoices import invoice_columns
from common.db.payments import payments_columns
from dagster_ar.defs.resources.database import DatabaseResource
from dagster_ar.defs.resources.unified import UnifiedAccountingResource
from common.db.customers import customers_columns


def categorize(days):
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


final_table_name = "invoices"
staging_table_name = "invoices_staging"


@dg.asset
def extract_customers(unified_api: UnifiedAccountingResource):
    """
    Fetches the customers from the Unified Accounting endpoint.
    """

    data = unified_api.get_customers(params={"env": "Sandbox", "limit": 50})
    return data


@dg.asset(ins={"customers": dg.AssetIn("extract_customers")})
def transform_customers(customers: list) -> pd.DataFrame:
    """
    Transforms raw customer data to calculate the days overdue,
    without assigning aging buckets.
    """

    df = pd.DataFrame(customers)

    customer_copy = df.copy()

    customers_df = customer_copy[customers_columns]

    return customers_df

@dg.asset(ins={"customers": dg.AssetIn("transform_customers")})
def load_customers(database: DatabaseResource, customers: pd.DataFrame) -> None:
    """
    Loads customers into Postgres.
    Updates existing rows only if current names are not '[Unknown Customer]' / '[Unknown Company]'.
    """
    if customers.empty:
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


@dg.asset(deps=["load_customers"])
def extract_invoices(unified_api: UnifiedAccountingResource):
    """
    Fetches the invoices from the Unified Accounting endpoint.
    """

    data = unified_api.get_invoices(params={"env": "Sandbox", "limit": 50})
    return data


@dg.asset
def extract_payments(unified_api: UnifiedAccountingResource):
    """
    Fetches the payments from the Unified Accounting endpoint.
    """
    data = unified_api.get_payments(params={"env": "Sandbox", "limit": 50})
    return data


@dg.asset(
    ins={
        "invoices": dg.AssetIn("extract_invoices"),
        "payments": dg.AssetIn("extract_payments"),
    }
)
def transform_invoices(invoices: list, payments: list) -> pd.DataFrame:
    if not invoices:
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
    ar_aging_df = merged.rename(
        columns={
            "id": "invoice_id",
            "contact_id": "customer_id",
        }
    )

    return ar_aging_df[invoice_columns]


@dg.asset(ins={"aging_data": dg.AssetIn("transform_invoices")})
def load_invoices(database: DatabaseResource, aging_data: pd.DataFrame) -> None:
    """
    Loads and UPSERTs (Update or Insert) the AR aging data using a temporary
    staging table. Ensures missing customers are inserted as placeholders.
    """
    if aging_data.empty:
        return

    aging_data = aging_data.copy()

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
        # conn.execute(text(f"DROP TABLE IF EXISTS {staging_table_name} CASCADE"))

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
            INSERT INTO {final_table_name} (
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

        # conn.execute(text(f"DROP TABLE {staging_table_name}"))


@dg.asset(ins={"payments": dg.AssetIn("extract_payments")})
def transform_payments(payments: list):
    """
    Transforms raw payment data to calculate the days overdue.
    """

    df = pd.DataFrame(payments)
    payments_df_copy = df.copy()
    payments_df = payments_df_copy[payments_columns].rename(
        columns={"id": "payment_id", "contact_id": "customer_id"}
    )
    return payments_df


@dg.asset(ins={"payments": dg.AssetIn("transform_payments")})
def load_payments(database: DatabaseResource, payments: pd.DataFrame) -> None:
    """
    Loads the final AR aging data into a dedicated Postgres table.
    (Implementation remains the same)
    """
    if payments.empty:
        return

    with database.get_connection() as conn:
        payments.to_sql("payments", con=conn, if_exists="replace", index=False)
