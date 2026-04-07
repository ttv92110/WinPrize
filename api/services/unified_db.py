from api.config import Config
from api.services.file_db import FileDB

class UnifiedDB:
    """
    Unified Database - Can switch between FileDB and Google Sheets
    without changing any existing code
    """
    
    def __init__(self, file_db: FileDB, sheets_db):
        self.file_db = file_db
        self.sheets_db = sheets_db
        self.use_sheets = Config.USE_GOOGLE_SHEETS and sheets_db and sheets_db._worksheet is not None

    def _get_active_db(self): 
        return self.sheets_db
    
    def read_all(self):
        return self._get_active_db().read_all()
    
    def write_all(self, data):
        return self._get_active_db().write_all(data)
    
    def insert(self, record):
        return self._get_active_db().insert(record)
    
    def find_by_id(self, id):
        return self._get_active_db().find_by_id(id)
    
    def find_by_field(self, field, value):
        return self._get_active_db().find_by_field(field, value)
    
    def update(self, id, updates):
        return self._get_active_db().update(id, updates)
    
    def delete(self, id):
        return self._get_active_db().delete(id)
    
    def sync_to_sheets(self):
        """Sync all FileDB data to Google Sheets"""
        if not self.use_sheets:
            all_data = self.file_db.read_all()
            self.sheets_db.write_all(all_data)
            print(f"✅ Synced {len(all_data)} records to Google Sheets")
    
    def sync_to_file(self):
        """Sync all Google Sheets data to FileDB"""
        if self.use_sheets:
            all_data = self.sheets_db.read_all()
            self.file_db.write_all(all_data)
            print(f"✅ Synced {len(all_data)} records to FileDB")