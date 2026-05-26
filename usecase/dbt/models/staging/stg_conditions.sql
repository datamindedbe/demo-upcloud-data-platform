select * from {{ source('raw', 'conditions') }}
