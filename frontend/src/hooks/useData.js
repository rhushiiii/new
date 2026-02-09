import { useState, useEffect, useCallback } from 'react';
import { anomalyAPI, metersAPI, uploadAPI } from '../services/api';

/**
 * Hook for fetching dashboard statistics
 */
export function useDashboardStats() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchStats = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await anomalyAPI.getStats();
            setStats(data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch statistics');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchStats();
    }, [fetchStats]);

    return { stats, loading, error, refetch: fetchStats };
}

/**
 * Hook for fetching anomaly results
 */
export function useAnomalyResults(suspiciousOnly = false) {
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchResults = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await anomalyAPI.getResults(suspiciousOnly);
            setResults(data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch results');
        } finally {
            setLoading(false);
        }
    }, [suspiciousOnly]);

    useEffect(() => {
        fetchResults();
    }, [fetchResults]);

    return { results, loading, error, refetch: fetchResults };
}

/**
 * Hook for fetching meter list
 */
export function useMeterList() {
    const [meters, setMeters] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchMeters = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await metersAPI.getIds();
            setMeters(data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch meters');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchMeters();
    }, [fetchMeters]);

    return { meters, loading, error, refetch: fetchMeters };
}

/**
 * Hook for fetching meter time series
 */
export function useMeterTimeSeries(meterId) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        if (!meterId) {
            setData(null);
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const response = await metersAPI.getTimeSeries(meterId);
            setData(response);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch meter data');
        } finally {
            setLoading(false);
        }
    }, [meterId]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return { data, loading, error, refetch: fetchData };
}

/**
 * Hook for running anomaly detection
 */
export function useAnomalyDetection() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);

    const runDetection = useCallback(async (options = {}) => {
        try {
            setLoading(true);
            setError(null);
            const data = await anomalyAPI.runDetection(options);
            setResult(data);
            return data;
        } catch (err) {
            const errorMsg = err.response?.data?.detail || 'Detection failed';
            setError(errorMsg);
            throw new Error(errorMsg);
        } finally {
            setLoading(false);
        }
    }, []);

    return { runDetection, loading, error, result };
}

/**
 * Hook for file upload
 */
export function useFileUpload() {
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);

    const upload = useCallback(async (file) => {
        try {
            setLoading(true);
            setProgress(0);
            setError(null);

            const data = await uploadAPI.uploadCSV(file, (percent) => {
                setProgress(percent);
            });

            setResult(data);
            return data;
        } catch (err) {
            const errorMsg = err.response?.data?.detail || 'Upload failed';
            setError(errorMsg);
            throw new Error(errorMsg);
        } finally {
            setLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setLoading(false);
        setProgress(0);
        setError(null);
        setResult(null);
    }, []);

    return { upload, loading, progress, error, result, reset };
}
