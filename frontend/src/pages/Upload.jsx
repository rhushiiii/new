import React, { useState, useCallback } from 'react';
import { Upload as UploadIcon, FileText, CheckCircle, AlertCircle, X, Play } from 'lucide-react';
import { useFileUpload, useAnomalyDetection, useDashboardStats } from '../hooks/useData';
import './Upload.css';

export default function Upload() {
    const [dragOver, setDragOver] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const { upload, loading: uploading, progress, error: uploadError, result: uploadResult, reset } = useFileUpload();
    const { runDetection, loading: detecting, error: detectError, result: detectResult } = useAnomalyDetection();
    const { refetch: refetchStats } = useDashboardStats();

    // Handle file selection
    const handleFileSelect = (e) => {
        const file = e.target.files?.[0];
        if (file && file.name.endsWith('.csv')) {
            setSelectedFile(file);
            reset();
        }
    };

    // Handle drag and drop
    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files?.[0];
        if (file && file.name.endsWith('.csv')) {
            setSelectedFile(file);
            reset();
        }
    }, [reset]);

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragOver(true);
    };

    const handleDragLeave = () => {
        setDragOver(false);
    };

    // Upload file
    const handleUpload = async () => {
        if (!selectedFile) return;

        try {
            await upload(selectedFile);
            refetchStats();
        } catch (err) {
            console.error('Upload failed:', err);
        }
    };

    // Run detection after upload
    const handleRunDetection = async () => {
        try {
            await runDetection({ model: 'isolation_forest' });
            refetchStats();
        } catch (err) {
            console.error('Detection failed:', err);
        }
    };

    // Clear selection
    const handleClear = () => {
        setSelectedFile(null);
        reset();
    };

    return (
        <div className="upload-page">
            {/* Page Header */}
            <header className="page-header">
                <div>
                    <h1 className="page-title">Upload Data</h1>
                    <p className="page-subtitle">
                        Upload smart meter CSV data for analysis and anomaly detection
                    </p>
                </div>
            </header>

            {/* Upload Zone */}
            <div className="upload-card">
                <div
                    className={`upload-zone ${dragOver ? 'dragover' : ''} ${uploadResult?.success ? 'success' : ''}`}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                >
                    <input
                        type="file"
                        id="file-input"
                        accept=".csv"
                        onChange={handleFileSelect}
                        className="file-input"
                    />

                    {!selectedFile ? (
                        <label htmlFor="file-input" className="upload-label">
                            <div className="upload-icon">
                                <UploadIcon size={48} />
                            </div>
                            <h3>Drop your CSV file here</h3>
                            <p>or click to browse</p>
                            <span className="upload-hint">Supports: .csv files</span>
                        </label>
                    ) : (
                        <div className="selected-file">
                            <FileText size={48} className="file-icon" />
                            <div className="file-info">
                                <h3>{selectedFile.name}</h3>
                                <p>{(selectedFile.size / 1024).toFixed(1)} KB</p>
                            </div>
                            <button className="btn-icon" onClick={handleClear}>
                                <X size={20} />
                            </button>
                        </div>
                    )}
                </div>

                {/* Progress Bar */}
                {uploading && (
                    <div className="progress-container">
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                        <span className="progress-text">{progress}% uploading...</span>
                    </div>
                )}

                {/* Upload Result */}
                {uploadResult && (
                    <div className={`upload-result ${uploadResult.success ? 'success' : 'error'}`}>
                        {uploadResult.success ? (
                            <>
                                <CheckCircle size={24} />
                                <div>
                                    <h4>Upload Successful!</h4>
                                    <p>
                                        {uploadResult.meters_count} meters, {uploadResult.readings_count.toLocaleString()} readings
                                    </p>
                                </div>
                            </>
                        ) : (
                            <>
                                <AlertCircle size={24} />
                                <div>
                                    <h4>Upload Failed</h4>
                                    <p>{uploadResult.message}</p>
                                </div>
                            </>
                        )}
                    </div>
                )}

                {/* Error Display */}
                {(uploadError || detectError) && (
                    <div className="upload-result error">
                        <AlertCircle size={24} />
                        <div>
                            <h4>Error</h4>
                            <p>{uploadError || detectError}</p>
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="upload-actions">
                    <button
                        className="btn btn-primary btn-lg"
                        onClick={handleUpload}
                        disabled={!selectedFile || uploading}
                    >
                        {uploading ? (
                            <>
                                <span className="loading-spinner small" />
                                Uploading...
                            </>
                        ) : (
                            <>
                                <UploadIcon size={20} />
                                Upload Data
                            </>
                        )}
                    </button>

                    {uploadResult?.success && (
                        <button
                            className="btn btn-secondary btn-lg"
                            onClick={handleRunDetection}
                            disabled={detecting}
                        >
                            {detecting ? (
                                <>
                                    <span className="loading-spinner small" />
                                    Detecting...
                                </>
                            ) : (
                                <>
                                    <Play size={20} />
                                    Run Anomaly Detection
                                </>
                            )}
                        </button>
                    )}
                </div>

                {/* Detection Result */}
                {detectResult && (
                    <div className="detection-result">
                        <CheckCircle size={24} className="text-success" />
                        <div>
                            <h4>Detection Complete!</h4>
                            <p>
                                Analyzed {detectResult.meters_analyzed} meters,
                                found {detectResult.suspicious_count} suspicious
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* CSV Format Help */}
            <div className="format-help card">
                <h3 className="card-title">Expected CSV Format</h3>
                <div className="format-content">
                    <p>Your CSV file should have the following columns:</p>
                    <table className="format-table">
                        <thead>
                            <tr>
                                <th>Column</th>
                                <th>Type</th>
                                <th>Example</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><code>meter_id</code></td>
                                <td>String</td>
                                <td>METER_0001</td>
                            </tr>
                            <tr>
                                <td><code>timestamp</code></td>
                                <td>ISO DateTime</td>
                                <td>2024-01-15T10:00:00</td>
                            </tr>
                            <tr>
                                <td><code>consumption_kwh</code></td>
                                <td>Float</td>
                                <td>2.45</td>
                            </tr>
                        </tbody>
                    </table>
                    <div className="sample-csv">
                        <h4>Sample:</h4>
                        <pre>
                            {`meter_id,timestamp,consumption_kwh
METER_0001,2024-01-15T00:00:00,0.85
METER_0001,2024-01-15T01:00:00,0.72
METER_0002,2024-01-15T00:00:00,1.23`}
                        </pre>
                    </div>
                </div>
            </div>
        </div>
    );
}
