"""
Bay Area Karaoke Business — Synthetic Data Generator
Simulates realistic Yelp/Google-style scraped data + transactional records
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import os

random.seed(42)
np.random.seed(42)

# ── Venue master data ──────────────────────────────────────────────────────────
VENUES = [
    {"id": "V001", "name": "The Mint Karaoke Lounge",     "city": "San Francisco", "neighborhood": "Castro",      "format": "public_stage", "rooms": 0,  "has_bar": True,  "yelp_rating": 4.2, "yelp_reviews": 1842, "google_rating": 4.1, "founded": 1993, "avg_hourly_rate": 0,   "cover_charge": 5},
    {"id": "V002", "name": "Pandora Karaoke & Bar",       "city": "San Francisco", "neighborhood": "Tenderloin",  "format": "hybrid",       "rooms": 6,  "has_bar": True,  "yelp_rating": 4.0, "yelp_reviews": 987,  "google_rating": 3.9, "founded": 2010, "avg_hourly_rate": 35,  "cover_charge": 0},
    {"id": "V003", "name": "K Time Karaoke",              "city": "San Francisco", "neighborhood": "Chinatown",   "format": "ktv_private",  "rooms": 10, "has_bar": True,  "yelp_rating": 4.3, "yelp_reviews": 756,  "google_rating": 4.2, "founded": 2018, "avg_hourly_rate": 45,  "cover_charge": 0},
    {"id": "V004", "name": "3910 Bar & Karaoke",          "city": "San Francisco", "neighborhood": "Richmond",    "format": "ktv_private",  "rooms": 8,  "has_bar": True,  "yelp_rating": 4.1, "yelp_reviews": 623,  "google_rating": 4.0, "founded": 2014, "avg_hourly_rate": 40,  "cover_charge": 0},
    {"id": "V005", "name": "Silver Cloud Restaurant",     "city": "San Francisco", "neighborhood": "Marina",      "format": "hybrid",       "rooms": 4,  "has_bar": True,  "yelp_rating": 4.4, "yelp_reviews": 1203, "google_rating": 4.3, "founded": 1982, "avg_hourly_rate": 50,  "cover_charge": 0},
    {"id": "V006", "name": "Bow Bow Lounge",              "city": "San Francisco", "neighborhood": "Chinatown",   "format": "public_stage", "rooms": 0,  "has_bar": True,  "yelp_rating": 4.5, "yelp_reviews": 512,  "google_rating": 4.4, "founded": 1986, "avg_hourly_rate": 0,   "cover_charge": 0},
    {"id": "V007", "name": "Focus Karaoke",               "city": "San Jose",      "neighborhood": "Japantown",   "format": "ktv_private",  "rooms": 12, "has_bar": True,  "yelp_rating": 4.2, "yelp_reviews": 891,  "google_rating": 4.1, "founded": 2016, "avg_hourly_rate": 30,  "cover_charge": 0},
    {"id": "V008", "name": "Pure Karaoke",                "city": "Milpitas",      "neighborhood": "Downtown",    "format": "ktv_private",  "rooms": 14, "has_bar": False, "yelp_rating": 4.0, "yelp_reviews": 445,  "google_rating": 3.9, "founded": 2019, "avg_hourly_rate": 28,  "cover_charge": 0},
    {"id": "V009", "name": "Millbrae Karaoke House",      "city": "Millbrae",      "neighborhood": "El Camino",   "format": "ktv_private",  "rooms": 8,  "has_bar": False, "yelp_rating": 3.9, "yelp_reviews": 135,  "google_rating": 3.8, "founded": 2015, "avg_hourly_rate": 25,  "cover_charge": 0},
    {"id": "V010", "name": "Karaoke One",                 "city": "San Jose",      "neighborhood": "Willow Glen", "format": "hybrid",       "rooms": 5,  "has_bar": True,  "yelp_rating": 4.1, "yelp_reviews": 334,  "google_rating": 4.0, "founded": 2017, "avg_hourly_rate": 32,  "cover_charge": 0},
    {"id": "V011", "name": "Melody Box Karaoke",          "city": "Fremont",       "neighborhood": "Centerville", "format": "ktv_private",  "rooms": 10, "has_bar": False, "yelp_rating": 4.2, "yelp_reviews": 278,  "google_rating": 4.1, "founded": 2020, "avg_hourly_rate": 26,  "cover_charge": 0},
    {"id": "V012", "name": "Singarama Lounge",            "city": "Oakland",       "neighborhood": "Temescal",    "format": "public_stage", "rooms": 0,  "has_bar": True,  "yelp_rating": 4.3, "yelp_reviews": 467,  "google_rating": 4.2, "founded": 2012, "avg_hourly_rate": 0,   "cover_charge": 8},
    {"id": "V013", "name": "Neon Star Karaoke",           "city": "San Jose",      "neighborhood": "Downtown",    "format": "ktv_private",  "rooms": 16, "has_bar": True,  "yelp_rating": 4.4, "yelp_reviews": 612,  "google_rating": 4.3, "founded": 2021, "avg_hourly_rate": 35,  "cover_charge": 0},
    {"id": "V014", "name": "The Vocal Booth",             "city": "San Francisco", "neighborhood": "SoMa",        "format": "ktv_private",  "rooms": 7,  "has_bar": True,  "yelp_rating": 4.0, "yelp_reviews": 289,  "google_rating": 3.9, "founded": 2022, "avg_hourly_rate": 50,  "cover_charge": 0},
    {"id": "V015", "name": "Pagoda Karaoke",              "city": "San Francisco", "neighborhood": "Japantown",   "format": "hybrid",       "rooms": 3,  "has_bar": False, "yelp_rating": 4.1, "yelp_reviews": 198,  "google_rating": 4.0, "founded": 2009, "avg_hourly_rate": 20,  "cover_charge": 0},
]

CITIES = {
    "San Francisco": {"county": "San Francisco", "region": "SF", "lat": 37.7749, "lng": -122.4194, "median_rent_sqft": 8.5},
    "San Jose":      {"county": "Santa Clara",   "region": "South Bay", "lat": 37.3382, "lng": -121.8863, "median_rent_sqft": 4.2},
    "Milpitas":      {"county": "Santa Clara",   "region": "South Bay", "lat": 37.4323, "lng": -121.8996, "median_rent_sqft": 3.8},
    "Millbrae":      {"county": "San Mateo",     "region": "Peninsula", "lat": 37.5985, "lng": -122.3869, "median_rent_sqft": 5.1},
    "Fremont":       {"county": "Alameda",       "region": "East Bay",  "lat": 37.5485, "lng": -121.9886, "median_rent_sqft": 3.5},
    "Oakland":       {"county": "Alameda",       "region": "East Bay",  "lat": 37.8044, "lng": -122.2712, "median_rent_sqft": 4.8},
}

PRICE_CATEGORIES = {"$": (1,15), "$$": (15,35), "$$$": (35,65), "$$$$": (65,150)}

def make_venues_df():
    rows = []
    for v in VENUES:
        city_meta = CITIES[v["city"]]
        # price category based on hourly rate / cover
        if v["avg_hourly_rate"] == 0 and v["cover_charge"] <= 5:
            price_cat = "$"
        elif v["avg_hourly_rate"] <= 30:
            price_cat = "$$"
        elif v["avg_hourly_rate"] <= 45:
            price_cat = "$$$"
        else:
            price_cat = "$$$$"
        row = {**v, **city_meta, "price_category": price_cat,
               "years_in_business": 2025 - v["founded"],
               "total_capacity": v["rooms"] * 10 if v["rooms"] > 0 else 80}
        rows.append(row)
    return pd.DataFrame(rows)

# ── Reviews data ───────────────────────────────────────────────────────────────
REVIEW_ASPECTS = ["sound quality", "song selection", "room cleanliness", "staff friendliness",
                  "value for money", "drinks quality", "atmosphere", "booking process"]
POSITIVE_PHRASES = ["great {a}", "loved the {a}", "excellent {a}", "amazing {a}", "solid {a}"]
NEGATIVE_PHRASES = ["poor {a}", "disappointing {a}", "{a} could be better", "mediocre {a}"]
VISIT_TYPES = ["birthday party", "date night", "work outing", "friends hangout",
               "bachelorette", "anniversary", "solo singing", "family outing"]

def make_reviews_df(n=3000):
    rows = []
    start = datetime(2022, 1, 1)
    end   = datetime(2025, 3, 31)
    for _ in range(n):
        v = random.choice(VENUES)
        base_r = v["yelp_rating"]
        rating = round(min(5, max(1, np.random.normal(base_r, 0.7))), 0)
        # seasonal boost: Fri/Sat, Dec, Feb (Valentine's), May (graduation)
        date = start + timedelta(days=random.randint(0, (end-start).days))
        if date.weekday() >= 4: rating = min(5, rating + 0.3)
        if date.month in [12, 2, 5]: rating = min(5, rating + 0.2)
        rating = int(round(rating))
        aspects = random.sample(REVIEW_ASPECTS, k=random.randint(2, 4))
        phrases = []
        for a in aspects:
            tpl = random.choice(POSITIVE_PHRASES if rating >= 4 else NEGATIVE_PHRASES)
            phrases.append(tpl.format(a=a))
        text = (f"Came for a {random.choice(VISIT_TYPES)}. " +
                ", ".join(phrases[:2]).capitalize() + ". " +
                (f"Would definitely come back!" if rating >= 4 else "Probably won't return."))
        rows.append({
            "review_id": f"R{len(rows)+1:05d}",
            "venue_id": v["id"],
            "venue_name": v["name"],
            "city": v["city"],
            "date": date.strftime("%Y-%m-%d"),
            "rating": rating,
            "visit_type": random.choice(VISIT_TYPES),
            "review_text": text,
            "sentiment_score": round((rating - 3) / 2 + np.random.normal(0, 0.1), 2),
            "helpful_votes": max(0, int(np.random.exponential(3))),
        })
    return pd.DataFrame(rows)

# ── Transactions data ──────────────────────────────────────────────────────────
ROOM_SIZES  = {"small": {"capacity": 6,  "base_rate": 1.0},
               "medium": {"capacity": 10, "base_rate": 1.4},
               "large":  {"capacity": 16, "base_rate": 2.0}}
MENU_ITEMS  = [
    ("Domestic Beer",    8,  "beverage"), ("Craft Beer",     12, "beverage"),
    ("Cocktail",        14,  "beverage"), ("Bottle Service", 180,"beverage"),
    ("Soft Drink",       5,  "beverage"), ("Sake (bottle)",  45, "beverage"),
    ("Fries",           10,  "food"),     ("Wings",          16, "food"),
    ("Nachos",          14,  "food"),     ("Fried Rice",     18, "food"),
    ("Edamame",          8,  "food"),     ("Karaoke Platter",32, "food"),
]

def make_transactions_df(n_bookings=8000):
    bookings, items = [], []
    start = datetime(2023, 1, 1)
    end   = datetime(2025, 3, 31)
    booking_id = 1

    for _ in range(n_bookings):
        v = random.choice([v for v in VENUES if v["format"] in ("ktv_private","hybrid") and v["rooms"] > 0])
        date = start + timedelta(days=random.randint(0, (end-start).days))
        is_weekend = date.weekday() >= 4
        is_peak_month = date.month in [12, 2, 5, 6, 10]

        hour_start = random.choices([17,18,19,20,21,22], weights=[5,10,20,25,25,15])[0]
        duration   = random.choices([1, 1.5, 2, 2.5, 3], weights=[15,20,35,20,10])[0]
        room_size  = random.choices(["small","medium","large"], weights=[40,40,20])[0]
        party_size = random.randint(2, ROOM_SIZES[room_size]["capacity"])

        base_rate  = v["avg_hourly_rate"] * ROOM_SIZES[room_size]["base_rate"]
        rate_mult  = 1.3 if is_weekend else 1.0
        rate_mult *= 1.15 if is_peak_month else 1.0
        room_rev   = round(base_rate * rate_mult * duration, 2)

        # F&B orders
        fb_items  = []
        fb_total  = 0.0
        for _ in range(party_size * random.randint(1, 3)):
            item_name, price, category = random.choice(MENU_ITEMS)
            qty = 1 if category == "food" else random.randint(1, 2)
            fb_items.append({"booking_id": f"B{booking_id:05d}", "item": item_name,
                              "category": category, "price": price, "qty": qty,
                              "total": price * qty, "date": date.strftime("%Y-%m-%d")})
            fb_total += price * qty

        visit_type = random.choices(
            ["walk_in", "birthday_party", "corporate", "bachelorette", "date_night", "friends"],
            weights=[30, 20, 15, 10, 15, 10])[0]

        bookings.append({
            "booking_id":   f"B{booking_id:05d}",
            "venue_id":     v["id"],
            "venue_name":   v["name"],
            "city":         v["city"],
            "date":         date.strftime("%Y-%m-%d"),
            "day_of_week":  date.strftime("%A"),
            "month":        date.month,
            "year":         date.year,
            "quarter":      f"Q{(date.month-1)//3+1}",
            "hour_start":   hour_start,
            "duration_hrs": duration,
            "room_size":    room_size,
            "party_size":   party_size,
            "is_weekend":   is_weekend,
            "visit_type":   visit_type,
            "room_revenue": room_rev,
            "fb_revenue":   round(fb_total, 2),
            "total_revenue":round(room_rev + fb_total, 2),
            "per_person_spend": round((room_rev + fb_total) / party_size, 2),
        })
        items.extend(fb_items)
        booking_id += 1

    return pd.DataFrame(bookings), pd.DataFrame(items)


# ── Market data ────────────────────────────────────────────────────────────────
def make_market_df():
    years = list(range(2019, 2026))
    data = {
        "year": years,
        "global_market_bn": [5.1, 4.2, 4.6, 5.0, 5.4, 5.7, 5.9],
        "us_market_bn":     [0.42, 0.33, 0.38, 0.43, 0.46, 0.48, 0.51],
        "cagr_pct":         [None, None, None, None, 3.4, 3.7, 4.3],
        "commercial_share_pct": [68, 69, 70, 70, 70, 71, 71],
        "private_room_growth_pct": [8, -15, 12, 15, 18, 20, 22],
    }
    return pd.DataFrame(data)


if __name__ == "__main__":
    out = "/home/claude/karaoke_analysis/data"
    os.makedirs(out, exist_ok=True)

    print("Generating venue data...")
    venues_df = make_venues_df()
    venues_df.to_csv(f"{out}/venues.csv", index=False)
    print(f"  → {len(venues_df)} venues")

    print("Generating reviews data...")
    reviews_df = make_reviews_df(3000)
    reviews_df.to_csv(f"{out}/reviews.csv", index=False)
    print(f"  → {len(reviews_df)} reviews")

    print("Generating transactions data...")
    bookings_df, items_df = make_transactions_df(8000)
    bookings_df.to_csv(f"{out}/bookings.csv", index=False)
    items_df.to_csv(f"{out}/menu_items.csv", index=False)
    print(f"  → {len(bookings_df)} bookings, {len(items_df)} menu item records")

    print("Generating market data...")
    market_df = make_market_df()
    market_df.to_csv(f"{out}/market_trends.csv", index=False)
    print(f"  → {len(market_df)} years of market data")

    print("\nAll data written to data/")
