# Flight Service Data-Flow Diagram

## 1. System-Level Data Flow

The service receives JSON requests through API Gateway, resolves routes in the Lambda function, performs validation and business operations, and reads or writes items in DynamoDB. The result travels back through Lambda and API Gateway to the client.

```mermaid
flowchart LR
    Client[API client]
    Gateway[Amazon API Gateway]
    Lambda[AWS Lambda\nlambda_handler]
    Resolver[AWS Lambda Powertools\nAPIGatewayRestResolver]
    FlightOps[Flight operations\ncreate, get, update]
    ReservationOps[Reservation operations\ncreate, get]
    Dynamo[(Amazon DynamoDB\nflight table)]
    GSI[gsi1\nemail_id index]
    Response[JSON response]

    Client -->|JSON POST request| Gateway
    Gateway -->|API Gateway event| Lambda
    Lambda --> Resolver
    Resolver -->|/flight/*| FlightOps
    Resolver -->|/reservation/*| ReservationOps
    FlightOps -->|read or write flight items| Dynamo
    ReservationOps -->|write reservation items| Dynamo
    ReservationOps -->|query by email_id| GSI
    GSI -->|reservation items| ReservationOps
    Dynamo -->|flight or reservation result| FlightOps
    FlightOps --> Response
    ReservationOps --> Response
    Response -->|Lambda result| Lambda
    Lambda --> Gateway
    Gateway --> Client
```

## 2. Flight Data Flow

```mermaid
flowchart TD
    Client[API client]
    Gateway[API Gateway]
    Handler[Lambda route handler]
    Validate[Validate flight fields]
    Operation{Flight operation}
    Create[Create flight\nPutItem with conditional check]
    Read[Find flight\nQuery pk and sk prefix]
    Update[Update flight\nUpdateItem with existence check]
    Table[(DynamoDB flight table)]
    Result[Flight item or operation message]

    Client -->|POST /flight/create| Gateway
    Client -->|POST /flight/get| Gateway
    Client -->|POST /flight/update| Gateway
    Gateway --> Handler
    Handler --> Validate
    Validate --> Operation
    Operation -->|create| Create
    Operation -->|get| Read
    Operation -->|update| Update
    Create -->|pk, sk, arrival_dt, capacity| Table
    Read -->|pk = origin#destination\nsk begins_with flight and departure| Table
    Update -->|pk, sk, optional arrival_dt/capacity| Table
    Table --> Result
    Create --> Result
    Update --> Result
    Result --> Gateway
    Gateway --> Client
```

### Flight key construction

- Partition key: `origin#destination`
- Flight sort-key prefix: `FLIGHT_NO:<flight_no>#DEPARTURE_DT:<departure_dt>`
- Arrival date format: `YYYY-MM-DD HHMMHR`
- Capacity: positive integer

## 3. Reservation Creation Data Flow

```mermaid
sequenceDiagram
    participant C as API client
    participant G as API Gateway
    participant L as Lambda and route resolver
    participant R as Reservation operation
    participant D as DynamoDB flight table

    C->>G: POST /reservation/create with flight key, email, passengers
    G->>L: API Gateway event
    L->>R: Parse JSON body and call insert_reservation
    R->>R: Validate pk, sk, email_id, and non-empty passenger_detail
    R->>R: Extract flight number and generate reservation number
    R->>D: Conditional UpdateItem using flight key plus reservation key
    D-->>R: Created attributes or duplicate-key error
    R-->>L: Reservation number and result message
    L-->>G: Resolved response
    G-->>C: JSON response
```

The reservation sort key is constructed as:

```text
<flight-sort-key>#RES_NUM:<flight-number>-<six random alphanumeric characters>
```

The reservation item stores `res_num`, `email_id`, `passenger_count`, and `passenger_list` along with `pk` and `sk`.

## 4. Reservation Lookup Data Flow

```mermaid
sequenceDiagram
    participant C as API client
    participant G as API Gateway
    participant L as Lambda and route resolver
    participant R as Reservation operation
    participant I as DynamoDB gsi1
    participant D as DynamoDB flight table

    C->>G: POST /reservation/get with email_id and flight_no
    G->>L: API Gateway event
    L->>R: Parse JSON body and call get_reservation
    R->>R: Validate email_id and flight_no
    R->>I: Query gsi1 where email_id equals request email
    I->>D: Locate indexed reservation items
    D-->>I: Indexed items
    I-->>R: Filter items where res_num contains flight_no
    R-->>L: Matching reservation list
    L-->>G: Resolved response
    G-->>C: JSON response
```

## 5. DynamoDB Data Relationships

```mermaid
erDiagram
    FLIGHT_ITEM ||--o{ RESERVATION_ITEM : "shares pk"
    FLIGHT_ITEM {
        string pk "origin#destination"
        string sk "FLIGHT_NO and DEPARTURE_DT"
        string arrival_dt
        integer capacity
    }
    RESERVATION_ITEM {
        string pk "flight partition key"
        string sk "flight key plus RES_NUM"
        string res_num
        string email_id
        integer passenger_count
        list passenger_list
    }
    GSI1 {
        string email_id "partition key"
        string indexed_reservation_attributes
    }
    GSI1 ||--o{ RESERVATION_ITEM : indexes
```

## 6. Error Flow

```mermaid
flowchart TD
    Request[Incoming JSON request]
    Validation{Required fields and values valid?}
    DynamoOperation[DynamoDB operation]
    DynamoResult{DynamoDB succeeds?}
    Success[Return operation result]
    ValidationError[Return validation error]
    DatabaseError[Return runtime error or structured message]

    Request --> Validation
    Validation -->|no| ValidationError
    Validation -->|yes| DynamoOperation
    DynamoOperation --> DynamoResult
    DynamoResult -->|yes| Success
    DynamoResult -->|no| DatabaseError
```

The current implementation does not define a single HTTP status-code or error-body convention. API Gateway or an additional error-handling layer should standardize those responses before production use.
