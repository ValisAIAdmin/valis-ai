"""
Valis AI - File Upload Routes
API endpoints for file upload and processing
"""

from flask import Blueprint, request, jsonify, send_file
import os
import base64
from werkzeug.utils import secure_filename
from core.file_processor import get_file_processor
from config import OPENAI_API_KEY

files_bp = Blueprint('files', __name__)

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process a file"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get user ID from request (in real app, this would come from auth)
        user_id = request.form.get('user_id', 'anonymous')
        
        # Read file data
        file_data = file.read()
        
        # Process file
        file_processor = get_file_processor(OPENAI_API_KEY)
        result = file_processor.process_file_upload(file_data, file.filename, user_id)
        
        return jsonify({
            'success': True,
            'file_id': result['file_id'],
            'filename': result['original_filename'],
            'file_type': result['file_type'],
            'file_size': result['file_size'],
            'analysis': result['analysis'],
            'processed': result['processed']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/info/<file_id>', methods=['GET'])
def get_file_info(file_id):
    """Get information about a processed file"""
    try:
        file_processor = get_file_processor(OPENAI_API_KEY)
        file_info = file_processor.get_file_info(file_id)
        
        if not file_info:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify({
            'success': True,
            'file_info': {
                'file_id': file_info['file_id'],
                'original_filename': file_info['original_filename'],
                'file_type': file_info['file_type'],
                'file_size': file_info['file_size'],
                'uploaded_at': file_info['uploaded_at'],
                'analysis': file_info['analysis'],
                'processed': file_info['processed']
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/user/<user_id>', methods=['GET'])
def get_user_files(user_id):
    """Get all files for a user"""
    try:
        file_processor = get_file_processor(OPENAI_API_KEY)
        user_files = file_processor.list_user_files(user_id)
        
        files_list = []
        for file_record in user_files:
            files_list.append({
                'file_id': file_record['file_id'],
                'original_filename': file_record['original_filename'],
                'file_type': file_record['file_type'],
                'file_size': file_record['file_size'],
                'uploaded_at': file_record['uploaded_at'],
                'processed': file_record['processed']
            })
        
        return jsonify({
            'success': True,
            'files': files_list,
            'count': len(files_list)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/process/<file_id>', methods=['POST'])
def process_file_with_ai(file_id):
    """Process a file with AI based on task description"""
    try:
        data = request.get_json()
        task_description = data.get('task_description', '')
        
        if not task_description:
            return jsonify({'error': 'Task description required'}), 400
        
        file_processor = get_file_processor(OPENAI_API_KEY)
        result = file_processor.process_with_ai(file_id, task_description)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'success': True,
            'processing_result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file"""
    try:
        file_processor = get_file_processor(OPENAI_API_KEY)
        success = file_processor.delete_file(file_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'File deleted successfully'
            })
        else:
            return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

