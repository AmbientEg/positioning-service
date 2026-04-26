# Positioning Service

A FastAPI-based service for indoor positioning using BLE (Bluetooth Low Energy) RSSI signals and deep learning. This service predicts user locations using a CNN model trained on RSSI fingerprinting data and manages spatial reference points (gridpoints) in a PostgreSQL database.

## Features

- **BLE Positioning**: Uses Bluetooth Low Energy received signal strength indicator (RSSI) data for indoor positioning
- **Deep Learning Model**: CNN-based positioning model (ONNX format) for accurate location prediction
- **REST API**: FastAPI endpoints for coordinate retrieval and gridpoint management
- **Database Integration**: PostgreSQL with SQLAlchemy ORM for storing gridpoint and location data
- **GeoJSON Support**: Import and manage gridpoints from GeoJSON files
- **Async/Await**: Asynchronous database operations for high concurrency
- **Docker Support**: Multi-stage Dockerfile for optimized production deployment
- **Development Tools**: Includes Postman collection for API testing

## Project Structure

```
PositioningService/
├── api/                          # API routes and endpoints
│   └── position_routes.py
├── core/                         # Core configuration
│   └── config.py
├── database/                     # Database setup and connections
│   └── database.py
├── DeepLearningModel/           # ML model files and utilities
│   ├── ble_position_model.h5    # Keras model
│   ├── ble_position_model.onnx  # ONNX model (runtime)
│   ├── converter.py             # Model format conversion
│   ├── loader.py                # Model loading utilities
│   └── preprocessor.py          # Data preprocessing
├── models/                       # SQLAlchemy ORM models
│   └── models.py
├── saved_model/                 # TensorFlow saved model format
├── schemas/                      # Pydantic request/response schemas
│   └── schemas.py
├── services/                     # Business logic
│   ├── cnn_service.py           # CNN prediction service
│   └── position_service.py      # Positioning logic
├── utils/                        # Utility functions
│   ├── db_utils.py
│   └── file_utils.py
├── postman/                      # API testing
│   ├── Positioning Service API.postman_collection.json
│   ├── postman_environment.json
│   └── samples/                  # Sample BLE data
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
└── README.md                     # This file
```

## Requirements

- Python 3.10+
- PostgreSQL 12+
- Docker (optional, for containerized deployment)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd PositioningService
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/positioningDb

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

### 3. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/macOS
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize Database

Ensure PostgreSQL is running and create the database:

```sql
CREATE DATABASE positioning_db;
```

## Usage

### Running Locally

```bash
python main.py
```

The service will start on `http://localhost:8000`

**API Documentation**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running with Docker

```bash
# Build the image
docker build -t positioning-service .

# Run the container
docker run -p 8003:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/positioning_db \
  positioning-service
```

## API Endpoints

### 1. Get Coordinates from Gridpoint

**Endpoint**: `POST /grid/coordinates`

**Request**:
```json
{
  "grid_label": "6"
}
```

**Response**:
```json
{
  "latitude": 40.7128,
  "longitude": 41.0060
}
```

### 2. Import Gridpoints from GeoJSON

**Endpoint**: `POST /grid/import`

**Request**: Form data with GeoJSON file

**Description**: Uploads a GeoJSON file containing gridpoints to the database

### 3. Predict Position from RSSI Data

**Endpoint**: `POST /predict`

**Request**: Form data with 5 CSV files (one for each beacon)

**File Format**:
- `beacon_1.csv`: RSSI readings from beacon 1
- `beacon_2.csv`: RSSI readings from beacon 2
- `beacon_3.csv`: RSSI readings from beacon 3
- `beacon_4.csv`: RSSI readings from beacon 4
- `beacon_5.csv`: RSSI readings from beacon 5

Each CSV file should contain RSSI values in a single column.

**Response**:
```json
{
  "predicted_gridpoint": "60",
}
```

**Description**: Uploads 5 beacon CSV files, processes the RSSI data through the CNN model, and returns the predicted gridpoint with confidence score

## Database Models

### GridPoint
- `id`: Unique identifier
- `grid_label`: Label/name of the gridpoint (e.g., "1", "2")
- `latitude`: Geographic latitude coordinate
- `longitude`: Geographic longitude coordinate
- `building_id`: Reference to building
- `floor_id`: Reference to floor level

### Building
- `id`: Unique identifier
- `name`: Building name
- `description`: Building description

### Floor
- `id`: Unique identifier
- `building_id`: Reference to building
- `floor_number`: Floor level number

## Services

### PositionService
Handles core positioning logic:
- Coordinate retrieval from gridpoints
- GeoJSON import and validation
- Spatial data management

### CNNService
Manages CNN model inference:
- RSSI data normalization
- Prediction using ONNX model
- Majority voting for multiple window predictions

## Deep Learning Model

<img width="1039" height="327" alt="gridpoints" src="https://github.com/user-attachments/assets/e62138fd-8043-493d-bbbe-3688bda07a7b" />


**Model Type**: Convolutional Neural Network (CNN)

**Input**: RSSI matrix (5 beacons × 20 time windows × 1 channel) = shape (5, 20, 1)

**Output**: Predicted gridpoint label (102 classes)

**Training Data**: 102 gridpoints with 1-3 meter accuracy

