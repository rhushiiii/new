import React, { useState, useMemo } from 'react';
import { ArrowUpDown, AlertTriangle, CheckCircle } from 'lucide-react';
import './DataTable.css';

/**
 * DataTable - Sortable table component for displaying data
 */
export default function DataTable({
    data = [],
    columns = [],
    loading = false,
    emptyMessage = 'No data available'
}) {
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

    // Handle sorting
    const handleSort = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    // Sort data
    const sortedData = useMemo(() => {
        if (!sortConfig.key) return data;

        return [...data].sort((a, b) => {
            const aVal = a[sortConfig.key];
            const bVal = b[sortConfig.key];

            if (aVal === null || aVal === undefined) return 1;
            if (bVal === null || bVal === undefined) return -1;

            if (typeof aVal === 'number' && typeof bVal === 'number') {
                return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
            }

            const aStr = String(aVal).toLowerCase();
            const bStr = String(bVal).toLowerCase();

            if (sortConfig.direction === 'asc') {
                return aStr.localeCompare(bStr);
            }
            return bStr.localeCompare(aStr);
        });
    }, [data, sortConfig]);

    // Render cell content
    const renderCell = (row, column) => {
        const value = row[column.key];

        if (column.render) {
            return column.render(value, row);
        }

        if (column.type === 'risk') {
            return <RiskBadge level={value} />;
        }

        if (column.type === 'score') {
            return <ScoreBar score={value} />;
        }

        if (column.type === 'boolean') {
            return value ? (
                <AlertTriangle size={18} className="text-warning" />
            ) : (
                <CheckCircle size={18} className="text-success" />
            );
        }

        if (typeof value === 'number') {
            return value.toFixed(column.decimals || 2);
        }

        return value ?? '-';
    };

    if (loading) {
        return (
            <div className="table-container">
                <div className="table-loading">
                    <div className="loading-spinner"></div>
                    <p>Loading data...</p>
                </div>
            </div>
        );
    }

    if (!data.length) {
        return (
            <div className="table-container">
                <div className="table-empty">
                    <p>{emptyMessage}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="table-container">
            <table className="data-table">
                <thead>
                    <tr>
                        {columns.map((column) => (
                            <th
                                key={column.key}
                                onClick={() => column.sortable !== false && handleSort(column.key)}
                                className={column.sortable !== false ? 'sortable' : ''}
                                style={{ width: column.width }}
                            >
                                <div className="th-content">
                                    <span>{column.label}</span>
                                    {column.sortable !== false && (
                                        <ArrowUpDown
                                            size={14}
                                            className={`sort-icon ${sortConfig.key === column.key ? 'active' : ''
                                                }`}
                                        />
                                    )}
                                </div>
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {sortedData.map((row, index) => (
                        <tr key={row.id || row.meter_id || index}>
                            {columns.map((column) => (
                                <td key={column.key}>
                                    {renderCell(row, column)}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

// Risk Badge Component
function RiskBadge({ level }) {
    const levels = {
        critical: { label: 'Critical', class: 'badge-danger' },
        high: { label: 'High', class: 'badge-danger' },
        medium: { label: 'Medium', class: 'badge-warning' },
        low: { label: 'Low', class: 'badge-success' },
    };

    const config = levels[level] || levels.low;

    return (
        <span className={`badge ${config.class}`}>
            {config.label}
        </span>
    );
}

// Score Bar Component
function ScoreBar({ score }) {
    const percentage = (score * 100).toFixed(0);
    const color = score >= 0.7 ? '#ef4444' : score >= 0.4 ? '#f59e0b' : '#10b981';

    return (
        <div className="score-bar">
            <div className="score-bar__track">
                <div
                    className="score-bar__fill"
                    style={{ width: `${percentage}%`, background: color }}
                />
            </div>
            <span className="score-bar__value">{percentage}%</span>
        </div>
    );
}
