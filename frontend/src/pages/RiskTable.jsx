import React, { useState } from 'react';
import { AlertTriangle, RefreshCw, Play, Filter } from 'lucide-react';
import DataTable from '../components/DataTable';
import { useAnomalyResults, useAnomalyDetection, useDashboardStats } from '../hooks/useData';
import './RiskTable.css';

export default function RiskTable() {
    const [suspiciousOnly, setSuspiciousOnly] = useState(false);
    const { results, loading, error, refetch } = useAnomalyResults(suspiciousOnly);
    const { runDetection, loading: detecting } = useAnomalyDetection();
    const { refetch: refetchStats } = useDashboardStats();
    const [selectedModel, setSelectedModel] = useState('isolation_forest');

    // Table columns
    const columns = [
        {
            key: 'meter_id',
            label: 'Meter ID',
            width: '140px'
        },
        {
            key: 'anomaly_score',
            label: 'Anomaly Score',
            type: 'score',
            width: '200px'
        },
        {
            key: 'risk_level',
            label: 'Risk Level',
            type: 'risk',
            width: '120px'
        },
        {
            key: 'is_suspicious',
            label: 'Flagged',
            type: 'boolean',
            width: '80px'
        },
        {
            key: 'hourly_avg',
            label: 'Hourly Avg (kWh)',
            decimals: 3,
            width: '130px'
        },
        {
            key: 'night_ratio',
            label: 'Night Ratio',
            decimals: 2,
            width: '100px'
        },
        {
            key: 'explanation',
            label: 'Explanation',
            render: (value) => (
                <span className="explanation-cell" title={value}>
                    {value?.substring(0, 80)}...
                </span>
            )
        },
    ];

    // Run new detection
    const handleRunDetection = async () => {
        try {
            await runDetection({ model: selectedModel });
            refetch();
            refetchStats();
        } catch (err) {
            console.error('Detection failed:', err);
        }
    };

    // Summary stats
    const criticalCount = results.filter(r => r.risk_level === 'critical').length;
    const highCount = results.filter(r => r.risk_level === 'high').length;
    const suspiciousCount = results.filter(r => r.is_suspicious).length;

    return (
        <div className="risk-table-page">
            {/* Page Header */}
            <header className="page-header">
                <div>
                    <h1 className="page-title">Risk Table</h1>
                    <p className="page-subtitle">
                        View and analyze all meter anomaly detection results
                    </p>
                </div>
                <div className="header-actions">
                    <button
                        className="btn btn-secondary"
                        onClick={refetch}
                        disabled={loading}
                    >
                        <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                        Refresh
                    </button>
                </div>
            </header>

            {/* Controls Bar */}
            <div className="controls-bar card">
                <div className="control-group">
                    <label className="control-label">Model</label>
                    <select
                        className="form-select"
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                    >
                        <option value="isolation_forest">Isolation Forest</option>
                        <option value="autoencoder">Autoencoder</option>
                    </select>
                </div>

                <div className="control-group">
                    <label className="control-label filter-label">
                        <input
                            type="checkbox"
                            checked={suspiciousOnly}
                            onChange={(e) => setSuspiciousOnly(e.target.checked)}
                        />
                        <Filter size={16} />
                        Suspicious Only
                    </label>
                </div>

                <button
                    className="btn btn-primary"
                    onClick={handleRunDetection}
                    disabled={detecting}
                >
                    {detecting ? (
                        <>
                            <span className="loading-spinner small" />
                            Running...
                        </>
                    ) : (
                        <>
                            <Play size={18} />
                            Run Detection
                        </>
                    )}
                </button>
            </div>

            {/* Summary Stats */}
            <div className="summary-bar">
                <div className="summary-item">
                    <span className="summary-value">{results.length}</span>
                    <span className="summary-label">Total Results</span>
                </div>
                <div className="summary-item danger">
                    <span className="summary-value">{criticalCount + highCount}</span>
                    <span className="summary-label">High/Critical Risk</span>
                </div>
                <div className="summary-item warning">
                    <span className="summary-value">{suspiciousCount}</span>
                    <span className="summary-label">Flagged Suspicious</span>
                </div>
            </div>

            {/* Error Display */}
            {error && (
                <div className="error-banner">
                    <AlertTriangle size={20} />
                    <span>{error}</span>
                </div>
            )}

            {/* Results Table */}
            <div className="table-section">
                <DataTable
                    data={results}
                    columns={columns}
                    loading={loading}
                    emptyMessage={
                        suspiciousOnly
                            ? "No suspicious meters found. Try running anomaly detection first."
                            : "No results available. Upload data and run anomaly detection to see results."
                    }
                />
            </div>

            {/* Legend */}
            <div className="legend">
                <h4>Risk Levels</h4>
                <div className="legend-items">
                    <div className="legend-item">
                        <span className="legend-dot critical" />
                        Critical (75-100%)
                    </div>
                    <div className="legend-item">
                        <span className="legend-dot high" />
                        High (50-74%)
                    </div>
                    <div className="legend-item">
                        <span className="legend-dot medium" />
                        Medium (25-49%)
                    </div>
                    <div className="legend-item">
                        <span className="legend-dot low" />
                        Low (0-24%)
                    </div>
                </div>
            </div>
        </div>
    );
}
