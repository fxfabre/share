# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "azure-identity>=1.19",
#     "requests>=2.32",
# ]
# ///
import os
import sys
import uuid
from datetime import datetime, timezone

import requests
from azure.identity import DefaultAzureCredential

DAG_NAME = "dag_to_launch"
AZURE_CLIENT_ID = "00000000-0000-0000-0000-000000000000"
AZURE_SCOPE = f"api://{AZURE_CLIENT_ID}/.default"


def main() -> int:
    base_url = os.environ["AIRFLOW_BASE_URL"].rstrip("/")

    credential = DefaultAzureCredential()
    token = credential.get_token(AZURE_SCOPE).token

    run_id = f"manual__{datetime.now(timezone.utc).isoformat()}__{uuid.uuid4().hex[:8]}"
    payload = {
        "dag_run_id": run_id,
        "logical_date": datetime.now(timezone.utc).isoformat(),
        "conf": {},
    }

    url = f"{base_url}/api/v2/dags/{DAG_NAME}/dagRuns"
    response = requests.post(
        url,
        json=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    print(f"Triggered {DAG_NAME}: run_id={data.get('dag_run_id')} state={data.get('state')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
