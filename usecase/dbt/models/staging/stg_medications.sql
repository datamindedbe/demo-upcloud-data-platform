select start, stop, patient, encounter, code, description, base_cost, totalcost from {{ source('raw', 'medications') }}
