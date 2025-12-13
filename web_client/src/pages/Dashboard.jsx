import React, { useState, useRef, useEffect, useContext } from 'react';
import StemRow from '../components/StemRow';
import { Link } from 'react-router-dom';
import ResultWaveform from '../components/ResultWaveform';
import { Upload, Play, Download, Music, Terminal, LogOut } from 'lucide-react';
import AuthContext from '../context/AuthContext';
import '../App.css';

const API_URL = 'http://localhost:8000';

function Dashboard() {
    const { user, logout } = useContext(AuthContext);
    const [stems, setStems] = useState({});
    const [isMixing, setIsMixing] = useState(false);
    const [mixUrl, setMixUrl] = useState(null);
    const [autoGain, setAutoGain] = useState(false);
    const [useCNN, setUseCNN] = useState(false);
    const [logs, setLogs] = useState("");
    const logsEndRef = useRef(null);

    const scrollToBottom = () => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [logs]);

    const handleFileUpload = async (event) => {
        const files = event.target.files;
        if (!files) return;

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch(`${API_URL}/upload`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                });

                if (!response.ok) throw new Error('Upload failed');

                const data = await response.json();

                const name = file.name.split('.')[0];
                setStems(prev => ({
                    ...prev,
                    [name]: {
                        filename: data.filename,
                        url: `${API_URL}${data.url}`,
                        gain: 0,
                        pan: 0
                    }
                }));
            } catch (error) {
                console.error("Upload failed", error);
                alert("Failed to upload file");
            }
        }
    };

    const handleUpdateStem = (name, settings) => {
        setStems(prev => ({
            ...prev,
            [name]: { ...prev[name], ...settings }
        }));
    };

    const handleDeleteStem = (name) => {
        const newStems = { ...stems };
        delete newStems[name];
        setStems(newStems);
    };

    const [progress, setProgress] = useState(0);

    const handleMix = async () => {
        setIsMixing(true);
        setMixUrl(null);
        setLogs("Initializing mix...\n");
        setProgress(0);

        // Simulate progress
        const progressInterval = setInterval(() => {
            setProgress(prev => {
                if (prev >= 90) return prev;
                return prev + 5;
            });
        }, 500);

        const mixRequest = {
            stems: {},
            gains: {},
            pans: {},
            auto_gain: autoGain,
            use_cnn: useCNN
        };

        Object.entries(stems).forEach(([name, data]) => {
            mixRequest.stems[name] = data.filename;
            mixRequest.gains[name] = data.gain;
            mixRequest.pans[name] = data.pan;
        });

        try {
            const response = await fetch(`${API_URL}/mix`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify(mixRequest)
            });

            if (!response.ok) throw new Error('Mix failed');

            clearInterval(progressInterval);
            setProgress(100);

            const data = await response.json();
            const timestamp = new Date().getTime();
            setMixUrl(`${API_URL}${data.url}?t=${timestamp}`);
            setLogs(data.logs || "Mix complete (no logs returned).");

            // Update stems with optimal gains ONLY if auto-gain was used
            if (autoGain && data.gains) {
                setStems(prev => {
                    const newStems = { ...prev };
                    Object.entries(data.gains).forEach(([name, gain]) => {
                        if (newStems[name]) {
                            newStems[name] = { ...newStems[name], gain: gain };
                        }
                    });
                    return newStems;
                });
            }
        } catch (error) {
            clearInterval(progressInterval);
            setProgress(0);
            console.error("Mixing failed", error);
            setLogs(prev => prev + "\nMixing failed: " + error.message);
            alert("Mixing failed");
        } finally {
            setIsMixing(false);
        }
    };

    return (
        <div className="app-container page-fade-in">
            <header className="app-header">
                <div className="header-left">
                    <div className="logo">
                        <Music size={32} color="#00e5ff" />
                        <h1>Auralis</h1>
                    </div>
                </div>

                <div className="header-center">
                    <div className="upload-btn-wrapper-center">
                        <button className="btn primary-btn add-stems-btn-center">
                            <Upload size={40} />
                        </button>
                        <input type="file" multiple accept="audio/*" onChange={handleFileUpload} />
                        <span className="upload-label">Import Stems</span>
                    </div>
                </div>

                <div className="header-right">
                    <span className="user-welcome">Welcome, {user?.username}</span>
                    <Link to="/history" className="btn nav-btn" title="History">
                        <Terminal size={20} />
                        <span>History</span>
                    </Link>
                    <button onClick={logout} className="btn nav-btn logout-btn" title="Logout">
                        <LogOut size={20} />
                        <span>Logout</span>
                    </button>
                </div>
            </header>

            <main className="main-content">
                <div className="stems-list">
                    {Object.keys(stems).length === 0 ? (
                        <div className="empty-state">
                            <p>No stems added. Upload audio files to start mixing.</p>
                        </div>
                    ) : (
                        Object.entries(stems).map(([name, data]) => (
                            <StemRow
                                key={name}
                                name={name}
                                url={data.url}
                                file={data} // Pass the full data object including gain/pan
                                onDelete={handleDeleteStem}
                                onUpdate={handleUpdateStem}
                            />
                        ))
                    )}
                </div>

                <div className="mix-controls">
                    <div className="mix-actions-wrapper">
                        <div className="mix-action-column">
                            <button
                                className={`btn ai-btn ${autoGain ? 'active' : ''}`}
                                onClick={() => {
                                    const newState = !autoGain;
                                    setAutoGain(newState);
                                    setUseCNN(newState); // Enable CNN by default when AI is on
                                }}
                            >
                                {autoGain ? <>CNN Based AI Auto Gain <span className="status-highlight">ACTIVE</span></> : 'Activate CNN Based AI Auto Gain'}
                            </button>
                        </div>

                        <div className="mix-action-column">
                            <button
                                className="btn mix-btn"
                                onClick={handleMix}
                                disabled={isMixing || Object.keys(stems).length === 0}
                            >
                                {isMixing ? 'Processing...' : 'Mix Audio'}
                            </button>
                        </div>
                    </div>

                    {(isMixing || mixUrl) && (
                        <div className="progress-container">
                            <div className="progress-bar" style={{ width: `${progress}%` }}></div>
                        </div>
                    )}

                    {logs && (
                        <div className="logs-container">
                            <div className="logs-header">
                                <Terminal size={16} />
                                <span>Processing Logs</span>
                            </div>
                            <pre className="logs-content">
                                {logs}
                                <div ref={logsEndRef} />
                            </pre>
                        </div>
                    )}

                    {mixUrl && (
                        <ResultWaveform url={mixUrl} />
                    )}
                </div>
            </main>
        </div>
    );
}

export default Dashboard;
