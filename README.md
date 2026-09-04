# VTIP — Virtual Traffic Intelligence Platform

## How to Run

1. Make sure Python 3 and Flask are installed:
   ```
   pip install flask
   ```

2. Run the app:
   ```
   python3 start.py
   ```
   OR directly:
   ```
   python3 app.py
   ```

3. Open your browser at: **http://localhost:5050**

---

## Features

- **Real city map** (OpenStreetMap via Leaflet) for 12 cities
- **Smooth canvas vehicles** moving along actual road coordinates
- **City search** — type any city name, press Enter or click
- **Quick picks** — Chennai, Mumbai, Trichy, Tokyo, Dubai
- **What-If Simulator** — changes saved to SQLite DB and reflected live on map
- **Digital Twin** — select individual roads, see live vehicle flow
- **Heatmap, Efficiency Gauge, System Health** panels

## Cities Included
India: Chennai, Mumbai, Delhi, Bengaluru, Tiruchirappalli, Thanjavur  
International: London, New York, Tokyo, Singapore, Paris, Dubai

## Database
All scenarios and traffic logs are saved in `vtip.db` (SQLite).
