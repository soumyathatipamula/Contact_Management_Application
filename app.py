from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "secretkey"


def get_db_connection():
    conn = sqlite3.connect("contacts.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create table
conn = get_db_connection()
conn.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    address TEXT,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL
)
""")
conn.commit()
conn.close()


@app.route("/")
def index():
    conn = get_db_connection()
    contacts = conn.execute("SELECT * FROM contacts").fetchall()
    conn.close()
    return render_template("index.html", contacts=contacts)


# ---------------- ADD CONTACT ----------------
@app.route("/add", methods=["GET", "POST"])
def add_contact():
    if request.method == "POST":
        first = request.form["first_name"].strip()
        last = request.form["last_name"].strip()
        address = request.form["address"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()

        session.pop('_flashes', None)

        if not first.isalpha() or not last.isalpha():
            flash("First name and Last name must contain only letters", "danger")
            return render_template(
                "add_contact.html",
                first_name=first, last_name=last,
                address=address, email=email, phone=phone
            )

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address", "danger")
            return render_template(
                "add_contact.html",
                first_name=first, last_name=last,
                address=address, email=email, phone=phone
            )

        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must contain exactly 10 digits", "danger")
            return render_template(
                "add_contact.html",
                first_name=first, last_name=last,
                address=address, email=email, phone=phone
            )

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO contacts (first_name, last_name, address, email, phone) VALUES (?, ?, ?, ?, ?)",
                (first, last, address, email, phone)
            )
            conn.commit()
            conn.close()
            flash("Contact added successfully", "success")
            return redirect(url_for("index"))

        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")
            return render_template(
                "add_contact.html",
                first_name=first, last_name=last,
                address=address, email=email, phone=phone
            )

    return render_template("add_contact.html")


# ---------------- EDIT CONTACT ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_contact(id):
    conn = get_db_connection()
    contact = conn.execute("SELECT * FROM contacts WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        first = request.form["first_name"].strip()
        last = request.form["last_name"].strip()
        address = request.form["address"].strip()
        email = request.form["email"].strip()
        phone = request.form["phone"].strip()

        session.pop('_flashes', None)

        temp_contact = {
            "first_name": first,
            "last_name": last,
            "address": address,
            "email": email,
            "phone": phone
        }

        if not first.isalpha() or not last.isalpha():
            flash("First name and Last name must contain only letters", "danger")
            return render_template("edit_contact.html", contact=temp_contact)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address", "danger")
            return render_template("edit_contact.html", contact=temp_contact)

        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must contain exactly 10 digits", "danger")
            return render_template("edit_contact.html", contact=temp_contact)

        try:
            conn.execute("""
                UPDATE contacts
                SET first_name=?, last_name=?, address=?, email=?, phone=?
                WHERE id=?
            """, (first, last, address, email, phone, id))
            conn.commit()
            flash("Contact updated successfully", "success")
            conn.close()
            return redirect(url_for("index"))

        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")
            return render_template("edit_contact.html", contact=temp_contact)

    conn.close()
    return render_template("edit_contact.html", contact=contact)


@app.route("/delete/<int:id>")
def delete_contact(id):
    session.pop('_flashes', None)
    conn = get_db_connection()
    conn.execute("DELETE FROM contacts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Contact deleted", "warning")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
