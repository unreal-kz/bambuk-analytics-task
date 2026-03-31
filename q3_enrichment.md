# Question 3 — External open data enrichment

The log already contains: booking ID, booker IP, payment timestamp, property coordinates,
and check-in / check-out dates. Below are the most valuable free/open data sources that can
be joined to this data and the analytical value each unlocks.

---

## 1. Reverse geocoding — GeoNames / OpenStreetMap Nominatim

**Join key:** latitude + longitude (fields 5–4)

**Data obtained:** country, region (oblast / county), city or nearest settlement,
terrain category (coast / mountain / forest / plain), distance to nearest water body.

**Use cases:**
- Group properties by geography for regional demand analysis.
- Build location-based features for pricing models (beach premium, mountain premium).
- Identify supply concentration vs. underserved areas.

---

## 2. Historical weather — Open-Meteo (ERA5 reanalysis, free API)

**Join key:** latitude + longitude + check-in/check-out date range

**Data obtained:** daily mean temperature, precipitation sum, sunshine hours,
wind speed, UV index — all at the property location during the actual stay window.

**Use cases:**
- Explain seasonality: hot summers and snowy winters drive distinct demand patterns.
- Price elasticity by weather: does rain reduce last-minute cancellations?
- Build "weather quality score" as a feature for predictive pricing.

---

## 3. Public holidays & school vacations — Nager.Date API / national holiday datasets

**Join key:** booker country (derived from IP, see §5) + check-in date

**Data obtained:** public holiday names, school vacation windows by country and region.

**Use cases:**
- Model demand spikes on long weekends and "bridge" days (Mon/Fri between holiday and weekend).
- Country-level lead-time shifts: some markets book further ahead for school holidays.
- Segmentation: family vs. couple travel patterns around school calendars.

---

## 4. IP geolocation — MaxMind GeoLite2 / ip-api (free tier)

**Join key:** IPv6 address (field 2)

**Data obtained:** booker country, city, ISP / ASN, VPN / proxy / datacenter flag.

**Use cases:**
- Domestic vs. international booking segmentation.
- Currency normalisation for cross-border price comparisons.
- Fraud detection: datacenter IPs or known VPN ranges booking high-value properties.
- Distance between booker origin and property (urban-escape hypothesis).

---

## 5. Population density — WorldPop / national census open data

**Join key:** booker city (derived from IP geolocation, §4)

**Data obtained:** population, density, urbanisation rate of the booker's origin city.

**Use cases:**
- "Urban escape" propensity modelling: dense cities generate more rural bookings.
- Distance-decay demand curves: how far do city residents travel for a country house?
- Market sizing by origin metro area.

---

## 6. Elevation & terrain — OpenTopoData / Copernicus DEM (30 m resolution)

**Join key:** latitude + longitude

**Data obtained:** elevation (m), terrain roughness, proximity to coast / lake / river / forest
(derived from OpenStreetMap land-use layers).

**Use cases:**
- Property feature engineering for pricing models (altitude bonus, lakeside premium).
- Cluster properties into "nature types" without manual tagging.
- Seasonal accessibility (high-altitude properties closed in winter).

---

## 7. Protected areas — Protected Planet / WDPA

**Join key:** latitude + longitude (spatial intersection)

**Data obtained:** national park, nature reserve, UNESCO biosphere boundary polygons.

**Use cases:**
- Tag premium "nature retreat" properties automatically.
- Predict demand from eco-tourism segments.
- Regulatory compliance (restrictions on new listings inside protected zones).

---

## 8. Macroeconomic indicators — World Bank Open Data / FRED

**Join key:** booker country + payment year-month

**Data obtained:** GDP per capita, consumer confidence index, CPI, exchange rates,
unemployment rate.

**Use cases:**
- Explain long-term booking volume trends across markets.
- Normalise prices across currencies for multi-country models.
- Leading indicators for demand forecasting (consumer confidence leads bookings by ~1–2 months).

---

## 9. Local events — Eventbrite public API / regional tourism boards

**Join key:** property coordinates + check-in date (spatial + temporal proximity)

**Data obtained:** concerts, festivals, sports events, fairs within N km of the property.

**Use cases:**
- Detect short-term demand spikes not explained by seasonality.
- Dynamic pricing triggers: raise prices before a nearby festival.
- Post-event attribution: do properties near event venues get re-booked by returning visitors?

---

## Summary table

| Source | Join key | Key signals |
|---|---|---|
| GeoNames / OSM Nominatim | lat/lon | Country, region, terrain type |
| Open-Meteo (ERA5) | lat/lon + date range | Temp, rain, sunshine hours |
| Nager.Date | booker country + date | Public holidays, school breaks |
| MaxMind GeoLite2 / ip-api | IPv6 | Booker location, VPN flag |
| WorldPop / census | booker city | Population density |
| OpenTopoData / Copernicus | lat/lon | Elevation, terrain |
| Protected Planet (WDPA) | lat/lon (spatial) | National park proximity |
| World Bank / FRED | country + year-month | GDP, CPI, exchange rates |
| Eventbrite / tourism boards | lat/lon + date | Nearby events & festivals |
