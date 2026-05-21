-- Age distribution of the patient population
-- Input:  iceberg.raw.patients
-- Output: iceberg.analytics.age_distribution

CREATE TABLE IF NOT EXISTS iceberg.analytics.age_distribution AS
SELECT
    CASE
        WHEN date_diff('year', date(BIRTHDATE), current_date) < 18 THEN '0-17'
        WHEN date_diff('year', date(BIRTHDATE), current_date) < 35 THEN '18-34'
        WHEN date_diff('year', date(BIRTHDATE), current_date) < 50 THEN '35-49'
        WHEN date_diff('year', date(BIRTHDATE), current_date) < 65 THEN '50-64'
        ELSE '65+'
    END AS age_group,
    COUNT(*) AS patient_count
FROM iceberg.raw.patients
GROUP BY age_group
ORDER BY age_group;
