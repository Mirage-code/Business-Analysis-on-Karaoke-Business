"""
Bay Area Karaoke — Exploratory Data Analysis & Business Intelligence
Runs all SQL queries, generates insights, and exports charts + summary stats.
"""

import pandas as pd
import numpy as np
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import os, warnings
warnings.filterwarnings("ignore")

# ── Style ──────────────────────────────────────────────────────────────────────
PALETTE   = ["#185FA5","#1D9E75","#EF9F27","#D85A30","#533BB7","#73726c"]
BLUE      = "#185FA5"
GREEN     = "#1D9E75"
AMBER     = "#EF9F27"
CORAL     = "#D85A30"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "grid.color":       "#ebebeb",
    "grid.linewidth":   0.6,
    "font.family":      "DejaVu Sans",
    "font.size":        11,
    "axes.titlesize":   13,
    "axes.titleweight": "bold",
    "axes.labelcolor":  "#444",
    "xtick.color":      "#666",
    "ytick.color":      "#666",
})

OUT_DIR = "/home/claude/karaoke_analysis/outputs"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load data into SQLite ──────────────────────────────────────────────────────
print("Loading data into SQLite...")
conn = sqlite3.connect(":memory:")

for fname, tbl in [("venues","venues"),("bookings","bookings"),
                   ("reviews","reviews"),("menu_items","menu_items")]:
    df = pd.read_csv(f"/home/claude/karaoke_analysis/data/{fname}.csv")
    df.to_sql(tbl, conn, if_exists="replace", index=False)
    print(f"  Loaded {len(df):,} rows → {tbl}")

def q(sql): return pd.read_sql_query(sql, conn)

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 1 — Revenue by City
# ─────────────────────────────────────────────────────────────────────────────
city_rev = q("""
    SELECT city,
           COUNT(*) AS bookings,
           ROUND(SUM(total_revenue),2) AS total_revenue,
           ROUND(AVG(per_person_spend),2) AS avg_per_person
    FROM bookings GROUP BY city ORDER BY total_revenue DESC
""")
print("\n── Revenue by City ──")
print(city_rev.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

axes[0].barh(city_rev["city"][::-1], city_rev["total_revenue"][::-1],
             color=PALETTE[:len(city_rev)], edgecolor="none", height=0.6)
axes[0].set_xlabel("Total Revenue ($)")
axes[0].set_title("Total Revenue by City (2023–2025)")
axes[0].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x,_: f"${x/1e6:.1f}M"))

axes[1].bar(city_rev["city"], city_rev["avg_per_person"],
            color=PALETTE[:len(city_rev)], edgecolor="none", width=0.55)
