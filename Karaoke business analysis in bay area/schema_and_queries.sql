-- =============================================================================
-- Bay Area Karaoke Business Intelligence — SQL Project
-- Database: SQLite (compatible with PostgreSQL with minor changes)
-- Author: Data Analyst Portfolio Project
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- SECTION 1: SCHEMA CREATION
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS venues (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    city                TEXT NOT NULL,
    neighborhood        TEXT,
    format              TEXT CHECK(format IN ('public_stage','hybrid','ktv_private')),
    rooms               INTEGER DEFAULT 0,
    has_bar             BOOLEAN,
    yelp_rating         REAL,
    yelp_reviews        INTEGER,
    google_rating       REAL,
    founded             INTEGER,
    avg_hourly_rate     REAL,
    cover_charge        REAL DEFAULT 0,
    price_category      TEXT,
    region              TEXT,
    lat                 REAL,
    lng                 REAL,
    years_in_business   INTEGER,
    total_capacity      INTEGER
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id          TEXT PRIMARY KEY,
    venue_id            TEXT REFERENCES venues(id),
    venue_name          TEXT,
    city                TEXT,
    date                DATE,
    day_of_week         TEXT,
    month               INTEGER,
    year                INTEGER,
    quarter             TEXT,
    hour_start          INTEGER,
    duration_hrs        REAL,
    room_size           TEXT CHECK(room_size IN ('small','medium','large')),
    party_size          INTEGER,
    is_weekend          BOOLEAN,
    visit_type          TEXT,
    room_revenue        REAL,
    fb_revenue          REAL,
    total_revenue       REAL,
    per_person_spend    REAL
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id           TEXT PRIMARY KEY,
    venue_id            TEXT REFERENCES venues(id),
    venue_name          TEXT,
    city                TEXT,
    date                DATE,
    rating              INTEGER CHECK(rating BETWEEN 1 AND 5),
    visit_type          TEXT,
    review_text         TEXT,
    sentiment_score     REAL,
    helpful_votes       INTEGER
);

