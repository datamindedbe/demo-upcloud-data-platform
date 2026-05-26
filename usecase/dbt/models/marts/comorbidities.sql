select
    a.DESCRIPTION                   as condition_a,
    b.DESCRIPTION                   as condition_b,
    count(distinct a.PATIENT)       as patient_count
from {{ ref('stg_conditions') }} a
join {{ ref('stg_conditions') }} b
    on  a.PATIENT     = b.PATIENT
    and a.DESCRIPTION < b.DESCRIPTION
group by 1, 2
having count(distinct a.PATIENT) >= 5
order by 3 desc
