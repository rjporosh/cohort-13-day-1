import json


class SessionState:

    def __init__(self):
        self.current_booking_id = None
        self.current_booking_reference = None

    def set_booking(self, booking_id, reference):
        self.current_booking_id = booking_id
        self.current_booking_reference = reference

    def has_booking(self):
        return self.current_booking_id is not None


class FlightTools:

    def __init__(self, service, state):
        self.service = service
        self.state = state

    def find_booking(self, booking_reference):

        result = self.service.find_booking(
            booking_reference
        )

        if result["success"]:
            self.state.set_booking(
                result["booking_id"],
                result["booking_reference"]
            )

        return result

    def get_flight_information(self):

        if not self.state.has_booking():
            return {
                "success": False,
                "message": (
                    "No booking is currently selected. "
                    "Ask the customer for their booking reference."
                )
            }

        return self.service.get_flight(
            self.state.current_booking_id
        )

    def change_seat(self, seat):

        if not self.state.has_booking():
            return {
                "success": False,
                "message": "No booking is currently selected."
            }

        return self.service.change_seat(
            self.state.current_booking_id,
            seat
        )

    def change_meal(self, meal):

        if not self.state.has_booking():
            return {
                "success": False,
                "message": "No booking is currently selected."
            }

        return self.service.change_meal(
            self.state.current_booking_id,
            meal
        )


def build_tool_definitions():

    return [

        {
            "type": "function",
            "name": "find_booking",
            "description": (
                "Find a customer booking using its booking reference. "
                "This should be used when the customer provides a PNR."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_reference": {
                        "type": "string"
                    }
                },
                "required": ["booking_reference"],
                "additionalProperties": False
            }
        },

        {
            "type": "function",
            "name": "get_flight_information",
            "description": (
                "Get flight information for the booking currently "
                "selected in application state. Use this for questions "
                "about delay, departure, arrival, terminal, gate, etc."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        },

        {
            "type": "function",
            "name": "change_seat",
            "description": (
                "Change the seat of the currently selected booking."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "seat": {
                        "type": "string"
                    }
                },
                "required": ["seat"],
                "additionalProperties": False
            }
        },

        {
            "type": "function",
            "name": "change_meal",
            "description": (
                "Change the meal preference of the currently "
                "selected booking."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "meal": {
                        "type": "string"
                    }
                },
                "required": ["meal"],
                "additionalProperties": False
            }
        }
    ]