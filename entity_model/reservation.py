from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random, string

DATE_FORMAT = "%Y-%m-%d"
chart = string.ascii_letters + string.digits

class Gender(Enum):
    M = "Male"
    F = "Female"

class Passenger:
    name_full: str
    passport: str
    dob: str
    address_full: str
    gender: Gender
    def __init__(self, name_full, passsport, dob, address_full, gender):
        self.name_full = name_full
        self.passport = passsport
        self.dob = dob
        self.address_full = address_full
        self.gender = gender

class Reservation:
    res_num: str
    email_id: str
    passenger_count: int
    passenger_detail: list[Passenger]
    def __init__(self, res_num, email_id, passenger_detail):
        self.res_num = res_num
        self.email_id = email_id
        self.passenger_detail =  passenger_detail

    @staticmethod
    def generate_res_num(flight_num: str) -> str:
        return flight_num + "-" + "".join(random.choices(chart,k=6)).upper()
        
