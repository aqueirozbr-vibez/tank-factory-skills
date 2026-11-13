@capability-anomaly-review
Feature: Flag anomaly
  A reading outside its asset's range is flagged for a planner.

  @SC-4
  Scenario Outline: A reading outside the range is flagged within 5 minutes
    Given the asset "PMP-0412" has the range 4.0 to 9.0 bar
    When a reading of <value> bar for "PMP-0412" syncs
    Then an open anomaly for that reading exists within 5 minutes

    Examples:
      | value |
      | 3.9   |
      | 9.1   |

  @SC-5
  Scenario: The summary states value, unit and difference from the mean
    Given the 30-day mean for "PMP-0412" is 6.85 bar
    When a reading of 9.10 bar for "PMP-0412" is flagged
    Then the anomaly's summary contains "9.10", "bar" and "2.25"
