from datetime import datetime
import os
import pandas_gbq
from dotenv import load_dotenv
from strava.oauth import refresh_access_token
from strava.strava import get_activities, make_activities_df, enrich_activities_with_details

load_dotenv()

def upload_to_bigquery(df):
    project_id = os.getenv("BIGQUERY_PROJECT")
    dataset_id = os.getenv("BIGQUERY_DATASET")
    table_id = os.getenv("BIGQUERY_TABLE")

    if not all([project_id, dataset_id, table_id]):
        print("❌ Missing BigQuery config in .env")
        return

    full_table_id = f"{dataset_id}.{table_id}"

    print(f"⬆️ Uploading to BigQuery: {project_id}.{full_table_id}...")

    pandas_gbq.to_gbq(
        df.reset_index(),  # include index if needed
        destination_table=full_table_id,
        project_id=project_id,
        if_exists="replace",  # or "append"
    )

    print(f"✅ Uploaded {len(df)} rows to {project_id}.{full_table_id}")


def main():
    # Optional filters
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    activity_types = ["Run", "Ride"]

    token = refresh_access_token()
    activities = get_activities(
        token,
        start_date=start_date,
        end_date=end_date,
        activity_types=activity_types
    )

    # Enrich with calories from detailed endpoint
    # activities = enrich_activities_with_details(activities, token, limit=100)

    df = make_activities_df(activities)

    if not df.empty:
        print(df.head())
        upload_to_bigquery(df)

if __name__ == "__main__":
    main()


