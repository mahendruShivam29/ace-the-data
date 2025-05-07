SELECT
    m.winner_id AS player_id,
    p.name_first,
    p.name_last,
    CONCAT(p.name_first, ' ', p.name_last) AS full_name,
    COUNT(*) AS matches_won,

    AVG(m.w_ace) AS avg_aces,
    AVG(m.w_df) AS avg_double_faults,
    AVG(m.w_1stIn / NULLIF(m.w_svpt, 0)) AS first_serve_in_pct,
    AVG(m.w_1stWon / NULLIF(m.w_1stIn, 0)) AS first_serve_win_pct,
    AVG(m.w_2ndWon / NULLIF((m.w_svpt - m.w_1stIn), 0)) AS second_serve_win_pct

FROM {{ ref('stg_raw_matches') }} m
JOIN {{ ref('stg_raw_players') }} p
  ON m.winner_id = p.player_id

WHERE m.winner_id IS NOT NULL
  AND m.w_svpt > 0

GROUP BY
  m.winner_id,
  p.name_first,
  p.name_last
