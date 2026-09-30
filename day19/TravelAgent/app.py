import os

from database import Database, BookingRepository, FlightRepository
from memory import CustomerMemory
from services import FlightSupportService
from tools import SessionState, FlightTools
from agent import FlightCustomerSupportAgent


def create_agent():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "airline.db")
    memory_path = os.path.join(base_dir, "memory")

    db = Database(db_path)
    db.initialize()

    booking_repository = BookingRepository(db)
    flight_repository = FlightRepository(db)
    memory = CustomerMemory(memory_path)

    service = FlightSupportService(
        booking_repository,
        flight_repository,
        memory
    )

    state = SessionState()
    tools = FlightTools(service, state)

    return FlightCustomerSupportAgent(tools)


def main():
    agent = create_agent()

    print("✈️ Flight Customer Support Agent")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Customer: ")

        if user_input.strip().lower() == "exit":
            break

        try:
            response = agent.ask(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()
