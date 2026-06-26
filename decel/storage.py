"""
Custom storage backend for Supabase Storage using REST API
"""
import os
import requests
from django.core.files.storage import Storage
from django.conf import settings
from urllib.parse import urljoin


class SupabaseStorage(Storage):
    """
    Django storage backend for Supabase Storage using REST API
    """
    
    def __init__(self):
        self.supabase_url = getattr(settings, 'SUPABASE_URL')
        self.supabase_key = getattr(settings, 'SUPABASE_KEY')
        self.bucket = getattr(settings, 'SUPABASE_BUCKET', 'decel-media')
        self.storage_url = f'{self.supabase_url}/storage/v1'
        self.headers = {
            'Authorization': f'Bearer {self.supabase_key}',
            'apikey': self.supabase_key,
        }
    
    def _url(self, path=''):
        """Build full URL for Supabase Storage API"""
        return urljoin(f'{self.storage_url}/object/{self.bucket}/', path)
    
    def _get_public_url(self, name):
        """Get public URL for a file"""
        return f'{self.supabase_url}/storage/v1/object/public/{self.bucket}/{name}'
    
    def _save(self, name, content):
        """Save file to Supabase Storage"""
        # Read file content
        content.seek(0)
        file_content = content.read()
        
        # Upload to Supabase
        url = self._url(name)
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/octet-stream'
        
        response = requests.put(url, headers=headers, data=file_content)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to upload to Supabase: {response.text}")
        
        return name
    
    def url(self, name):
        """Return public URL for file"""
        return self._get_public_url(name)
    
    def exists(self, name):
        """Check if file exists"""
        url = self._url(name)
        response = requests.head(url, headers=self.headers)
        return response.status_code == 200
    
    def delete(self, name):
        """Delete file from Supabase Storage"""
        url = self._url(name)
        response = requests.delete(url, headers=self.headers)
        if response.status_code not in [200, 204]:
            raise Exception(f"Failed to delete from Supabase: {response.text}")
    
    def size(self, name):
        """Return file size"""
        url = self._url(name)
        response = requests.head(url, headers=self.headers)
        if response.status_code == 200:
            return int(response.headers.get('Content-Length', 0))
        return 0
    
    def get_available_name(self, name, max_length=None):
        """Return available filename (no collision handling for simplicity)"""
        return name
