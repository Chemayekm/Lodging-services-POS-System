# modules/pos_manager.py
from modules.models import Client, Reservation, Payment

class POSManager:
    """Handles core business logic: reservations, check-ins, check-outs, and payments."""
    def __init__(self):
        self.clients = {}         # Key: client_id
        self.reservations = {}    # Key: reservation_id
        self.payments = {}        # Key: payment_id

    def create_client(self, name, contact="Not Provided", phone: str ="1234567", email: str=""):
        client = Client(name, contact, phone, email)
        self.clients[client.id] = client
        return client
    
    def delete_client(self, client_id: str) -> bool:
        """
        Deletes a client record from the clients dictionary.
        Returns True if the deletion was successful.
        """
        if client_id in self.clients:
            del self.clients[client_id]
            return True
        return False


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
        
    def delete_reservation(self, reservation_id: str) -> bool:
        """
        Deletes a reservation record.
        Returns True if successful.
        """
        if reservation_id in self.reservations:
            del self.reservations[reservation_id]
            return True
        return False


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
            nights = reservation.number_of_nights()
            rate_per_night = 100  # Example rate per night
            # Here you might calculate the stay cost. For demonstration we return a dummy value.
            amount_due = nights * rate_per_night
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
    
    def generate_report(self, rate_per_night=100):
        """
        Generate a summary report that groups checked-out reservations by client.
        Each report row contains:
          - client_name
          - rooms (comma-separated list)
          - total_nights
          - total_amount (sum of nights * rate)
          - amount_paid (sum of payments for checked-out reservations)
        """
        report_data = {}
        # Process reservations that have been checked out.
        for reservation in self.reservations.values():
            if reservation.checked_out:
                client_id = reservation.client.id
                if client_id not in report_data:
                    report_data[client_id] = {
                        'client_name': reservation.client.name,
                        'rooms': set(),
                        'total_nights': 0,
                        'total_amount': 0,
                        'amount_paid': 0,
                    }
                report_data[client_id]['rooms'].add(reservation.room_number)
                nights = reservation.number_of_nights()
                report_data[client_id]['total_nights'] += nights
                report_data[client_id]['total_amount'] += nights * rate_per_night

        # Process payments for checked-out reservations.
        for payment in self.payments.values():
            if payment.reservation.checked_out:
                client_id = payment.reservation.client.id
                if client_id in report_data:
                    report_data[client_id]['amount_paid'] += payment.amount

        # Convert the room sets into comma-separated strings and compile list.
        report_list = []
        for client_id, data in report_data.items():
            data['rooms'] = ", ".join(data['rooms'])
            report_list.append(data)
        return report_list