CREATE TABLE IF NOT EXISTS menu_items (
    booking_id          TEXT REFERENCES bookings(booking_id),
    item                TEXT,
    category            TEXT CHECK(category IN ('food','beverage')),
    price               REAL,
    qty                 INTEGER,
    total               REAL,
    date                DATE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_bookings_venue    ON bookings(venue_id);
CREATE INDEX IF NOT EXISTS idx_bookings_date     ON bookings(date);
CREATE INDEX IF NOT EXISTS idx_bookings_city     ON bookings(city);
CREATE INDEX IF NOT EXISTS idx_reviews_venue     ON reviews(venue_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating    ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_menu_booking      ON menu_items(booking_id);


-- =============================================================================
-- SECTION 2: ANALYTICAL QUERIES
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- Q1: Revenue by city — which market generates the most?
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    b.city,
    COUNT(DISTINCT b.booking_id)        AS total_bookings,
    COUNT(DISTINCT b.venue_id)          AS venue_count,
    ROUND(SUM(b.total_revenue), 2)      AS total_revenue,
    ROUND(AVG(b.total_revenue), 2)      AS avg_booking_value,
    ROUND(SUM(b.total_revenue) /
          COUNT(DISTINCT b.venue_id), 2) AS revenue_per_venue,
    ROUND(AVG(b.per_person_spend), 2)   AS avg_spend_per_person
FROM bookings b
GROUP BY b.city
ORDER BY total_revenue DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q2: Weekend vs weekday revenue split (key business pattern)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    CASE WHEN is_weekend THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*)                               AS bookings,
    ROUND(AVG(total_revenue), 2)           AS avg_revenue,
    ROUND(AVG(duration_hrs), 2)            AS avg_duration_hrs,
    ROUND(AVG(party_size), 2)              AS avg_party_size,
    ROUND(AVG(per_person_spend), 2)        AS avg_per_person,
    ROUND(SUM(total_revenue), 2)           AS total_revenue,
    ROUND(SUM(total_revenue) * 100.0 /
          (SELECT SUM(total_revenue) FROM bookings), 1) AS revenue_share_pct
FROM bookings
GROUP BY is_weekend
ORDER BY revenue_share_pct DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q3: Top venues by revenue with rating context
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    v.name,
    v.city,
    v.format,
    v.yelp_rating,
    COUNT(b.booking_id)                    AS total_bookings,
    ROUND(SUM(b.total_revenue), 2)         AS total_revenue,
    ROUND(AVG(b.total_revenue), 2)         AS avg_booking_value,
    ROUND(SUM(b.fb_revenue) * 100.0 /
          SUM(b.total_revenue), 1)         AS fb_revenue_pct,
    ROUND(AVG(b.party_size), 1)            AS avg_party_size
FROM venues v
JOIN bookings b ON v.id = b.venue_id
GROUP BY v.id, v.name, v.city, v.format, v.yelp_rating
ORDER BY total_revenue DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q4: Monthly revenue trend — seasonality analysis
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    year,
    month,
    CASE month
        WHEN 1  THEN 'Jan' WHEN 2  THEN 'Feb' WHEN 3  THEN 'Mar'
        WHEN 4  THEN 'Apr' WHEN 5  THEN 'May' WHEN 6  THEN 'Jun'
        WHEN 7  THEN 'Jul' WHEN 8  THEN 'Aug' WHEN 9  THEN 'Sep'
        WHEN 10 THEN 'Oct' WHEN 11 THEN 'Nov' WHEN 12 THEN 'Dec'
    END AS month_name,
    COUNT(*)                                AS bookings,
    ROUND(SUM(total_revenue), 2)            AS total_revenue,
    ROUND(AVG(total_revenue), 2)            AS avg_booking_value,
    ROUND(AVG(per_person_spend), 2)         AS avg_per_person
FROM bookings
GROUP BY year, month
ORDER BY year, month;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q5: Visit type analysis — which customer segments spend most?
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    visit_type,
    COUNT(*)                                AS bookings,
    ROUND(AVG(party_size), 1)               AS avg_party_size,
    ROUND(AVG(duration_hrs), 2)             AS avg_duration_hrs,
    ROUND(AVG(total_revenue), 2)            AS avg_total_revenue,
    ROUND(AVG(per_person_spend), 2)         AS avg_per_person,
    ROUND(AVG(fb_revenue / NULLIF(total_revenue,0)) * 100, 1) AS fb_pct_of_revenue
FROM bookings
GROUP BY visit_type
ORDER BY avg_total_revenue DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q6: Room size economics — which room type is most profitable?
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    room_size,
    COUNT(*)                                AS total_bookings,
    ROUND(AVG(duration_hrs), 2)             AS avg_duration_hrs,
    ROUND(AVG(party_size), 1)               AS avg_party_size,
    ROUND(AVG(room_revenue), 2)             AS avg_room_revenue,
    ROUND(AVG(fb_revenue), 2)               AS avg_fb_revenue,
    ROUND(AVG(total_revenue), 2)            AS avg_total_revenue,
    ROUND(AVG(per_person_spend), 2)         AS avg_per_person,
    ROUND(SUM(total_revenue), 2)            AS total_revenue_contribution
FROM bookings
GROUP BY room_size
ORDER BY avg_total_revenue DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q7: Hourly demand heatmap data (hour × day_of_week)
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    day_of_week,
    hour_start,
    COUNT(*)                                AS bookings,
    ROUND(AVG(total_revenue), 2)            AS avg_revenue,
    ROUND(AVG(party_size), 1)               AS avg_party_size
FROM bookings
GROUP BY day_of_week, hour_start
ORDER BY
    CASE day_of_week
        WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7
    END, hour_start;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q8: Review sentiment by venue format — does format drive satisfaction?
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    v.format,
    COUNT(r.review_id)                      AS review_count,
    ROUND(AVG(r.rating), 2)                 AS avg_rating,
    ROUND(AVG(r.sentiment_score), 3)        AS avg_sentiment,
    SUM(CASE WHEN r.rating >= 4 THEN 1 ELSE 0 END) * 100.0
        / COUNT(*) AS pct_positive,
    SUM(CASE WHEN r.rating <= 2 THEN 1 ELSE 0 END) * 100.0
        / COUNT(*) AS pct_negative
FROM venues v
JOIN reviews r ON v.id = r.venue_id
GROUP BY v.format
ORDER BY avg_rating DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q9: F&B menu item popularity and revenue contribution
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    m.item,
    m.category,
    m.price,
    SUM(m.qty)                              AS total_sold,
    ROUND(SUM(m.total), 2)                  AS total_revenue,
    ROUND(SUM(m.total) * 100.0 /
        (SELECT SUM(total) FROM menu_items), 2) AS revenue_share_pct,
    ROUND(AVG(m.qty), 2)                    AS avg_qty_per_order
FROM menu_items m
GROUP BY m.item, m.category, m.price
ORDER BY total_revenue DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q10: Year-over-year growth by city
-- ─────────────────────────────────────────────────────────────────────────────
WITH yearly AS (
    SELECT
        city,
        year,
        SUM(total_revenue)  AS revenue,
        COUNT(*)            AS bookings
    FROM bookings
    GROUP BY city, year
)
SELECT
    a.city,
    a.year,
    ROUND(a.revenue, 2)                     AS revenue,
    ROUND(b.revenue, 2)                     AS prev_year_revenue,
    ROUND((a.revenue - b.revenue) * 100.0 /
          NULLIF(b.revenue, 0), 1)          AS yoy_growth_pct,
    a.bookings,
    b.bookings                              AS prev_year_bookings
FROM yearly a
LEFT JOIN yearly b ON a.city = b.city AND a.year = b.year + 1
WHERE b.revenue IS NOT NULL
ORDER BY a.city, a.year;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q11: Cohort analysis — which months retain the highest-value customers?
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    quarter,
    visit_type,
    COUNT(*)                                AS bookings,
    ROUND(AVG(total_revenue), 2)            AS avg_revenue,
    ROUND(AVG(per_person_spend), 2)         AS avg_per_person,
    ROUND(SUM(total_revenue), 2)            AS total_revenue
FROM bookings
GROUP BY quarter, visit_type
ORDER BY quarter, total_revenue DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- Q12: Underserved market gap analysis
-- ─────────────────────────────────────────────────────────────────────────────
SELECT
    v.region,
    v.city,
    COUNT(DISTINCT v.id)                    AS venue_count,
    SUM(v.rooms)                            AS total_private_rooms,
    ROUND(AVG(v.yelp_rating), 2)            AS avg_rating,
    ROUND(SUM(b.total_revenue) /
          COUNT(DISTINCT v.id), 2)          AS avg_revenue_per_venue,
    ROUND(AVG(b.per_person_spend), 2)       AS avg_per_person_spend,
    v.median_rent_sqft
FROM venues v
JOIN bookings b ON v.id = b.venue_id
LEFT JOIN (SELECT city, median_rent_sqft FROM (
    VALUES ('San Francisco',8.5),('San Jose',4.2),('Milpitas',3.8),
           ('Millbrae',5.1),('Fremont',3.5),('Oakland',4.8)
) AS t(city, median_rent_sqft)) rent ON v.city = rent.city
GROUP BY v.region, v.city, v.median_rent_sqft
ORDER BY avg_revenue_per_venue DESC;
