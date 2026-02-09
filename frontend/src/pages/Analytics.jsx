import React, { useState } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceDot,
    Legend,
    Area,
    ComposedChart
} from 'recharts';
import { BarChart3, AlertTriangle, Activity, Info } from 'lucide-react';
import { useMeterList, useMeterTimeSeries } from '../hooks/useData';
import './Analytics.css';

export default function Analytics() {
    const [selectedMeter, setSelectedMeter] = useState('');
    const { meters, loading: metersLoading } = useMeterList();
    const { data: meterData, loading: dataLoading, error } = useMeterTimeSeries(selectedMeter);

    // Process chart data
    const chartData = meterData?.readings?.map((reading, index) => ({
        index,
        timestamp: new Date(reading.timestamp).toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit'
        }),
        consumption: reading.consumption_kwh,
        isAnomaly: reading.is_anomaly,
    })) || [];

    // Get anomaly points for highlighting
    const anomalyPoints = chartData.filter(point => point.isAnomaly);

    // Custom tooltip
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="chart-tooltip">
                    <p className="tooltip-label">{label}</p>
                    <p className="tooltip-value">
                        <span className="tooltip-dot" style={{ background: '#6366f1' }} />
                        Consumption: {data.consumption.toFixed(3)} kWh
                    </p>
                    {data.isAnomaly && (
                        <p className="tooltip-anomaly">
                            <AlertTriangle size={14} />
                            Anomaly Detected
                        </p>
                    )}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="analytics-page">
            {/* Page Header */}
            <header className="page-header">
                <div>
                    <h1 className="page-title">Analytics</h1>
                    <p className="page-subtitle">
                        Visualize consumption patterns and identify anomalies
                    </p>
                </div>
            </header>

            {/* Meter Selector */}
            <div className="meter-selector card">
                <div className="selector-header">
                    <BarChart3 size={24} className="selector-icon" />
                    <div>
                        <h3>Select Meter</h3>
                        <p>Choose a meter to view its consumption data</p>
                    </div>
                </div>
                <select
                    className="form-select"
                    value={selectedMeter}
                    onChange={(e) => setSelectedMeter(e.target.value)}
                    disabled={metersLoading}
                >
                    <option value="">
                        {metersLoading ? 'Loading meters...' : 'Select a meter'}
                    </option>
                    {meters.map(meterId => (
                        <option key={meterId} value={meterId}>
                            {meterId}
                        </option>
                    ))}
                </select>
            </div>

            {/* Chart Area */}
            {selectedMeter && (
                <div className="chart-section">
                    {/* Main Chart */}
                    <div className="chart-card card">
                        <div className="card-header">
                            <h3 className="card-title">
                                <Activity size={20} />
                                Consumption Over Time
                            </h3>
                            {meterData?.anomaly_result?.is_suspicious && (
                                <span className="badge badge-warning">
                                    <AlertTriangle size={14} />
                                    Suspicious
                                </span>
                            )}
                        </div>

                        {dataLoading ? (
                            <div className="chart-loading">
                                <div className="loading-spinner" />
                                <p>Loading chart data...</p>
                            </div>
                        ) : error ? (
                            <div className="chart-error">
                                <AlertTriangle size={32} />
                                <p>{error}</p>
                            </div>
                        ) : chartData.length > 0 ? (
                            <div className="chart-container">
                                <ResponsiveContainer width="100%" height={400}>
                                    <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorConsumption" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid
                                            strokeDasharray="3 3"
                                            stroke="rgba(255,255,255,0.1)"
                                            vertical={false}
                                        />
                                        <XAxis
                                            dataKey="timestamp"
                                            stroke="#64748b"
                                            fontSize={12}
                                            tickLine={false}
                                            interval="preserveStartEnd"
                                        />
                                        <YAxis
                                            stroke="#64748b"
                                            fontSize={12}
                                            tickLine={false}
                                            axisLine={false}
                                            label={{
                                                value: 'kWh',
                                                angle: -90,
                                                position: 'insideLeft',
                                                fill: '#64748b'
                                            }}
                                        />
                                        <Tooltip content={<CustomTooltip />} />
                                        <Legend />
                                        <Area
                                            type="monotone"
                                            dataKey="consumption"
                                            stroke="#6366f1"
                                            fillOpacity={1}
                                            fill="url(#colorConsumption)"
                                            name="Consumption (kWh)"
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="consumption"
                                            stroke="#6366f1"
                                            strokeWidth={2}
                                            dot={false}
                                            activeDot={{ r: 6, fill: '#6366f1' }}
                                            name="Consumption"
                                        />
                                        {/* Highlight anomaly points */}
                                        {anomalyPoints.map((point, idx) => (
                                            <ReferenceDot
                                                key={idx}
                                                x={point.timestamp}
                                                y={point.consumption}
                                                r={8}
                                                fill="#ef4444"
                                                stroke="#fff"
                                                strokeWidth={2}
                                            />
                                        ))}
                                    </ComposedChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <div className="chart-empty">
                                <Info size={32} />
                                <p>No data available for this meter</p>
                            </div>
                        )}
                    </div>

                    {/* Meter Stats & Anomaly Info */}
                    {meterData && (
                        <div className="stats-row">
                            {/* Feature Stats */}
                            <div className="card stats-card">
                                <h3 className="card-title">Feature Analysis</h3>
                                <div className="stats-grid">
                                    <StatItem
                                        label="Hourly Average"
                                        value={`${(meterData.stats?.hourly_avg || 0).toFixed(3)} kWh`}
                                    />
                                    <StatItem
                                        label="Daily Variance"
                                        value={(meterData.stats?.daily_variance || 0).toFixed(3)}
                                    />
                                    <StatItem
                                        label="Night Ratio"
                                        value={`${((meterData.stats?.night_ratio || 0) * 100).toFixed(1)}%`}
                                    />
                                    <StatItem
                                        label="Total Readings"
                                        value={chartData.length}
                                    />
                                </div>
                            </div>

                            {/* Anomaly Result */}
                            {meterData.anomaly_result && (
                                <div className={`card anomaly-card ${meterData.anomaly_result.is_suspicious ? 'suspicious' : ''}`}>
                                    <h3 className="card-title">
                                        {meterData.anomaly_result.is_suspicious ? (
                                            <>
                                                <AlertTriangle size={20} className="text-warning" />
                                                Anomaly Detected
                                            </>
                                        ) : (
                                            <>
                                                <Activity size={20} className="text-success" />
                                                Normal Pattern
                                            </>
                                        )}
                                    </h3>
                                    <div className="anomaly-details">
                                        <div className="anomaly-score">
                                            <span className="score-label">Anomaly Score</span>
                                            <span className={`score-value risk-${meterData.anomaly_result.risk_level}`}>
                                                {(meterData.anomaly_result.anomaly_score * 100).toFixed(1)}%
                                            </span>
                                        </div>
                                        <p className="anomaly-explanation">
                                            {meterData.anomaly_result.explanation}
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Empty State */}
            {!selectedMeter && (
                <div className="empty-state card">
                    <BarChart3 size={64} className="empty-icon" />
                    <h3>Select a Meter to View Analytics</h3>
                    <p>
                        Choose a meter from the dropdown above to visualize its consumption
                        patterns and anomaly detection results.
                    </p>
                </div>
            )}
        </div>
    );
}

// Stat Item Component
function StatItem({ label, value }) {
    return (
        <div className="stat-item">
            <span className="stat-label">{label}</span>
            <span className="stat-value">{value}</span>
        </div>
    );
}
