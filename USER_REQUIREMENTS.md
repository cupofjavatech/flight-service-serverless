# Flight Service User Requirements

## 1. Purpose

The Flight Service is a serverless AWS backend for managing flight records and passenger reservations. It exposes HTTP endpoints through Amazon API Gateway and processes requests with an AWS Lambda function. Flight and reservation data is stored in Amazon DynamoDB.

The service is intended to let authorized consumers:

- Create a flight record.
- Find a flight by route, flight number, and departure date.
- Update selected flight details.
- Create a reservation for a flight.
- Find reservations by passenger email address and flight number.

## 2. Users and External Systems

### Users

The service is intended for client applications or API consumers that need to manage flights and reservations. The current code does not implement user authentication or authorization; those controls must be provided by API Gateway, an authorizer, or another upstream service.

### External systems

- **Amazon API Gateway** receives HTTP requests and forwards API Gateway events to Lambda.
- **AWS Lambda** runs the `lambda_handler` entry point.
- **Amazon DynamoDB** stores flight and reservation items.
- **AWS SDK for Python (`boto3`)** provides DynamoDB access.
- **AWS Lambda Powertools for Python** resolves API routes and reads request bodies.

## 3. Functional Requirements

### FR-01: Flight creation

The service shall expose `POST /flight/create` to create a flight record.

The request body shall contain:

```json
{
  "table": "flight_service",
  "pk": "ARN#STO",
  "sk": "FLIGHT_NO:SK123#DEPARTURE_DT:2026-08-22 1030HR",
  "arrival_dt": "2026-08-22 1230HR",
  "capacity": 180
}
```

The service shall:

- Require `pk` and `sk`.
- Require `arrival_dt` in the format `YYYY-MM-DD HHMMHR`.
- Require `capacity` to be a positive integer.
- Reject creation when the item already exists.
- Store `pk`, `sk`, `arrival_dt`, and `capacity` in DynamoDB.
- Return a success message when the record is created.

The partition key convention is `origin#destination`. The sort key convention is `FLIGHT_NO:<flight-number>#DEPARTURE_DT:<departure-date-and-time>`.

### FR-02: Flight lookup

The service shall expose `POST /flight/get` to find flights.

The request body shall contain:

```json
{
  "table": "flight_service",
  "origin": "ARN",
  "destination": "STO",
  "flight_no": "SK123",
  "departure_dt": "2026-08-22 1030HR"
}
```

The service shall query DynamoDB using:

- Partition key: `<origin>#<destination>`
- Sort-key prefix: `FLIGHT_NO:<flight_no>#DEPARTURE_DT:<departure_dt>`

The service shall return the matching DynamoDB items, or an empty list when no items match.

### FR-03: Flight update

The service shall expose `POST /flight/update` to update an existing flight.

The request body shall contain `table`, `pk`, and `sk`, and may contain either or both of:

```json
{
  "table": "flight_service",
  "pk": "ARN#STO",
  "sk": "FLIGHT_NO:SK123#DEPARTURE_DT:2026-08-22 1030HR",
  "arrival_dt": "2026-08-22 1230HR",
  "capacity": 170
}
```

The service shall:

- Update only the supplied `arrival_dt` and `capacity` fields.
- Validate `arrival_dt` using `YYYY-MM-DD HHMMHR`.
- Validate `capacity` as a positive integer.
- Reject an update when neither mutable field is supplied.
- Reject an update when the flight does not exist.
- Return the updated DynamoDB item after a successful update.

### FR-04: Reservation creation

The service shall expose `POST /reservation/create` to create a reservation for a flight.

The request body shall contain:

```json
{
  "table": "flight_service",
  "pk": "ARN#STO",
  "sk": "FLIGHT_NO:SK123#DEPARTURE_DT:2026-08-22 1030HR",
  "email_id": "traveler@example.com",
  "passenger_detail": [
    {
      "name_full": "Alex Morgan",
      "passport": "P1234567",
      "dob": "1990-04-12",
      "address_full": "Example address",
      "gender": "Male"
    }
  ]
}
```

The service shall:

- Require `pk`, `sk`, and `email_id`.
- Require `passenger_detail` to be a non-empty list.
- Generate a reservation number using the flight number and six random alphanumeric characters.
- Store the reservation as a separate DynamoDB item using the flight key and generated reservation number.
- Store the reservation email, passenger count, and passenger list.
- Prevent duplicate reservation item keys.
- Return the generated reservation number and stored reservation attributes.

