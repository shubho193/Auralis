import React, { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import './Welcome.css';

const Welcome = () => {
    const { user } = useContext(AuthContext);
    const navigate = useNavigate();
    const [fadeState, setFadeState] = useState(''); // Start invisible

    useEffect(() => {
        // Trigger fade in after mount
        requestAnimationFrame(() => {
            setFadeState('fade-in');
        });

        // After 2.5 seconds, start fading out
        const timer = setTimeout(() => {
            setFadeState('fade-out');
        }, 2500);

        // After fade out completes (e.g. 1s transition), navigate
        const navTimer = setTimeout(() => {
            navigate('/');
        }, 3500); // 2500 + 1000

        return () => {
            clearTimeout(timer);
            clearTimeout(navTimer);
        };
    }, [navigate]);

    return (
        <div className={`welcome-page ${fadeState}`}>
            <div className="welcome-container">
                <div className="welcome-sub">Welcome,</div>
                <div className="welcome-text">
                    {user ? user.username : 'User'}
                </div>
            </div>
        </div>
    );
};

export default Welcome;
