import os
import json
import requests
import xml.etree.ElementTree as ET
from azure.identity import DefaultAzureCredential

def export_apim_content(resource_group_name, apim_name, export_folder):
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

    # Prepare export folders
    media_folder = os.path.join(export_folder, "Media")
    os.makedirs(export_folder, exist_ok=True)
    os.makedirs(media_folder, exist_ok=True)

    print(f"Exporting Azure API Management Developer portal content to: {export_folder}")

    # Fetch content types
    content_types_url = f"{base_uri}/contentTypes?api-version=2019-12-01"
    response = requests.get(content_types_url, headers=headers)
    print("Content Types Response Status Code:", response.status_code)
    #print("Content Types Response Text:", response.text)
    response.raise_for_status()
    content_types = response.json()

    content_items = {}

    # Fetch content items for each content type
    for content_type_item in content_types.get("value", []):
        content_type_id = content_type_item["id"]
        content_items_url = f"{base_uri}/{content_type_id}/contentItems?api-version=2019-12-01"
        response = requests.get(content_items_url, headers=headers)
        print(f"Content Items Response for {content_type_id} Status Code:", response.status_code)
        #print(f"Content Items Response for {content_type_id} Text:", response.text)
        response.raise_for_status()
        content_type_items = response.json()

        for content_item in content_type_items.get("value", []):
            content_items[content_item["id"]] = content_item

    # Save content items to JSON
    with open(os.path.join(export_folder, "data.json"), "w") as file:
        json.dump(content_items, file, indent=4)

    # Fetch storage account details for media content
    media_secrets_url = f"{base_uri}/portalSettings/mediaContent/listSecrets?api-version=2019-12-01"
    response = requests.post(media_secrets_url, headers=headers)
    print("Media Secrets Response Status Code:", response.status_code)
    print("Media Secrets Response Text:", response.text)
    response.raise_for_status()
    storage = response.json()
    container_sas_url = storage["containerSasUrl"]

    # Download media files
    total_files = 0
    container_base_url, sas_token = container_sas_url.split("?")
    response = requests.get(f"{container_base_url}?restype=container&comp=list&{sas_token}")
    print("Blob List Response Status Code:", response.status_code)
    #print("Blob List Response Text:", response.text)
    response.raise_for_status()
    blobs = ET.fromstring(response.text)  # Parse XML response

    blob_items = blobs.findall(".//Blob")  # Find all Blob elements
    for blob in blob_items:
        blob_name = blob.find("Name").text
        print("Blob Name:", blob_name)
        target_file = os.path.join(media_folder, blob_name)
        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        blob_url = f"{container_base_url}/{blob_name}?{sas_token}"
        blob_response = requests.get(blob_url)
        print(f"Blob Download Response for {blob_name} Status Code:", blob_response.status_code)
        blob_response.raise_for_status()

        if os.path.exists(target_file):
            print(f"Skipping existing file: {target_file}")
            continue


        with open(target_file, "wb") as file:
            file.write(blob_response.content)
        total_files += 1

    print(f"Downloaded {total_files} files from container.")
    print("Export completed.")

# Parameters (replace with actual values or provide dynamically)

EXPORT_FOLDER = "./Export"
RESOURCE_GROUP_NAME = os.environ.get("RESOURCE_GROUP_NAME")
APIM_NAME = os.environ.get("APIM_NAME")

export_apim_content(RESOURCE_GROUP_NAME, APIM_NAME, EXPORT_FOLDER)

