# IoT Motion Analysis – Raspberry Pi & Python Backend

An IoT-based motion data collection and analysis system using a Raspberry Pi, MQTT, Python, and machine learning.

The project demonstrates an end-to-end IoT pipeline, from edge-device data generation and transmission to backend processing, persistent storage, and AI-based motion classification.

## Project Overview

The goal of this project is to build a modular IoT system capable of collecting, processing, storing, and analyzing motion data.

A Raspberry Pi 4 acts as an edge device, generating simulated three-axis motion data and transmitting it to a backend via MQTT.

The backend receives the data and will eventually store it in a PostgreSQL database, expose it through a FastAPI REST API, and use machine learning to classify different motion patterns.

The project is designed as a practical learning environment for IoT communication, backend development, database integration, and machine learning.

## Technology Stack

| Component | Technology |
|---|---|
| Edge Device | Raspberry Pi 4 Model B |
| Programming Language | Python |
| Communication | MQTT (Paho MQTT) |
| Backend API | FastAPI (planned) |
| Database | PostgreSQL (planned) |
| Machine Learning | Python-based ML model (planned) |
| Deployment | Linux VM / Docker (planned) |
| Version Control | Git & GitHub |

## System Architecture

The planned architecture follows a modular edge-to-backend approach.

```text
┌───────────────────────────┐
│      Raspberry Pi 4       │
│                           │
│   Motion Data Simulation  │
│   Future: IMU Sensor      │
└─────────────┬─────────────┘
              │
              │ MQTT Publish
              ▼
┌───────────────────────────┐
│        MQTT Broker        │
└─────────────┬─────────────┘
              │
              │ MQTT Subscribe
              ▼
┌───────────────────────────┐
│       Python Backend      │
│                           │
│   MQTT Subscriber         │
│   Data Validation         │
│   Data Processing         │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       PostgreSQL          │
│       (Planned)           │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│    FastAPI / ML Model     │
│         (Planned)         │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│   Data Visualization      │
│         (Planned)         │
└───────────────────────────┘
```

## Motion Data Simulation

Until a physical motion sensor is integrated, the Raspberry Pi generates simulated motion data.

Three motion patterns are supported:

**1. Resting (`resting`)**

Simulates a stationary device with small random fluctuations around zero.

**2. Walking (`walking`)**

Simulates continuous movement with a directional component and added noise.

**3. Shaking (`shaking`)**

Simulates irregular movement with randomized acceleration values along all three axes.

The simulation continuously cycles through these motion patterns and publishes measurements via MQTT.

### Example MQTT Message

```json
{
  "device_id": "raspberry01",
  "timestamp": "2026-11-20T13:11:21.035327+00:00",
  "x": 2.4495,
  "y": -0.1633,
  "z": 3.8451,
  "mode": "shaking"
}
```

Each message contains:

- `device_id`: Unique identifier of the edge device
- `timestamp`: Measurement timestamp in UTC
- `x`, `y`, `z`: Simulated three-axis motion values
- `mode`: Current simulated motion pattern

The simulation labels will later serve as ground-truth data for training and evaluating motion classification models.

## Current Implementation

The following components are implemented:

- Raspberry Pi 4 configured for headless operation via SSH
- Python-based motion data simulation
- Three simulated motion patterns with noise and randomness
- MQTT publisher running on the edge device
- MQTT subscriber running in the backend
- JSON-based data transmission
- Configurable MQTT connection settings using environment variables
- MQTT connection and subscription logging

The MQTT communication between the Raspberry Pi and the backend has been successfully tested.

## Getting Started

### Prerequisites

- Python 3
- Running MQTT broker
- Raspberry Pi or another Linux-compatible device
- Network connectivity between publisher, broker, and subscriber

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Core dependencies include:

```text
paho-mqtt
python-dotenv
numpy
```

Additional dependencies will be introduced as the backend and machine learning components are implemented.

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```dotenv
MQTT_HOST=<broker-ip-address>
MQTT_PORT=1883
MQTT_DEVICE_ID=raspberry01
```

Replace `<broker-ip-address>` with the IP address or hostname of your MQTT broker.

Do not commit the `.env` file to Git.

### 5. Start MQTT Communication

Ensure that the MQTT broker is running and accessible.

Start the backend MQTT subscriber and the Raspberry Pi publisher using their respective Python entry points.

The publisher continuously generates and transmits motion data, while the subscriber receives and processes incoming MQTT messages.

## Development Roadmap

### Phase 1 – Edge Device & MQTT

- [x] Configure Raspberry Pi for remote development
- [x] Implement simulated motion data
- [x] Set up MQTT communication
- [x] Implement Python MQTT subscriber
- [x] Configure environment variables

### Phase 2 – Backend & Database

- [ ] Set up PostgreSQL
- [ ] Design database schema for sensor measurements
- [ ] Implement persistent data storage
- [ ] Integrate FastAPI
- [ ] Implement REST API endpoints
- [ ] Add data validation and error handling

### Phase 3 – Machine Learning

- [ ] Collect labeled motion datasets
- [ ] Preprocess and normalize sensor data
- [ ] Train a motion classification model
- [ ] Evaluate model performance
- [ ] Integrate inference into the backend
- [ ] Compare predicted and actual motion states

### Phase 4 – Visualization & Deployment

- [ ] Implement data visualization
- [ ] Display historical sensor measurements
- [ ] Visualize predicted motion classes
- [ ] Containerize backend services using Docker
- [ ] Deploy services to a Linux VM
- [ ] Add automated tests and CI/CD

### Phase 5 – Physical Sensor Integration

- [ ] Connect an IMU sensor to the Raspberry Pi
- [ ] Replace simulated measurements with real sensor data
- [ ] Evaluate model performance on physical measurements

## Project Goals

This project focuses on developing practical experience in:

- **IoT Systems:** Edge-to-server communication using MQTT
- **Backend Development:** Building modular Python services and REST APIs
- **Database Integration:** Managing time-series sensor data with PostgreSQL
- **Machine Learning:** Training and deploying models for motion classification
- **Linux & Deployment:** Running distributed services on Linux systems
- **Software Engineering:** Version control, testing, modular architecture, and CI/CD

## Project Status

**Work in Progress**

The current development focus is on backend integration and persistent storage of incoming MQTT measurements.

Machine learning, visualization, and deployment features are planned for subsequent development phases.

## License

License to be determined.