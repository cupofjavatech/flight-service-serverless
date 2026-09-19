# Flight Service UML Diagrams

## 1. Domain Class Diagram

This diagram reflects the Python domain classes currently defined in the project. The API handlers and DynamoDB operations are shown separately as service components because they are implemented as functions, not classes.

```mermaid
classDiagram
    class Flight {
        +str pk
        +str sk
        +str origin
        +str destination
        +str flight_no
        +str departure_dt
        +str arrival_dt
        +int capacity
        +list~Reservation~ reservation
        +__init__(pk, sk, arrival_dt, capacity, reservation=None)
        +to_dict() dict
        +set_org_dest(pk) void
        +set_flightnum_departure(sk) void
        +get_flight_num(sk) str
        +is_valid_date(dt_str, dt_format) bool
        +is_valid_capacity(val) bool
    }

    class Reservation {
        +str res_num
        +str email_id
        +int passenger_count
        +list~Passenger~ passenger_detail
        +__init__(res_num, email_id, passenger_detail)
        +generate_res_num(flight_num) str
    }

    class Passenger {
        +str name_full
        +str passport
        +str dob
        +str address_full
        +Gender gender
        +__init__(name_full, passport, dob, address_full, gender)
    }

    class Gender {
        <<enumeration>>
        M Male
        F Female
    }

    Flight "1" o-- "0..*" Reservation : contains
    Reservation "1" *-- "1..*" Passenger : includes
    Passenger --> Gender : has
```

### Domain relationships

- A flight may have zero or more reservations in the domain model.
- A reservation contains one or more passengers according to the service input requirement.
- A passenger has a `Gender` enum value of `Male` or `Female`.
- A flight derives `origin` and `destination` from `pk` and derives `flight_no` and `departure_dt` from `sk`.
- A reservation number is generated from the flight number and six random alphanumeric characters.

## 2. Application Component Diagram

```mermaid
classDiagram
    class APIClient {
        <<external actor>>
        Sends JSON HTTP requests
    }

    class APIGateway {
        <<AWS service>>
        Receives HTTP requests
        Forwards API Gateway events
    }

    class LambdaFunction {
        <<AWS Lambda>>
        lambda_handler(event, context)
        Resolves API routes
    }

    class FlightRoutes {
        <<module>>
        get_flight_handler()
        create_flight_handler()
        update_flight_handler()
    }

    class ReservationRoutes {
        <<module>>
        get_reservation_handler()
        create_reservation_handler()
    }

    class FlightOperations {
        <<module>>
        get_flight()
        flight_insert()
        update_flight()
    }

    class ReservationOperations {
        <<module>>
        get_reservation()
        insert_reservation()
    }

    class DatabaseConfig {
        <<module>>
        get_dynamodb_resource()
        get_dynamodb_client()
    }

    class DynamoDB {
        <<AWS service>>
        Flight items
        Reservation items
        gsi1 index
    }

    APIClient --> APIGateway : HTTP JSON
    APIGateway --> LambdaFunction : API Gateway event
    LambdaFunction --> FlightRoutes : /flight/*
    LambdaFunction --> ReservationRoutes : /reservation/*
    FlightRoutes --> FlightOperations : calls
    ReservationRoutes --> ReservationOperations : calls
    FlightOperations --> DatabaseConfig : obtains resource
    ReservationOperations --> DatabaseConfig : obtains resource
    DatabaseConfig --> DynamoDB : boto3 read/write
    ReservationOperations --> DynamoDB : queries gsi1
```

## 3. Module Dependency Diagram

```mermaid
flowchart TD
    LF[lambda_function.py]
    GR[gateway_resolver.py]
    FR[flight_operation.py]
    RAR[reservation_api_route.py]
    RO[reservation.py]
    DC[dbconfig.py]
    FM[entity_model/flight.py]
    RM[entity_model/reservation.py]
    DE[entity_model/DecimalEncoder.py]
    BOTO3[boto3 and botocore]
    POWERTOOLS[aws-lambda-powertools]
    DDB[(Amazon DynamoDB)]

    LF --> FR
    LF --> RAR
    LF --> FM
    LF --> RM
    LF --> DE
    LF --> GR
    FR --> DC
    FR --> FM
    FR --> BOTO3
    RAR --> GR
    RAR --> RO
    RO --> DC
    RO --> FM
    RO --> RM
    RO --> BOTO3
    GR --> POWERTOOLS
    DC --> BOTO3
    BOTO3 --> DDB
```

## 4. Main API Operations

| Operation | Route handler | Operation function | Persistence action |
|---|---|---|---|
| Create flight | `create_flight_handler` | `flight_insert` | Conditional DynamoDB write |
| Get flight | `get_flight_handler` | `get_flight` | Query by route and sort-key prefix |
| Update flight | `update_flight_handler` | `update_flight` | Conditional DynamoDB update |
| Create reservation | `create_reservation_handler` | `insert_reservation` | Conditional DynamoDB update using generated reservation key |
| Get reservation | `get_reservation_handler` | `get_reservation` | Query `gsi1` by `email_id`, then filter by flight number |
