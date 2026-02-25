from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class RegisteredPerson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    disability_type = db.Column(db.String(120))
    support_needs = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def geocode_address(address: str):
    """
    Geocode an address using OpenStreetMap Nominatim API.
    This does not require an API key but must respect their usage policy.
    """
    if not address:
        return None, None

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": address, "format": "json", "limit": 1},
            headers={"User-Agent": "disability-support-app/1.0"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            return None, None
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    except Exception:
        return None, None


def find_nearby_services(latitude: float, longitude: float, radius_m=3000):
    """
    Use the Overpass API to find nearby hospitals and police stations.
    Returns a list of services with name, type and coordinates.
    """
    if latitude is None or longitude is None:
        return []

    overpass_url = "https://overpass-api.de/api/interpreter"
    # Overpass QL query:
    # Find hospitals and police within radius of given coordinates
    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius_m},{latitude},{longitude});
      node["amenity"="clinic"](around:{radius_m},{latitude},{longitude});
      node["amenity"="doctors"](around:{radius_m},{latitude},{longitude});
      node["amenity"="police"](around:{radius_m},{latitude},{longitude});
      node["amenity"="fire_station"](around:{radius_m},{latitude},{longitude});
    );
    out body;
    """
    try:
        response = requests.post(
            overpass_url,
            data=query.encode("utf-8"),
            headers={"User-Agent": "disability-support-app/1.0"},
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        elements = data.get("elements", [])
        services = []
        for el in elements:
            tags = el.get("tags", {})
            services.append(
                {
                    "name": tags.get("name") or "Unnamed location",
                    "type": tags.get("amenity", "service"),
                    "lat": el.get("lat"),
                    "lon": el.get("lon"),
                    "address": ", ".join(
                        filter(
                            None,
                            [
                                tags.get("addr:housenumber"),
                                tags.get("addr:street"),
                                tags.get("addr:city"),
                                tags.get("addr:country"),
                            ],
                        )
                    ),
                }
            )
        # Sort by type then name for readability
        services.sort(key=lambda s: (s["type"], s["name"]))
        return services
    except Exception:
        return []


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    full_name = request.form.get("full_name", "").strip()
    if not full_name:
        return redirect(url_for("index"))

    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    city = request.form.get("city", "").strip()
    country = request.form.get("country", "").strip()
    disability_type = request.form.get("disability_type", "").strip()
    support_needs = request.form.get("support_needs", "").strip()

    lat = request.form.get("latitude")
    lon = request.form.get("longitude")

    latitude = float(lat) if lat else None
    longitude = float(lon) if lon else None

    if latitude is None or longitude is None:
        # Try geocoding the textual address if coordinates are missing
        composed_address = ", ".join(
            part for part in [address, city, country] if part
        )
        if composed_address:
            latitude, longitude = geocode_address(composed_address)

    person = RegisteredPerson(
        full_name=full_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        country=country,
        disability_type=disability_type,
        support_needs=support_needs,
        latitude=latitude,
        longitude=longitude,
    )

    db.session.add(person)
    db.session.commit()

    services = []
    if latitude is not None and longitude is not None:
        services = find_nearby_services(latitude, longitude)

    return render_template(
        "confirmation.html",
        person=person,
        services=services,
    )


@app.route("/api/nearby", methods=["POST"])
def api_nearby():
    data = request.get_json(silent=True) or {}
    lat = data.get("latitude")
    lon = data.get("longitude")
    try:
        latitude = float(lat)
        longitude = float(lon)
    except (TypeError, ValueError):
        return jsonify({"services": []})

    services = find_nearby_services(latitude, longitude)
    return jsonify({"services": services})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

