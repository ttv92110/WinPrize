import json 
from typing import List, Dict, Any, Optional
import uuid
from pathlib import Path

class FileDB:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file exists with valid JSON"""
        # Create parent directory if it doesn't exist
        self.file_path.parent.mkdir(exist_ok=True, parents=True)
        
        if not self.file_path.exists():
            with open(self.file_path, 'w') as f:
                json.dump([], f)
        else:
            # Check if file is empty or contains invalid JSON
            try:
                with open(self.file_path, 'r') as f:
                    content = f.read().strip()
                    if not content:  # File is empty
                        with open(self.file_path, 'w') as f:
                            json.dump([], f)
                    else:
                        json.loads(content)  # Validate JSON
            except (json.JSONDecodeError, ValueError):
                # File contains invalid JSON, reinitialize
                with open(self.file_path, 'w') as f:
                    json.dump([], f)
    
    def read_all(self) -> List[Dict]:
        """Read all records from JSON file"""
        try:
            with open(self.file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            # If there's an error, return empty list and reset file
            self._ensure_file_exists()
            return []
    
    def write_all(self, data: List[Dict]):
        """Write all records to JSON file"""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    def insert(self, record: Dict) -> Dict:
        """Insert a new record"""
        data = self.read_all()
        
        # Add ID if not present
        if 'id' not in record:
            record['id'] = str(uuid.uuid4())
            
        data.append(record)
        self.write_all(data)
        return record
    
    def find_by_id(self, id: str) -> Optional[Dict]:
        """Find record by ID"""
        data = self.read_all()
        for record in data:
            if record.get('id') == id:
                return record
        return None
    
    def find_by_field(self, field: str, value: Any) -> List[Dict]:
        """Find records by field value"""
        data = self.read_all()
        return [r for r in data if r.get(field) == value]
    
    def update(self, id: str, updates: Dict) -> Optional[Dict]:
        """Update a record by ID"""
        data = self.read_all()
        for i, record in enumerate(data):
            if record.get('id') == id:
                data[i].update(updates)
                self.write_all(data)
                return data[i]
        return None
    
    def delete(self, id: str) -> bool:
        """Delete a record by ID"""
        data = self.read_all()
        new_data = [r for r in data if r.get('id') != id]
        if len(new_data) < len(data):
            self.write_all(new_data)
            return True
        return False
    