from gateway_resolver import app
from reservation import get_reservation, insert_reservation

@app.post("/reservation/get")
def get_reservation_handler():
    """Handle the Post method to get reservation - /reservation/get """
    body = app.current_event.json_body or {}
    
    table = body.get("table")
    email = body.get("email_id")
    flight_no = body.get("flight_no")

    return get_reservation(table, email, flight_no)


@app.post("/reservation/create")
def create_reservation_handler():
    """ Handle the Post method to Create new Reservation"""
    body = app.current_event.json_body or {}
    table = body.get("table")
    pk = body.get("pk")
    sk = body.get("sk")
    email_id = body.get("email_id")
    passenger_detail = body.get("passenger_detail")

    return insert_reservation(table, pk, sk, email_id, passenger_detail)