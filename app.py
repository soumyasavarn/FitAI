import os
import csv
from datetime import datetime, time, timedelta
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)  # Or another secret key
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fitness.db")
        
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def default_page():

    return render_template("layout.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("id"):
            return apology("must provide id", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE id = ?", request.form.get("id"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        global user_c_id;
        user_c_id = rows[0]["id"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Clear the entire session
    session.clear()
    return redirect(url_for('login'))


@app.route("/register", methods=["GET","POST"])
def register():
    """Register user"""
    if request.method == "POST":
        id = request.form.get("id")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        c_password = request.form.get("confirmation")
        curr_weight = request.form.get("curr_weight")
        target_weight = request.form.get("target_weight")
        height = request.form.get("height")
        gender = request.form.get("gender")
        age = request.form.get("age")
        time_joined = datetime.now()
        if not password or not c_password:
            return apology("Either field Password or Re-enter Password is blank")
        if password != c_password:
            return apology("The two passwords do not match")
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        try:
            db.execute("INSERT INTO user (id, username, email, password, time_joined, curr_weight, target_weight, height, gender, age) VALUES(?,?,?,?,?,?,?,?,?,?)", id, username, email, hash, time_joined, curr_weight, target_weight, height, gender, age)
        except ValueError:
            return apology("ID already in use, please enter a different ID!")
        return render_template("login.html")
    else:
        return render_template("register.html")
    
@app.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    u4 = user_c_id
    if request.method == "POST":
        o_password = request.form.get("originalpwd")
        password = request.form.get("newpwd")
        c_password = request.form.get("confirmpwd")
        if not o_password:
            return apology("Enter original password!")
        if not password:
            return apology("Enter new password!")
        if not c_password:
            return apology("Re-enter new password!")
        if password == o_password:
            return apology("Old password and New password cannot be the same!")
        if password != c_password:
            return apology("Passwords do not match!")
        d = db.execute("SELECT * FROM user WHERE id = ?", u4)
        if not check_password_hash(d[0]["hash"],o_password):
            return apology("Incorrect old password!")
        else:
            db.execute("UPDATE user SET hash = ? WHERE id = ?", generate_password_hash(password), u4)
        return redirect("/login")
    else:
        return render_template("changepwd.html")

@app.route("/homepage")
@login_required
def home():
    try:
        user_details = db.execute("""
            SELECT id, username, email, time_joined, curr_weight, target_weight, height, gender, age
            FROM user
            WHERE id = ? 
        """, (user_c_id))
        print(user_details)
        h = user_details[0]["height"]/100
        bmi = round((user_details[0]["curr_weight"]/(h*h)), 2)
        bmi_target = round((user_details[0]["target_weight"]/(h*h)), 2)
        # Pass the data to the menu template
        return render_template("home.html", user_details= user_details, bmi=bmi, bmi_target = bmi_target)
    
    except Exception as e:
        # Log the error for debugging purposes
        print(f"An error occurred: {e}")
        # Return an error message to the user
        return render_template("error.html", message="An internal server error occurred.")

@app.route("/calories", methods=["GET", "POST"])
@login_required
def calories():
    # The `user_id` should be retrieved from the session
    user_id = user_c_id  # Ensure you have user_id set in the session

    if request.method == "POST":
        # Retrieve data from form
        calories = request.form.get("calories")
        date_log = request.form.get("date_log")

        # Check if calories or date_log is not provided
        if not calories or not date_log:
            return apology("Missing calories or date!", 400)

        user_details = db.execute("SELECT * FROM calorie_details WHERE id = ? AND date_log = ?", user_c_id, date_log)

        if(user_details):
            db.execute("UPDATE calorie_details SET calories = ? WHERE id = ? AND date_log = ?", calories, user_c_id, date_log)
            flash("Another record for the same day was found, the number of calories has been updated!")
        else:
            # Insert the form data into the calorie_details table
            db.execute("INSERT INTO calorie_details (user_id, calories, date_log) VALUES (?, ?, ?)",
                    user_id, calories, date_log)

            # Flash a success message
            flash("Calorie details added successfully!")
        return redirect(url_for("calories"))

    else:  # If method is GET
        return render_template("calories.html")
    
@app.route("/exercise", methods=["GET", "POST"])
@login_required
def exercise():
    # The `user_id` should be retrieved from the session
    user_id = user_c_id  # Ensure you have user_id set in the session

    if request.method == "POST":
        # Retrieve data from form
        steps = request.form.get("steps")
        date_log = request.form.get("date_log")

        # Check if steps or date_log is not provided
        if not steps or not date_log:
            return apology("Missing steps or date!", 400)

        user_details = db.execute("SELECT * FROM exercise_details WHERE user_id = ? AND date_log = ?", user_c_id, date_log)
        if(user_details):
            prev_steps = user_details[0]["steps"]
            db.execute("UPDATE exercise_details SET steps = ? WHERE user_id = ? AND date_log = ?", steps + prev_steps, user_c_id, date_log)
            flash("Another record for the same day was found, it has been updated with the total!")
        else:
            # Insert the form data into the exercise_details table
            db.execute("INSERT INTO exercise_details (user_id, steps, date_log) VALUES (?, ?, ?)",
                   user_id, steps, date_log)
            # Flash a success message
            flash("Exercise details added successfully!")
        return redirect(url_for("exercise"))

    else:  # If method is GET
        return render_template("exercise.html")

@app.route("/log_weight", methods=["GET", "POST"])
@login_required
def log_weight():
    # The `user_id` should be retrieved from the session
    user_id = user_c_id  # Ensure you have user_id set in the session
    
    if request.method == "POST":
        weight = request.form.get("weight")
        date_log = request.form.get("date_log")
        
        # Validate form input
        if not weight or not date_log:
            return apology("Must provide weight and date", 400)
        
        user_details = db.execute("SELECT * FROM weight_details WHERE user_id = ? AND date_log = ?", user_id, date_log)
        if(user_details):
            db.execute("UPDATE weight_details SET weight = ? WHERE user_id = ? AND date_log = ?", weight, user_id, date_log)
            flash("A record for that day already exists! Weight updated successfully!")
        else:
            # Insert the form data into the weight_details table
            db.execute("INSERT INTO weight_details (user_id, weight, date_log) VALUES (?, ?, ?)", 
                    user_id, weight, date_log)
            flash("Weight logged successfully!")
        return redirect(url_for("log_weight"))
    else:
        return render_template("weight.html")

@app.route("/add_illness", methods=["GET", "POST"])
@login_required
def add_illness():
    if request.method == "POST":
        # Get the selected illness id and severity from the form
        selected_illness_id = request.form.get("illness")
        illness_severity = request.form.get("severity")
        
        # Get the user_id from the session
        user_id = session["user_id"]

        # Insert illness and severity into the user_illness table
        db.execute("INSERT INTO user_illness (illness_id, user_id, severity) VALUES (?, ?, ?)", 
                   selected_illness_id, user_id, illness_severity)
        
        flash("Illness added to your history.")
        return redirect(url_for("homepage"))  # Replace some_page with your desired endpoint

    # If GET request, fetch illnesses with their ids from the database
    illnesses = db.execute("SELECT id, illness_name FROM illness_details")
    return render_template("add_illness.html", illnesses=illnesses)

@app.route("/view_illness_history")
@login_required
def view_illness_history():
    user_id = session["user_id"]

    # Fetch the user's illness history along with the illness details
    illness_history = db.execute("""
        SELECT ui.severity, id.illness_name 
        FROM user_illness ui
        JOIN illness_details id ON ui.illness_id = id.id
        WHERE ui.user_id = ?
    """, user_id)
    
    return render_template("view_illness_history.html", illness_history=illness_history)

@app.route("/view_calories")
@login_required
def view_calories():
    calorie_details = db.execute("SELECT * FROM calorie_details WHERE user_id = ?", session["user_id"])
    return render_template("view_calories.html", calorie_details=calorie_details)

@app.route("/view_weights")
@login_required
def view_weights():
    weight_details = db.execute("SELECT * FROM weight_details WHERE user_id = ?", session["user_id"])
    return render_template("view_weights.html", weight_details=weight_details)

@app.route("/view_exercises")
@login_required
def view_exercises():
    exercise_details = db.execute("SELECT * FROM exercise_details WHERE user_id = ?", session["user_id"])
    return render_template("view_exercises.html", exercise_details=exercise_details)
