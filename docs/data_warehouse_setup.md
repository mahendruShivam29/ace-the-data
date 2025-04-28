
# Snowflake Data Warehouse Setup

## 1. Schema Structure

To organize the tennis analytics project in Snowflake, two separate schemas have been created:

| Schema Name | Purpose |
|-------------|---------|
| `GROUP_PROJECT_RAW` | Stores **raw ingested tables** loaded directly from the original CSV datasets |
| `GROUP_PROJECT_ANALYTICS` | Stores **transformed tables** created via dbt models, ready for analysis and dashboarding |

---

## 2. Raw Tables in `GROUP_PROJECT_RAW`

The following raw tables were created to hold unprocessed tennis data:

### `RAW_MATCHES`
Stores detailed match-level data extracted from the ATP match CSVs.

| Column Name       | Data Type   | Description |
|-------------------|-------------|-------------|
| tourney_id         | STRING       | Unique tournament ID |
| tourney_name       | STRING       | Tournament name |
| surface            | STRING       | Surface type (e.g., Hard, Clay, Grass) |
| draw_size          | NUMBER       | Size of the tournament draw |
| tourney_level      | STRING       | Tournament category (e.g., Grand Slam, Masters) |
| tourney_date       | NUMBER       | Tournament start date (format: `YYYYMMDD`) |
| match_num          | NUMBER       | Match number within tournament |
| winner_id          | NUMBER       | Winner's player ID |
| winner_seed        | STRING       | Seed number of the winner |
| winner_entry       | VARCHAR(5)   | Entry type of the winner (e.g., WC, Q) |
| winner_name        | STRING       | Winner's full name |
| winner_hand        | STRING       | Playing hand (R, L, A) |
| winner_ht          | NUMBER       | Winner's height (in cm) |
| winner_ioc         | STRING       | Winner's country (IOC code) |
| winner_age         | FLOAT8       | Winner's age at the time of match |
| loser_id           | NUMBER       | Loser's player ID |
| loser_seed         | NUMBER       | Seed number of the loser |
| loser_entry        | VARCHAR(5)   | Entry type of the loser |
| loser_name         | STRING       | Loser's full name |
| loser_hand         | STRING       | Playing hand of loser |
| loser_ht           | NUMBER       | Loser's height |
| loser_ioc          | STRING       | Loser's country |
| loser_age          | FLOAT8       | Loser's age at the time of match |
| score              | STRING       | Match score summary |
| best_of            | NUMBER       | Number of sets played (3 or 5) |
| round              | STRING       | Round of the match (e.g., R32, SF, F) |
| minutes            | NUMBER       | Match duration in minutes |
| w_ace, w_df, w_svpt, w_1stIn, w_1stWon, w_2ndWon, w_SvGms, w_bpSaved, w_bpFaced | NUMBER | Winner’s serve statistics |
| l_ace, l_df, l_svpt, l_1stIn, l_1stWon, l_2ndWon, l_SvGms, l_bpSaved, l_bpFaced | NUMBER | Loser’s serve statistics |
| winner_rank, winner_rank_points | NUMBER | Winner's ATP rank and ranking points |
| loser_rank, loser_rank_points   | NUMBER | Loser's ATP rank and ranking points |

---

### `RAW_PLAYERS`
Stores metadata for all players appearing in the matches.

| Column Name   | Data Type  | Description |
|---------------|------------|-------------|
| PLAYER_ID     | INTEGER    | Unique player identifier |
| NAME_FIRST    | VARCHAR(50) | Player’s first name |
| NAME_LAST     | VARCHAR(50) | Player’s last name |
| HAND          | VARCHAR(5) | Playing hand (Right, Left, Ambidextrous) |
| DOB           | DATE       | Date of birth |
| IOC           | VARCHAR(5) | Country code (IOC format) |
| HEIGHT        | FLOAT      | Player’s height in cm |
| WIKIDATA_ID   | VARCHAR(20) | Link to player’s Wikidata profile |

---

### `RAW_RANKINGS`
Stores weekly ATP player rankings over time.

| Column Name   | Data Type  | Description |
|---------------|------------|-------------|
| RANKING_DATE  | NUMBER     | Ranking week (format: `YYYYMMDD`) |
| RANK          | NUMBER     | Player’s rank number |
| PLAYER        | NUMBER     | Player’s unique ID |
| POINTS        | NUMBER     | Ranking points |

---

# Analytics Views (GROUP_PROJECT_ANALYTICS)

## View: `DASHBOARD_OVERVIEW`

**Purpose**:  
Provides a lightweight, cleaned match-level dataset for quick KPI calculations and chart building.

**Source**:  
`GROUP_PROJECT_RAW.RAW_MATCHES`

**Columns**:
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| tourney_id | STRING | Unique Tournament ID |
| tourney_name | STRING | Tournament Name |
| surface | STRING | Surface Type (Hard, Clay, Grass, Carpet) |
| tourney_date | DATE | Tournament Start Date (converted from numeric YYYYMMDD format) |
| winner_id | NUMBER | Winner's Player ID |
| loser_id | NUMBER | Loser's Player ID |
| minutes | NUMBER | Match Duration in Minutes |

**Notes**:
- Filters out matches where either winner or loser is missing (NULL).
- Ensures `tourney_date` is properly cast as `DATE` for easy time-based analysis.

---

## View: `UNIQUE_PLAYERS`

**Purpose**:  
Generates a distinct list of player IDs who appeared either as a winner or loser across all matches.

**Source**:  
`DASHBOARD_OVERVIEW`

**Columns**:
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| player_id | NUMBER | Unique Player ID (either as winner or loser) |

**Notes**:
- Combines winners and losers using UNION to eliminate duplicates.
- Useful for calculating KPIs like **Total Unique Players**.

---

## View: `MATCHES_OVER_YEAR`

**Purpose**:  
Aggregates total matches per year, broken down by surface type, to analyze match volume trends.

**Source**:  
`GROUP_PROJECT_RAW.RAW_MATCHES`

**Columns**:
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| match_year | NUMBER (4,0) | Year (e.g., 2024) extracted from tournament date |
| surface | STRING | Surface Type (Hard, Clay, Grass, Carpet) |
| matches | NUMBER | Number of Matches played that year on that surface |

**Notes**:
- `tourney_date` is safely converted from numeric to `DATE` type before extracting year.
- Enables Surface-level filtering and Year-over-Year time-series analysis.
- Designed to power charts like **Matches Over Time** and **Matches by Surface by Year**.

