-- Co-morbidity analysis: which conditions appear together in the same patients
-- Input:  iceberg.raw.conditions
-- Output: iceberg.analytics.comorbidities
--
-- Aggregated at condition-pair level — no individual patient is identifiable.

CREATE TABLE IF NOT EXISTS iceberg.analytics.comorbidities AS
SELECT
    a.DESCRIPTION AS condition_a,
    b.DESCRIPTION AS condition_b,
    COUNT(DISTINCT a.PATIENT) AS patient_count
FROM iceberg.raw.conditions a
JOIN iceberg.raw.conditions b
    ON  a.PATIENT = b.PATIENT
    AND a.DESCRIPTION < b.DESCRIPTION  -- deduplicate pairs, exclude self-pairs
GROUP BY a.DESCRIPTION, b.DESCRIPTION
HAVING COUNT(DISTINCT a.PATIENT) >= 5  -- k-anonymity: suppress rare pairs
ORDER BY patient_count DESC;
