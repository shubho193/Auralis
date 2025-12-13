import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import { Clock, Download, FileText, ArrowLeft, Play, Trash2 } from 'lucide-react';
import ResultWaveform from '../components/ResultWaveform';
import './History.css';
import '../App.css';

const API_URL = 'http://localhost:8000';

const History = () => {
    const { token, logout } = useContext(AuthContext);
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedLogs, setExpandedLogs] = useState({});

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await fetch(`${API_URL}/history`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (response.ok) {
                    const data = await response.json();
                    setHistory(data);
                }
            } catch (error) {
                console.error("Failed to fetch history", error);
            } finally {
                setLoading(false);
            }
        };

        if (token) {
            fetchHistory();
        }
    }, [token]);

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this mix log?")) return;

        try {
            const response = await fetch(`${API_URL}/history/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                setHistory(prev => prev.filter(item => item.id !== id));
            } else {
                alert("Failed to delete history item");
            }
        } catch (error) {
            console.error("Error deleting item:", error);
            alert("Error deleting item");
        }
    };

    const toggleLogs = (id) => {
        setExpandedLogs(prev => ({
            ...prev,
            [id]: !prev[id]
        }));
    };

    const formatDate = (isoString) => {
        return new Date(isoString).toLocaleString();
    };

    return (
        <div className="history-page page-fade-in">
            <div className="history-header">
                <div>
                    <Link to="/" className="back-btn">
                        <ArrowLeft size={20} /> Back to Mixer
                    </Link>
                    <h1>Mix History</h1>
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', color: 'var(--text-dim)' }}>Loading history...</div>
            ) : history.length === 0 ? (
                <div className="empty-state">
                    <Clock size={48} style={{ marginBottom: 20, opacity: 0.5 }} />
                    <p>No mix history found. Start mixing to see your logs here!</p>
                    <Link to="/" className="btn auth-btn" style={{ maxWidth: 200, margin: '20px auto', textDecoration: 'none' }}>Go to Mixer</Link>
                </div>
            ) : (
                <div className="history-list">
                    {history.map(item => (
                        <div key={item.id} className="history-item">
                            <div className="history-item-header">
                                <div>
                                    <div className="history-date">{formatDate(item.timestamp)}</div>
                                    <div className="history-summary">{item.settings_summary}</div>
                                </div>
                                <div className="history-actions">
                                    <button
                                        className="btn secondary-btn btn-small"
                                        onClick={() => toggleLogs(item.id)}
                                        title="View Logs"
                                        style={{ background: 'rgba(255,255,255,0.1)', color: '#fff' }}
                                    >
                                        <FileText size={18} /> {expandedLogs[item.id] ? 'Hide Logs' : 'View Logs'}
                                    </button>
                                    <button
                                        className="btn btn-small delete-history-btn"
                                        onClick={() => handleDelete(item.id)}
                                        title="Delete Log"
                                    >
                                        <Trash2 size={18} /> Delete
                                    </button>
                                </div>
                            </div>

                            {expandedLogs[item.id] && (
                                <div className="log-viewer">
                                    {item.logs}
                                </div>
                            )}

                            <div style={{ marginTop: '20px' }}>
                                <ResultWaveform url={`${API_URL}${item.output_url}`} />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default History;
