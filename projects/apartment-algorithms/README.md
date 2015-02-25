# Rentlytics Engineering Exercises

Contained within this gist are two exercises, along with two JSON files containing the datasets you will need to complete the exercises.  You may use any language or tool you prefer.  Please do not spend more than 2 hours per solution.

After you've finished the exercises, please email your solutions to phil@rentlytics.com to set up a technical interview at our offices.

## Exercises
* Leasing Agent Leaderboard - see `exercise_leasing_agent_leaderboards.md`
* Apartment Marketing Fees - see `exercise_marketing_fees.md`

## Dataset Descriptions
* **guest_cards.json** - Each record is a unique person who has visited the apartment.  The record will let you determine who leased a unit.

* **unit_market_rents.json** - Provides a historical rent price for a unit.  A rent price is in effect until a newer record is added for that unit.

## Metric Definitions

* **Closing Time** - Each record contains a "first_seen" and "lease_signed" value.  A lease is considered closed when there is a date in "lease_signed."  You should use the delta in days as the time to close.

* **Increase in Unit Market Rent** - Each record in the guest cards dataset will contain a "unit_name" field, this will point to units in the UnitMarketRent dataset.  An increase in market rent is determined by the delta of "resident_rent" and a corresponding "market_rent".

* **Closing Rate** - The total number of records with "lease_signed" in a month.