# Audio Stem Mixer

A Python program that takes multiple audio stems (drums, vocals, synth, bass, etc.) and mixes them together with adjustable parameters like gain, panning, and EQ. Now features a modern Web Interface with Authentication!

## Features

- **Web Interface**: Modern React-based UI with login, registration, and dashboard.
- **Individual Gain Control**: Adjust volume for each stem in decibels.
- **AI-Powered Auto-Gain**: CNN-based automatic gain prediction for optimal balance.
- **Panning**: Control left/right stereo position for each stem.
- **EQ Filtering**: Apply high-pass and low-pass filters to individual stems.
- **Automatic Sample Rate Conversion**: Handles different sample rates automatically.
- **Mono to Stereo Conversion**: Converts mono audio to stereo automatically.
- **Length Normalization**: Automatically handles stems of different lengths.
- **Output Normalization**: Prevents clipping in the final mix.

## Installation

### Prerequisites

- Python 3.8+
- Node.js & npm (for Web Client)

### 1. Backend Setup

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Frontend Setup

Navigate to the `web_client` directory and install Node.js dependencies:

```bash
cd web_client
npm install
```

## Running the Application

To interpret the full application, you need to run both the backend server and the frontend client.

### 1. Start Support Backend

From the root directory:

```bash
uvicorn web_server.main:app --reload
```
The API will run at `http://localhost:8000`.

### 2. Start Web Client

Open a new terminal, navigate to `web_client`, and start the dev server:

```bash
cd web_client
npm run dev
```
The web application will run at `http://localhost:5173`.

## Usages

### Web Interface

1.  **Register/Login**: Create an account to access the mixer.
2.  **Dashboard**:
    *   **Upload Stems**: Add your audio files (wav, mp3, etc.).
    *   **Adjust Controls**: Set gain and panning for each stem.
    *   **AI Auto-Gain**: Toggle the AI feature to automatically balance levels.
    *   **Mix**: Click "Mix Audio" to process.
    *   **Download**: Listen to and download the final mix.

### CLI & Python API

You can still use the command line tools and Python API as before.

#### Quick Start

```bash
python quick_start.py
```

#### CLI Command

```bash
python audio_mixer.py <stems_directory> [output_file]
```

## Structure

```
Audio Processor/
├── audio_mixer.py          # Core mixer logic
├── web_server/             # FastAPI Backend
│   ├── main.py             # API endpoints
│   ├── models.py           # DB models
│   ├── auth.py             # Auth logic
│   └── ...
├── web_client/             # React Frontend
│   ├── src/
│   │   ├── components/     # UI Components
│   │   ├── pages/          # Login, Dashboard, etc.
│   │   └── context/        # Auth Context
│   └── ...
├── stems/                  # Default stems directory
└── ... (other scripts)
```

## License

This project is open source and available for educational and personal use.
