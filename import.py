import os
import json
import requests
import xml.etree.ElementTree as ET
from azure.identity import DefaultAzureCredential
import time

def build_url(base_uri, *segments, api_version="2019-12-01"):
    """
    Helper function to construct API URLs dynamically and handle trailing/leading slashes.
    """
    sanitized_segments = [segment.strip("/") for segment in segments]
    path = "/".join(sanitized_segments)
    return f"{base_uri}/{path}?api-version={api_version}"

def import_apim_content(resource_group_name, apim_name, import_folder):
    # Authenticate and get a token
    credential = DefaultAzureCredential()
    token = credential.get_token("https://management.azure.com/.default").token

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Base API URL
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        raise ValueError("AZURE_SUBSCRIPTION_ID environment variable is not set.")
    base_uri = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.ApiManagement/service/{apim_name}"

    # Resolve import paths
    if not os.path.exists(import_folder):
        raise FileNotFoundError(f"Import folder not found: {import_folder}")

    media_folder = os.path.join(import_folder, "Media")
    data_file = os.path.join(import_folder, "data.json")

    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Data file not found: {data_file}")

    if not os.path.exists(media_folder):
        os.makedirs(media_folder, exist_ok=True)
        print(f"Media folder not found. Created: {media_folder}")

    print(f"Importing Azure API Management Developer portal content from: {import_folder}")

    # Load content items
    with open(data_file, "r", encoding="utf-8") as file:
        content_items = json.load(file)

    # Upload content
    print("Uploading content...")
    for key, content_item in content_items.items():
        key_sanitized = key.strip("/")
        existing_items_url = build_url(base_uri, key_sanitized)
        response = requests.get(existing_items_url, headers=headers)
        if response.status_code == 200:
            existing_item = response.json()
            if existing_item == content_item:
                print(f"Skipping unchanged content item: {key_sanitized}")
                continue

        upload_url = build_url(base_uri, key_sanitized)
        print(f"Uploading content to: {upload_url}")
        response = requests.put(upload_url, headers=headers, json=content_item)
        response.raise_for_status()

    # Clean up storage
    print("Cleaning up target storage...")
    storage_secrets_url = build_url(base_uri, "portalSettings/mediaContent/listSecrets")
    response = requests.post(storage_secrets_url, headers=headers)
    response.raise_for_status()
    storage = response.json()
    container_sas_url = storage["containerSasUrl"]

    container_base_url, sas_token = container_sas_url.split("?")
    blob_list_url = f"{container_base_url}?restype=container&comp=list&{sas_token}"
    response = requests.get(blob_list_url)
    response.raise_for_status()
    blobs = ET.fromstring(response.text)

    for blob in blobs.findall(".//Blob"):
        blob_name = blob.find("Name").text
        delete_blob_url = f"{container_base_url}/{blob_name}?{sas_token}"
        print(f"Deleting blob: {delete_blob_url}")
        requests.delete(delete_blob_url).raise_for_status()

    print("Storage cleaned up.")

    # Upload media files
# Upload media files
    print("Uploading media files...")
    for root, _, files in os.walk(media_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, media_folder).replace("\\", "/")
            upload_blob_url = f"{container_base_url}/{relative_path}?{sas_token}"
            head_response = requests.head(upload_blob_url)
            if head_response.status_code == 200:
                print(f"Skipping existing media file: {relative_path}")
                continue


            with open(file_path, "rb") as file:
                print(f"Uploading file: {upload_blob_url}")
                response = requests.put(
                    upload_blob_url,
                    headers={"x-ms-blob-type": "BlockBlob"},  # Specify blob type
                    data=file,
                )
                response.raise_for_status()


    # Publish developer portal
    print("Publishing developer portal...")
    revision = f"Migration-{int(time.time())}"
    publish_url = build_url(base_uri, f"portalRevisions/{revision}")
    publish_payload = {
        "properties": {
            "description": f"Migration {revision}",
            "isCurrent": True
        }
    }
    response = requests.put(publish_url, headers=headers, json=publish_payload)
    response.raise_for_status()

    if response.status_code == 202:
        print("Import completed successfully.")
    else:
        raise RuntimeError("Could not publish developer portal.")

# Parameters (replace with actual values or provide dynamically)
RESOURCE_GROUP_NAME = os.environ.get("RESOURCE_GROUP_NAME")
APIM_NAME = os.environ.get("APIM_NAME")
IMPORT_FOLDER = "./Import"

import_apim_content(RESOURCE_GROUP_NAME, APIM_NAME, IMPORT_FOLDER)

