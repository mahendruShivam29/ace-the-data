
SELECT
    TRY_TO_DATE(TO_VARCHAR(r.ranking_date), 'YYYYMMDD') AS ranking_date,
    r.player,
    CONCAT(p.name_first, ' ', p.name_last) AS player_name,
    r.rank,
    r.points
FROM {{ ref('stg_raw_rankings') }} r
JOIN {{ ref('stg_raw_players') }} p
    ON r.player = p.player_id

