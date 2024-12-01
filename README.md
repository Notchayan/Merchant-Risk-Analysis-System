
# Merchant Risk Analysis System

## Live System Links
- **API Backend**: [https://winter-assignment.onrender.com/](https://winter-assignment.onrender.com/)
- **API Documentation**: [https://winter-assignment.onrender.com/docs](https://winter-assignment.onrender.com/docs)
- **Data Generator Documentation**: [docs/data_generator.md](docs/data_generator.md)
- **Risk Metrics Documentation**: [docs/risk_metrics.md](docs/risk_metrics.md)
- **Database Schemas & Models Documentation**: [docs/database_schemas_models.md](docs/database_schemas_models.md)
- **Database**: [PostgreSQL on Render](https://render.com/)

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Configuration](#configuration)
5. [Usage](#usage)
   - [API Endpoints](#api-endpoints)
6. [Documentation](#documentation)
7. [Database](#database)
8. [Testing](#testing)
9. [Deployment](#deployment)
10. [Contributing](#contributing)
11. [Support](#support)
12. [License](#license)
13. [Acknowledgments](#acknowledgments)

## Overview

The **Merchant Risk Analysis System** is an intelligent platform designed to analyze merchant transactions, calculate risk metrics, generate transaction summaries, and detect unusual patterns in merchant behavior. This system assists financial institutions and merchants in identifying potential fraud, monitoring transaction patterns, and maintaining compliance with regulatory standards.

## Features

- **Risk Metrics Calculation**: Computes various risk scores (e.g., late-night transactions, sudden spikes) to assess the overall risk associated with merchant activities.
- **Transaction Summarization**: Aggregates transaction data to provide daily summaries, including total volume, average amounts, and unique customer counts.
- **Timeline Event Detection**: Identifies and flags unusual activities such as round amount transactions, late-night transactions, and sudden spikes in transaction volume.
- **Robust API**: Provides RESTful API endpoints for initiating risk analysis, transaction summarization, and timeline event generation.
- **Database Integration**: Stores all computed metrics, summaries, and events in a relational database for easy access and reporting.
- **Comprehensive Logging**: Implements detailed logging for monitoring, debugging, and auditing purposes.

## Architecture

The system is built using **FastAPI** for the API layer, **SQLAlchemy** for ORM and database interactions, and **Pandas** for data aggregation. It follows a modular architecture, separating concerns into different components:

- **Main Application (`main.py`)**: Defines API endpoints and orchestrates interactions between different modules.
- **Risk Metrics (`risk_metrics.py`)**: Contains logic for calculating various risk scores.
- **Transaction Summarization (`transaction_summary.py`)**: Handles the aggregation and summarization of transaction data.
- **Timeline Events (`timeline_events.py`)**: Detects and manages unusual transaction events.
- **Models (`models.py`)**: Defines the database schema using SQLAlchemy models.
- **Generator (`data_generator.py`)**: Includes utilities for generating synthetic transaction data for testing purposes.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **PostgreSQL** (or any other SQL-compatible database)
- **Virtual Environment Tool** (`venv`, `conda`, etc.)
- **Git**

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/merchant-risk-analysis.git
   cd merchant-risk-analysis
   ```

2. **Create a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**

   Ensure you have PostgreSQL installed and running. Create a new database:

   ```bash
   psql -U postgres
   CREATE DATABASE merchant_risk_db;
   \q
   ```

5. **Configure Environment Variables**

   Create a `.env` file in the project root and add the following:

   ```env
   DATABASE_URL=postgresql://username:password@localhost/merchant_risk_db
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   ```

6. **Run Database Migrations**

   ```bash
   alembic upgrade head
   ```

### Configuration

Ensure all configurations such as database URLs, logging levels, and other settings are correctly set in the `.env` file or your environment.

## Usage

### API Endpoints

The system provides several API endpoints to interact with the risk analysis features. Below are the primary endpoints:

- **Calculate Risk Metrics**
  - **Endpoint**: `POST /calculate-risk-metrics/{merchant_id}`
  - **Description**: Calculates risk metrics for a given merchant based on their transactions over a specified lookback period.

- **Generate Transaction Summary**
  - **Endpoint**: `GET /merchant/{merchant_id}/transaction-summaries`
  - **Description**: Retrieves daily summaries of transactions for a specific merchant.

- **Generate Timeline Events**
  - **Endpoint**: `GET /merchant/{merchant_id}/timeline-events`
  - **Description**: Retrieves detected timeline events for a specific merchant.

- **Retrieve Data**
  - **Endpoints**:
    - `GET /merchants/`
    - `GET /transactions/`
    - `GET /merchant/{merchant_id}/transactions`
  - **Description**: Fetches merchants, transactions, and transactions related to a specific merchant.

For detailed API usage, refer to the [API Documentation](https://winter-assignment.onrender.com/docs).

## Documentation

Comprehensive documentation is available to help you understand and interact with the system:

- [Risk Metrics Documentation](/documentation/risk_metrics)
- [Data Generator Documentation](/documentation/data_generator)
- [Database Schemas & Models](/documentation/database_schemas_models)
- [Testing Guide](/docs/testing.md)

## Database

The system uses a PostgreSQL database hosted on Render. Key configurations include:

- **Connection Pooling**: Pool size of 5 with a maximum overflow of 10.
- **Connection Timeout**: 30 seconds.
- **Health Checks**: Enabled to ensure connection stability.
- **URL Conversion**: Automatically converts `postgres://` to `postgresql://` for compatibility.

### Live Database Connection String

```plaintext
postgresql://chayan_user:lt5JCxzG0BPWKPOOKvS5ReOZ8FYqVlrE@dpg-ct5fll3tq21c7398l28g-a.oregon-postgres.render.com/chayan
```

*Ensure to keep your database credentials secure and do not expose them in public repositories.*

## Testing

To ensure the system works as expected, follow these testing steps:

1. **Run Unit Tests**

   ```bash
   pytest tests/
   ```

2. **Test API Endpoints**

   Use tools like **Postman** or **cURL** to interact with the API endpoints and verify responses.

3. **Generate Sample Data**

   Utilize the provided data generator to create synthetic data for testing purposes.

   ```bash
   POST /generate-and-store-data/
   ```

Refer to the [Testing Documentation](https://github.com/yourusername/merchant-risk-analysis/blob/main/docs/testing.md) for more detailed information.

## Deployment

The system is deployed on Render with the following configuration:

```yaml
services:
  - type: web
    name: fraud-detection-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: fraud-detection-db
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.12.0

databases:
  - name: fraud-detection-db
    databaseName: fraud_detection
    plan: free
```

### Steps for Deployment

1. **Push to Repository**

   Ensure all changes are committed and pushed to your Git repository.

2. **Connect to Render**

   Link your repository to Render and configure the `render.yaml` as shown above.

3. **Monitor Deployment**

   Use the Render dashboard to monitor build logs, service status, and performance metrics.

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository**

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -m "Add Your Feature"
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Open a Pull Request**

Please ensure your code follows the project's coding standards and includes relevant tests.


## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM for database interactions
- [Render](https://render.com/) - Hosting platform
- [PostgreSQL](https://www.postgresql.org/) - Database system
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management
- [Pytest](https://pytest.org/) - Testing framework
