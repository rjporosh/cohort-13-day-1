import json
import os

from openai import OpenAI
from tools import build_tool_definitions


def _positive_int(name: str, default: int) -> int:
    try:
        return max(1, int(os.getenv(name, default)))
    except ValueError:
        return default


class FlightCustomerSupportAgent:

    def __init__(self, tools):
        self.client = OpenAI()
        self.tools = tools
        self.tool_definitions = build_tool_definitions()
        self.history = []

        self.max_iterations = _positive_int("MAX_AGENT_ITERATIONS", 8)
        self.max_tool_calls = _positive_int("MAX_TOOL_CALLS", 12)
        self.max_input_length = _positive_int("MAX_INPUT_LENGTH", 2000)

        self.instructions = """
You are an airline customer support agent.

Help customers with their flight bookings using only the available tools.

Rules:
1. If a booking reference is provided, use find_booking.
2. Once a booking is found, application state remembers it. Follow-up questions
   must reuse the selected booking; do not ask for the reference again.
3. Use get_flight_information for status, delay, departure, arrival, terminal and gate.
4. Use booking information for seat, meal, baggage and booking status.
5. Before changing a seat, let the change_seat tool check availability.
6. Use change_meal for meal changes.
7. Use retrieve_memory when a response may depend on a previously remembered
   customer preference or fact.
8. Use save_memory for meaningful, stable, non-sensitive travel preferences
   such as preferred meal or airport. Do not save secrets, passwords, payment
   details, or unnecessary personal information.
9. Memory is customer-specific. Never reveal or use another customer's memory.
10. Never invent booking, flight, seat, baggage or memory information.
11. If a tool reports failure, explain the failure and do not pretend it succeeded.
12. Be concise, friendly and professional.
13. If there is no selected booking and booking-specific information is needed,
    ask for the booking reference.
"""

    def ask(self, message):
        if not isinstance(message, str) or not message.strip():
            return "Please enter a question."

        if len(message) > self.max_input_length:
            return f"Your message is too long. Please keep it under {self.max_input_length} characters."

        self._current_message = message.strip()
        self.history.append({"role": "user", "content": self._current_message})

        total_tool_calls = 0

        for _ in range(self.max_iterations):
            response = self.client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
                instructions=self.instructions,
                input=self.history,
                tools=self.tool_definitions
            )

            tool_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:
                self.history.extend(response.output)
                return response.output_text

            if total_tool_calls + len(tool_calls) > self.max_tool_calls:
                return (
                    "I couldn't safely complete that request within the allowed "
                    "number of tool attempts. Please try again."
                )

            self.history.extend(response.output)

            for call in tool_calls:
                try:
                    arguments = json.loads(call.arguments)
                    result = self.execute_tool(call.name, arguments)
                except (json.JSONDecodeError, KeyError, TypeError) as error:
                    result = {
                        "success": False,
                        "message": f"Invalid tool request: {error}"
                    }

                self.history.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result)
                })
                total_tool_calls += 1

        return (
            "I couldn't complete the request within the configured maximum "
            "number of attempts. Please try a simpler request."
        )


    def _find_booking_safely(self, booking_reference):
        result = self.tools.find_booking(booking_reference)

        if result.get("success"):
            new_customer_id = result.get("customer_id")
            previous_customer_id = getattr(self.tools.state, "previous_customer_id", None)

            # A single agent process may serve multiple customers. Do not allow
            # the previous customer's conversation to enter the new customer's context.
            if (
                previous_customer_id is not None
                and new_customer_id != previous_customer_id
            ):
                self.history = [
                    {"role": "user", "content": self._current_message}
                ]

            self.tools.state.previous_customer_id = new_customer_id

        return result

    def execute_tool(self, name, arguments):
        handlers = {
            "find_booking": lambda: self._find_booking_safely(
                arguments["booking_reference"]
            ),
            "get_flight_information": self.tools.get_flight_information,
            "change_seat": lambda: self.tools.change_seat(arguments["seat"]),
            "change_meal": lambda: self.tools.change_meal(arguments["meal"]),
            "save_memory": lambda: self.tools.save_memory(
                arguments["key"], arguments["value"]
            ),
            "retrieve_memory": lambda: self.tools.retrieve_memory(
                arguments["query"]
            ),
        }

        handler = handlers.get(name)
        if not handler:
            return {"success": False, "message": f"Unknown tool: {name}"}

        try:
            return handler()
        except Exception as error:
            return {
                "success": False,
                "message": "The requested operation could not be completed safely."
            }
