import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import { Music } from 'lucide-react';
import bgPic from '../assets/bgpic1.jpg';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await login(username, password);
            navigate('/welcome');
        } catch (err) {
            setError('Invalid credentials');
        }
    };

    const [isExiting, setIsExiting] = useState(false);

    const handleRegisterClick = (e) => {
        e.preventDefault();
        setIsExiting(true);
        setTimeout(() => {
            navigate('/register');
        }, 500); // Match animation duration
    };

    return (
        <div className={`auth-page page-fade-in ${isExiting ? 'page-fade-out' : ''}`}>
            <div className="auth-left">
                <div className="auth-container glass-panel">
                    <div className="logo">
                        <Music size={48} color="#00e5ff" />
                        <h1>Auralis</h1>
                    </div>
                    <h2>Welcome Back</h2>
                    <p>Sign in to continue your audio mixing journey.</p>

                    {error && <div className="error-message">{error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label>Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <button type="submit" className="btn auth-btn">Login</button>
                    </form>

                    <div className="auth-footer">
                        New to Auralis? <a href="/register" onClick={handleRegisterClick}>Create Account</a>
                    </div>
                </div>
            </div>
            <div className="auth-right">
                <img src={bgPic} alt="Background" />
            </div>
        </div>
    );
};

export default Login;
