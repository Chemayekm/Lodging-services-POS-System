import datetime
import random  # Import the random module to generate short IDs

class Client:
    """
    Represents a client using the lodging services.
    """
    def __init__(self, name: str, contact: int = "", phone: str = "", email: str = ""):
        self.id = str(random.randint(10000, 99999))  # Generate a 5-digit ID
        self.name = name
        self.contact = contact
        self.phone = phone
        self.email = email

    def __str__(self):
        return f"{self.name} ({self.contact})"


class Reservation:
    """
    Represents a room reservation.
    """
    def __init__(self, client: Client, room_number: str, check_in_date: str, check_out_date: str):
        self.id = str(random.randint(10000, 99999))  # Generate a 5-digit ID
        self.client = client
        self.room_number = room_number
        self.check_in_date = datetime.datetime.strptime(check_in_date, "%Y-%m-%d")
        self.check_out_date = datetime.datetime.strptime(check_out_date, "%Y-%m-%d")
        self.checked_in = False
        self.checked_out = False

    def number_of_nights(self) -> int:
        """
        Returns the number of nights for the reservation.
        """
        delta = self.check_out_date - self.check_in_date
        return delta.days

    def __str__(self):
        return (f"Reservation {self.id} for {self.client.name} in Room {self.room_number} "
                f"from {self.check_in_date.date()} to {self.check_out_date.date()}.")


class Payment:
    """
    Represents a payment made for a reservation.
    """
    def __init__(self, reservation: Reservation, payment_method: str, amount: float):
        self.id = str(random.randint(10000, 99999))  # Generate a 5-digit ID
        self.reservation = reservation
        self.payment_method = payment_method
        self.amount = float(amount)
        self.date = datetime.datetime.now()

    def __str__(self):
        return (f"Payment {self.id}: Reservation {self.reservation.id}, "
                f"Method: {self.payment_method}, Amount: {self.amount} on "
                f"{self.date.strftime('%Y-%m-%d %H:%M:%S')}")