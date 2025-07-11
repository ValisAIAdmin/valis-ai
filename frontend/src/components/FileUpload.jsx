import React, { useState, useRef } from 'react';

const FileUpload = ({ onFileUpload, disabled = false, maxSize = 10 * 1024 * 1024 }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleFiles = async (files) => {
    for (const file of files) {
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large. Maximum size is ${maxSize / (1024 * 1024)}MB`);
        continue;
      }

      await uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    setUploadProgress({ fileName: file.name, progress: 0 });

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', 'current_user'); // In real app, get from auth

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev.progress >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return { ...prev, progress: prev.progress + 10 };
        });
      }, 200);

      const response = await fetch('/api/files/upload', {
        method: 'POST',
        body: formData
      });

      clearInterval(progressInterval);
      setUploadProgress({ fileName: file.name, progress: 100 });

      if (response.ok) {
        const result = await response.json();
        
        const fileData = {
          id: result.file_id,
          name: result.filename,
          type: result.file_type,
          size: result.file_size,
          analysis: result.analysis,
          uploadedAt: new Date().toISOString()
        };

        setUploadedFiles(prev => [...prev, fileData]);
        
        if (onFileUpload) {
          onFileUpload(fileData);
        }

        setTimeout(() => setUploadProgress(null), 1000);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadProgress(null);
      alert(`Failed to upload ${file.name}`);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type) => {
    if (type.startsWith('image/')) return '🖼️';
    if (type.startsWith('video/')) return '🎥';
    if (type.startsWith('audio/')) return '🎵';
    if (type.includes('pdf')) return '📄';
    if (type.includes('text') || type.includes('code')) return '📝';
    if (type.includes('zip') || type.includes('archive')) return '📦';
    return '📁';
  };

  return (
    <div className="space-y-4">
      {/* Upload Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200
          ${isDragging 
            ? 'border-cyan-400 bg-cyan-400/10' 
            : 'border-gray-600 hover:border-gray-500'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-800/50'}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          disabled={disabled}
        />
        
        <div className="space-y-4">
          <div className="text-4xl">📁</div>
          <div>
            <div className="text-lg font-semibold text-white">
              {isDragging ? 'Drop files here' : 'Upload Files'}
            </div>
            <div className="text-sm text-gray-400 mt-1">
              Drag and drop files here, or click to select
            </div>
            <div className="text-xs text-gray-500 mt-2">
              Maximum file size: {maxSize / (1024 * 1024)}MB
            </div>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploadProgress && (
        <div className="bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-white">{uploadProgress.fileName}</span>
            <span className="text-sm text-gray-400">{uploadProgress.progress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-gray-300">Uploaded Files</h4>
          {uploadedFiles.map((file) => (
            <div key={file.id} className="bg-gray-800 rounded-lg p-3 flex items-center space-x-3">
              <span className="text-2xl">{getFileIcon(file.type)}</span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-white truncate">{file.name}</div>
                <div className="text-xs text-gray-400">
                  {formatFileSize(file.size)} • {file.type}
                </div>
                {file.analysis && (
                  <div className="text-xs text-cyan-400 mt-1 truncate">
                    AI Analysis: {file.analysis.summary || 'Processing...'}
                  </div>
                )}
              </div>
              <div className="flex space-x-2">
                <button className="text-cyan-400 hover:text-cyan-300 text-xs">
                  View
                </button>
                <button className="text-red-400 hover:text-red-300 text-xs">
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUpload;

