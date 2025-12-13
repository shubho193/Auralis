import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, Download, Music } from 'lucide-react';

const ResultWaveform = ({ url }) => {
    const containerRef = useRef(null);
    const wavesurfer = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [duration, setDuration] = useState('0:00');
    const [currentTime, setCurrentTime] = useState('0:00');

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    useEffect(() => {
        if (!containerRef.current) return;

        // Create gradient
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 150);
        gradient.addColorStop(0, '#00e5ff'); // Cyan
        gradient.addColorStop(0.5, '#bd00ff'); // Purple
        gradient.addColorStop(1, '#00e5ff'); // Cyan

        wavesurfer.current = WaveSurfer.create({
            container: containerRef.current,
            waveColor: gradient,
            progressColor: 'rgba(255, 255, 255, 0.3)',
            cursorColor: '#ffffff',
            barWidth: 3,
            barGap: 2,
            barRadius: 3,
            height: 120,
            normalize: true,
            backend: 'WebAudio',
        });

        if (url) {
            wavesurfer.current.load(url);
        }

        wavesurfer.current.on('ready', () => {
            setDuration(formatTime(wavesurfer.current.getDuration()));
        });

        wavesurfer.current.on('audioprocess', () => {
            setCurrentTime(formatTime(wavesurfer.current.getCurrentTime()));
        });

        wavesurfer.current.on('finish', () => setIsPlaying(false));
        wavesurfer.current.on('play', () => setIsPlaying(true));
        wavesurfer.current.on('pause', () => setIsPlaying(false));

        return () => {
            wavesurfer.current.destroy();
        };
    }, [url]);

    const togglePlay = () => {
        if (wavesurfer.current) {
            wavesurfer.current.playPause();
        }
    };

    return (
        <div className="result-waveform-card">
            <div className="result-header">
                <Music size={20} color="#bd00ff" />
                <h3>Final Master Mix</h3>
            </div>

            <div className="waveform-display" ref={containerRef}></div>

            <div className="result-controls">
                <div className="time-display">{currentTime}</div>

                <button
                    className={`play-btn-large ${isPlaying ? 'playing' : ''}`}
                    onClick={togglePlay}
                >
                    {isPlaying ? <Pause size={32} fill="white" /> : <Play size={32} fill="white" className="play-icon" />}
                </button>

                <div className="time-display">{duration}</div>
            </div>

            <a href={url} download className="download-link">
                <Download size={16} /> Download Audio
            </a>
        </div>
    );
};

export default ResultWaveform;
