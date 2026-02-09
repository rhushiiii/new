import React from 'react';
import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Upload,
    BarChart3,
    AlertTriangle,
    Settings,
    HelpCircle,
    Moon,
    Sun,
    Shield
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import './Sidebar.css';

const navigation = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Upload Data', path: '/upload', icon: Upload },
    { name: 'Analytics', path: '/analytics', icon: BarChart3 },
    { name: 'Risk Table', path: '/risk-table', icon: AlertTriangle },
];

const secondaryNav = [
    { name: 'Settings', path: '/settings', icon: Settings },
    { name: 'Help', path: '/help', icon: HelpCircle },
];

export default function Sidebar() {
    const { theme, toggleTheme } = useTheme();

    return (
        <aside className="sidebar">
            {/* Logo */}
            <div className="sidebar-logo">
                <div className="logo-icon">
                    <Shield size={24} />
                </div>
                <span className="logo-text">PowerGuard</span>
            </div>

            {/* Main Navigation */}
            <nav className="sidebar-nav">
                <div className="nav-section">
                    <span className="nav-section-title">Main Menu</span>
                    <ul className="nav-list">
                        {navigation.map((item) => (
                            <li key={item.name}>
                                <NavLink
                                    to={item.path}
                                    className={({ isActive }) =>
                                        `nav-link ${isActive ? 'active' : ''}`
                                    }
                                >
                                    <item.icon size={20} className="nav-icon" />
                                    <span>{item.name}</span>
                                </NavLink>
                            </li>
                        ))}
                    </ul>
                </div>

                <div className="nav-section">
                    <span className="nav-section-title">Support</span>
                    <ul className="nav-list">
                        {secondaryNav.map((item) => (
                            <li key={item.name}>
                                <NavLink
                                    to={item.path}
                                    className={({ isActive }) =>
                                        `nav-link ${isActive ? 'active' : ''}`
                                    }
                                >
                                    <item.icon size={20} className="nav-icon" />
                                    <span>{item.name}</span>
                                </NavLink>
                            </li>
                        ))}
                    </ul>
                </div>
            </nav>

            {/* Theme Toggle */}
            <div className="theme-toggle-container">
                <button
                    className="theme-toggle"
                    onClick={toggleTheme}
                    aria-label="Toggle theme"
                >
                    {theme === 'dark' ? (
                        <>
                            <Sun size={18} />
                            <span>Light Mode</span>
                        </>
                    ) : (
                        <>
                            <Moon size={18} />
                            <span>Dark Mode</span>
                        </>
                    )}
                </button>
            </div>

            {/* Footer */}
            <div className="sidebar-footer">
                <div className="status-indicator">
                    <span className="status-dot"></span>
                    <span className="status-text">System Online</span>
                </div>
                <p className="version">v1.0.0</p>
            </div>
        </aside>
    );
}
