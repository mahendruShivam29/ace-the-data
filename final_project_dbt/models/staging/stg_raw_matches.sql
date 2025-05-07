SELECT
  *
FROM {{ source('group_project_raw', 'raw_matches') }}
WHERE TOURNEY_ID IS NOT NULL
  AND MATCH_NUM IS NOT NULL

