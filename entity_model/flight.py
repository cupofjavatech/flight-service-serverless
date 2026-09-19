from dataclasses import dataclass, field, asdict
from datetime import datetime
from .reservation import Passenger, Reservation

@dataclass
class Flight:
    pk: str
    sk: str
    origin: str
    destination: str
    flight_no: str
    departure_dt: str
    arrival_dt: str
    capacity: int
    reservation : list[Reservation] = field(default_factory=list)

    def __init__(self, pk, sk, arrival_dt, capacity, reservation=None):
        self.pk = pk
        self.sk = sk
        self.arrival_dt = arrival_dt
        self.capacity = capacity
        self.set_org_dest(pk)
        self.set_flightnum_departure(sk)
        self.reservation = reservation if reservation is not None else []
        
    def to_dict(self):
        return asdict(self)

    def set_org_dest(self, pk: str):
        arr = pk.split("#")
        self.origin = arr[0]
        self.destination = arr[1]

    def set_flightnum_departure(self, sk: str):
        arr1 = sk.split("#")
        arr2 = arr1[0].split(":")
        arr3 = arr1[1].split(":")
        self.flight_no = arr2[1]
        self.departure_dt = arr3[1]

    @staticmethod
    def get_flight_num(sk : str):
        arr1 = sk.split("#")
        flight_num = ""
        if len(arr1) > 0:
            arr1 = arr1[0].split(":")
            if len(arr1) == 2:
                flight_num = arr1[1]

        return flight_num


    @staticmethod
    def is_valid_date(dt_str : str, dt_format: str) -> bool:
        try:
            datetime.strptime(dt_str, dt_format)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_capacity(val: any) -> bool:
        return isinstance(val, int) and (val > 0)