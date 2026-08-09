class HotelRoom {
    #available = true;

    constructor(roomNumber, pricePerNight) {
        if (roomNumber <= 0) {
            throw new Error("Room number must be greater than zero.");
        }

        if (pricePerNight <= 0) {
            throw new Error("Price must be greater than zero.");
        }

        this.roomNumber = roomNumber;
        this.pricePerNight = pricePerNight;
    }

    get isAvailable() {
        return this.#available;
    }

    book() {
        if (!this.#available) {
            throw new Error("Room is already booked.");
        }

        this.#available = false;
    }

    checkout() {
        if (this.#available) {
            throw new Error("Room is already available.");
        }

        this.#available = true;
    }
}