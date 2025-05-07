SELECT
  *
FROM {{ source('group_project_raw', 'raw_players') }}
WHERE PLAYER_ID IS NOT NULL


  