axes[1].set_xlabel("City")
axes[1].set_ylabel("Avg Spend per Person ($)")
axes[1].set_title("Avg Spend per Person by City")
for bar, val in zip(axes[1].patches, city_rev["avg_per_person"]):
    axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 f"${val:.0f}", ha="center", va="bottom", fontsize=9)

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/01_revenue_by_city.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → saved 01_revenue_by_city.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 2 — Weekend vs Weekday
# ─────────────────────────────────────────────────────────────────────────────
day_split = q("""
    SELECT CASE WHEN is_weekend THEN 'Weekend' ELSE 'Weekday' END AS day_type,
           COUNT(*) AS bookings,
           ROUND(SUM(total_revenue),2) AS total_revenue,
           ROUND(AVG(total_revenue),2) AS avg_booking_value,
           ROUND(AVG(per_person_spend),2) AS avg_per_person
    FROM bookings GROUP BY is_weekend ORDER BY total_revenue DESC
""")
print("\n── Weekend vs Weekday ──")
print(day_split.to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 3 — Monthly Seasonality
# ─────────────────────────────────────────────────────────────────────────────
monthly = q("""
    SELECT year, month,
           ROUND(SUM(total_revenue),2) AS revenue,
           COUNT(*) AS bookings
    FROM bookings GROUP BY year, month ORDER BY year, month
""")
monthly["period"] = pd.to_datetime(monthly[["year","month"]].assign(day=1))

fig, ax = plt.subplots(figsize=(14, 4.5))
for yr, grp in monthly.groupby("year"):
    ax.plot(grp["period"], grp["revenue"], marker="o", markersize=4,
            linewidth=2, label=str(yr))
ax.set_title("Monthly Revenue Trend — All Venues")
ax.set_ylabel("Revenue ($)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,_: f"${x/1e3:.0f}K"))
ax.legend(title="Year", frameon=False)

# Highlight peak months
for m, label in [(2,"Valentine's"), (5,"Grad Season"), (12,"Holiday")]:
    for yr in monthly["year"].unique():
        row = monthly[(monthly["year"]==yr) & (monthly["month"]==m)]
        if not row.empty:
            ax.axvline(row["period"].values[0], color="#ddd", linewidth=1, linestyle="--", zorder=0)

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/02_monthly_seasonality.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → saved 02_monthly_seasonality.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 4 — Visit Type Revenue Comparison
# ─────────────────────────────────────────────────────────────────────────────
visit = q("""
    SELECT visit_type,
           COUNT(*) AS bookings,
           ROUND(AVG(total_revenue),2) AS avg_revenue,
           ROUND(AVG(per_person_spend),2) AS avg_per_person,
           ROUND(AVG(duration_hrs),2) AS avg_duration,
           ROUND(AVG(party_size),1) AS avg_party
    FROM bookings GROUP BY visit_type ORDER BY avg_revenue DESC
""")
print("\n── Visit Type Analysis ──")
print(visit.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
colors = [PALETTE[i % len(PALETTE)] for i in range(len(visit))]

axes[0].barh(visit["visit_type"][::-1], visit["avg_revenue"][::-1],
             color=colors[::-1], edgecolor="none", height=0.6)
axes[0].set_title("Avg Booking Revenue by Visit Type")
axes[0].set_xlabel("Avg Revenue ($)")
for bar, val in zip(axes[0].patches, visit["avg_revenue"][::-1]):
    axes[0].text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
                 f"${val:.0f}", va="center", fontsize=9)

axes[1].barh(visit["visit_type"][::-1], visit["avg_per_person"][::-1],
             color=colors[::-1], edgecolor="none", height=0.6)
axes[1].set_title("Avg Spend per Person by Visit Type")
axes[1].set_xlabel("Avg Per Person ($)")

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/03_visit_type_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → saved 03_visit_type_analysis.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 5 — Hourly Demand Heatmap
# ─────────────────────────────────────────────────────────────────────────────
heatmap_data = q("""
    SELECT day_of_week, hour_start, COUNT(*) AS bookings
    FROM bookings GROUP BY day_of_week, hour_start
""")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
heatmap_pivot = heatmap_data.pivot(index="day_of_week", columns="hour_start", values="bookings")
heatmap_pivot = heatmap_pivot.reindex(day_order)

fig, ax = plt.subplots(figsize=(12, 4.5))
sns.heatmap(heatmap_pivot, ax=ax, cmap="Blues", annot=True, fmt=".0f",
            linewidths=0.4, linecolor="#eee", cbar_kws={"label":"Bookings"})
ax.set_title("Booking Demand Heatmap — Day × Hour")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/04_demand_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → saved 04_demand_heatmap.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 6 — Menu Item Revenue Contribution
# ─────────────────────────────────────────────────────────────────────────────
menu = q("""
    SELECT item, category,
           SUM(qty) AS total_sold,
           ROUND(SUM(total),2) AS total_revenue
    FROM menu_items GROUP BY item, category ORDER BY total_revenue DESC LIMIT 12
""")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
bev  = menu[menu["category"]=="beverage"]
food = menu[menu["category"]=="food"]

axes[0].barh(bev["item"][::-1], bev["total_revenue"][::-1],
             color=BLUE, edgecolor="none", height=0.6)
axes[0].set_title("Beverage Revenue (Top Items)")
axes[0].set_xlabel("Revenue ($)")
axes[0].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x,_: f"${x/1e3:.0f}K"))

axes[1].barh(food["item"][::-1], food["total_revenue"][::-1],
             color=GREEN, edgecolor="none", height=0.6)
axes[1].set_title("Food Revenue (Top Items)")
axes[1].set_xlabel("Revenue ($)")
axes[1].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x,_: f"${x/1e3:.0f}K"))

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/05_menu_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → saved 05_menu_revenue.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 7 — Yelp Rating vs Revenue Scatter
# ─────────────────────────────────────────────────────────────────────────────
venue_perf = q("""
    SELECT v.name, v.city, v.format, v.yelp_rating, v.yelp_reviews,
           COUNT(b.booking_id) AS bookings,
           ROUND(SUM(b.total_revenue),2) AS total_revenue,
           ROUND(AVG(b.per_person_spend),2) AS avg_per_person
    FROM venues v JOIN bookings b ON v.id=b.venue_id
    GROUP BY v.id, v.name, v.city, v.format, v.yelp_rating, v.yelp_reviews
""")

