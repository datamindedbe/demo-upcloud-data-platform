select START, STOP, PATIENT, ENCOUNTER, CODE, DESCRIPTION from {{ source('raw', 'conditions') }}
