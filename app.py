import os
import csv
from datetime import datetime, time, timedelta
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from model import view_result_regression, predict
from helpers import apology, login_required
import numpy as np
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
        global user_c_id
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
        if not check_password_hash(d[0]["password"],o_password):
            return apology("Incorrect old password!")
        else:
            db.execute("UPDATE user SET password = ? WHERE id = ?", generate_password_hash(password,method='pbkdf2:sha256', salt_length=8), u4)
        return redirect("/login")
    else:
        return render_template("changepwd.html")

@app.route("/homepage")
@login_required
def home():
    try:
        user_details = db.execute("""
            SELECT id, username, email, time_joined, curr_weight, target_weight, height, gender, age, activity_level
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

        user_details = db.execute("SELECT * FROM calorie_details WHERE user_id = ? AND date_log = ?", user_c_id, date_log)

        if(user_details):
            db.execute("UPDATE calorie_details SET calories = ? WHERE user_id = ? AND date_log = ?", calories, user_c_id, date_log)
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
    
@app.route("/calories_automated", methods=["GET", "POST"])
@login_required
def calories_automated():
    # The `user_id` should be retrieved from the session
    user_id = user_c_id  # Ensure you have user_id set in the session
    img = None
    if request.method == "POST":
        try:
        # Retrieve data from form
            if 'mess_menu' in request.files:
                img = request.files['mess_menu']
            else:
                return 'No image uploaded'
            from datetime import datetime
            today_date = datetime.today().date()
            date_log = today_date.strftime('%Y-%m-%d')
            from genai import get_calories
            img.save('tmp.jpg')
            from PIL import Image
            img = Image.open('tmp.jpg')
            calories = get_calories(img)
            print (calories)
            if calories < 0:
                flash ("An Error Occured !")

            else:
            # Check if calories or date_log is not provided
                if not img:
                    flash("Missing image!", 400)
                    er+=1
                user_details = []
                # print (date_log)
                try:
                    user_details = db.execute("SELECT * FROM calorie_details WHERE user_id = ? AND date_log = ?", user_c_id, date_log)
                except Exception as e:
                    return apology ("An error occurred while executing your request ! ", e)
                # print(user_details)
                if(len(user_details)>=1):
                    try: 
                        db.execute("UPDATE calorie_details SET calories = ? WHERE user_id = ? AND date_log = ?", calories, user_c_id, date_log)
                        flash ("Another record for the same day was found, the number of calories has been updated!")
                    except Exception as e:
                        return apology ("An error occurred while executing your request !", e)
                else:
                    try:
                        db.execute("INSERT INTO calorie_details (user_id, calories, date_log) VALUES (?, ?, ?)",
                                user_id, calories, date_log)
                        flash ("Calorie details added successfully!")
                    except Exception as e:
                        return apology ("An error occurred while executing your request  ", e)
                
                return redirect(url_for("view_calories"))
                
        except:
            return apology("Error uploading calories!", 400)
    else:  # If method is GET
        return render_template("calories_automated.html")
       
@app.route("/exercise", methods=["GET", "POST"])
@login_required
def exercise():
    user_id = session["user_id"]  # Ensure you have user_id set in the session
    
    if request.method == "POST":
            try:
            # Retrieve data from form
                distance_covered = request.form.get("distance_covered")
                time_taken = request.form.get("time_taken")
                date_log = request.form.get("date_log")

                # Check if distance_covered, time_taken, or date_log is not provided
                if not distance_covered or not time_taken or not date_log:
                    return apology("Missing exercise details or date!", 400)

                # Check if a record for that user and date already exists
                user_details = db.execute("SELECT * FROM exercise_details WHERE user_id = ? AND date_log = ?", user_id, date_log)
                
                if user_details:
                    # There's already a record for that day, so accumulate the distances and times
                    db.execute("UPDATE exercise_details SET distance_covered = distance_covered + ?, time_taken = time_taken + ? WHERE user_id = ? AND date_log = ?",
                            distance_covered, time_taken, user_id, date_log)
                    flash("Exercise details for the day updated successfully!")
                else:
                    # No record for that day exists, insert new entry
                    db.execute("INSERT INTO exercise_details (user_id, distance_covered, time_taken, date_log) VALUES (?, ?, ?, ?)",
                            user_id, distance_covered, time_taken, date_log)
                    flash("New exercise details added successfully!")

                return redirect(url_for("exercise"))
            except:
                return apology("Error uploading exercise details!", 400)
    else:  # If method is GET
        return render_template("exercise.html")


@app.route("/log_weight", methods=["GET", "POST"])
@login_required
def log_weight():
    user_id = session["user_id"]  # Get the user's ID from the session
    
    if request.method == "POST":
        weight = request.form.get("weight")
        date_log = request.form.get("date_log")
        
        # Validate form input
        if not weight or not date_log:
            return apology("Must provide weight and date", 400)
        
        # Check for existing weight details for that date
        user_details = db.execute("SELECT * FROM weight_details WHERE user_id = ? AND date_log = ?", user_id, date_log)
        if user_details:
            # Update the existing record with the new weight
            db.execute("UPDATE weight_details SET weight = ? WHERE user_id = ? AND date_log = ?", weight, user_id, date_log)
            flash("A record for that day already exists! Weight updated successfully!")
        else:
            # Insert the new weight log
            db.execute("INSERT INTO weight_details (user_id, weight, date_log) VALUES (?, ?, ?)", user_id, weight, date_log)
            flash("Weight logged successfully!")
            
            # Get the latest weight log date
            latest_log = db.execute("SELECT MAX(date_log) as latest_date FROM weight_details WHERE user_id = ?", user_id)
            # Check if the new log is the latest
            if latest_log and latest_log[0]['latest_date'] <= date_log:
                # Update the user's current weight
                db.execute("UPDATE user SET curr_weight = ? WHERE id = ?", weight, user_id)
                flash("Current weight updated successfully!")
        
        return redirect(url_for("log_weight"))
    else:
        # Display the form to log a new weight
        return render_template("weight.html")

@app.route("/activity_level", methods=["GET", "POST"])
@login_required
def activity_level():
    if request.method == "POST":
        user_id = user_c_id
        level = request.form.get("activity_level")
        
        # Assuming 'db' is the database connection object
        db.execute("UPDATE user SET activity_level = ? WHERE id = ?", (int)(level), user_id)
        
        flash("Activity level updated successfully!")
        return redirect(url_for('activity_level'))

    # If GET request or initial page load
    return render_template("activity_level.html")
@app.route("/generate_fitness_plan", methods=["GET", "POST"])
@login_required
def generate_fitness_plan():
    if request.method == "POST":
        # Retrieve data from form
        time_to_lose_weight = request.form.get("time_to_lose_weight")
        daily_activity_minutes = request.form.get("daily_activity_minutes")
        
        user_details = db.execute("SELECT curr_weight, target_weight, height, gender, age FROM user WHERE id = ?", user_c_id)

        c_weight = user_details[0]["curr_weight"]
        t_weight = user_details[0]["target_weight"]
        gender = user_details[0]["gender"]
        age = user_details[0]["age"]
        height = user_details[0]["height"]
        diff = c_weight-t_weight
        a = db.execute("SELECT activity_level FROM user WHERE id = ?", user_c_id)
        print(a)
        print(f"Length of a is {len(a)}")
        al = 1.3 # default
        if(gender == "male"):
            if(a[0]['activity_level']):
                al = 0.2*(a[0]["activity_level"]+5)
                print(f"Activity Level multiplier is: {al}")
            bmr = (66+13.7*c_weight+5*height-6.8*age)*al
        else:
            if(a[0]['activity_level']):
                al = 0.15*(a[0]["activity_level"]+4)
                print(f"Activity Level multiplier is: {al}")
            bmr = (655+9.6*c_weight+1.8*height-4.7*age)*al
        cal = db.execute("SELECT AVG(calories) as average_daily_calories FROM calorie_details WHERE user_id = ?", user_c_id)
        print(cal)
        if not(cal[0]['average_daily_calories']):
            flash("You need to enter atleast one food log to generate fitness plan!")
            return redirect(url_for('calories'))
        avg_cal = cal[0]["average_daily_calories"]
        deficit = diff*7700
        print(f"deficit: {deficit}")
        print(f"bmr: {bmr}")
        print(f"avg_cal: {avg_cal}")
        exer_burn = (deficit/float(time_to_lose_weight))+avg_cal-bmr
        print(f"exer_burn: {exer_burn}")
        val = np.array([c_weight, exer_burn])
        reg, scaler = view_result_regression()
        res = predict(val, reg, scaler)
        print(f"res: {res}")
        d_hour = float(daily_activity_minutes)/60
        if(res[0] < 0):
            res[0] *= -1
        severity = db.execute("SELECT severity FROM user_illness WHERE user_id = ?", user_c_id)
        f = 0
        for s in severity:
            if(s["severity"] >= 4):
                f = 1
                break
        r_speed = res[0]/d_hour
        if(f == 1):
            if(r_speed >= 7.2):
                r_speed = 7.2
                d_hour = res[0]/r_speed
                daily_activity_minutes = d_hour*60
        g = 0
        if(r_speed > 12):
            r_speed = 12
            d_hour = res[0]/r_speed
            daily_activity_minutes = d_hour*60
            g = 1
        current_date = datetime.now().date()
        db.execute("INSERT INTO fitness_plan_user(user_id,r_calories,r_mins_activity,r_distance, date_log, time_taken) VALUES (?, ?, ?, ?, ?, ?)", user_c_id, exer_burn, int(daily_activity_minutes), res[0], current_date, (int)(time_to_lose_weight))        

        # Placeholder for where you would flash a success message or redirect
        flash("Fitness plan generated successfully!")
        if(f == 1):
            flash("The required speed in your fitness plan is too high(as you have a severe medical condition), hence it has been lowered to near 7.2 km/h and your activity time has been adjusted accordingly!")
        if(g == 1):
            flash("The required speed in your fitness plan was > 12 km/h, it has been reduced to near 12 and the daily activity time has been adjusted accordingly!")
        return redirect(url_for('view_fitness_plans'))  # Redirect to the homepage or dashboard
        
    else:  # If method is GET, display the form
        return render_template("generate_fitness_plan.html")
@app.route("/view_fitness_plans")
@login_required
def view_fitness_plans():
    user_id = user_c_id  # Get the user's ID from the session
    
    # Retrieve the fitness plans for the user from the database
    fitness_plans_raw = db.execute("SELECT * FROM fitness_plan_user WHERE user_id = ?", user_id)
    
    # Calculate the speed for each fitness plan and format the data
    fitness_plans = []
    for plan in fitness_plans_raw:
        if plan["r_mins_activity"]:  # Avoid division by zero
            speed = (plan["r_distance"] / (plan["r_mins_activity"] / 60))  # Convert minutes to hours and calculate speed
        else:
            speed = 0
        plan["speed"] = speed  # Add speed to the plan
        fitness_plans.append(plan)
    
    return render_template("view_fitness_plans.html", fitness_plans=fitness_plans)
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
        return redirect(url_for("home"))  # Replace some_page with your desired endpoint

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
    calorie_details = db.execute("SELECT * FROM calorie_details WHERE user_id = ? ORDER BY date_log ASC", session["user_id"])
    return render_template("view_calories.html", calorie_details=calorie_details)

@app.route("/view_weights")
@login_required
def view_weights():
    # Fetch the weight details for the logged-in user, ordered by date_log ascending
    weight_details = db.execute("SELECT * FROM weight_details WHERE user_id = ? ORDER BY date_log ASC", session["user_id"])
    
    # Pass the ordered weight details to the template
    return render_template("view_weights.html", weight_details=weight_details)

@app.route("/view_exercises")
@login_required
def view_exercises():
    # Retrieve exercise details for the current user
    exercise_details_raw = db.execute("SELECT * FROM exercise_details WHERE user_id = ? ORDER BY date_log ASC", session["user_id"])
    
    # Calculate speed for each record and add it to the details
    exercise_details = []
    for detail in exercise_details_raw:
        speed = 0
        if detail["time_taken"]:  # To avoid division by zero
            # Convert time from minutes to hours and calculate speed
            speed = detail["distance_covered"] / (detail["time_taken"] / 60.0)
        # Append the detail with speed to the list
        exercise_details.append({
            "date_log": detail["date_log"],
            "distance_covered": detail["distance_covered"],
            "time_taken": detail["time_taken"],
            "speed": speed  # This is the speed in km/h
        })

    return render_template("view_exercises.html", exercise_details=exercise_details)
