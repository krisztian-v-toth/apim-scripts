# APIM Developer Portal Scripts

This repository contains two Python scripts for managing Azure API Management (APIM) Developer Portal content:

1. **`export.py`**: Exports content and media files from an APIM Developer Portal to a local folder.
2. **`import.py`**: Imports content and media files from a local folder into an APIM Developer Portal.

## Prerequisites

- **Python 3.9 or later**
- Azure SDK: Install the required Python packages:
  ```bash
  pip install azure-identity requests
  ```
- Authentication is handled using `DefaultAzureCredential`, which supports:
  - **Azure CLI login**: Log in using `az login`. This is not required but simplifies setup by avoiding manual environment variable configuration.
  - **Service principal credentials**: Set environment variables for `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`, and `AZURE_SUBSCRIPTION_ID`.
  - **Managed Identity**: Use when running on Azure resources like VMs or App Services with appropriate permissions.
- Ensure your environment has the necessary permissions to access the APIM instance.

## Scripts Overview

### `export.py`

#### Description
Exports all content and media files from the APIM Developer Portal to a specified local folder.

#### Parameters
- `RESOURCE_GROUP_NAME`: The name of the Azure resource group containing the APIM instance.
- `APIM_NAME`: The name of the APIM service.
- `EXPORT_FOLDER`: The folder where the exported content and media files will be saved.

#### Usage
1. Authenticate with Azure:
   - **With Azure CLI**:
     ```bash
     az login
     az account set --subscription <Subscription-ID>
     ```
   - **Without Azure CLI** (using service principal):
     ```bash
     export AZURE_CLIENT_ID=<your-client-id>
     export AZURE_TENANT_ID=<your-tenant-id>
     export AZURE_CLIENT_SECRET=<your-client-secret>
     export AZURE_SUBSCRIPTION_ID=<your-subscription-id>
     ```
2. Run the script:
   ```bash
   python export.py
   ```

### `import.py`

#### Description
Imports content and media files from a local folder to the APIM Developer Portal.

#### Parameters
- `RESOURCE_GROUP_NAME`: The name of the Azure resource group containing the APIM instance.
- `APIM_NAME`: The name of the APIM service.
- `IMPORT_FOLDER`: The folder containing the content and media files to be imported.

#### Usage
1. Prepare the `IMPORT_FOLDER`:
   - Ensure it contains:
     - A `data.json` file with the content to import.
     - A `Media` folder with all media files.
2. Authenticate with Azure:
   - **With Azure CLI**:
     ```bash
     az login
     az account set --subscription <Subscription-ID>
     ```
   - **Without Azure CLI** (using service principal):
     ```bash
     export AZURE_CLIENT_ID=<your-client-id>
     export AZURE_TENANT_ID=<your-tenant-id>
     export AZURE_CLIENT_SECRET=<your-client-secret>
     export AZURE_SUBSCRIPTION_ID=<your-subscription-id>
     ```
3. Run the script:
   ```bash
   python import.py
   ```

## Notes
- The Azure CLI is not strictly required. You can authenticate using service principal credentials or managed identity instead.
- Media files will be overwritten during import if they exist.
- Both scripts handle authentication using `DefaultAzureCredential`, supporting Azure CLI login, service principals, or managed identity.

## Troubleshooting
- If authentication fails, verify your Azure credentials and permissions.
- For large imports or exports, monitor the logs for progress and errors.


