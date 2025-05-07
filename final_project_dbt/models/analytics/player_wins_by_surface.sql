SELECT
    m.winner_id AS player_id,
    p.name_first,
    p.name_last,
    CONCAT(p.name_first, ' ', p.name_last) AS full_name,
    m.surface,
    COUNT(*) AS wins
FROM {{ ref('stg_raw_matches') }} m
JOIN {{ ref('stg_raw_players') }} p
    ON m.winner_id = p.player_id
WHERE m.winner_id IS NOT NULL
  AND m.surface IS NOT NULL
GROUP BY
    m.winner_id,
    p.name_first,
    p.name_last,
    m.surface