The reservation item sort key convention is:

`<flight-sort-key>#RES_NUM:<generated-reservation-number>`

### FR-05: Reservation lookup

The service shall expose `POST /reservation/get` to find reservations.

The request body shall contain:

```json
{
  "table": "flight_service",
  "email_id": "traveler@example.com",
  "flight_no": "SK123"
}
```

The service shall:

- Require `email_id` and `flight_no`.
- Query the DynamoDB global secondary index named `gsi1` using `email_id` as the index partition key.
- Filter results for reservation numbers containing the requested flight number.
- Return the matching reservation items, or an empty list when no items match.

## 4. Data Requirements

### Flight item

A flight item shall contain:

| Attribute | Requirement |
|---|---|
| `pk` | DynamoDB partition key; expected format `<origin>#<destination>` |
| `sk` | DynamoDB sort key; expected to identify flight number and departure time |
| `arrival_dt` | String in `YYYY-MM-DD HHMMHR` format |
| `capacity` | Positive integer |

### Reservation item

A reservation item shall contain:

| Attribute | Requirement |
|---|---|
| `pk` | Same flight partition key as the associated flight |
| `sk` | Flight sort key plus `#RES_NUM:<reservation-number>` |
| `res_num` | Generated reservation identifier |
| `email_id` | Email address supplied by the client |
| `passenger_count` | Number of entries in `passenger_list` |
| `passenger_list` | Non-empty list of passenger objects |

Each passenger object is expected to contain `name_full`, `passport`, `dob`, `address_full`, and `gender`. The current implementation does not validate these fields individually.

### DynamoDB indexes

The reservation lookup requires a global secondary index named `gsi1` with `email_id` as its partition key. The exact sort-key definition is not specified in the application code and must be configured in the DynamoDB table infrastructure.

## 5. Operational Requirements

- The Lambda function shall run in AWS Region `eu-north-1` as currently configured in the database helper.
- The Lambda execution role shall have permission to read and write the configured DynamoDB table.
- The DynamoDB table name shall be provided in each request through the `table` field.
- DynamoDB connection settings shall use AWS SDK configuration with signature version `v4`, adaptive retries, a five-second connection timeout, and a ten-second read timeout.
- API Gateway events shall be compatible with `APIGatewayRestResolver`.
- API consumers shall send JSON request bodies.

## 6. Error and Validation Requirements

The service shall reject invalid requests when required fields are missing or values fail validation. Current validation failures include:

- Missing flight `pk` or `sk`.
- Invalid flight arrival date.
- Non-positive or non-integer flight capacity.
- Missing reservation email address.
- Missing reservation passenger list or an empty passenger list.
- Missing reservation lookup email or flight number.
- Attempting to update a flight without mutable fields.
- Attempting to update a flight that does not exist.

DynamoDB client errors shall be converted to runtime errors or structured message responses depending on the operation. A production API should standardize HTTP status codes and error response bodies at the API boundary.

## 7. Non-Functional Requirements

- **Serverless execution:** The service shall run without managing application servers.
- **Persistence:** Flight and reservation data shall be persisted in DynamoDB.
- **Scalability:** The design shall support AWS Lambda and DynamoDB scaling characteristics.
- **Reliability:** Flight creation and reservation creation shall use conditional writes to reduce duplicate records.
- **Observability:** Operational logging and metrics should be added through AWS Lambda Powertools or an equivalent logging and monitoring solution.
- **Security:** Authentication, authorization, input-size limits, sensitive-data protection, and least-privilege IAM permissions should be configured outside or alongside this code.

## 8. Current Scope and Known Gaps

The current implementation does not yet provide:

- Authentication or authorization.
- Explicit HTTP status-code mapping for validation and database errors.
- Pagination for DynamoDB query results.
- Availability checks against flight capacity when creating reservations.
- Validation that the referenced flight exists before creating a reservation.
- Validation of passenger fields, email format, date of birth, or gender values.
- Cancellation, deletion, or modification of reservations.
- A guaranteed reservation-number uniqueness check beyond the generated DynamoDB key and conditional write.
- Infrastructure definitions for the DynamoDB table, `gsi1`, API Gateway, IAM role, or Lambda deployment.
- Automated tests.

These gaps should be addressed before exposing the service to untrusted or production traffic.
