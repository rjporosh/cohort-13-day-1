from database import BookingRepository, FlightRepository


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
        flights: FlightRepository
    ):
        self.bookings = bookings
        self.flights = flights

    def find_booking(self, reference: str):

        booking = self.bookings.get_by_reference(reference)

        if not booking:
            return {
                "success": False,
                "message": f"Booking {reference} was not found."
            }

        return {
            "success": True,
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "seat": booking.seat_number,
            "status": booking.status,
            "meal": booking.meal_preference,
            "baggage": booking.baggage_allowance
        }

    def get_flight(self, booking_id: int):

        booking = self.bookings.get(booking_id)

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        flight = self.flights.get_by_id(booking.flight_id)

        if not flight:
            return {
                "success": False,
                "message": "Flight not found."
            }

        return {
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

    def change_seat(
        self,
        booking_id: int,
        seat: str
    ):

        booking = self.bookings.get(booking_id)

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        old_seat = booking.seat_number

        self.bookings.update_seat(
            booking_id,
            seat
        )

        return {
            "success": True,
            "message": (
                f"Seat changed from {old_seat} "
                f"to {seat.upper()}."
            )
        }

    def change_meal(
        self,
        booking_id: int,
        meal: str
    ):

        normalized = meal.lower()

        if normalized not in self.VALID_MEALS:
            return {
                "success": False,
                "message": (
                    f"Unsupported meal preference: {meal}"
                )
            }

        booking = self.bookings.get(booking_id)

        if not booking:
            return {
                "success": False,
                "message": "Booking not found."
            }

        old_meal = booking.meal_preference

        self.bookings.update_meal(
            booking_id,
            normalized
        )

        return {
            "success": True,
            "message": (
                f"Meal changed from {old_meal} "
                f"to {normalized}."
            )
        }