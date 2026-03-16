"""
Question 3 — External Data Enrichment
======================================
Six API caller functions that enrich a log row with:
  - Reverse geocoding   (OSM Nominatim)
  - Elevation           (OpenTopoData SRTM30m)
  - Historical weather  (Open-Meteo archive)
  - Public holidays     (Nager.Date)
  - IP geolocation      (ip-api)
  - GDP per capita      (World Bank)

All errors are caught and return None so the pipeline never crashes.
"""

import time
import requests

HEADERS = {"User-Agent": "bambuk-interview-demo/1.0"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_coord(s: str) -> float:
    """'55,75' → 55.75"""
    return float(s.replace(",", "."))


# ---------------------------------------------------------------------------
# 1. Reverse geocoding — OSM Nominatim
# ---------------------------------------------------------------------------

def reverse_geocode(lat: float, lon: float) -> dict | None:
    """lat/lon → {country_code, country, state, city}"""
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers=HEADERS,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        addr = data.get("address", {})
        return {
            "country_code": addr.get("country_code", "").upper(),
            "country":      addr.get("country", ""),
            "state":        addr.get("state", ""),
            "city":         addr.get("city") or addr.get("town") or addr.get("village") or "",
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 2. Elevation — OpenTopoData SRTM30m
# ---------------------------------------------------------------------------

def get_elevation(lat: float, lon: float) -> float | None:
    """lat/lon → elevation in metres"""
    try:
        r = requests.get(
            "https://api.opentopodata.org/v1/srtm30m",
            params={"locations": f"{lat},{lon}"},
            timeout=10,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            return results[0].get("elevation")
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 3. Historical weather — Open-Meteo archive
# ---------------------------------------------------------------------------

def get_weather(lat: float, lon: float, start_date: str, end_date: str) -> dict | None:
    """
    start_date / end_date: 'YYYY-MM-DD'
    Returns {temp_mean_c, precip_mm, sunshine_h}
    """
    try:
        r = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude":  lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date":   end_date,
                "daily": "temperature_2m_mean,precipitation_sum,sunshine_duration",
                "timezone": "UTC",
            },
            timeout=10,
        )
        r.raise_for_status()
        daily = r.json().get("daily", {})

        def mean(lst):
            lst = [x for x in lst if x is not None]
            return round(sum(lst) / len(lst), 2) if lst else None

        return {
            "temp_mean_c": mean(daily.get("temperature_2m_mean", [])),
            "precip_mm":   round(sum(x for x in daily.get("precipitation_sum", []) if x is not None), 1),
            # sunshine_duration is in seconds → convert to hours
            "sunshine_h":  round(sum(x for x in daily.get("sunshine_duration", []) if x is not None) / 3600, 1),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 4. Public holidays — Nager.Date
# ---------------------------------------------------------------------------

def get_holidays(country_code: str, year: int) -> list | None:
    """country_code ('RU', 'FR', …) + year → list of date strings"""
    try:
        r = requests.get(
            f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}",
            timeout=10,
        )
        if r.status_code == 404:
            return []          # country not supported by Nager.Date
        r.raise_for_status()
        return [h["date"] for h in r.json()]
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 5. IP geolocation — ip-api
# ---------------------------------------------------------------------------

def geolocate_ip(ipv6: str) -> dict | None:
    """IPv6 string → {booker_country, booker_city, isp}  (None if ip-api fails)"""
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ipv6}",
            params={"fields": "status,country,city,isp"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "success":
            return None
        return {
            "booker_country": data.get("country", ""),
            "booker_city":    data.get("city", ""),
            "isp":            data.get("isp", ""),
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 6. GDP per capita — World Bank
# ---------------------------------------------------------------------------

def get_gdp(country_code: str) -> float | None:
    """2-letter ISO country code → most-recent GDP per capita (current USD)"""
    try:
        r = requests.get(
            f"https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.PCAP.CD",
            params={"format": "json", "mrv": 1},
            timeout=10,
        )
        r.raise_for_status()
        payload = r.json()
        if len(payload) < 2 or not payload[1]:
            return None
        value = payload[1][0].get("value")
        return round(value, 0) if value is not None else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Standalone demo — enrich all 5 sample rows
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from q1_regex import LINE, SAMPLE_ROWS

    fields = ["booking_id", "ipv6", "paid_at", "lon", "lat", "checkin", "checkout"]

    for i, row in enumerate(SAMPLE_ROWS, 1):
        m = LINE.fullmatch(row)
        if not m:
            print(f"Row {i}: FAILED to parse"); continue

        d = dict(zip(fields, m.groups()))
        lat = parse_coord(d["lat"])
        lon = parse_coord(d["lon"])
        ipv6    = d["ipv6"]
        checkin  = d["checkin"]
        checkout = d["checkout"]
        year = int(checkin[:4])

        print(f"\n── Row {i} ── lat={lat}, lon={lon}")

        geo = reverse_geocode(lat, lon)
        time.sleep(1)          # Nominatim rate limit
        print(f"  Geocode : {geo}")

        elev = get_elevation(lat, lon)
        print(f"  Elevation: {elev} m")

        wx = get_weather(lat, lon, checkin, checkout)
        print(f"  Weather : {wx}")

        cc = geo["country_code"] if geo else ""
        hols = get_holidays(cc, year) if cc else None
        if hols is not None:
            # count holidays that fall within the stay
            stay_hols = [h for h in hols if checkin <= h <= checkout]
            print(f"  Holidays in stay: {len(stay_hols)}  {stay_hols}")

        ip_info = geolocate_ip(ipv6)
        print(f"  IP geo  : {ip_info}")

        gdp = get_gdp(cc) if cc else None
        print(f"  GDP/cap : {gdp}")
