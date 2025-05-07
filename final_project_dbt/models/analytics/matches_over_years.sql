SELECT
    CAST(EXTRACT(YEAR FROM TRY_TO_DATE(TO_VARCHAR(tourney_date), 'YYYYMMDD')) AS NUMBER(4, 0)) AS match_year,
    surface,
    COUNT(*) AS matches
FROM {{ ref('stg_raw_matches') }}
WHERE winner_id IS NOT NULL
  AND loser_id IS NOT NULL
GROUP BY match_year, surface
ORDER BY match_year ASC
