# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from modules.pos_manager import POSManager

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key in production

# In-memory storage for user credentials.
# In production, use a database and proper password hashing.
user_credentials = {}

# Initialize the POS manager (business logic container)
pos_manager = POSManager()

# Enforce login on all routes except the allowed ones
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'static']
    if request.endpoint not in allowed_routes and not session.get('logged_in'):
        return redirect(url_for('login'))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Sign-up route.
    Allows new users to register by entering a new username and password.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in user_credentials:
            flash("Username already exists. Please choose a different username.", "danger")
        else:
            # In production, remember to hash your passwords
            user_credentials[username] = password
            flash("Sign up successful! You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login route.
    Authenticates users based on the provided username and password.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        stored_password = user_credentials.get(username)
        if stored_password and stored_password == password:
            # Login successful
            session["logged_in"] = True
            session["username"] = username
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log out the current user by clearing the session."""
    session.pop("logged_in", None)
    session.pop("username", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/")
def home():
    """Simple home (dashboard) page."""
    return render_template("base.html")

@app.route("/registrations", methods=["GET", "POST"])
def registrations():
    if request.method == "POST":
        # Process client registration form submission
        name = request.form["name"]
        contact = request.form["contact"]
        phone = request.form["phone"]
        email = request.form["email"]
        client = pos_manager.create_client(name, contact, phone, email)
        if client:
            flash("Client registered successfully!", "success")
        else:
            flash("Error registering client.", "danger")
        # Redisplay the registration page (the table will update)
        return redirect(url_for("registrations"))
    # On GET, display the registration form and the list of registered clients
    clients_list = pos_manager.get_clients()
    return render_template("registrations.html", clients=clients_list)

@app.route("/reservations", methods=["GET", "POST"])
def reservations():
    if request.method == "POST":
        client_name = request.form["client_name"]
        room_number = request.form["room_number"]
        check_in = request.form["check_in"]
        check_out = request.form["check_out"]
        client = pos_manager.clients.get(client_id)
        if not client:
            flash("Invalid client selection.", "danger")
            return redirect(url_for("reservations"))
        reservation = pos_manager.create_reservation(client, room_number, check_in, check_out)
        if reservation:
            flash("Reservation created successfully!", "success")
        else:
            flash("Error creating reservation.", "danger")
        return redirect(url_for("reservations"))
    res_data = pos_manager.get_reservations()
    clients_list = pos_manager.get_clients()
    return render_template("reservations.html", reservations=res_data, clients=clients_list)

@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if request.method == "POST":
        reservation_id = request.form["reservation_id"]
        if pos_manager.checkin(reservation_id):
            flash("Checked in successfully!", "success")
        else:
            flash("Check-in failed. Verify the reservation ID.", "danger")
        return redirect(url_for("checkin"))
    pending_reservations = pos_manager.get_pending_checkins()
    no_res_clients = pos_manager.get_clients_without_reservations()
    return render_template("checkin.html", reservations=pending_reservations, clients_without_reservation=no_res_clients)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        reservation_id = request.form["reservation_id"]
        result, amount_due = pos_manager.checkout(reservation_id)
        if result:
            flash(f"Checked out successfully! Amount Due: ${amount_due}", "success")
        else:
            flash("Checkout failed. Verify the reservation ID.", "danger")
        return redirect(url_for("checkout"))
    active_checkins = pos_manager.get_active_checkins()
    no_res_clients = pos_manager.get_clients_without_reservations()
    return render_template("checkout.html", reservations=active_checkins, clients_without_reservation=no_res_clients)

@app.route("/clients")
def clients():
    clients = pos_manager.get_clients()
    return render_template("clients.html", clients=clients)

@app.route("/payments", methods=["GET", "POST"])
def payments():
    if request.method == "POST":
        reservation_id = request.form["reservation_id"]
        payment_method = request.form["payment_method"]
        amount = request.form["amount"]
        payment = pos_manager.process_payment(reservation_id, payment_method, amount)
        if payment:
            flash("Payment processed successfully!", "success")
        else:
            flash("Payment processing failed. Verify details and try again.", "danger")
        return redirect(url_for("payments"))
    payment_list = pos_manager.get_payments()
    return render_template("payments.html", payments=payment_list)

@app.route("/gallery")
def gallery():
    """
    Gallery page that displays service images.
    For simplicity, a list of image filenames (stored in static/images) is passed to the template.
    """
    images = ["service1.jpg", "service2.jpg", "service3.jpg"]
    return render_template("gallery.html", images=images)

if __name__ == "__main__":
    app.run(debug=True)