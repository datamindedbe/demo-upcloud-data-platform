select id, birthdate, deathdate, gender, race, ethnicity from {{ source('raw', 'patients') }}
