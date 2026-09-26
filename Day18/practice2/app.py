from database import (
    Database,
    BookingRepository,
    FlightRepository
)

from services import FlightSupportService
from tools import SessionState, FlightTools
from agent import FlightCustomerSupportAgent


def create_agent():

    db = Database()
    db.initialize()

    booking_repository = BookingRepository(db)
    flight_repository = FlightRepository(db)

    service = FlightSupportService(
        booking_repository,
        flight_repository
    )

    state = SessionState()

    tools = FlightTools(
        service,
        state
    )

    return FlightCustomerSupportAgent(tools)


def main():

    agent = create_agent()

    print("✈️ Flight Customer Support Agent")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("Customer: ")

        if user_input.lower() == "exit":
            break

        try:
            response = agent.ask(user_input)

            print(f"\nAgent: {response}\n")

        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()