select
    c.DESCRIPTION                                                       as condition,
    count(distinct c.PATIENT)                                           as patient_count,
    count(distinct e.Id)                                                as total_encounters,
    cast(count(distinct e.Id) as double) / count(distinct c.PATIENT)   as avg_encounters_per_patient,
    round(avg(cast(e.TOTAL_CLAIM_COST as double)), 2)                   as avg_encounter_cost
from {{ ref('stg_conditions') }} c
join {{ ref('stg_encounters') }} e on c.PATIENT = e.PATIENT
group by 1
having count(distinct c.PATIENT) >= 5
order by 4 desc
