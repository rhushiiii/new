import React, { useState } from 'react';
import {
    Moon,
    Sun,
    Bell,
    Shield,
    Database,
    Trash2,
    RefreshCw,
    Download,
    Save,
    AlertTriangle
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import './Settings.css';

export default function Settings() {
    const { theme, setTheme, toggleTheme, isDark } = useTheme();
    const [settings, setSettings] = useState({
        anomalyThreshold: 0.5,
        model: 'isolation_forest',
        autoDetect: false,
        notifications: true,
        highRiskAlerts: true,
    });
    const [saved, setSaved] = useState(false);

    const handleSettingChange = (key, value) => {
        setSettings(prev => ({ ...prev, [key]: value }));
        setSaved(false);
    };

    const handleSave = () => {
        localStorage.setItem('powerguard-settings', JSON.stringify(settings));
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    const handleClearData = async () => {
        if (window.confirm('Are you sure you want to clear all data? This cannot be undone.')) {
            try {
                await fetch('http://localhost:8000/api/v1/upload/clear', { method: 'POST' });
                window.location.reload();
            } catch (err) {
                console.error('Failed to clear data:', err);
            }
        }
    };

    const handleExportResults = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/anomaly/results');
            const data = await response.json();

            const csv = [
                ['meter_id', 'anomaly_score', 'risk_level', 'is_suspicious', 'explanation'].join(','),
                ...data.map(r => [
                    r.meter_id,
                    r.anomaly_score,
                    r.risk_level,
                    r.is_suspicious,
                    `"${r.explanation || ''}"`
                ].join(','))
            ].join('\n');

            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'powerguard_results.csv';
            a.click();
        } catch (err) {
            console.error('Failed to export:', err);
        }
    };

    return (
        <div className="settings-page">
            {/* Page Header */}
            <header className="page-header">
                <div>
                    <h1 className="page-title">Settings</h1>
                    <p className="page-subtitle">Configure PowerGuard application settings</p>
                </div>
                <button className="btn btn-primary" onClick={handleSave}>
                    <Save size={18} />
                    {saved ? 'Saved!' : 'Save Settings'}
                </button>
            </header>

            <div className="settings-grid">
                {/* Appearance Settings */}
                <section className="settings-section card">
                    <div className="section-header">
                        <div className="section-icon">
                            {isDark ? <Moon size={20} /> : <Sun size={20} />}
                        </div>
                        <div>
                            <h3>Appearance</h3>
                            <p>Customize the look and feel</p>
                        </div>
                    </div>

                    <div className="settings-content">
                        <div className="setting-item">
                            <div className="setting-info">
                                <label>Theme Mode</label>
                                <p>Choose between light and dark theme</p>
                            </div>
                            <div className="theme-switcher">
                                <button
                                    className={`theme-btn ${!isDark ? 'active' : ''}`}
                                    onClick={() => setTheme('light')}
                                >
                                    <Sun size={18} />
                                    Light
                                </button>
                                <button
                                    className={`theme-btn ${isDark ? 'active' : ''}`}
                                    onClick={() => setTheme('dark')}
                                >
                                    <Moon size={18} />
                                    Dark
                                </button>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Detection Settings */}
                <section className="settings-section card">
                    <div className="section-header">
                        <div className="section-icon detection">
                            <Shield size={20} />
                        </div>
                        <div>
                            <h3>Detection</h3>
                            <p>Configure anomaly detection parameters</p>
                        </div>
                    </div>

                    <div className="settings-content">
                        <div className="setting-item">
                            <div className="setting-info">
                                <label>Anomaly Threshold</label>
                                <p>Score threshold for flagging suspicious meters (0.0 - 1.0)</p>
                            </div>
                            <input
                                type="range"
                                min="0"
                                max="1"
                                step="0.05"
                                value={settings.anomalyThreshold}
                                onChange={(e) => handleSettingChange('anomalyThreshold', parseFloat(e.target.value))}
                                className="range-input"
                            />
                            <span className="range-value">{settings.anomalyThreshold.toFixed(2)}</span>
                        </div>

                        <div className="setting-item">
                            <div className="setting-info">
                                <label>Default Model</label>
                                <p>Choose the ML model for detection</p>
                            </div>
                            <select
                                className="form-select"
                                value={settings.model}
                                onChange={(e) => handleSettingChange('model', e.target.value)}
                            >
                                <option value="isolation_forest">Isolation Forest</option>
                                <option value="autoencoder">Autoencoder</option>
                            </select>
                        </div>

                        <div className="setting-item">
                            <div className="setting-info">
                                <label>Auto-detect on Upload</label>
                                <p>Automatically run detection after uploading data</p>
                            </div>
                            <label className="toggle-switch">
                                <input
                                    type="checkbox"
                                    checked={settings.autoDetect}
                                    onChange={(e) => handleSettingChange('autoDetect', e.target.checked)}
                                />
                                <span className="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                </section>

                {/* Notification Settings */}
                <section className="settings-section card">
                    <div className="section-header">
                        <div className="section-icon notifications">
                            <Bell size={20} />
                        </div>
                        <div>
                            <h3>Notifications</h3>
                            <p>Manage alert preferences</p>
                        </div>
                    </div>

                    <div className="settings-content">
                        <div className="setting-item">
                            <div className="setting-info">
                                <label>Enable Notifications</label>
                                <p>Receive in-app notifications</p>
                            </div>
                            <label className="toggle-switch">
                                <input
                                    type="checkbox"
                                    checked={settings.notifications}
                                    onChange={(e) => handleSettingChange('notifications', e.target.checked)}
                                />
                                <span className="toggle-slider"></span>
                            </label>
                        </div>

                        <div className="setting-item">
                            <div className="setting-info">
                                <label>High-Risk Alerts</label>
                                <p>Show alerts for critical/high risk meters</p>
                            </div>
                            <label className="toggle-switch">
                                <input
                                    type="checkbox"
                                    checked={settings.highRiskAlerts}
                                    onChange={(e) => handleSettingChange('highRiskAlerts', e.target.checked)}
                                />
                                <span className="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                </section>

                {/* Data Management */}
                <section className="settings-section card">
                    <div className="section-header">
                        <div className="section-icon data">
                            <Database size={20} />
                        </div>
                        <div>
                            <h3>Data Management</h3>
                            <p>Export and manage your data</p>
                        </div>
                    </div>

                    <div className="settings-content">
                        <div className="setting-item">
                            <div className="setting-info">
                                <label>Export Results</label>
                                <p>Download anomaly detection results as CSV</p>
                            </div>
                            <button className="btn btn-secondary" onClick={handleExportResults}>
                                <Download size={16} />
                                Export CSV
                            </button>
                        </div>

                        <div className="setting-item danger-zone">
                            <div className="setting-info">
                                <label>Clear All Data</label>
                                <p>Remove all meters, readings, and results</p>
                            </div>
                            <button className="btn btn-danger" onClick={handleClearData}>
                                <Trash2 size={16} />
                                Clear Data
                            </button>
                        </div>
                    </div>
                </section>
            </div>

            {/* API Info */}
            <section className="api-info card">
                <div className="section-header">
                    <div className="section-icon api">
                        <RefreshCw size={20} />
                    </div>
                    <div>
                        <h3>API Information</h3>
                        <p>Backend connection details</p>
                    </div>
                </div>
                <div className="api-details">
                    <div className="api-item">
                        <span className="api-label">API URL</span>
                        <code>http://localhost:8000</code>
                    </div>
                    <div className="api-item">
                        <span className="api-label">Documentation</span>
                        <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
                            Swagger UI
                        </a>
                    </div>
                    <div className="api-item">
                        <span className="api-label">Version</span>
                        <span>v1.0.0</span>
                    </div>
                </div>
            </section>
        </div>
    );
}
