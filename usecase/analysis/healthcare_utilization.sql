-- Healthcare utilization: which conditions drive the most hospital visits
-- Input:  iceberg.raw.conditions, iceberg.raw.encounters
-- Output: iceberg.analytics.healthcare_utilization
--
-- Aggregated at condition level — no individual patient is identifiable.

CREATE TABLE IF NOT EXISTS iceberg.analytics.healthcare_utilization AS
SELECT
    c.DESCRIPTION                                                        AS condition,
    COUNT(DISTINCT c.PATIENT)                                            AS patient_count,
    COUNT(DISTINCT e.Id)                                                 AS total_encounters,
    CAST(COUNT(DISTINCT e.Id) AS DOUBLE) / COUNT(DISTINCT c.PATIENT)    AS avg_encounters_per_patient,
    ROUND(AVG(e.TOTAL_CLAIM_COST), 2)                                   AS avg_encounter_cost
FROM iceberg.raw.conditions c
JOIN iceberg.raw.encounters e ON c.PATIENT = e.PATIENT
GROUP BY c.DESCRIPTION
HAVING COUNT(DISTINCT c.PATIENT) >= 5  -- k-anonymity: suppress rare conditions
ORDER BY avg_encounters_per_patient DESC;
