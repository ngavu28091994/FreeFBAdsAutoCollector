import gspread
from google.oauth2.service_account import Credentials

# Đường dẫn tới file JSON chứa thông tin xác thực
creds_json_path = './key.json'  # Cập nhật đường dẫn đúng

# Tạo credentials
creds = Credentials.from_service_account_file(
    creds_json_path,
    scopes=['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']
)

# Kết nối với Google Sheets
client = gspread.authorize(creds)
# Please replace with your google sheet id
# Mở Google Sheet bằng URL của nó
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/google_sheet_id')

worksheet_name = 'Token'
worksheet = sheet.worksheet(worksheet_name)
access_token = worksheet.acell('A2').value

import datetime
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights

# Please change your add account id
ad_account_id = 'act_[your_account_id]'
FacebookAdsApi.init(access_token=access_token)

# Lấy ngày hiện tại và ngày đầu tiên của tháng hiện tại
today = datetime.datetime.today() - datetime.timedelta(days=1)
first_day_of_month = today.replace(day=1)

# Lấy danh sách các quảng cáo đang chạy trong tháng hiện tại
fields = [
    'ad_id',
    'ad_name',
    'campaign_id',
    'campaign_name',
    'spend',
    'impressions',
    'clicks',
    'actions'
]
params = {
    'time_range': {'since': first_day_of_month.strftime('%Y-%m-%d'), 'until': today.strftime('%Y-%m-%d')},
    'level': 'ad',
    'time_increment': 1,
}

ads = AdAccount(ad_account_id).get_insights(fields=fields, params=params)

data = []
for ad in ads:
    messages_count = 0
    if 'actions' in ad:
        for action in ad['actions']:
            if action['action_type'] == 'onsite_conversion.messaging_conversation_started_7d':
                messages_count = action['value']
                break
    data.append({
        'ad_id': ad['ad_id'],
        'ad_name': ad['ad_name'],
        'campaign_id': ad['campaign_id'],
        'campaign_name': ad['campaign_name'],
        'spend': ad['spend'],
        'impressions': ad['impressions'],
        'clicks': ad['clicks'],
        'date_start': ad['date_start'],
        'date_stop': ad['date_stop'],
        'messages': int(messages_count)
    })

import pandas as pd
df = pd.DataFrame(data)
#df.to_csv('ads_data.csv', index=False)
#df.head()

worksheet_name = today.strftime('%Y%m')
try:
    # Kiểm tra nếu worksheet đã tồn tại
    worksheet = sheet.worksheet(worksheet_name)
    sheet.del_worksheet(worksheet)
    worksheet = sheet.worksheet(worksheet_name)
except gspread.exceptions.WorksheetNotFound:
    # Tạo worksheet mới nếu không tồn tại
    worksheet = sheet.add_worksheet(title=worksheet_name, rows="100", cols="20")

# Dữ liệu mà bạn muốn ghi vào
data  = [df.columns.values.tolist()] + df.values.tolist()

# Ghi dữ liệu vào worksheet, bắt đầu từ ô A1
worksheet.update('A1', data)

worksheet_name = 'Token'
worksheet = sheet.worksheet(worksheet_name)
from datetime import datetime
import pytz

# Lấy múi giờ Asia/Ho_Chi_Minh
ho_chi_minh_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# Lấy thời gian hiện tại theo múi giờ Ho Chi Minh
current_time_ho_chi_minh = datetime.now(ho_chi_minh_tz)

# Định dạng thời gian hiện tại thành chuỗi
formatted_time = current_time_ho_chi_minh.strftime('%Y-%m-%d %H:%M:%S')
worksheet.update_cell(2,2, formatted_time)
