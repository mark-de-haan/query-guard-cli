from concurrent import futures
import sys
from typing import cast

from google.auth import default
from google.auth.credentials import Credentials
from google.cloud.bigquery import Client as BigQueryClient


def get_bq_client(project_id: str | None = None) -> BigQueryClient:
    """
    Authenticates using local Application Default Credentials (ADC).
    Returns a configured BigQueryClient.
    """
    try:
        credentials, default_project = default()
        target_project = project_id or default_project

        if not target_project:
            print(
                "Error: No Google Cloud project found. Please pass --project or set a default in gcloud.")
            sys.exit(1)

        return BigQueryClient(project=target_project, credentials=cast(Credentials, credentials))

    except Exception as e:
        print(f"Authentication Error: {e}")
        print("Tip: Run 'gcloud auth application-default login' to authenticate.")
        sys.exit(1)


def discover_active_regions(client: BigQueryClient, project_id: str) -> list[str]:
    """
    Auto-detects active regions by listing datasets.
    Accesses _properties directly as DatasetListItem does not expose .location.
    """
    print(f"   ... Auto-discovering active regions for {project_id} ...")
    try:
        datasets = list(client.list_datasets(project=project_id))
    except Exception as e:
        print(f"   Warning: Could not list datasets to discover regions ({e})")
        return ["us", "eu"] # Fallback defaults

    regions = set()
    for dataset in datasets:
        # Accessing the raw resource dict
        props = dataset._properties
        if "location" in props:
            regions.add(props["location"].lower())
    
    found = list(regions)
    if not found:
        print("   Warning: No datasets found. Defaulting to 'us'.")
        return ["us"]
        
    print(f"   Found active data in: {', '.join(found)}")
    return found


def _fetch_single_region(client: BigQueryClient, project_id: str, region: str, days: int, limit: int) -> list[dict]:
    """Worker: Scans one specific region."""
    table_id = f"`{project_id}`.`region-{region}`.INFORMATION_SCHEMA.JOBS"
    
    query = f"""
        SELECT
        job_id,
        user_email,
        total_bytes_billed,
        query,
        creation_time,
        total_slot_ms,
        statement_type
    FROM
        {table_id}
    WHERE
        creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        AND job_type = 'QUERY'
        AND statement_type != 'SCRIPT'
        AND total_bytes_billed > 0
    ORDER BY
        total_bytes_billed DESC
    LIMIT {limit}
    """
    try:
        query_job = client.query(query)
        return [dict(row) | {"region": region} for row in query_job.result()]
    except Exception:
        return []


def fetch_recent_jobs(client: BigQueryClient, project_id: str, region: str, days: int, global_scan: bool, limit: int) -> list[dict]:
    """
    Fetches jobs from a single region OR auto-discovers all regions if global_scan is True.
    """
    if not global_scan:
        return _fetch_single_region(client, project_id, region.lower(), days, limit)
    
    regions_to_scan: list[str] = discover_active_regions(client, project_id)
    all_jobs: list[dict] = []
    
    print(f"   ... Scanning {len(regions_to_scan)} regions in parallel ...")
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_region = {
            executor.submit(_fetch_single_region, client, project_id, r, days, limit): r 
            for r in regions_to_scan
        }
        
        for future in futures.as_completed(future_to_region):
            data = future.result()
            if data:
                all_jobs.extend(data)
            
    seen_jobs = set()
    unique_jobs = []
    for job in all_jobs:
        if job['job_id'] not in seen_jobs:
            unique_jobs.append(job)
            seen_jobs.add(job['job_id'])

    unique_jobs.sort(key=lambda x: x.get('total_bytes_billed', 0), reverse=True)
    return unique_jobs[:limit]
