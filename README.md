## Disability Support Registry Web App

This is a small web application designed to **register people with disabilities** and
automatically look up **nearby hospitals, clinics, and authorities** based on their
location.

It is built for quick deployment in local communities, NGOs, or pilot projects that
want to keep structured information and know who to call when urgent help is needed.

---

### 1. Features

- **Registration form**
  - Full name (required)
  - Email and phone (optional)
  - Disability / condition
  - Important information and support needs
  - Address (street, city, country)
  - Optional automatic location using the browser's GPS (if available)

- **Storage**
  - Data is stored in a local **SQLite** database (`data.db`).

- **Nearby services**
  - After a person is registered, the app:
    - Uses the coordinates from GPS, or
    - Geocodes the textual address (via OpenStreetMap Nominatim),
    - Then queries the Overpass API to find nearby:
      - Hospitals
      - Clinics
      - Doctors
      - Police
      - Fire stations

> You should treat any collected data as **sensitive** and protect it according to
> your local privacy and data protection rules.

---

### 2. Prerequisites

- Python **3.10+** installed
- (Optional but recommended) A virtual environment

---

### 3. Set up and run

From your `coding` folder (where `app.py` lives):

```bash
python -m venv .venv
source .venv/bin/activate  # on macOS / Linux
# .venv\Scripts\activate   # on Windows PowerShell

pip install -r requirements.txt
```

Then run the app:

```bash
python app.py
```

You should see Flask start on `http://127.0.0.1:5000/`.

Open that address in your browser to use the web app.

On first run, the app will automatically create a `data.db` SQLite file in the same
folder.

---

### 4. How it works (high level)

- `app.py`
  - Defines the Flask application.
  - Sets up a `RegisteredPerson` model using SQLAlchemy and SQLite.
  - Exposes:
    - `GET /` – show the registration form.
    - `POST /register` – save the data, look up nearby services, and show a
      confirmation page.
    - `POST /api/nearby` – JSON API to look up services given a latitude and
      longitude.
  - Uses **Nominatim** (OpenStreetMap) for geocoding addresses if no GPS is provided.
  - Uses the **Overpass API** to search for nearby hospitals, clinics, doctors,
    police, and fire stations.

- `templates/index.html`
  - Accessible, mobile-friendly registration form with optional "Use my current
    location" button.

- `templates/confirmation.html`
  - Shows a summary of the registered person.
  - Lists nearby services with their type, name, approximate address, and
    coordinates when available.

- `static/styles.css`
  - Simple, modern styling with good contrast and larger touch-friendly targets.

- `static/app.js`
  - Handles the "Use my current location" button using the browser Geolocation API,
    filling hidden latitude/longitude fields.

---

### 5. Notes on external services

- The app uses public OpenStreetMap services (Nominatim + Overpass).
- For production/large-scale use, you should:
  - Read and comply with their usage policies.
  - Consider running your own instance or using a paid mapping provider.

If external access is blocked (e.g., no internet), the app will still **save the
registration**, but the "nearby services" list may be empty.

---

### 6. Next steps / customization ideas

- Add authentication so only authorized staff can view or register people.
- Add an admin dashboard to search and list registered persons.
- Add fields for official IDs, guardians, or case workers.
- Integrate with SMS or email notifications to contact authorities.
- Translate the interface into your local language.

