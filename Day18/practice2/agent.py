import json
from openai import OpenAI

from tools import build_tool_definitions


class FlightCustomerSupportAgent:

    def __init__(self, tools):

        self.client = OpenAI()

        self.tools = tools

        self.tool_definitions = build_tool_definitions()

        self.history = []

        self.instructions = """
You are an airline customer support agent.

Your job is to help customers with their flight bookings.

Rules:

1. If the customer gives a booking reference, use find_booking.

2. Once a booking has been found, the application remembers it.
   For follow-up questions, DO NOT ask for the booking reference again.

3. Use get_flight_information for:
   - flight status
   - delay
   - departure time
   - arrival time
   - terminal
   - gate
   - airport information

4. Use the booking information returned by find_booking for:
   - seat
   - meal
   - baggage allowance
   - booking status

5. Use change_seat when the customer asks to change their seat.

6. Use change_meal when the customer asks to change their meal.

7. Never invent flight or booking information.

8. Be concise, friendly and professional.

9. If there is no selected booking and the customer asks about
   booking-specific information, ask for their booking reference.
"""

    def ask(self, message):

        self.history.append({
            "role": "user",
            "content": message
        })

        while True:

            response = self.client.responses.create(
                model="gpt-5.5",
                instructions=self.instructions,
                input=self.history,
                tools=self.tool_definitions
            )

            tool_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:

                self.history.extend(response.output)

                return response.output_text

            self.history.extend(response.output)

            for call in tool_calls:

                arguments = json.loads(
                    call.arguments
                )

                result = self.execute_tool(
                    call.name,
                    arguments
                )

                self.history.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result)
                })

    def execute_tool(self, name, arguments):

        if name == "find_booking":
            return self.tools.find_booking(
                arguments["booking_reference"]
            )

        if name == "get_flight_information":
            return self.tools.get_flight_information()

        if name == "change_seat":
            return self.tools.change_seat(
                arguments["seat"]
            )

        if name == "change_meal":
            return self.tools.change_meal(
                arguments["meal"]
            )

        return {
            "success": False,
            "message": f"Unknown tool: {name}"
        }