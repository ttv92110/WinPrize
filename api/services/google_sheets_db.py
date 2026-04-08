import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
from datetime import datetime
import json
import os 

class GoogleSheetsDB:
    """Google Sheets based database"""
    
    def __init__(self, sheet_name: str, worksheet_name: str):
        self.sheet_name = sheet_name
        self.worksheet_name = worksheet_name
        self._client = None
        self._worksheet = None
        self._init_client()
         
    def _init_client(self):
        """Initialize Google Sheets client from environment variable or file"""
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets", 
                     "https://www.googleapis.com/auth/drive"]
             
            creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
            
            if creds_json:
                # Environment variable سے JSON parse کریں
                try:
                    creds_dict = json.loads(creds_json)
                    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
                    self._client = gspread.authorize(creds)
                    print(f"✅ Connected using environment variable credentials")
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing GOOGLE_SHEETS_CREDENTIALS: {str(e)}")
                    return
            else:
                # اگر environment variable نہ ہو تو file سے try کریں (local development)
                base_dir = Path(__file__).parent.parent
                creds_file = base_dir / "credentials.json"
                
                if creds_file.exists():
                    creds = Credentials.from_service_account_file(str(creds_file), scopes=scopes)
                    self._client = gspread.authorize(creds)
                    print(f"✅ Connected using credentials file: {creds_file}")
                else:
                    print(f"❌ No credentials found. Set GOOGLE_SHEETS_CREDENTIALS environment variable or add credentials.json file")
                    return
            
            # Open spreadsheet and worksheet
            spreadsheet = self._client.open(self.sheet_name)
            self._worksheet = spreadsheet.worksheet(self.worksheet_name)
             
            
        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {str(e)}")
            self._client = None
            self._worksheet = None
    
    def _ensure_headers(self, headers: List[str]):
        """Ensure worksheet has proper headers"""
        if not self._worksheet:
            return
        
        try:
            existing_data = self._worksheet.get_all_values()
            if not existing_data or len(existing_data) < 1:
                self._worksheet.append_row(headers) 
        except Exception as e:
            print(f"Error ensuring headers: {str(e)}")
    
    def read_all(self) -> List[Dict]: 
        if not self._worksheet:
            return []
        
        try:
            records = self._worksheet.get_all_records()
            return [dict(record) for record in records]
        except Exception as e:
            print(f"Error reading from Google Sheets: {str(e)}")
            return []
    
    def insert(self, record: Dict) -> Dict:
        """Insert a new record"""
        if not self._worksheet:
            return record
        
        try:
            # Add ID if not present
            if 'id' not in record:
                record['id'] = str(uuid.uuid4())
            
            # Add created_at if not present
            if 'created_at' not in record:
                record['created_at'] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
            
            # Get headers from first row
            headers = self._worksheet.row_values(1)
            
            # If no headers, create them from record keys
            if not headers:
                headers = list(record.keys())
                self._worksheet.append_row(headers)
            
            # Prepare row data in correct order
            row_data = []
            for header in headers:
                val = record.get(header, "")
                row_data.append(str(val) if val is not None else "")
            
            # Append row
            self._worksheet.append_row(row_data)
            return record
        except Exception as e:
            print(f"Error inserting into Google Sheets: {str(e)}")
            return record
    
    def find_by_id(self, id: str) -> Optional[Dict]: 
        if not self._worksheet:
            return None
        
        try:
            all_records = self.read_all()
            for record in all_records:
                if record.get("id") == id:
                    return record
            return None
        except Exception as e:
            print(f"Error finding by ID: {str(e)}")
            return None
    
    def find_by_field(self, field: str, value: Any) -> List[Dict]: 
        if not self._worksheet:
            return []
        
        try:
            all_records = self.read_all()
            result = []
            search_value = str(value).lower().strip()
            
            for r in all_records:
                # Check multiple possible field name variations
                record_value = None
                for key in r.keys():
                    if key.lower() == field.lower():
                        record_value = r.get(key, "")
                        break
                
                if record_value is None:
                    record_value = r.get(field, "")
                
                if str(record_value).lower().strip() == search_value:
                    result.append(r)
             
            return result
        except Exception as e:
            print(f"Error finding by field: {str(e)}")
            return []
    
    def update(self, id: str, updates: Dict) -> Optional[Dict]:
        """Update a record by ID"""
        if not self._worksheet:
            return None
        
        try:
            # Find row index by ID 
            all_records = self.read_all()
            headers = self._worksheet.row_values(1)
            
            row_index = None
            for idx, record in enumerate(all_records, start=2):
                if record.get("id") == id:
                    row_index = idx
                    break
            
            if not row_index:
                return None
            
            # Update record
            record = self.find_by_id(id)
            if record:
                record.update(updates)
                record['updated_at'] = datetime.now().strftime("%d/%m/%YT%Hh:%Mm:%Ss")
                
                # Update each cell
                for col_idx, header in enumerate(headers, start=1):
                    value = str(record.get(header, ""))
                    self._worksheet.update_cell(row_index, col_idx, value)
                
                return record
            return None
        except Exception as e:
            print(f"Error updating in Google Sheets: {str(e)}")
            return None
    
    def delete(self, id: str) -> bool:
        """Delete a record by ID"""
        try:
            all_records = self.read_all()
            for idx, record in enumerate(all_records, start=2):
                if record.get("id") == id:
                    self._worksheet.delete_rows(idx)
                    return True
            return False
        except Exception as e:
            print(f"Error deleting from Google Sheets: {str(e)}")
            return False
    
    def write_all(self, data: List[Dict]):
        """Write all records (clear and rewrite)"""
        if not self._worksheet:
            return
        
        try:
            # Clear existing data
            self._worksheet.clear()
            
            if data:
                # Get headers
                headers = list(data[0].keys())
                self._worksheet.append_row(headers)
                
                for record in data:
                    row = [str(record.get(h, "")) for h in headers]
                    self._worksheet.append_row(row)
        except Exception as e:
            print(f"Error writing to Google Sheets: {str(e)}")

# Database instances
class GoogleSheetsDBManager:
    def __init__(self):
        self.users_db = GoogleSheetsDB("WinPrize_Users", "users")
        self.draws_db = GoogleSheetsDB("WinPrize_Draws", "draws")
        self.payments_db = GoogleSheetsDB("WinPrize_Payments", "payments")
        self.user_draws_db = GoogleSheetsDB("WinPrize_UserDraws", "user_draws")
        self.notifications_db = GoogleSheetsDB("WinPrize_Notifications", "notifications")
        self.verifications_db = GoogleSheetsDB("WinPrize_Verifications", "verifications")
        self.password_resets_db = GoogleSheetsDB("WinPrize_PasswordResets", "password_resets")

# Create global instance
sheets_db_manager = GoogleSheetsDBManager()
