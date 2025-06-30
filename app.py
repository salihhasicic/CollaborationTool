from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy-Userdaten (kann später durch DB ersetzt werden)
users = {
    "salih": {
        "username": "salih",
        "name": "Salih Kaya",
        "photo": "image.png",
        "skills": ["Python", "Flask", "HTML"]
    },
    "lea": {
        "username": "lea",
        "name": "Lea Meier",
        "photo": "image.png",
        "skills": ["UX", "CSS", "JavaScript"]
    }
}

# Startseite leitet weiter zum Login
@app.route("/")
def index():
    return redirect(url_for("login"))

# Login-Ansicht + Verarbeitung
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username in users:
            return redirect(url_for("profile", username=username))
        return render_template("login.html", error="Benutzer nicht gefunden.")
    return render_template("login.html")

# Profilanzeige für Benutzer
@app.route("/profile/<username>")
def profile(username):
    user = users.get(username)
    if user:
        return render_template("profile.html", user=user)
    return "Benutzer nicht gefunden", 404

if __name__ == "__main__":
    app.run(debug=True,  port=5001)
