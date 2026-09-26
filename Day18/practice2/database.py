import sqlite3
from dataclasses import dataclass
from typing import Optional


DB_NAME = "airline.db"


@dataclass
class Booking:
    id: int
    booking_reference: str
    customer_id: int
    flight_id: int
    seat_number: str
    status: str
    meal_preference: str
    baggage_allowance: str


@dataclass
class Flight:
    id: int
    flight_number: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    flight_status: str
    terminal: str
    gate: str
    delay_minutes: int


class Database:
    def __init__(self, db_name=DB_NAME):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row

    def initialize(self):
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY,
            flight_number TEXT NOT NULL,
            airline TEXT NOT NULL,
            departure_airport TEXT NOT NULL,
            arrival_airport TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            arrival_time TEXT NOT NULL,
            flight_status TEXT NOT NULL,
            terminal TEXT NOT NULL,
            gate TEXT NOT NULL,
            delay_minutes INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            booking_reference TEXT UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            flight_id INTEGER NOT NULL,
            seat_number TEXT NOT NULL,
            status TEXT NOT NULL,
            meal_preference TEXT NOT NULL,
            baggage_allowance TEXT NOT NULL,

            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(flight_id) REFERENCES flights(id)
        );
        """)

        self._seed()

    def _seed(self):
        self.connection.executescript("""
        INSERT OR IGNORE INTO customers
        VALUES (
            1,
            'Rahim Ahmed',
            'rahim@example.com',
            '+8801712345678'
        );

        INSERT OR IGNORE INTO flights
        VALUES (
            1,
            'BG305',
            'Biman Bangladesh Airlines',
            'DAC',
            'DXB',
            '2026-09-28 08:30',
            '2026-09-28 12:45',
            'Scheduled',
            'Terminal 1',
            'A12',
            0
        );

        INSERT OR IGNORE INTO bookings
        VALUES (
            1,
            'BG7K92',
            1,
            1,
            '14C',
            'Confirmed',
            'Standard',
            '30 KG'
        );
        """)

        self.connection.commit()


class BookingRepository:

    def __init__(self, db: Database):
        self.db = db

    def get_by_reference(
        self,
        reference: str
    ) -> Optional[Booking]:

        row = self.db.connection.execute(
            """
            SELECT *
            FROM bookings
            WHERE booking_reference = ?
            """,
            (reference.upper(),)
        ).fetchone()

        if not row:
            return None

        return Booking(**dict(row))

    def get(self, booking_id: int) -> Optional[Booking]:

        row = self.db.connection.execute(
            """
            SELECT *
            FROM bookings
            WHERE id = ?
            """,
            (booking_id,)
        ).fetchone()

        if not row:
            return None

        return Booking(**dict(row))

    def update_seat(
        self,
        booking_id: int,
        seat: str
    ):
        self.db.connection.execute(
            """
            UPDATE bookings
            SET seat_number = ?
            WHERE id = ?
            """,
            (seat.upper(), booking_id)
        )

        self.db.connection.commit()

    def update_meal(
        self,
        booking_id: int,
        meal: str
    ):
        self.db.connection.execute(
            """
            UPDATE bookings
            SET meal_preference = ?
            WHERE id = ?
            """,
            (meal, booking_id)
        )

        self.db.connection.commit()


class FlightRepository:

    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, flight_id: int) -> Optional[Flight]:

        row = self.db.connection.execute(
            """
            SELECT *
            FROM flights
            WHERE id = ?
            """,
            (flight_id,)
        ).fetchone()

        if not row:
            return None

        return Flight(**dict(row))