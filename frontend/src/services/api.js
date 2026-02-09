/**
 * PowerGuard API Service
 * Handles all HTTP communication with the backend
 */

import axios from 'axios';

// API base URL - uses environment variable in production, proxy in development
const API_BASE = import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api/v1`
    : '/api/v1';

// Create axios instance with defaults
const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
});

// Request interceptor for logging
api.interceptors.request.use(
    (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('[API Error]', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

/**
 * Upload API
 */
export const uploadAPI = {
    /**
     * Upload CSV file with meter data
     * @param {File} file - CSV file to upload
     * @param {function} onProgress - Progress callback (0-100)
     * @returns {Promise<object>} Upload response
     */
    uploadCSV: async (file, onProgress = null) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post('/upload/data', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
                if (onProgress && progressEvent.total) {
                    const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    onProgress(percent);
                }
            },
        });

        return response.data;
    },

    /**
     * Clear all data from database
     * @returns {Promise<object>}
     */
    clearData: async () => {
        const response = await api.post('/upload/clear');
        return response.data;
    },
};

/**
 * Anomaly Detection API
 */
export const anomalyAPI = {
    /**
     * Run anomaly detection
     * @param {object} options - Detection options
     * @param {string} options.model - 'isolation_forest' or 'autoencoder'
     * @param {number} options.threshold - Custom threshold (0-1)
     * @param {string[]} options.meterIds - Specific meters to analyze
     * @returns {Promise<object>} Detection results
     */
    runDetection: async (options = {}) => {
        const response = await api.post('/anomaly/detect', {
            model: options.model || 'isolation_forest',
            threshold: options.threshold,
            meter_ids: options.meterIds,
        });
        return response.data;
    },

    /**
     * Get all anomaly results
     * @param {boolean} suspiciousOnly - Filter to suspicious only
     * @param {number} limit - Max results
     * @returns {Promise<object[]>} Anomaly results
     */
    getResults: async (suspiciousOnly = false, limit = 100) => {
        const response = await api.get('/anomaly/results', {
            params: { suspicious_only: suspiciousOnly, limit },
        });
        return response.data;
    },

    /**
     * Get dashboard statistics
     * @returns {Promise<object>} Dashboard stats
     */
    getStats: async () => {
        const response = await api.get('/anomaly/stats');
        return response.data;
    },

    /**
     * Get result for specific meter
     * @param {string} meterId - Meter ID
     * @returns {Promise<object>} Meter anomaly result
     */
    getMeterResult: async (meterId) => {
        const response = await api.get(`/anomaly/result/${meterId}`);
        return response.data;
    },
};

/**
 * Meters API
 */
export const metersAPI = {
    /**
     * Get all meters
     * @param {number} limit - Max results
     * @returns {Promise<object[]>} Meter list
     */
    getAll: async (limit = 100) => {
        const response = await api.get('/meters/', { params: { limit } });
        return response.data;
    },

    /**
     * Get all meter IDs
     * @returns {Promise<string[]>} Meter ID list
     */
    getIds: async () => {
        const response = await api.get('/meters/ids');
        return response.data;
    },

    /**
     * Get meter time series data
     * @param {string} meterId - Meter ID
     * @returns {Promise<object>} Time series data with anomaly info
     */
    getTimeSeries: async (meterId) => {
        const response = await api.get(`/meters/${meterId}`);
        return response.data;
    },

    /**
     * Get detailed meter analysis
     * @param {string} meterId - Meter ID
     * @returns {Promise<object>} Detailed analysis
     */
    getAnalysis: async (meterId) => {
        const response = await api.get(`/meters/${meterId}/analysis`);
        return response.data;
    },
};

/**
 * Health Check API
 */
export const healthAPI = {
    /**
     * Check API health
     * @returns {Promise<object>} Health status
     */
    check: async () => {
        const response = await axios.get('/health');
        return response.data;
    },
};

// Export combined API
export default {
    upload: uploadAPI,
    anomaly: anomalyAPI,
    meters: metersAPI,
    health: healthAPI,
};
