select
    case
        when date_diff('year', date(BIRTHDATE), current_date) < 18 then '0-17'
        when date_diff('year', date(BIRTHDATE), current_date) < 35 then '18-34'
        when date_diff('year', date(BIRTHDATE), current_date) < 50 then '35-49'
        when date_diff('year', date(BIRTHDATE), current_date) < 65 then '50-64'
        else '65+'
    end                 as age_group,
    count(1)            as patient_count
from {{ ref('stg_patients') }}
group by 1
order by 1
