import json

from flight_operation import flight_insert, get_flight as fetch_flight_from_db, update_flight
from reservation_api_route import get_reservation_handler, create_reservation_handler
from entity_model.flight import Flight
from entity_model.reservation import Reservation, Passenger
from entity_model.DecimalEncoder import DecimalEncoder
from gateway_resolver import app

@app.post("/flight/get")
def get_flight_handler():
    body = app.current_event.json_body or {}
    
    table = body.get("table")
    origin = body.get("origin")
    destination = body.get("destination")
    flight_no = body.get("flight_no")
    departure_dt = body.get("departure_dt")

    response = fetch_flight_from_db(table, origin, destination, flight_no, departure_dt) 
    return response

@app.post("/flight/create")
def create_flight_handler():
    body = app.current_event.json_body or {}
    
    table = body.get("table")
    pk = body.get("pk")
    sk = body.get("sk")
    capacity = body.get("capacity")
    arrival_dt = body.get("arrival_dt")
    response = flight_insert(table, pk, sk, arrival_dt, capacity, )
    return response

@app.post("/flight/update")
def update_flight_handler():
    body = app.current_event.json_body or {}

    table = body.get("table")
    pk = body.get("pk")
    sk = body.get("sk")
    capacity = body.get("capacity")
    arrival_dt = body.get("arrival_dt")

    response = update_flight(table, pk, sk, arrival_dt, capacity)
    return response

def lambda_handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)
