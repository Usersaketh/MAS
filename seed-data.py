#!/usr/bin/env python3
"""
Seed the MAS backend with sample customer support documents.
Requires: requests library and running backend at http://localhost:8000
"""
import json
import requests
import sys

API_BASE = "http://localhost:8000"
API_KEY = "dev-interview-key"

# Load sample documents
try:
    with open("sample-documents.json", "r") as f:
        documents = json.load(f)
except FileNotFoundError:
    print("Error: sample-documents.json not found")
    sys.exit(1)

headers = {"X-API-Key": API_KEY}

# Ingest documents
print(f"Ingesting {len(documents)} documents...")
try:
    response = requests.post(
        f"{API_BASE}/documents",
        json={"documents": documents},
        headers=headers,
    )
    response.raise_for_status()
    result = response.json()
    print(f"✓ Success! Added {result['added_count']} documents.")
    print(f"  Total documents in index: {result['total_documents']}")
except requests.exceptions.HTTPError as e:
    print(f"✗ HTTP Error {e.response.status_code}: {e.response.reason}")
    try:
        error_detail = e.response.json()
        print(f"  Details: {error_detail}")
    except:
        print(f"  Response: {e.response.text}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Get stats
print("\nFetching index statistics...")
try:
    response = requests.get(f"{API_BASE}/documents/stats", headers=headers)
    response.raise_for_status()
    stats = response.json()
    print(f"✓ Index size: {stats['index_size']}")
    print(f"✓ Metadata count: {stats['metadata_count']}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n✓ Ready! Start the frontend and begin querying.")
