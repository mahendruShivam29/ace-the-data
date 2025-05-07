{% snapshot dashboard_overview_snapshot %}
{{
  config(
    target_schema='snapshot',
    unique_key='tourney_id',
    strategy='timestamp',
    updated_at='tourney_date',
    invalidate_hard_deletes=True
  )
}}

SELECT * FROM {{ ref('dashboard_overview') }}

{% endsnapshot %}
