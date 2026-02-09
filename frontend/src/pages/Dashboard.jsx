import React from 'react';
import {
    Gauge,
    Users,
    AlertTriangle,
    Activity,
    TrendingUp,
    Zap,
    Clock
} from 'lucide-react';
import StatCard from '../components/StatCard';
import DataTable from '../components/DataTable';
import { useDashboardStats, useAnomalyResults } from '../hooks/useData';
import './Dashboard.css';

export default function Dashboard() {
    const { stats, loading: statsLoading, refetch: refetchStats } = useDashboardStats();
    const { results, loading: resultsLoading } = useAnomalyResults(true); // suspicious only

    // Table columns for high-risk alerts
    const alertColumns = [
        { key: 'meter_id', label: 'Meter ID', width: '150px' },
        { key: 'anomaly_score', label: 'Score', type: 'score', width: '180px' },
        { key: 'risk_level', label: 'Risk Level', type: 'risk', width: '120px' },
        {
            key: 'explanation',
            label: 'Reason',
            render: (value) => (
                <span className="explanation-text" title={value}>
                    {value?.substring(0, 60)}...
                </span>
            )
        },
    ];

    // Get only high/critical risk results for alerts
    const highRiskResults = results.filter(r =>
        ['high', 'critical'].includes(r.risk_level)
    ).slice(0, 5);

    return (
        <div className="dashboard">
            {/* Page Header */}
            <header className="page-header">
                <div>
                    <h1 className="page-title">Dashboard</h1>
                    <p className="page-subtitle">
                        Real-time overview of smart meter monitoring and anomaly detection
                    </p>
                </div>
                <button className="btn btn-primary" onClick={refetchStats}>
                    <Activity size={18} />
                    Refresh Data
                </button>
            </header>

            {/* Stats Grid */}
            <section className="stats-grid">
                <StatCard
                    title="Total Meters"
                    value={stats?.total_meters || 0}
                    icon={Users}
                    loading={statsLoading}
                />
                <StatCard
                    title="Total Readings"
                    value={stats?.total_readings || 0}
                    icon={Gauge}
                    loading={statsLoading}
                />
                <StatCard
                    title="Suspicious Meters"
                    value={stats?.suspicious_meters || 0}
                    icon={AlertTriangle}
                    variant="warning"
                    loading={statsLoading}
                />
                <StatCard
                    title="Suspicious Rate"
                    value={`${(stats?.suspicious_percentage || 0).toFixed(1)}%`}
                    icon={TrendingUp}
                    variant={stats?.suspicious_percentage > 20 ? 'danger' : 'success'}
                    loading={statsLoading}
                />
            </section>

            {/* Risk Breakdown */}
            <section className="risk-section">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">Risk Distribution</h3>
                    </div>
                    <div className="risk-breakdown">
                        <RiskCard
                            level="high"
                            count={stats?.high_risk_count || 0}
                            icon={Zap}
                            loading={statsLoading}
                        />
                        <RiskCard
                            level="medium"
                            count={stats?.medium_risk_count || 0}
                            icon={AlertTriangle}
                            loading={statsLoading}
                        />
                        <RiskCard
                            level="low"
                            count={stats?.low_risk_count || 0}
                            icon={Activity}
                            loading={statsLoading}
                        />
                    </div>
                </div>
            </section>

            {/* High Risk Alerts Table */}
            <section className="alerts-section">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">
                            <AlertTriangle size={20} className="text-warning" />
                            High-Risk Alerts
                        </h3>
                        <span className="badge badge-warning">
                            {highRiskResults.length} Alert{highRiskResults.length !== 1 ? 's' : ''}
                        </span>
                    </div>
                    <DataTable
                        data={highRiskResults}
                        columns={alertColumns}
                        loading={resultsLoading}
                        emptyMessage="No high-risk meters detected. Run anomaly detection to analyze data."
                    />
                </div>
            </section>

            {/* Last Detection Info */}
            {stats?.last_detection && (
                <div className="last-detection">
                    <Clock size={16} />
                    <span>
                        Last detection: {new Date(stats.last_detection).toLocaleString()}
                    </span>
                </div>
            )}
        </div>
    );
}

// Risk Card Sub-component
function RiskCard({ level, count, icon: Icon, loading }) {
    const config = {
        high: { label: 'High Risk', color: '#ef4444', bg: 'rgba(239, 68, 68, 0.1)' },
        medium: { label: 'Medium Risk', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.1)' },
        low: { label: 'Low Risk', color: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },
    };

    const { label, color, bg } = config[level];

    if (loading) {
        return (
            <div className="risk-card loading">
                <div className="loading-skeleton" />
            </div>
        );
    }

    return (
        <div className="risk-card" style={{ borderColor: color }}>
            <div className="risk-card__icon" style={{ background: bg, color }}>
                <Icon size={24} />
            </div>
            <div className="risk-card__content">
                <p className="risk-card__value" style={{ color }}>{count}</p>
                <p className="risk-card__label">{label}</p>
            </div>
        </div>
    );
}
