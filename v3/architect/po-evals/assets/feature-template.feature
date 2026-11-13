@capability-<capability-slug>
Feature: <The feature's slug in words>
  <One line: the guarantee this feature carries.>

  Background:
    Given <the state every scenario starts from>

  @SC-<n>
  Scenario: <An observable result, in the product's words>
    Given <state, with a concrete value from the PRD's object examples>
    When <one action by a named role>
    Then <the result a person or a test can observe>

  @SC-<n> @ui @screen-<S-01>
  Scenario: <A result seen on a screen>
    Given <state>
    When <action on the screen>
    Then <what the screen shows>

  @SC-<n> @manual
  Scenario: <A result only a person can judge>
    Given <state>
    When <action>
    Then <what the tester should see>
