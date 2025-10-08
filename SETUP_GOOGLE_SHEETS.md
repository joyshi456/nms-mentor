# Google Sheets Setup for Student Answer Logging

This guide will help you set up Google Sheets to automatically log student answers when your app is deployed on Streamlit Cloud.

## Step 1: Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it something like "NMS Student Responses"
4. Add headers in the first row: `Timestamp | Student Name | Problem ID | Answer`
5. Copy the URL of this sheet (you'll need it later)

## Step 2: Create a Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the Google Sheets API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Enable the Google Drive API:
   - Search for "Google Drive API"
   - Click "Enable"
5. Create a Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "streamlit-logger")
   - Click "Create and Continue"
   - Skip optional steps, click "Done"
6. Create a JSON key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose "JSON" format
   - Click "Create" - this downloads a JSON file

## Step 3: Share Your Google Sheet with the Service Account

1. Open the JSON file you just downloaded
2. Find the `client_email` field (looks like: `something@project-name.iam.gserviceaccount.com`)
3. Copy this email address
4. Go back to your Google Sheet
5. Click "Share" button
6. Paste the service account email
7. Give it "Editor" access
8. Click "Send"

## Step 4: Configure Streamlit Cloud Secrets

When deploying to Streamlit Cloud:

1. Go to your app settings in Streamlit Cloud
2. Find the "Secrets" section
3. Add the following (replace with your actual values):

```toml
sheet_url = "YOUR_GOOGLE_SHEET_URL_HERE"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

**Important:** Copy the entire contents of your downloaded JSON file into the `[gcp_service_account]` section, formatting it as TOML.

## Step 5: Deploy Your App

1. Push your code to GitHub
2. Deploy on Streamlit Cloud
3. The app will automatically log student answers to both:
   - Local file (when running locally)
   - Google Sheets (when deployed with secrets configured)

## Testing Locally (Optional)

If you want to test Google Sheets locally:

1. Create a `.streamlit/secrets.toml` file in your project
2. Add the same secrets as above
3. **NEVER commit this file to git** (it's already in `.gitignore`)

## Troubleshooting

- **"Permission denied" errors**: Make sure you shared the sheet with the service account email
- **"Sheet not found"**: Check that the `sheet_url` in secrets matches your actual sheet URL
- **No data appearing**: Check the Streamlit Cloud logs for error messages
- **Local logging always works**: Even if Google Sheets fails, answers are still saved locally

## Viewing Student Responses

Once deployed, all student answers will appear in real-time in your Google Sheet with:
- Timestamp
- Student name
- Problem ID (e.g., "logic_statements", "coins_key_insight")
- Full text of their answer
