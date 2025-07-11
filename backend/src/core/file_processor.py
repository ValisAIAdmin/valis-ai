"""
Valis AI - File Processing System
Advanced file upload, analysis, and processing with AI integration
"""

import os
import uuid
import time
import json
import mimetypes
import base64
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import openai
from werkzeug.utils import secure_filename

class FileProcessor:
    """
    Advanced file processing system with AI analysis
    """
    
    def __init__(self, openai_api_key: str, upload_folder: str = "/tmp/valis_uploads"):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.upload_folder = upload_folder
        self.processed_files = {}
        
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        # Supported file types
        self.supported_types = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'],
            'code': ['.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml'],
            'data': ['.csv', '.xlsx', '.xls', '.json', '.xml'],
            'archives': ['.zip', '.tar', '.gz', '.rar'],
            'audio': ['.mp3', '.wav', '.ogg', '.m4a'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        }
    
    def process_file_upload(self, file_data: bytes, filename: str, user_id: str = None) -> Dict[str, Any]:
        """
        Process uploaded file with AI analysis
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Secure filename
        secure_name = secure_filename(filename)
        file_extension = os.path.splitext(secure_name)[1].lower()
        
        # Create unique filename
        unique_filename = f"{file_id}_{secure_name}"
        file_path = os.path.join(self.upload_folder, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Get file info
        file_size = len(file_data)
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        file_type = self._detect_file_type(file_extension)
        
        # Create file record
        file_record = {
            'file_id': file_id,
            'original_filename': filename,
            'secure_filename': secure_name,
            'unique_filename': unique_filename,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': mime_type,
            'file_type': file_type,
            'file_extension': file_extension,
            'user_id': user_id,
            'uploaded_at': time.time(),
            'processed': False,
            'analysis': None,
            'metadata': {}
        }
        
        # Store file record
        self.processed_files[file_id] = file_record
        
        # Process file based on type
        try:
            if file_type == 'images':
                analysis = self._analyze_image(file_path, file_data)
            elif file_type == 'documents':
                analysis = self._analyze_document(file_path)
            elif file_type == 'code':
                analysis = self._analyze_code(file_path)
            elif file_type == 'data':
                analysis = self._analyze_data(file_path)
            else:
                analysis = self._analyze_generic(file_path, file_type)
            
            file_record['analysis'] = analysis
            file_record['processed'] = True
            
        except Exception as e:
            file_record['analysis'] = {
                'error': str(e),
                'processed': False
            }
        
        return file_record
    
    def _detect_file_type(self, extension: str) -> str:
        """Detect file type category based on extension"""
        for category, extensions in self.supported_types.items():
            if extension in extensions:
                return category
        return 'unknown'
    
    def _analyze_image(self, file_path: str, file_data: bytes) -> Dict[str, Any]:
        """Analyze image files with AI vision"""
        try:
            # Get image metadata
            with Image.open(file_path) as img:
                width, height = img.size
                format_info = img.format
                mode = img.mode
            
            # Encode image for AI analysis
            base64_image = base64.b64encode(file_data).decode('utf-8')
            
            # AI analysis
            response = openai.ChatCompletion.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image and provide a detailed description including: content, style, colors, composition, potential use cases, and any text visible in the image. Format as JSON."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                'type': 'image',
                'dimensions': {'width': width, 'height': height},
                'format': format_info,
                'mode': mode,
                'ai_description': ai_analysis,
                'suggestions': self._generate_image_suggestions(ai_analysis),
                'processed': True
            }
            
        except Exception as e:
            return {
                'type': 'image',
                'error': str(e),
                'processed': False
            }
    
    def _analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Analyze document files"""
        try:
            # Read text content
            if file_path.endswith('.txt') or file_path.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # For other document types, we'd need additional libraries
                content = "Document content extraction not implemented for this type"
            
            # AI analysis
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the document content and provide insights about its purpose, key topics, structure, and potential improvements. Format as JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Document content:\n{content[:4000]}"  # Limit content length
                    }
                ],
                max_tokens=1000
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                'type': 'document',
                'content_length': len(content),
                'word_count': len(content.split()),
                'ai_analysis': ai_analysis,
                'suggestions': self._generate_document_suggestions(content),
                'processed': True
            }
            
        except Exception as e:
            return {
                'type': 'document',
                'error': str(e),
                'processed': False
            }
    
    def _analyze_code(self, file_path: str) -> Dict[str, Any]:
        """Analyze code files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # AI code analysis
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze this code and provide insights about its functionality, quality, potential improvements, security issues, and best practices. Format as JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Code content:\n{code_content}"
                    }
                ],
                max_tokens=1500
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                'type': 'code',
                'lines_of_code': len(code_content.split('\n')),
                'language': self._detect_programming_language(file_path),
                'ai_analysis': ai_analysis,
                'suggestions': self._generate_code_suggestions(code_content),
                'processed': True
            }
            
        except Exception as e:
            return {
                'type': 'code',
                'error': str(e),
                'processed': False
            }
    
    def _analyze_data(self, file_path: str) -> Dict[str, Any]:
        """Analyze data files"""
        try:
            # Basic data file analysis
            file_size = os.path.getsize(file_path)
            
            analysis = {
                'type': 'data',
                'file_size': file_size,
                'suggestions': [
                    'Data visualization',
                    'Statistical analysis',
                    'Data cleaning and processing',
                    'Machine learning model training'
                ],
                'processed': True
            }
            
            # For CSV files, we could add more detailed analysis
            if file_path.endswith('.csv'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        first_lines = [f.readline() for _ in range(5)]
                    
                    analysis['preview'] = first_lines
                    analysis['estimated_rows'] = sum(1 for line in open(file_path, 'r'))
                except:
                    pass
            
            return analysis
            
        except Exception as e:
            return {
                'type': 'data',
                'error': str(e),
                'processed': False
            }
    
    def _analyze_generic(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Generic file analysis"""
        try:
            file_size = os.path.getsize(file_path)
            
            return {
                'type': file_type,
                'file_size': file_size,
                'suggestions': [
                    'File conversion',
                    'Content extraction',
                    'Format analysis'
                ],
                'processed': True
            }
            
        except Exception as e:
            return {
                'type': file_type,
                'error': str(e),
                'processed': False
            }
    
    def _detect_programming_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        extension = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.ts': 'TypeScript'
        }
        
        return language_map.get(extension, 'Unknown')
    
    def _generate_image_suggestions(self, ai_analysis: str) -> List[str]:
        """Generate suggestions for image files"""
        return [
            'Use as website hero image',
            'Create variations with AI',
            'Extract colors for design palette',
            'Generate similar images',
            'Optimize for web use',
            'Create responsive versions'
        ]
    
    def _generate_document_suggestions(self, content: str) -> List[str]:
        """Generate suggestions for document files"""
        return [
            'Convert to different format',
            'Create summary',
            'Extract key points',
            'Generate presentation',
            'Translate to other languages',
            'Create interactive version'
        ]
    
    def _generate_code_suggestions(self, code_content: str) -> List[str]:
        """Generate suggestions for code files"""
        return [
            'Code review and optimization',
            'Add documentation',
            'Create unit tests',
            'Security analysis',
            'Performance optimization',
            'Convert to different language'
        ]
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a processed file"""
        return self.processed_files.get(file_id)
    
    def list_user_files(self, user_id: str) -> List[Dict[str, Any]]:
        """List all files for a user"""
        return [
            file_record for file_record in self.processed_files.values()
            if file_record.get('user_id') == user_id
        ]
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file and its record"""
        if file_id in self.processed_files:
            file_record = self.processed_files[file_id]
            
            # Delete physical file
            try:
                if os.path.exists(file_record['file_path']):
                    os.remove(file_record['file_path'])
            except:
                pass
            
            # Remove from records
            del self.processed_files[file_id]
            return True
        
        return False
    
    def process_with_ai(self, file_id: str, task_description: str) -> Dict[str, Any]:
        """
        Process a file with AI based on task description
        """
        if file_id not in self.processed_files:
            return {'error': 'File not found'}
        
        file_record = self.processed_files[file_id]
        
        # Generate AI processing based on file type and task
        prompt = f"""Process the following file based on the user's request:

File Type: {file_record['file_type']}
Original Filename: {file_record['original_filename']}
File Analysis: {json.dumps(file_record['analysis'], indent=2)}

User Request: {task_description}

Provide a detailed response on how to process this file and what actions to take."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI file processing expert. Provide detailed instructions and code for processing files based on user requests."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                'file_id': file_id,
                'task_description': task_description,
                'ai_processing_instructions': ai_response,
                'processed_at': time.time()
            }
            
        except Exception as e:
            return {
                'file_id': file_id,
                'error': str(e)
            }

# Global file processor instance
file_processor = None

def get_file_processor(openai_api_key: str) -> FileProcessor:
    """Get or create the global file processor instance"""
    global file_processor
    if file_processor is None:
        file_processor = FileProcessor(openai_api_key)
    return file_processor

