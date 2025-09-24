import json
import gspread
from google.oauth2.service_account import Credentials
import os
import pandas as pd
import traceback
import sys

def push_to_google_sheets_enhanced(dataframe, sheet_url, worksheet_name, credentials_json_str):
    """
    Function đẩy df lên Google Sheets

    Args:
        dataframe: dataframe pandas cần upload
        sheet_url: URL của file Google Sheets
        worksheet_name: Tên của worksheet/tab
        credentials_json_str: Service Account credentials (JSON)
    """
    try:
        # Lấy spreadsheet ID từ URL file Google Sheets
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]

        # Thiết lập credentials cần thiết để truy cập & viết vào file Google Sheets
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        credentials_dict = json.loads(credentials_json_str)
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        gs_client = gspread.authorize(creds)

        # Mở spreadsheet
        sheet = gs_client.open_by_key(sheet_id)

        # Check xem có worksheet này chưa. Nếu có rồi thì replace, chưa có thì tạo mới
        try:
            worksheet = sheet.worksheet(worksheet_name)
            print(f"📄 Found existing worksheet: '{worksheet_name}'")

            # Xóa data cũ
            worksheet.clear()
            print("🧹 Cleared existing data")

        except gspread.WorksheetNotFound:
            print(f"📝 Creating new worksheet: '{worksheet_name}'")
            worksheet = sheet.add_worksheet(
                title=worksheet_name,
                rows=dataframe.shape[0]+1,  # +1 dòng cho header
                cols=dataframe.shape[1]
            )

        # Convert dataframe thành list để upload (bao gồm dòng header)
        data_to_upload = [dataframe.columns.tolist()] + dataframe.values.tolist()

        # Upload dataframe
        print(f"⬆️ Uploading {len(dataframe)} rows x {len(dataframe.columns)} columns...")
        worksheet.update(values=data_to_upload, range_name='A1')
        print(f"🔗 View at: {sheet_url}")
        print(f"📊 Sheet: '{worksheet_name}' with {len(dataframe)} rows")

        return True

    except Exception as e:
        print(f"❌ Error uploading to Google Sheets: {str(e)}")
        traceback.print_exc()
        return False

def get_project_root():
    """
    Lấy link thư mục gốc của project 1 cách linh hoạt --> dùng được cho Airflow, local, Jupyter Notebook, Python script.
    """
    env_root = os.environ.get("PROJECT_ROOT")
    if env_root:
        return env_root
    try:
        # Nếu chạy từ file Python script
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        # Nếu chạy từ Jupyter Notebook
        return os.path.dirname(os.getcwd())

# Lấy biến môi trường nếu có
google_service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

# Nếu không có biến môi trường, thử load từ file
if not google_service_account_json:
    project_root = get_project_root()
    service_account_path = os.path.join(project_root, 'credentials', 'google_cloud_service_account_key.json')
    try:
        with open(service_account_path, "r", encoding="utf-8") as f:
            google_service_account_json = f.read()
        print(f"✅ Loaded Google Service Account credentials from: {service_account_path}")
    except Exception as e:
        google_service_account_json = None
        print(f"❌ Failed to load Google Service Account credentials from: {service_account_path}\n{e}")

if not google_service_account_json:
    print("❌ GOOGLE_SERVICE_ACCOUNT_JSON not found in environment variables or file!")
else:
    print("✅ Google Service Account credentials loaded!")

# Google Sheets URL
sheets_url = "https://docs.google.com/spreadsheets/d/1g1rfkYk-Khm0HnxU3vtBsZvgi-3Bn_Q9ynVqbfpgPSo/edit?usp=sharing"

# Lấy đường dẫn file csv bằng get_project_root()
topcv_data_analyst_jobs_path = os.path.join(get_project_root(), "data-files", "topcv_data_analyst_jobs.csv")

df = pd.read_csv(topcv_data_analyst_jobs_path).copy()
df = df.replace([float('inf'), float('-inf')], pd.NA).fillna("")

print("🚀 Pushing df to Google Sheets...")
print(f"📋 Data shape: {df.shape}")

success = push_to_google_sheets_enhanced(
    dataframe=df,
    sheet_url=sheets_url,
    worksheet_name="TopCV Data Jobs",
    credentials_json_str=google_service_account_json
)

if success:
    print("🎉 Upload completed successfully!")
else:
    print("💔 Upload failed. Please check credentials and permissions.")
    sys.exit(1) # Báo lỗi cho Airflow