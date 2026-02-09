import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Analytics from './pages/Analytics';
import RiskTable from './pages/RiskTable';
import Settings from './pages/Settings';
import './App.css';

function App() {
    return (
        <ThemeProvider>
            <Router>
                <div className="app-layout">
                    <Sidebar />
                    <main className="main-content">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/upload" element={<Upload />} />
                            <Route path="/analytics" element={<Analytics />} />
                            <Route path="/risk-table" element={<RiskTable />} />
                            <Route path="/settings" element={<Settings />} />
                            <Route path="/help" element={<HelpPage />} />
                        </Routes>
                    </main>
                </div>
            </Router>
        </ThemeProvider>
    );
}

// Simple Help Page
function HelpPage() {
    return (
        <div className="help-page">
            <header className="page-header">
                <h1 className="page-title">Help & Documentation</h1>
                <p className="page-subtitle">Learn how to use PowerGuard</p>
            </header>

            <div className="help-content">
                <section className="card">
                    <h3 className="card-title">Getting Started</h3>
                    <ol className="help-list">
                        <li>
                            <strong>Upload Data:</strong> Go to the Upload page and upload your smart meter CSV file.
                        </li>
                        <li>
                            <strong>Run Detection:</strong> After uploading, click "Run Anomaly Detection" to analyze the data.
                        </li>
                        <li>
                            <strong>View Results:</strong> Check the Dashboard for an overview or Risk Table for detailed results.
                        </li>
                        <li>
                            <strong>Analyze Patterns:</strong> Use the Analytics page to visualize individual meter consumption.
                        </li>
                    </ol>
                </section>

                <section className="card">
                    <h3 className="card-title">CSV Format</h3>
                    <p>Your CSV file must have these columns:</p>
                    <ul className="help-list">
                        <li><code>meter_id</code> - Unique identifier for each meter</li>
                        <li><code>timestamp</code> - ISO format datetime (e.g., 2024-01-15T10:00:00)</li>
                        <li><code>consumption_kwh</code> - Energy consumption in kilowatt-hours</li>
                    </ul>
                </section>

                <section className="card">
                    <h3 className="card-title">Understanding Risk Levels</h3>
                    <ul className="help-list">
                        <li><strong className="risk-critical">Critical (75-100%):</strong> Immediate investigation required</li>
                        <li><strong className="risk-high">High (50-74%):</strong> High likelihood of anomaly</li>
                        <li><strong className="risk-medium">Medium (25-49%):</strong> Moderate suspicion, worth monitoring</li>
                        <li><strong className="risk-low">Low (0-24%):</strong> Normal consumption patterns</li>
                    </ul>
                </section>

                <section className="card">
                    <h3 className="card-title">API Documentation</h3>
                    <p>
                        Access the full API documentation at{' '}
                        <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
                            http://localhost:8000/docs
                        </a>
                    </p>
                </section>
            </div>
        </div>
    );
}

export default App;