fig, ax = plt.subplots(figsize=(10, 6))
format_colors = {"ktv_private": BLUE, "hybrid": GREEN, "public_stage": AMBER}
for fmt, grp in venue_perf.groupby("format"):
    ax.scatter(grp["yelp_rating"], grp["total_revenue"],
               s=grp["yelp_reviews"]/4, alpha=0.75,
               c=format_colors[fmt], label=fmt.replace("_"," ").title(), edgecolors="white", linewidth=0.5)
    for _, row in grp.iterrows():
        ax.annotate(row["name"].split()[0], (row["yelp_rating"], row["total_revenue"]),
                    fontsize=7.5, color="#555", ha="left", va="bottom",
                    xytext=(4, 3), textcoords="offset points")

ax.set_xlabel("Yelp Rating")
ax.set_ylabel("Total Revenue (2023–2025)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x,_: f"${x/1e6:.1f}M"))
ax.set_title("Yelp Rating vs Revenue — bubble size = review count")
ax.legend(title="Format", frameon=False)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/06_rating_vs_revenue.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → saved 06_rating_vs_revenue.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 8 — Room Size Economics
# ─────────────────────────────────────────────────────────────────────────────
room = q("""
    SELECT room_size,
           COUNT(*) AS bookings,
           ROUND(AVG(room_revenue),2) AS avg_room_rev,
           ROUND(AVG(fb_revenue),2)   AS avg_fb_rev,
           ROUND(AVG(total_revenue),2) AS avg_total,
           ROUND(AVG(per_person_spend),2) AS avg_per_person
    FROM bookings GROUP BY room_size ORDER BY avg_total DESC
""")

fig, ax = plt.subplots(figsize=(8, 4.5))
x = np.arange(len(room))
w = 0.35
bars1 = ax.bar(x - w/2, room["avg_room_rev"],  width=w, label="Room rental", color=BLUE, edgecolor="none")
bars2 = ax.bar(x + w/2, room["avg_fb_rev"],    width=w, label="F&B",         color=GREEN, edgecolor="none")
ax.set_xticks(x)
ax.set_xticklabels(room["room_size"].str.capitalize())
ax.set_ylabel("Avg Revenue per Booking ($)")
ax.set_title("Room Size Economics — Room vs F&B Revenue")
ax.legend(frameon=False)
for bar in list(bars1)+list(bars2):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
            f"${bar.get_height():.0f}", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/07_room_size_economics.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → saved 07_room_size_economics.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 9 — Review Rating Distribution
# ─────────────────────────────────────────────────────────────────────────────
ratings = q("""
    SELECT v.format, r.rating, COUNT(*) AS cnt
    FROM reviews r JOIN venues v ON r.venue_id=v.id
    GROUP BY v.format, r.rating
""")
pivot = ratings.pivot(index="rating", columns="format", values="cnt").fillna(0)

fig, ax = plt.subplots(figsize=(9, 4.5))
pivot.plot(kind="bar", ax=ax, color=list(format_colors.values()),
           edgecolor="none", width=0.7)
ax.set_xlabel("Star Rating")
ax.set_ylabel("Review Count")
ax.set_title("Review Rating Distribution by Venue Format")
ax.legend(title="Format", labels=[k.replace("_"," ").title() for k in pivot.columns], frameon=False)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/08_review_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("  → saved 08_review_distribution.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 10 — Executive Summary Stats
# ─────────────────────────────────────────────────────────────────────────────
summary = q("""
    SELECT
        COUNT(DISTINCT venue_id)            AS total_venues,
        COUNT(*)                            AS total_bookings,
        ROUND(SUM(total_revenue),2)         AS total_revenue,
        ROUND(AVG(total_revenue),2)         AS avg_booking_value,
        ROUND(AVG(per_person_spend),2)      AS avg_per_person,
        ROUND(SUM(fb_revenue)*100.0/SUM(total_revenue),1) AS fb_share_pct,
        ROUND(SUM(CASE WHEN is_weekend THEN total_revenue ELSE 0 END)*100.0/
              SUM(total_revenue),1)         AS weekend_revenue_pct
    FROM bookings
""")
print("\n══ EXECUTIVE SUMMARY ══")
for col in summary.columns:
    print(f"  {col:30s}: {summary[col].values[0]}")

# Save summary to CSV
summary.to_csv(f"{OUT_DIR}/executive_summary.csv", index=False)

conn.close()
print(f"\nAll outputs saved to {OUT_DIR}/")
