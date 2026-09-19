from boto3.dynamodb.conditions import Key, Attr
from dbconfig import get_dynamodb_client, get_dynamodb_resource
from entity_model.flight import Flight
from botocore.exceptions import ClientError

TABLE = "flight_service"
db = get_dynamodb_resource()
FLIGHT_NO = "FLIGHT_NO:"
DEPARTURE_DT = "DEPARTURE_DT:"
DATE_FORMAT = "%Y-%m-%d %H%MHR"

def get_flight(table : str, origin : str, destination: str, flight_no : str, date : str):
    """Get Flight Details - based on Parameters defined
        Return the List of Flight Objecct
    """
    try:

           
        flight = db.Table(table)
        response = flight.query(
            KeyConditionExpression = 
                Key("pk").eq(f"{origin}#{destination}")
                & Key("sk").begins_with(f"{FLIGHT_NO}{flight_no}#{DEPARTURE_DT}{date}"),
                # FilterExpression=Attr("status").contains("DELAYED") # For Attribute value contains 
        )

        return response.get("Items", [])
        
    except ClientError as e:
        raise RuntimeError(
            f"DynamoDB query failed: {e.response['Error']['Message']}"
        ) from e

def flight_insert(table: str , pk: str, sk: str, arrival_dt : str, capacity : str):
    """
    Insert Flight details. 
    Input : table , pk, sk, arrival_date (format Y%-M%-DD% H%M%HR)
            capacit (number ) 
    Output : Json Response 
    """
    if not pk or not sk:
        raise ValueError("pk and sk are required")

    if not Flight.is_valid_date(arrival_dt, DATE_FORMAT):
        raise ValueError("Invalid arrival date")

    if not Flight.is_valid_capacity(capacity):
        raise ValueError("Invalid capacity")
    
    try:
        flight = db.Table(table)
        response = flight.get_item(Key={"pk": pk, "sk" : sk})
        if "Item" in response:
            print("Record exist : {response}")
            return { "message" : f"record with pk : '{pk}', sk: '{sk}' already exist"}
        else:
            response = flight.put_item(
                Item = {
                    "pk" : pk,
                    "sk" : sk,
                    "arrival_dt" : arrival_dt,
                    "capacity" : capacity,
                },
                ConditionExpression="attribute_not_exists(pk)"
            )

            return { "message" : f"record with pk : '{pk}', sk: '{sk}' created"}

    except ClientError as e:

        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return { "message": "Flight record already exists" }

        return { "message": e.response["Error"]["Message"] }


def update_flight(table: str, pk: str, sk: str,
                  arrival_dt: str = None,
                  capacity: str = None):
    """Updating the Flight deails. Only Allows to update Arrival Date, Capacity
        Return the Json Response with Flight Details
    """

    flight = db.Table(table)

    update_parts = []
    expression_names = {}
    expression_values = {}

    if arrival_dt:
        if not Flight.is_valid_date(arrival_dt, DATE_FORMAT):
            raise ValueError("Invalid Date")

        update_parts.append("#arrival_dt = :arrival_dt")
        expression_values[":arrival_dt"] = arrival_dt
        expression_names["#arrival_dt"] = "arrival_dt"

    if capacity:
        if not Flight.is_valid_capacity(capacity):
            raise ValueError("Invalid Capacity")

        update_parts.append("#capacity = :capacity")
        expression_values[":capacity"] = int(capacity)
        expression_names["#capacity"] = "capacity"

    if not update_parts:
        return {"message": "No fields supplied for update"}

    try:
        response = flight.update_item(
            Key={
                "pk": pk,
                "sk": sk
            },
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names,
            ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)",
            ReturnValues="ALL_NEW"
        )

        return {
            "message": "Flight updated successfully",
            "item": response.get("Attributes")
        }

    except ClientError as ex:
        if ex.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {
                "message": f"record with pk='{pk}', sk='{sk}' does not exist"
            }
        raise