**Files**:
- `ble_position_model.h5`: Keras/TensorFlow model
- `ble_position_model.onnx`: ONNX runtime model
- `saved_model/`: TensorFlow saved model format

### CNN Architecture

<img width="7170" height="2970" alt="CNN_Architecture_Visual(1)" src="https://github.com/user-attachments/assets/b95172cb-d78b-4a24-8455-c6718305a415" />

The model uses a sequential architecture optimized for RSSI-based positioning:

```
Input Layer (5, 20, 1)
├── Conv2D(32, kernel=3×3, activation=relu, padding=same)
├── BatchNormalization()
├── Conv2D(64, kernel=3×3, activation=relu, padding=same)
├── BatchNormalization()
├── MaxPooling2D(2×2)
├── Dropout(0.25)
├── Conv2D(128, kernel=3×3, activation=relu, padding=same)
├── BatchNormalization()
├── MaxPooling2D(2×2)
├── Dropout(0.25)
├── Flatten()
├── Dense(256, activation=relu)
├── Dropout(0.4)
└── Dense(102, activation=softmax)
```

**Architecture Details**:

| Layer | Type | Units/Filters | Kernel | Activation | Notes |
|-------|------|---------------|--------|------------|-------|
| 1 | Input | - | - | - | Shape: (5, 20, 1) |
| 2 | Conv2D | 32 | 3×3 | ReLU | Padding: same |
| 3 | BatchNorm | - | - | - | Normalizes activations |
| 4 | Conv2D | 64 | 3×3 | ReLU | Padding: same |
| 5 | BatchNorm | - | - | - | Normalizes activations |
| 6 | MaxPooling2D | - | 2×2 | - | Reduces spatial dimensions |
| 7 | Dropout | - | - | - | Rate: 0.25 |
| 8 | Conv2D | 128 | 3×3 | ReLU | Padding: same |
| 9 | BatchNorm | - | - | - | Normalizes activations |
| 10 | MaxPooling2D | - | 2×2 | - | Reduces spatial dimensions |
| 11 | Dropout | - | - | - | Rate: 0.25 |
| 12 | Flatten | - | - | - | Converts to 1D |
| 13 | Dense | 256 | - | ReLU | Fully connected |
| 14 | Dropout | - | - | - | Rate: 0.4 |
| 15 | Output | 102 | - | Softmax | 102 gridpoint classes |

**Model Compilation**:
- **Optimizer**: Adam
- **Loss Function**: Sparse Categorical Crossentropy
- **Metrics**: Accuracy

**Performance**:
- **Coverage**: 102 gridpoints across the building
- **Accuracy**: 1-3 meter localization accuracy
- **Input Rate**: 20-sample sliding windows for temporal context
- **Inference**: ONNX runtime for optimized predictions

**Preprocessing**:
- Normalization using mean and standard deviation from training data
- Sliding window approach for temporal features (20 samples per window)
- Majority voting for robust predictions across multiple windows

## Testing

Use the included Postman collection:

1. Import `postman/Positioning Service API.postman_collection.json` into Postman
2. Configure environment using `postman/postman_environment.json`
3. Use sample BLE data from `postman/samples/` for testing

Sample RSSI data files:
- `beacon-1.csv` through `beacon-5.csv`: Individual beacon RSSI readings
- `gridpoints.geojson`: Sample gridpoint locations

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string (required) |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PYTHONUNBUFFERED` | `1` | Python output buffering |

### Default Building Configuration

The service automatically creates a default building and floor:
- **Building**: "Special Building"
- **Description**: "This is the special building of software engineering major in my university"
- **Default Floor**: Floor 3

## Logging

Logs are configured with timestamps, log level, logger name, and message:

```
2024-04-26 10:30:45,123 INFO positioning-service Starting application...
```

## Performance Considerations

- **Async Database Operations**: Leverages SQLAlchemy async for concurrent requests
- **ONNX Runtime**: Uses ONNX for optimized model inference
- **Model Caching**: ML model loaded once at startup
- **Connection Pooling**: PostgreSQL connection pooling for efficient database access

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running
- Verify `DATABASE_URL` format: `postgresql+asyncpg://user:password@host:port/dbname`
- Check firewall rules and network connectivity

### Model Loading Errors

- Verify ONNX model file exists: `DeepLearningModel/ble_position_model.onnx`
- Ensure ONNX runtime is installed: `pip install onnxruntime`

### API Response Errors

- Check log level: Set `LOG_LEVEL=DEBUG` for detailed error information
- Validate request schemas against Swagger documentation
- Use Postman collection for template requests

## Dependencies

Key dependencies (see `requirements.txt` for complete list):

| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.136.0 | Web framework |
| Uvicorn | 0.44.0 | ASGI server |
| SQLAlchemy | 2.0.49 | ORM |
| asyncpg | 0.31.0 | PostgreSQL driver |
| Pydantic | 2.13.1 | Data validation |
| NumPy | 1.26.4 | Numerical computing |
| ONNX Runtime | 1.18.1 | ML model inference |

## Version History

### v1.0.0
- Initial release
- BLE positioning with CNN model
- GeoJSON gridpoint management
- REST API endpoints
- PostgreSQL integration
