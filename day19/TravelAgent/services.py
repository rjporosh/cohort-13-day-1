from database import BookingRepository, FlightRepository
from memory import CustomerMemory


class FlightSupportService:

    VALID_MEALS = {
        "standard",
        "vegetarian",
        "vegan",
        "halal",
        "kosher",
        "gluten-free",
        "child meal"
    }

    def __init__(
        self,
        bookings: BookingRepository,
        flights: FlightRepository,
        memory: CustomerMemory
    ):
        self.bookings = bookings
        self.flights = flights
        self.memory = memory

    def find_booking(self, reference: str):
        reference = reference.strip().upper()

        # Identity routing cache: only maps a booking reference to a customer ID.
        customer_id = self.memory.get_cached(0, f"customer_for:{reference}")
        booking = None

        if customer_id is not None:
            cached = self.memory.get_cached(customer_id, f"booking:{reference}")
            if cached:
                return cached

        # Cache miss: the repository is the source of truth.
        booking = self.bookings.get_by_reference(reference)

        if not booking:
            return {
                "success": False,
                "message": f"Booking {reference} was not found."
            }

        customer_id = booking.customer_id
        result = {
            "success": True,
            "customer_id": customer_id,
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "flight_id": booking.flight_id,
            "seat": booking.seat_number,
            "status": booking.status,
            "meal": booking.meal_preference,
            "baggage": booking.baggage_allowance
        }

        self.memory.set_cached(0, f"customer_for:{reference}", customer_id)
        self.memory.set_cached(customer_id, f"booking:{reference}", result)
        return result

    def get_flight(self, customer_id: int, booking_id: int):
        cached = self.memory.get_cached(customer_id, f"flight_for_booking:{booking_id}")
        if cached:
            return cached

        booking = self.bookings.get(booking_id)
        if not booking or booking.customer_id != customer_id:
            return {"success": False, "message": "Booking not found."}

        flight = self.flights.get_by_id(booking.flight_id)
        if not flight:
            return {"success": False, "message": "Flight not found."}

        result = {
            "success": True,
            "flight_number": flight.flight_number,
            "airline": flight.airline,
            "departure_airport": flight.departure_airport,
            "arrival_airport": flight.arrival_airport,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
            "flight_status": flight.flight_status,
            "terminal": flight.terminal,
            "gate": flight.gate,
            "delay_minutes": flight.delay_minutes
        }
        self.memory.set_cached(customer_id, f"flight_for_booking:{booking_id}", result)
        return result

    def change_seat(self, customer_id: int, booking_id: int, seat: str):
        seat = seat.strip().upper()

        booking = self.bookings.get(booking_id)
        if not booking or booking.customer_id != customer_id:
            return {"success": False, "message": "Booking not found."}

        if not seat or len(seat) > 5:
            return {"success": False, "message": "Invalid seat number."}

        if not self.bookings.seat_is_available(
            booking.flight_id, seat, booking_id
        ):
            return {
                "success": False,
                "message": f"Seat {seat} is not available. Please choose another seat."
            }

        old_seat = booking.seat_number
        self.bookings.update_seat(booking_id, seat)

        cached = self.memory.get_cached(
            customer_id, f"booking:{booking.booking_reference}"
        )
        if cached:
            cached["seat"] = seat
            self.memory.set_cached(
                customer_id, f"booking:{booking.booking_reference}", cached
            )

        return {
            "success": True,
            "message": f"Seat changed from {old_seat} to {seat}."
        }

    def change_meal(self, customer_id: int, booking_id: int, meal: str):
        normalized = meal.strip().lower()

        if normalized not in self.VALID_MEALS:
            return {
                "success": False,
                "message": f"Unsupported meal preference: {meal}"
            }

        booking = self.bookings.get(booking_id)
        if not booking or booking.customer_id != customer_id:
            return {"success": False, "message": "Booking not found."}

        old_meal = booking.meal_preference
        self.bookings.update_meal(booking_id, normalized)

        cached = self.memory.get_cached(
            customer_id, f"booking:{booking.booking_reference}"
        )
        if cached:
            cached["meal"] = normalized
            self.memory.set_cached(
                customer_id, f"booking:{booking.booking_reference}", cached
            )

        return {
            "success": True,
            "message": f"Meal changed from {old_meal} to {normalized}."
        }
