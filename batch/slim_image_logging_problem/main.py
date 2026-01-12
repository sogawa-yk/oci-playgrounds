import os
import oci
import json
from datetime import datetime

# 環境変数から設定を取得
BUCKET_NAME = os.environ.get("BUCKET_NAME")
NAMESPACE = os.environ.get("NAMESPACE")
INPUT_FILE = "input.txt"

def process_data():
    print("Initialize OCI Auth (Resource Principal)...")
    signer = oci.auth.signers.get_resource_principals_signer()
    object_storage = oci.object_storage.ObjectStorageClient(config={}, signer=signer)

    print(f"Reading {INPUT_FILE} from bucket {BUCKET_NAME}...")
    try:
        resp = object_storage.get_object(NAMESPACE, BUCKET_NAME, INPUT_FILE)
        content = resp.data.text
        
        line_count = len(content.splitlines())
        print(f"Process complete. Line count: {line_count}")
        result_data = {
            "original_file": INPUT_FILE,
            "line_count": line_count,
            "processed_at": datetime.now().isoformat(),
            "status": "SUCCESS"
        }
        
        output_filename = f"result_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        object_storage.put_object(
            NAMESPACE,
            BUCKET_NAME,
            output_filename,
            json.dumps(result_data, indent=2).encode('utf-8')
        )
        print(f"Result written to {output_filename}")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    if not BUCKET_NAME or not NAMESPACE:
        print("Error: BUCKET_NAME and NAMESPACE env vars are required.")
        exit(1)
    process_data()