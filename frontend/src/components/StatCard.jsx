import React from 'react';
import './StatCard.css';

/**
 * StatCard - Display a statistic with icon and optional trend
 */
export default function StatCard({
    title,
    value,
    icon: Icon,
    trend = null,
    trendLabel = '',
    variant = 'default',
    loading = false
}) {
    const variantClass = `stat-card--${variant}`;

    const formatValue = (val) => {
        if (typeof val === 'number') {
            if (val >= 1000000) {
                return `${(val / 1000000).toFixed(1)}M`;
            }
            if (val >= 1000) {
                return `${(val / 1000).toFixed(1)}K`;
            }
            if (Number.isInteger(val)) {
                return val.toLocaleString();
            }
            return val.toFixed(1);
        }
        return val;
    };

    if (loading) {
        return (
            <div className={`stat-card ${variantClass} loading`}>
                <div className="stat-card__skeleton"></div>
            </div>
        );
    }

    return (
        <div className={`stat-card ${variantClass}`}>
            {Icon && (
                <div className="stat-card__icon">
                    <Icon size={24} />
                </div>
            )}
            <div className="stat-card__content">
                <p className="stat-card__label">{title}</p>
                <p className="stat-card__value">{formatValue(value)}</p>
                {trend !== null && (
                    <div className={`stat-card__trend ${trend >= 0 ? 'positive' : 'negative'}`}>
                        <span>{trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%</span>
                        {trendLabel && <span className="trend-label">{trendLabel}</span>}
                    </div>
                )}
            </div>
        </div>
    );
}
