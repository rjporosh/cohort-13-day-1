class SessionState:

    def __init__(self):
        self.customer_id = None
        self.current_booking_id = None
        self.current_booking_reference = None

    def set_booking(self, customer_id, booking_id, reference):
        self.customer_id = customer_id
        self.current_booking_id = booking_id
        self.current_booking_reference = reference

    def has_booking(self):
        return self.current_booking_id is not None and self.customer_id is not None


class FlightTools:

    def __init__(self, service, state):
        self.service = service
        self.state = state

    def find_booking(self, booking_reference):
        result = self.service.find_booking(booking_reference)

        if result["success"]:
            self.state.set_booking(
                result["customer_id"],
                result["booking_id"],
                result["booking_reference"]
            )

        return result

    def get_flight_information(self):
        if not self.state.has_booking():
            return {
                "success": False,
                "message": "No booking is currently selected. Ask for the booking reference."
            }

        return self.service.get_flight(
            self.state.customer_id,
            self.state.current_booking_id
        )

    def change_seat(self, seat):
        if not self.state.has_booking():
            return {"success": False, "message": "No booking is currently selected."}

        return self.service.change_seat(
            self.state.customer_id,
            self.state.current_booking_id,
            seat
        )

    def change_meal(self, meal):
        if not self.state.has_booking():
            return {"success": False, "message": "No booking is currently selected."}

        return self.service.change_meal(
            self.state.customer_id,
            self.state.current_booking_id,
            meal
        )

    def save_memory(self, key, value):
        if self.state.customer_id is None:
            return {
                "success": False,
                "message": "Customer identity is unknown. Find the booking first."
            }
        return self.service.memory.save(
            self.state.customer_id, key.strip(), value.strip()
        )

    def retrieve_memory(self, query):
        if self.state.customer_id is None:
            return {
                "success": False,
                "message": "Customer identity is unknown. Find the booking first."
            }
        return self.service.memory.retrieve(
            self.state.customer_id, query
        )


def build_tool_definitions():
    return [
        {
            "type": "function",
            "name": "find_booking",
            "description": "Find a customer booking using its PNR/booking reference.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {"booking_reference": {"type": "string"}},
                "required": ["booking_reference"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "get_flight_information",
            "description": "Get flight status, delay, departure, arrival, terminal or gate for the selected booking.",
            "strict": True,
            "parameters": {
                "type": "object", "properties": {}, "required": [], "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "change_seat",
            "description": "Change the seat of the selected booking. The system checks availability before changing it.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {"seat": {"type": "string"}},
                "required": ["seat"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "change_meal",
            "description": "Change the meal preference of the selected booking.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {"meal": {"type": "string"}},
                "required": ["meal"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "save_memory",
            "description": "Save a useful customer preference or stable fact for future interactions. Use only for meaningful, non-sensitive travel preferences.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"}
                },
                "required": ["key", "value"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "retrieve_memory",
            "description": "Retrieve relevant memories for the currently identified customer.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
                "additionalProperties": False
            }
        }
    ]
