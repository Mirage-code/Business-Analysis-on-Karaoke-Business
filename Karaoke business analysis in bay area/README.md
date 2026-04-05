# Bay Area Karaoke Business — Data Analyst Portfolio Project

A full end-to-end data analytics project simulating real business intelligence work
for a karaoke industry client in the San Francisco Bay Area.

## Project Structure

```
karaoke_analysis/
├── src/
│   └── generate_data.py      # Synthetic data generator (Yelp/Google style)
├── data/
│   ├── venues.csv            # 15 venues with ratings, format, location
│   ├── bookings.csv          # 8,000 room booking transactions (2023–2025)
│   ├── reviews.csv           # 3,000 customer reviews
│   ├── menu_items.csv        # 93,000+ F&B line items
│   └── market_trends.csv     # Global/US market data (2019–2025)
├── sql/
│   └── schema_and_queries.sql  # 12 business intelligence SQL queries
├── notebooks/
│   └── analysis.py           # Full EDA + 8 chart outputs (Python/pandas)
├── dashboard/
│   └── index.html            # Interactive web dashboard (Chart.js)
└── outputs/
    ├── 01_revenue_by_city.png
    ├── 02_monthly_seasonality.png
    ├── 03_visit_type_analysis.png
    ├── 04_demand_heatmap.png
    ├── 05_menu_revenue.png
    ├── 06_rating_vs_revenue.png
    ├── 07_room_size_economics.png
    ├── 08_review_distribution.png
    └── executive_summary.csv
```

## Skills Demonstrated

| Skill Area | Tools |
|---|---|
| Data collection / scraping | Python (simulated Yelp/Google data) |
| Data cleaning & EDA | pandas, numpy |
| SQL analytics | SQLite (12 BI queries incl. CTEs, window functions) |
| Visualization | matplotlib, seaborn |
| Dashboard | HTML + Chart.js |
| Business analysis | Market sizing, competitive analysis, SWOT |

## How to Run

```bash
# 1. Generate all data
python src/generate_data.py

# 2. Run analysis + generate charts
python notebooks/analysis.py

# 3. Open dashboard
open dashboard/index.html
```

## Key Business Findings

- **SF dominates** with $2.46M revenue (52%) but South Bay is growing faster
- **Weekdays = 56% of revenue** — corporate/daytime segment is underutilized
- **F&B drives 81% of revenue** — room rental is the hook, drinks are the margin
- **Corporate events** have the highest avg booking value ($585+) after friends
- **South Bay (SJ/Milpitas)** has lower rent but comparable spend-per-person to SF
- **KTV private room format** has highest repeat visit rates and review scores

## Top Opportunities Identified

1. Corporate team events (post-RTO demand, $2K–$10K per booking)
2. K-pop / anime themed rooms (Gen Z, viral marketing)
3. South Bay expansion (lower costs, underserved demographics)
4. Mini KTV kiosks (BART stations, malls — low capex)
5. AI voice enhancement as differentiator

## SQL Highlights

- CTE-based year-over-year growth analysis
- Window functions for cohort revenue tracking
- Multi-table JOINs across venues, bookings, reviews, and menu items
- Demand heatmap aggregation (day × hour)
- Market gap / underserved area analysis

---
*Data is synthetically generated based on publicly available market research.*
*Project by: [Your Name] | GitHub: [your-github]*
