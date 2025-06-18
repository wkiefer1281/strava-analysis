import time
import pandas as pd
import requests
from datetime import datetime
from typing import Optional, List


def get_activities(
    access_token: str,
    per_page: int = 200,
    max_pages: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    activity_types: Optional[List[str]] = None,
):
    activities = []
    params = {"per_page": per_page}

    if start_date:
        params["after"] = int(start_date.timestamp())
    if end_date:
        params["before"] = int(end_date.timestamp())

    for page in range(1, max_pages + 1):
        params["page"] = page
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break

        # Filter by activity type (Strava API doesn't support it directly)
        if activity_types:
            batch = [act for act in batch if act['type'] in activity_types]

        activities.extend(batch)

    return activities


def get_activity_details(activity_id, access_token):
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        print("⏱️ Rate limit hit, sleeping 15 minutes...")
        time.sleep(900)
        return get_activity_details(activity_id, access_token)

    response.raise_for_status()
    return response.json()


def enrich_activities_with_details(activities, access_token, limit=None):
    enriched = []
    for i, activity in enumerate(activities):
        if limit and i >= limit:
            break
        details = get_activity_details(activity['id'], access_token)
        activity['calories'] = details.get('calories', None)
        enriched.append(activity)

        # Optional: avoid hitting rate limits too quickly
        time.sleep(0.1)

    return enriched


def make_activities_df(activities):
    df = pd.DataFrame(activities)
    if df.empty:
        print("No activities found.")
        return df

    df['start_date'] = pd.to_datetime(df['start_date'])

    # Distance in miles
    df['distance_mi'] = df['distance'] / 1609.34

    # Time in minutes
    df['elapsed_minutes'] = df['elapsed_time'] / 60
    df['moving_minutes'] = df['moving_time'] / 60

    # Pace in min/mile (was min/km)
    df['pace_min_per_mi'] = df['moving_minutes'] / df['distance_mi']

    df['activity_type'] = df['type']

    # Optional fields, converted to imperial where applicable
    df['elevation_gain_ft'] = df.get('total_elevation_gain', 0) * 3.28084
    df['average_speed_mph'] = df.get('average_speed', 0) * 2.23694
    df['max_speed_mph'] = df.get('max_speed', 0) * 2.23694

    # Optional fields (safe defaults)
    optional_cols = [
        'average_heartrate',
        'max_heartrate',
        'calories'
    ]
    for col in optional_cols:
        if col not in df.columns:
            df[col] = None

    # Flatten lat/lng coordinates
    def extract_latlng(value, index):
        if isinstance(value, list) and len(value) == 2:
            return value[index]
        return None

    df['start_lat'] = df['start_latlng'].apply(lambda x: extract_latlng(x, 0))
    df['start_lng'] = df['start_latlng'].apply(lambda x: extract_latlng(x, 1))
    df['end_lat'] = df['end_latlng'].apply(lambda x: extract_latlng(x, 0))
    df['end_lng'] = df['end_latlng'].apply(lambda x: extract_latlng(x, 1))

    # Drop original nested columns
    df.drop(columns=['start_latlng', 'end_latlng'], errors='ignore', inplace=True)

    df.set_index(['activity_type', 'start_date'], inplace=True)
    return df
