import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import { Music } from 'lucide-react';
import bgPic from '../assets/bgpic2.jpg';

const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { register } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await register(username, email, password);
            navigate('/');
        } catch (err) {
            setError('Registration failed. Username or Email may be taken.');
        }
    };

    const [isExiting, setIsExiting] = useState(false);

    const handleLoginClick = (e) => {
        e.preventDefault();
        setIsExiting(true);
        setTimeout(() => {
            navigate('/login');
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
                    <h2>Create Account</h2>
                    <p>Join the next generation of audio mixing.</p>

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
                            <label>Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
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
                        <button type="submit" className="btn auth-btn">Sign Up</button>
                    </form>

                    <div className="auth-footer">
                        Already have an account? <a href="/login" onClick={handleLoginClick}>Login</a>
                    </div>
                </div>
            </div>
            <div className="auth-right">
                <img src={bgPic} alt="Background" />
            </div>
        </div>
    );
};

export default Register;
