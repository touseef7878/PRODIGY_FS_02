"""
File Upload Utilities
"""
import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_size(file):
    """Validate file size."""
    file.seek(0, os.SEEK_END)  # Move to end of file
    file_size = file.tell()  # Get current position (file size)
    file.seek(0)  # Reset file position to beginning
    
    return file_size <= MAX_FILE_SIZE


def generate_unique_filename(original_filename, prefix=''):
    """Generate a unique filename."""
    if not original_filename:
        return None
    
    # Extract file extension
    file_ext = ''
    if '.' in original_filename:
        file_ext = original_filename.rsplit('.', 1)[1].lower()
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())[:8]
    if prefix:
        filename = f"{prefix}_{unique_id}.{file_ext}"
    else:
        filename = f"{unique_id}.{file_ext}"
    
    return secure_filename(filename)


def create_thumbnail(image_path, thumbnail_path, size=(150, 150)):
    """Create thumbnail from image."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (for RGBA images)
            if img.mode in ('RGBA', 'LA'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                else:
                    background.paste(img)
                img = background
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        current_app.logger.error(f"Error creating thumbnail: {str(e)}")
        return False


def validate_image(file):
    """Validate that the file is a valid image."""
    try:
        with Image.open(file) as img:
            # Verify it's a valid image by checking format
            img.verify()
        file.seek(0)  # Reset file position
        return True
    except Exception:
        file.seek(0)  # Reset file position
        return False


def safe_remove_file(file_path):
    """Safely remove a file without raising errors."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except OSError as e:
        current_app.logger.error(f"Error removing file {file_path}: {str(e)}")
    return False


def get_file_info(file_path):
    """Get file information."""
    try:
        if os.path.exists(file_path):
            stat_info = os.stat(file_path)
            return {
                'size': stat_info.st_size,
                'created': stat_info.st_ctime,
                'modified': stat_info.st_mtime,
                'exists': True
            }
    except OSError:
        pass
    
    return {'exists': False}


class FileUploadHandler:
    """Handle file upload operations."""
    
    def __init__(self, upload_folder, allowed_extensions=None):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS
    
    def validate_file(self, file):
        """Validate uploaded file."""
        errors = []
        
        # Check if file has a filename
        if not file or file.filename == '':
            errors.append("No file selected")
            return errors
        
        # Check file extension
        if not self.is_allowed_file(file.filename):
            errors.append(f"Invalid file type. Allowed types: {', '.join(self.allowed_extensions)}")
        
        # Check file size
        if not validate_file_size(file):
            errors.append(f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")
        
        # Validate it's a proper image
        if not errors and not validate_image(file):
            errors.append("Invalid image file")
        
        return errors
    
    def is_allowed_file(self, filename):
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_file(self, file, subfolder='', filename_prefix=''):
        """Save uploaded file and return file info."""
        # Validate file first
        errors = self.validate_file(file)
        if errors:
            return {'success': False, 'errors': errors}
        
        try:
            # Create upload directory
            upload_dir = os.path.join(self.upload_folder, subfolder) if subfolder else self.upload_folder
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            filename = generate_unique_filename(file.filename, filename_prefix)
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            file.save(file_path)
            
            # Create thumbnail if it's an image
            thumbnail_path = None
            if subfolder == 'profiles':
                thumbnail_filename = f"thumb_{filename}"
                thumbnail_path = os.path.join(upload_dir, thumbnail_filename)
                create_thumbnail(file_path, thumbnail_path)
            
            # Return relative path for database storage
            relative_path = os.path.join(subfolder, filename).replace('\\', '/') if subfolder else filename
            
            return {
                'success': True,
                'filename': filename,
                'relative_path': relative_path,
                'absolute_path': file_path,
                'thumbnail_path': thumbnail_path,
                'file_size': os.path.getsize(file_path)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error saving file: {str(e)}")
            return {'success': False, 'errors': ['Failed to save file']}
    
    def delete_file(self, relative_path):
        """Delete file and its thumbnail."""
        try:
            # Delete main file
            file_path = os.path.join(self.upload_folder, relative_path)
            success = safe_remove_file(file_path)
            
            # Delete thumbnail if exists
            if 'profiles/' in relative_path:
                filename = os.path.basename(relative_path)
                thumbnail_filename = f"thumb_{filename}"
                thumbnail_path = os.path.join(
                    self.upload_folder, 
                    os.path.dirname(relative_path), 
                    thumbnail_filename
                )
                safe_remove_file(thumbnail_path)
            
            return success
            
        except Exception as e:
            current_app.logger.error(f"Error deleting file: {str(e)}")
            return False