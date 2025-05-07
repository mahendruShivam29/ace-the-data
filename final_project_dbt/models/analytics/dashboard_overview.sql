SELECT
    tourney_id,
    tourney_name,
    surface,
    TRY_TO_DATE(TO_VARCHAR(tourney_date), 'YYYYMMDD') AS tourney_date,
    winner_id,
    loser_id,
    minutes
FROM {{ ref('stg_raw_matches') }}
WHERE winner_id IS NOT NULL
  AND loser_id IS NOT NULL
