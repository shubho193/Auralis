import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { X, Volume2, VolumeX, Play, Pause } from 'lucide-react';

const StemRow = ({ file, url, name, onDelete, onUpdate }) => {
    const containerRef = useRef(null);
    const wavesurfer = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [gain, setGain] = useState(0); // dB
    const [pan, setPan] = useState(0); // -1 to 1

    useEffect(() => {
        if (!containerRef.current) return;

        wavesurfer.current = WaveSurfer.create({
            container: containerRef.current,
            waveColor: '#4a9eff',
            progressColor: '#00e5ff',
            cursorColor: '#ffffff',
            barWidth: 2,
            barGap: 1,
            barRadius: 2,
            height: 60,
            normalize: true,
            backend: 'WebAudio',
        });

        if (url) {
            wavesurfer.current.load(url);
        }

        wavesurfer.current.on('finish', () => setIsPlaying(false));
        wavesurfer.current.on('play', () => setIsPlaying(true));
        wavesurfer.current.on('pause', () => setIsPlaying(false));

        return () => {
            wavesurfer.current.destroy();
        };
    }, [url]);

    // Sync props to state
    useEffect(() => {
        if (file && file.gain !== undefined) {
            setGain(file.gain);
            if (wavesurfer.current) {
                wavesurfer.current.setVolume(Math.pow(10, file.gain / 20));
            }
        }
        if (file && file.pan !== undefined) {
            setPan(file.pan);
        }
    }, [file]);

    // Handle Gain Change
    const handleGainChange = (e) => {
        const newGain = parseFloat(e.target.value);
        setGain(newGain);
        if (wavesurfer.current) {
            wavesurfer.current.setVolume(Math.pow(10, newGain / 20)); // Convert dB to linear
        }
        onUpdate(name, { gain: newGain, pan });
    };

    // Handle Pan Change
    const handlePanChange = (e) => {
        const newPan = parseFloat(e.target.value);
        setPan(newPan);
        // Note: WaveSurfer doesn't natively support panning easily without plugin, 
        // but we track it for the backend mix.
        onUpdate(name, { gain, pan: newPan });
    };

    const toggleMute = () => {
        const newMuted = !isMuted;
        setIsMuted(newMuted);
        wavesurfer.current.setMuted(newMuted);
    };

    const togglePlay = () => {
        if (wavesurfer.current) {
            wavesurfer.current.playPause();
        }
    };

    return (
        <div className="stem-row">
            <div className="stem-info">
                <span className="stem-name">{name}</span>
                <button className="icon-btn delete-btn" onClick={() => onDelete(name)}>
                    <X size={16} />
                </button>
            </div>

            <div className="waveform-container" ref={containerRef}></div>

            <div className="stem-controls">
                <div className="control-group">
                    <button
                        className={`icon-btn ${isPlaying ? 'active' : ''}`}
                        onClick={togglePlay}
                        title={isPlaying ? "Pause" : "Play"}
                    >
                        {isPlaying ? <Pause size={18} /> : <Play size={18} />}
                    </button>
                    <button
                        className={`icon-btn ${isMuted ? 'active' : ''}`}
                        onClick={toggleMute}
                        title="Mute"
                    >
                        {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
                    </button>
                </div>

                <div className="control-group slider-group">
                    <div className="slider-label">
                        <label>Gain</label>
                        <span className="value-display">{gain.toFixed(1)}dB</span>
                    </div>
                    <input
                        type="range"
                        min="-6"
                        max="6"
                        step="0.1"
                        value={gain}
                        onChange={handleGainChange}
                    />
                </div>

                <div className="control-group slider-group">
                    <div className="slider-label">
                        <label>Pan</label>
                        <span className="value-display">{pan}</span>
                    </div>
                    <input
                        type="range"
                        min="-1"
                        max="1"
                        step="0.1"
                        value={pan}
                        onChange={handlePanChange}
                    />
                </div>
            </div>
        </div>
    );
};

export default StemRow;
