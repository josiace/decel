"""
Custom storage backend for Supabase Storage using REST API
"""
import os
import requests
import logging
from django.core.files.storage import Storage
from django.conf import settings
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class SupabaseStorage(Storage):
    """
    Django storage backend for Supabase Storage using REST API
    """
    
    def __init__(self):
        self.supabase_url = getattr(settings, 'SUPABASE_URL')
        self.supabase_key = getattr(settings, 'SUPABASE_KEY')
        self.bucket = getattr(settings, 'SUPABASE_BUCKET', 'decel-media')
        
        # Check if configuration is valid
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase storage not configured properly, falling back to local storage")
            self.use_supabase = False
        else:
            self.use_supabase = True
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
        if not self.use_supabase:
            # Fallback to local storage
            return self._save_local(name, content)
        
        try:
            # Read file content
            content.seek(0)
            file_content = content.read()
            
            # Upload to Supabase
            url = self._url(name)
            headers = self.headers.copy()
            headers['Content-Type'] = 'application/octet-stream'
            
            response = requests.put(url, headers=headers, data=file_content, timeout=30)
            
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to upload to Supabase: {response.text}")
                raise Exception(f"Failed to upload to Supabase: {response.text}")
            
            return name
        except Exception as e:
            logger.error(f"Supabase upload failed: {str(e)}")
            # Fallback to local storage
            return self._save_local(name, content)
    
    def _save_local(self, name, content):
        """Fallback to local storage"""
        import os
        from django.conf import settings
        
        media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
        full_path = os.path.join(media_root, name)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Save file
        with open(full_path, 'wb') as f:
            content.seek(0)
            f.write(content.read())
        
        return name
    
    def url(self, name):
        """Return public URL for file"""
        if not self.use_supabase:
            # Fallback to local URL
            return f'/media/{name}'
        
        try:
            return self._get_public_url(name)
        except Exception as e:
            logger.error(f"Failed to generate Supabase URL: {str(e)}")
            # Fallback to local URL
            return f'/media/{name}'
    
    def exists(self, name):
        """Check if file exists"""
        if not self.use_supabase:
            # Check local file
            import os
            from django.conf import settings
            media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
            return os.path.exists(os.path.join(media_root, name))
        
        try:
            url = self._url(name)
            response = requests.head(url, headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to check file existence: {str(e)}")
            return False
    
    def delete(self, name):
        """Delete file from Supabase Storage"""
        if not self.use_supabase:
            # Delete local file
            import os
            from django.conf import settings
            media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
            full_path = os.path.join(media_root, name)
            if os.path.exists(full_path):
                os.remove(full_path)
            return
        
        try:
            url = self._url(name)
            response = requests.delete(url, headers=self.headers, timeout=10)
            if response.status_code not in [200, 204]:
                logger.error(f"Failed to delete from Supabase: {response.text}")
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
    
    def size(self, name):
        """Return file size"""
        if not self.use_supabase:
            # Get local file size
            import os
            from django.conf import settings
            media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
            full_path = os.path.join(media_root, name)
            if os.path.exists(full_path):
                return os.path.getsize(full_path)
            return 0
        
        try:
            url = self._url(name)
            response = requests.head(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return int(response.headers.get('Content-Length', 0))
        except Exception as e:
            logger.error(f"Failed to get file size: {str(e)}")
        return 0
    
    def get_available_name(self, name, max_length=None):
        """Return available filename (no collision handling for simplicity)"""
        return name
    
    def open(self, name, mode='rb'):
        """Open the file for reading"""
        if not self.use_supabase:
            # Open local file
            import os
            from django.conf import settings
            media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
            full_path = os.path.join(media_root, name)
            return open(full_path, mode)
        
        try:
            # Download from Supabase and return as file-like object
            url = self._url(name)
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Failed to download from Supabase: {response.text}")
            
            # Create a file-like object from the response content
            from io import BytesIO
            return BytesIO(response.content)
        except Exception as e:
            logger.error(f"Failed to open file: {str(e)}")
            # Fallback to local file
            import os
            from django.conf import settings
            media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(settings.BASE_DIR, 'media'))
            full_path = os.path.join(media_root, name)
            if os.path.exists(full_path):
                return open(full_path, mode)
            raise
