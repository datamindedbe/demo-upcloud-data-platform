select Id, START, STOP, PATIENT, encounterclass, description, base_encounter_cost, total_claim_cost from {{ source('raw', 'encounters') }}
