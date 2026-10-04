# Flight Service Serverless

A serverless Python microservice built on AWS Lambda and Amazon DynamoDB for managing flights and passenger reservations.

---

## 🛠️️ Tech Stack & Requirements

* **Language**: Python (3.15+)
* **Database**: Amazon DynamoDB
* **AWS SDK**: Boto3
* **Editor/IDE**: Visual Studio Code

---

## 📂 Project Structure

```text
flight-service-serverless/
├── entity_model/
│   ├── DecimalEncoder.py   # Custom JSON encoder for DynamoDB Decimal types
│   ├── flight.py           # Flight entity model and data access methods
│   └── reservation.py      # Reservation entity model and logic
├── USER_REQUIREMENTS.md     # Business requirements and functional specs
├── .gitignore
└── README.md
```

---

## 🔑 Key Components & Entities

### 1. `entity_model/flight.py`
Defines the `Flight` domain entity, schema, and helper methods for querying and updating flight data in DynamoDB.

### 2. `entity_model/reservation.py`
Manages flight bookings and passenger reservation details.

### 3. `entity_model/DecimalEncoder.py`
A custom `json.JSONEncoder` class that handles DynamoDB's native `Decimal` numeric type to enable smooth JSON serialization in AWS Lambda HTTP responses.

---

## ⚙️ Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/cupofjavatech/flight-service-serverless.git
cd flight-service-serverless
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install boto3
```

---

## 🚀 Deployment

Deploy to AWS Lambda via AWS Serverless Framework:


---

## 📄 Documentation

For full project requirements and detailed business logic specifications, refer to [`USER_REQUIREMENTS.md`](./USER_REQUIREMENTS.md).

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.