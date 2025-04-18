# modules/pos_manager.py
from modules.models import Client, Reservation, Payment

class POSManager:
    """Handles core business logic: reservations, check-ins, check-outs, and payments."""
    def __init__(self):
        self.clients = {}         # Key: client_id
        self.reservations = {}    # Key: reservation_id
        self.payments = {}        # Key: payment_id

    def create_client(self, name, contact="Not Provided", phone: str ="", email: str=""):
        client = Client(name, contact, phone, email)
        self.clients[client.id] = client
        return client

    def create_reservation(self, client_name, room_number, check_in, check_out):
        # Lookup client by name; create if not found.
        client = next((c for c in self.clients.values() if c.name == client_name), None)
        if not client:
            client = self.create_client(client_name)
        try:
            reservation = Reservation(client, room_number, check_in, check_out)
            self.reservations[reservation.id] = reservation
            return reservation
        except Exception as e:
            print(f"Reservation creation error: {e}")
            return None

    def get_reservations(self):
        return list(self.reservations.values())

    def checkin(self, reservation_id):
        reservation = self.reservations.get(reservation_id)
        if reservation and not reservation.checked_in:
            reservation.checked_in = True
            return True
        return False

    def get_pending_checkins(self):
        return [res for res in self.reservations.values() if not res.checked_in]

    def checkout(self, reservation_id):
        reservation = self.reservations.get(reservation_id)
        if reservation and reservation.checked_in and not reservation.checked_out:
            reservation.checked_out = True
            # Here you might calculate the stay cost. For demonstration we return a dummy value.
            amount_due = 100
            return True, amount_due
        return False, 0

    def get_active_checkins(self):
        return [res for res in self.reservations.values() if res.checked_in and not res.checked_out]

    def get_clients(self):
        return list(self.clients.values())

    def process_payment(self, reservation_id, payment_method, amount):
        reservation = self.reservations.get(reservation_id)
        if reservation:
            payment = Payment(reservation, payment_method, amount)
            self.payments[payment.id] = payment
            return payment
        return None

    def get_payments(self):
        return list(self.payments.values())