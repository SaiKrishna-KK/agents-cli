# src/file_manager.py
import os
import shutil
from pathlib import Path

def create_file(file_path, content):
    """Create a new file with the given content.
    
    Args:
        file_path: Path to the file to create
        content: Content to write to the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error creating file {file_path}: {str(e)}")
        return False

def modify_file(file_path, new_content):
    """Modify an existing file with new content.
    
    Args:
        file_path: Path to the file to modify
        new_content: New content for the file
        
    Returns:
        True if successful, False otherwise
    """
    return create_file(file_path, new_content)  # Overwrites

def append_to_file(file_path, content):
    """Append content to an existing file.
    
    Args:
        file_path: Path to the file to append to
        content: Content to append
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error appending to file {file_path}: {str(e)}")
        return False

def read_file(file_path):
    """Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string if successful, None otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None

def file_exists(file_path):
    """Check if a file exists.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file exists, False otherwise
    """
    return os.path.exists(file_path)

def is_file(file_path):
    """Check if a path is a file.
    
    Args:
        file_path: Path to check
        
    Returns:
        True if the path is a file, False otherwise
    """
    return os.path.isfile(file_path)

def is_directory(dir_path):
    """Check if a path is a directory.
    
    Args:
        dir_path: Path to check
        
    Returns:
        True if the path is a directory, False otherwise
    """
    return os.path.isdir(dir_path)

def list_files(dir_path, pattern=None):
    """List files in a directory.
    
    Args:
        dir_path: Path to the directory to list
        pattern: Optional glob pattern to filter files
        
    Returns:
        List of file paths
    """
    path = Path(dir_path)
    if not path.exists() or not path.is_dir():
        return []
        
    if pattern:
        return [str(f) for f in path.glob(pattern)]
    else:
        return [str(f) for f in path.iterdir() if f.is_file()]

def list_directories(dir_path):
    """List subdirectories in a directory.
    
    Args:
        dir_path: Path to the directory to list
        
    Returns:
        List of directory paths
    """
    path = Path(dir_path)
    if not path.exists() or not path.is_dir():
        return []
        
    return [str(d) for d in path.iterdir() if d.is_dir()]

def create_directory(dir_path):
    """Create a directory.
    
    Args:
        dir_path: Path to the directory to create
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {dir_path}: {str(e)}")
        return False

def delete_file(file_path):
    """Delete a file.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if file_exists(file_path) and is_file(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {str(e)}")
        return False

def delete_directory(dir_path, recursive=False):
    """Delete a directory.
    
    Args:
        dir_path: Path to the directory to delete
        recursive: Whether to recursively delete contents
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if is_directory(dir_path):
            if recursive:
                shutil.rmtree(dir_path)
            else:
                os.rmdir(dir_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting directory {dir_path}: {str(e)}")
        return False

def copy_file(src_path, dst_path):
    """Copy a file.
    
    Args:
        src_path: Path to the source file
        dst_path: Path to the destination file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if file_exists(src_path) and is_file(src_path):
            Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
            return True
        return False
    except Exception as e:
        print(f"Error copying file from {src_path} to {dst_path}: {str(e)}")
        return False

def move_file(src_path, dst_path):
    """Move a file.
    
    Args:
        src_path: Path to the source file
        dst_path: Path to the destination file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if file_exists(src_path) and is_file(src_path):
            Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src_path, dst_path)
            return True
        return False
    except Exception as e:
        print(f"Error moving file from {src_path} to {dst_path}: {str(e)}")
        return False
