from flask import Flask, render_template, request, redirect, url_for, session
from ultralytics import YOLO
import os
import time
from datetime import datetime
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Upload folder
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Load YOLO model
model = YOLO("model.pt")

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",            
            password="Xaseelkhsroo_1",
            database="EvoWaste"
        )
        return connection
    except Error as e:
        print("Error while connecting to MySQL:", e)
        return None

# ---------------------------
# AUTHENTICATION ROUTES
# ---------------------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home_page"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_profiles WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user["password"] == password:
            session["user_id"] = user["id"]
            session["first_name"] = user["first_name"]
            session["last_name"] = user["last_name"]
            session["email"] = user["email"]
            session["location"] = user["location"] or ""
            return redirect(url_for("home_page"))
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form.get("name")
        first_name, *last_name_parts = full_name.split(" ")
        last_name = " ".join(last_name_parts) if last_name_parts else ""
        email = request.form.get("email")
        password = request.form.get("password")
        location = request.form.get("location")

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = """
            INSERT INTO user_profiles (first_name, last_name, location, email, password)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (first_name, last_name, location, email, password))
            conn.commit()
            cursor.close()
            conn.close()

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_profiles WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            session["user_id"] = user["id"]
            session["first_name"] = user["first_name"]
            session["last_name"] = user["last_name"]
            session["email"] = user["email"]
            session["location"] = user["location"] or ""
            
            return redirect(url_for("home_page"))
        except Error as e:
            print("Signup error:", e)
            cursor.close()
            conn.close()
            return render_template("signup.html", error="Email already exists")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------
# HOMEPAGE ROUTE
# ---------------------------

@app.route("/home")
def home_page():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template(
        "home.html",
        user_name=session.get("first_name"),
        location=session.get("location", "Unknown")
    )


# ---------------------------
# CLASSIFICATION PAGE
# ---------------------------

def save_classification(user_id, image_path, classification, location, confidence):
    now = datetime.now()
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO classification_results (user_id, image_path, classification, date, time, location, confidence)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        user_id,
        image_path,
        classification,
        now.date(),
        now.time(),
        location,
        confidence
    ))
    conn.commit()
    cursor.close()
    conn.close()


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))

    prediction = None
    confidence = None
    image_path = None
    upload_location = session.get("location", "")

    if request.method == "POST":
        file = request.files.get("image")
        upload_location = request.form.get("uploadLocation", session.get("location", "Unknown"))

        if not file or file.filename == "":
            return render_template("upload.html", error="No file selected", location=upload_location)

        # Save file
        filename = str(int(time.time())) + "_" + file.filename
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        # YOLO prediction
        results = model.predict(save_path)[0]
        pred_class = results.names[results.probs.top1]
        conf = float(results.probs.top1conf)

        prediction = pred_class
        confidence = round(conf * 100, 2)
        image_path = "uploads/" + filename

        # Save to DB
        save_classification(session["user_id"], image_path, prediction, upload_location, confidence)

        # Update session
        session["location"] = upload_location
        session.modified = True

    return render_template(
        "upload.html",
        prediction=prediction,
        confidence=confidence,
        image_path=image_path,
        location=upload_location
    )


# ---------------------------
# HISTORY PAGE
# ---------------------------

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT image_path, classification, date, time, location, confidence
        FROM classification_results
        WHERE user_id = %s
        ORDER BY date DESC, time DESC
    """, (session["user_id"],))
    history_data = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("history.html", history=history_data)


# ---------------------------
# PROFILE PAGE
# ---------------------------

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        new_location = request.form.get("location")
        new_name = request.form.get("name")

        first_name, *last_name_parts = new_name.split(" ")
        last_name = " ".join(last_name_parts) if last_name_parts else ""

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_profiles
            SET first_name=%s, last_name=%s, location=%s
            WHERE id=%s
        """, (first_name, last_name, new_location, session["user_id"]))
        conn.commit()
        cursor.close()
        conn.close()

        # Update session
        session["first_name"] = first_name
        session["last_name"] = last_name
        session["location"] = new_location
        session.modified = True

    return render_template(
        "profile.html",
        name=f"{session.get('first_name')} {session.get('last_name')}",
        email=session.get("email"),
        location=session.get("location", "Not set")
    )


# ---------------------------
# MAIN
# ---------------------------

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=5001)
