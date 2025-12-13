import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    const API_URL = 'http://localhost:8000';

    const parseJwt = (token) => {
        try {
            return JSON.parse(atob(token.split('.')[1]));
        } catch (e) {
            return null;
        }
    };

    useEffect(() => {
        if (token) {
            const decoded = parseJwt(token);
            if (decoded) {
                setUser({ username: decoded.sub });
            }
        }
        setLoading(false);
    }, [token]);

    const login = async (username, password) => {
        const res = await axios.post(`${API_URL}/login`, { username, password });
        localStorage.setItem('token', res.data.access_token);
        setToken(res.data.access_token);
        const decoded = parseJwt(res.data.access_token);
        setUser({ username: decoded.sub });
        return true;
    };

    const register = async (username, email, password) => {
        const res = await axios.post(`${API_URL}/register`, { username, email, password });
        localStorage.setItem('token', res.data.access_token);
        setToken(res.data.access_token);
        const decoded = parseJwt(res.data.access_token);
        setUser({ username: decoded.sub });
        return true;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
