@capability-reading-capture
Feature: Offline queue
  Readings saved without a connection reach the server exactly once.

  Background:
    Given an inspector signed in on a phone
    And the asset "PMP-0412" is on today's route

  @SC-1
  Scenario: A reading saved offline syncs once
    Given the phone has no connection
    When the inspector saves the reading 7.25 for "PMP-0412"
    And the connection returns
    Then the server holds exactly 1 reading for "PMP-0412" with the value 7.25

  @SC-1
  Scenario: The same reading sent twice is stored once
    Given a reading for "PMP-0412" has already synced
    When the phone sends the same reading again
    Then the server holds exactly 1 reading for "PMP-0412"
    And the second answer equals the first
