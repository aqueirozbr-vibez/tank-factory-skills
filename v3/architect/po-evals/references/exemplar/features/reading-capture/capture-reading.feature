@capability-reading-capture
Feature: Capture reading
  An inspector records a reading against a known asset in a few taps.

  Background:
    Given an inspector signed in on a phone
    And the asset "PMP-0412" with the unit "bar" is on today's route

  @SC-2 @ui @screen-S-01 @smoke
  Scenario: Recording a reading takes at most 3 taps
    Given the inspector has entered the tag "PMP-0412" on Reading Capture
    When the inspector enters the value 7.25 and saves
    Then the reading 7.25 bar for "PMP-0412" is in today's list
    And the inspector made at most 3 taps after entering the tag

  @SC-3 @ui @screen-S-01
  Scenario: An unknown tag is refused with the next step
    Given the tag "XXX-0000" is not in the asset list
    When the inspector enters the value 7.25 for "XXX-0000" and saves
    Then no reading is saved
    And Reading Capture shows "Tag not found. Check the tag or ask your planner."
    And the value 7.25 is still on screen

  @SC-2 @ui @screen-S-01 @manual
  Scenario: The save target can be hit with a gloved thumb
    Given the inspector wears work gloves
    When the inspector saves 5 readings in a row on a 360 px phone
    Then every save lands on the first press
