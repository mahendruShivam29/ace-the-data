SELECT
  *
FROM {{ source('group_project_raw', 'raw_rankings') }}
WHERE RANKING_DATE IS NOT NULL
  AND PLAYER IS NOT NULL