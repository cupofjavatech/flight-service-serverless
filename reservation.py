from boto3.dynamodb.conditions import Key, Attr
from dbconfig import get_dynamodb_client, get_dynamodb_resource
from entity_model.flight import Flight 
from entity_model.reservation import Passenger, Reservation
from botocore.exceptions import ClientError

TABLE = "flight_service"
db = get_dynamodb_resource()
FLIGHT_NO = "FLIGHT_NO:"
DEPARTURE_DT = "DEPARTURE_DT:"
RES_NUM_CONST = "RES_NUM:"
DATE_FORMAT = "%Y-%m-%d %H%MHR"

def insert_reservation(table_name : str,  pk : str, sk : str, email_id: str, passenger_detail):
    """Add New Reservation with Parameters
        Return the Json Response for Reservation Insert
    """
    if not pk or not sk:
        raise ValueError("pk and sk are required")

    if not email_id:
        raise ValueError("email_id is required")

    if not isinstance(passenger_detail, list) or not passenger_detail:
        raise ValueError("passenger_detail must be a non-empty list")

    try:
        flight = db.Table(table_name)
        res_num = Reservation.generate_res_num(Flight.get_flight_num(sk))

        response = flight.update_item(
            Key={
                "pk": pk,
                "sk": f"{sk}#{RES_NUM_CONST}{res_num}"
            },
            UpdateExpression="""
                SET res_num = :res_num,
                    email_id = :email_id,
                    passenger_count = :passenger_count,
                    passenger_list = :passenger_list
            """,
            ExpressionAttributeValues={
                ":res_num": res_num,
                ":email_id": email_id,
                ":passenger_count": len(passenger_detail),
                ":passenger_list": passenger_detail,
            },
            ConditionExpression="attribute_not_exists(pk)",
            ReturnValues="ALL_NEW"
        )

        return {
            "message": "Reservation created successfully",
            "reservation_number": res_num,
            "reservation": response.get("Attributes", {})
        }
    
    except ClientError as ex:
        if ex.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {
                "message": "Reservation already exists"
            }
        raise

def get_reservation(table_name: str, email_id: str, flight_no: str):
    """Get Reservation details
        Return the Json Response 
    """
    if not email_id or not flight_no:
        raise ValueError("Please provide email_id / valid flight_no")
    try:
        flight = db.Table(table_name)
        response = flight.query(
            IndexName="gsi1",
            KeyConditionExpression = 
                Key("email_id").eq(email_id),
                FilterExpression=Attr("res_num").contains(flight_no) # For Attribute value contains 
        )

        return response.get("Items", [])
    except ClientError as e:
        raise RuntimeError(
            f"Query execution failed: {e.response['Error']['Message']}"
        ) from e


def insert_reservation_archieve1(event: any):
    flight = db.Table(event.get("table"))

    res_num = Reservation.generate_res_num( Flight.get_flight_num(event["sk"]) )

    response = flight.update_item(
        Key={"pk": event["pk"], "sk": event["sk"]},
        UpdateExpression="SET reservation = list_append(if_not_exists(reservation, :empty_list), :new_reservation)",
        ExpressionAttributeValues={
            ":new_reservation": [
                {
                    "res_num" : res_num,
                    "email_id" : event["email_id"],
                    "passenger_count": len(event["passenger_detail"]),
                    "passenger_detail" : event["passenger_detail"]
                }
            ],
            ":empty_list" : [],
        },
        ReturnValues="ALL_NEW",  # Optional: returns the updated item state
    )

    return response


