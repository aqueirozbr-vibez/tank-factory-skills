@capability-anomaly-review
Feature: Review queue
  A planner confirms or dismisses each flagged reading.

  Background:
    Given an open anomaly for the asset "PMP-0412"

  @SC-6
  Scenario: A decision by an inspector is refused
    Given an inspector is signed in
    When the inspector tries to confirm the anomaly
    Then the decision is refused
    And the anomaly is still open

  @SC-7 @ui @screen-S-02
  Scenario: The planner sees the anomaly with the asset's range
    Given a planner is signed in
    When the planner opens Review Queue
    Then the anomaly for "PMP-0412" is listed with the range 4.0 to 9.0 bar
