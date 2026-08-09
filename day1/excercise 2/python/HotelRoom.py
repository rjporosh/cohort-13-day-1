class HotelRoom:
    def __init__(self, room_number: int, price_per_night: float):
        if room_number <= 0:
            raise ValueError("Room number must be greater than zero.")

        if price_per_night <= 0:
            raise ValueError("Price must be greater than zero.")

        self._room_number = room_number
        self._price_per_night = price_per_night
        self._is_available = True

    @property
    def room_number(self) -> int:
        return self._room_number

    @property
    def price_per_night(self) -> float:
        return self._price_per_night

    @property
    def is_available(self) -> bool:
        return self._is_available

    def book(self) -> None:
        if not self._is_available:
            raise RuntimeError("Room is already booked.")

        self._is_available = False

    def checkout(self) -> None:
        if self._is_available:
            raise RuntimeError("Room is already available.")

        self._is_available = True