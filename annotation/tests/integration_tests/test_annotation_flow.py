import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

import django

django.setup()

from rest_framework.test import APIClient
import pytest

from annotation.helpers.utils.constants.constants import (
    KEY_IN_REQUEST_RML,
    KEY_IN_REQUEST_EPPG,
    KEY_IN_REQUEST_REQUIRED_FILTERS,
)

"""
This file contains tests that imitate the whole annotation flow process, but for specific situations of the created structures: continuous_structures and EventsStructures 
The whole tests of this file can be run with the CLI: pytest -s annotation/tests/integration_tests/test_annotation_flow.py (this method is faster)
"""


def run_annotation_test(rml_path, eppg_path, expected_output_path, output_path, selected_filters):
    client = APIClient()

    # 1) Upload RML
    with open(rml_path, "rb") as rml_file:
        response = client.post("/annotation/filters/", data={KEY_IN_REQUEST_RML: rml_file})
        filters = response.json()["result"]["filters"]

    # 2) Post selected filters
    response = client.post("/annotation/filters/selected/", data=selected_filters, format="json")

    # 3) Upload ePPG
    with open(eppg_path, "rb") as eppg_file:
        response = client.post("/annotation/files/eppg/", data={KEY_IN_REQUEST_EPPG: eppg_file})

    # 4) Annotate
    response = client.get("/annotation/annotate/")
    assert response.status_code == 200

    # 5) Save output
    # Make sure the output directory exists:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as out_file:
        for chunk in response.streaming_content:
            out_file.write(chunk)

    # 6) Compare result to expected
    with open(output_path, "r") as result, open(expected_output_path, "r") as expected:
        result_content = result.read()
        expected_content = expected.read()

    assert result_content == expected_content, (
        f"Output did not match expected for {rml_path}."
    )


# MAIN GENERAL DIRECTORIES
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

rml_base_directory = os.path.join(BASE_DIR, "test_data")
eppg_path = os.path.join(BASE_DIR, "test_data", "ePPG_Data.txt")
expected_out_base_directory = os.path.join(BASE_DIR, "test_data", "ExpectedResults")
out_base_directory = os.path.join(BASE_DIR, "test_outputs")

# -------------------------------------EVENTS-----------------------------------------
rml_events_path = os.path.join(rml_base_directory, "EventsStructureTesting")
expected_events_path = os.path.join(expected_out_base_directory, "EventsStructureTesting")
out_events_path = os.path.join(out_base_directory, "EventsStructureTesting")
# There will be two test suites: Events as List and as Element

# -----------------EVENTS AS LIST-----------------------------------------------------
# This section tests the annotation of different situations for events as list structure
rml_list_events_path = os.path.join(rml_events_path, "ListInstance")
expected_list_events_path = os.path.join(expected_events_path, "ListInstance")
out_events_list_path = os.path.join(out_events_path, "ListInstance")

# --------Synchronization Tests-------------------------------------------------------
rml_list_events_synch_path = os.path.join(rml_list_events_path, "SynchronizationTesting")
expected_list_events_synch_path = os.path.join(expected_list_events_path, "SynchronizationTesting")
out_events_list_synch_path = os.path.join(out_events_list_path, "SynchronizationTesting")

# Checks skip_events_before_start_of_ePPG
# There can be 3 situations:
# test_1: two events are skipped, because were recorded earlier in the RML
#   this time preference can be changed by changing the time of record in source RML file
# test_2: checks, whether 2 events are written to the file, if they were recorded within the timing of RML and ePPG
# test_3: checks, whether 1 event is not recorded (because out of sync), 2 event is recorded (because within sync)
#   also, this test checks, whether the event has an synchronized time
#   in detail, the rml started the recording 2 seconds earlier than eppg, and all events should be annotated with the offset -2 seconds
synchronization_tests = [
    (
        os.path.join(rml_list_events_synch_path, "test_1_events_recorded_earlier.rml"),
        eppg_path,
        os.path.join(expected_list_events_synch_path, "test_1.txt"),
        os.path.join(out_events_list_synch_path, "test_1.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"], "Cardiac": ["Tachycardia"]}},
    ),
    (
        os.path.join(rml_list_events_synch_path, "test_2_events_recorded_after.rml"),
        eppg_path,
        os.path.join(expected_list_events_synch_path, "test_2.txt"),
        os.path.join(out_events_list_synch_path, "test_2.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"], "Cardiac": ["Tachycardia"]}},
    ),
    (
        os.path.join(rml_list_events_synch_path, "test_3_events_recorded_before_and_after.rml"),
        eppg_path,
        os.path.join(expected_list_events_synch_path, "test_3.txt"),
        os.path.join(out_events_list_synch_path, "test_3.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"], "Cardiac": ["Tachycardia"]}},
    ),

]
# --------Filters Tests-------------------------------------------------------
rml_list_events_filters_path = os.path.join(rml_list_events_path, "FiltersTesting")
expected_list_events_filters_path = os.path.join(expected_list_events_path, "FiltersTesting")
out_events_list_filters_path = os.path.join(out_events_list_path, "FiltersTesting")

# Checks skip_filter_oriented_events
# There are 2 situations (timedelta between files equals to 0):
# test_1: the first event is not in filters, the second is in filters
# test_2: two events in the filters
# The checking of empty filters is omitted, because this situation could not happen (the List Structure will not exist)
filters_tests = [
    (
        os.path.join(rml_list_events_filters_path, "test_1_2.rml"),
        eppg_path,
        os.path.join(expected_list_events_filters_path, "test_1.txt"),
        os.path.join(out_events_list_filters_path, "test_1.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"]}},
    ),
    (
        os.path.join(rml_list_events_filters_path, "test_1_2.rml"),
        eppg_path,
        os.path.join(expected_list_events_filters_path, "test_2.txt"),
        os.path.join(out_events_list_filters_path, "test_2.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"], "Cardiac": ["Tachycardia"]}},
    )
]
# --------Start Events Tests-------------------------------------------------------
rml_list_events_start_path = os.path.join(rml_list_events_path, "StartEventsTesting")
expected_list_events_start_path = os.path.join(expected_list_events_path, "StartEventsTesting")
out_events_list_start_path = os.path.join(out_events_list_path, "StartEventsTesting")

# Checks find_events_with_the_same_time_start
# There are 3 situations(timedelta between files equals to 0):
# the first and second events have different times and both in filters (it was tested by filters testing test_2)
# test_1: two events have the same time and both in filters
# test_2: two events have the same time, but the second is not in filters
start_events = [
    (
        os.path.join(rml_list_events_start_path, "test_1_2.rml"),
        eppg_path,
        os.path.join(expected_list_events_start_path, "test_1.txt"),
        os.path.join(out_events_list_start_path, "test_1.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"], "Cardiac": ["Tachycardia"]}},
    ),
    (
        os.path.join(rml_list_events_start_path, "test_1_2.rml"),
        eppg_path,
        os.path.join(expected_list_events_start_path, "test_2.txt"),
        os.path.join(out_events_list_start_path, "test_2.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Cardiac": ["Tachycardia"]}},
    )
]
# --------End Events Tests-------------------------------------------------------
rml_list_events_end_path = os.path.join(rml_list_events_path, "EndEventsTesting")
expected_list_events_end_path = os.path.join(expected_list_events_path, "EndEventsTesting")
out_events_list_end_path = os.path.join(out_events_list_path, "EndEventsTesting")

# Checks update_end_events_waiting_dictionary
# There are 3 situations(timedelta between files equals to 0):
# only one end event happen at specific time (tested in filters test_2)
# two end events happen at the specific time (tested in start_events test_1)
# test_1: three events happen at the specific time
end_events = [
    (
        os.path.join(rml_list_events_end_path, "test_1.rml"),
        eppg_path,
        os.path.join(expected_list_events_end_path, "test_1.txt"),
        os.path.join(out_events_list_end_path, "test_1.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"], "Cardiac": ["Tachycardia", "Bradycardia"]}},
    ),
]


# --------write_START_events_into_comment_line Tests-------------------------------------------------------
# There could be situation, which wasn't mention, but already tested: three events (2 at the same start time, one not)
# It was tested in end_events test_1
# ---------------------------------------------------Test function-----------------------------------------

@pytest.mark.parametrize("rml,eppg,expected,output,filters",
                         synchronization_tests + filters_tests + start_events + end_events)
def test_events_list_structure_annotation(rml, eppg, expected, output, filters):
    run_annotation_test(rml, eppg, expected, output, filters)


# -----------------EVENTS AS ELEMENT-----------------------------------------------------
# Testing this structure, there could be the next situations:
# 1. The single event is not in filters, then the structure EventsRecordsNotList does not exist =>test is omitted
# 2. (test_1) The element is skipped because of the synchronization time, or it is type of "User" (will be tested only first condition)
# 3. (test_2) The event is annotated

rml_element_event_path = os.path.join(rml_events_path, "ElementInstance")
expected_element_event_path = os.path.join(expected_events_path, "ElementInstance")
out_element_event_path = os.path.join(out_events_path, "ElementInstance")

element_events = [
    (
        os.path.join(rml_element_event_path, "test_1.rml"),
        eppg_path,
        os.path.join(expected_element_event_path, "test_1.txt"),
        os.path.join(out_element_event_path, "test_1.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"]}},
    ),
    (
        os.path.join(rml_element_event_path, "test_2.rml"),
        eppg_path,
        os.path.join(expected_element_event_path, "test_2.txt"),
        os.path.join(out_element_event_path, "test_2.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"Respiration": ["Apnea"]}},
    )
]


@pytest.mark.parametrize("rml,eppg,expected,output,filters", element_events)
def test_events_element_structure_annotation(rml, eppg, expected, output, filters):
    run_annotation_test(rml, eppg, expected, output, filters)


# -------------------------------------CONTINUOUS STRUCTURE-----------------------------------------
rml_continuous_structure_path = os.path.join(rml_base_directory, "ContinuousStructureTesting")
expected_continuous_structure_path = os.path.join(expected_out_base_directory, "ContinuousStructureTesting")
out_continuous_structure_path = os.path.join(out_base_directory, "ContinuousStructureTesting")
# There will be two test suites: Continuous Structures as List and as Element

# -----------------CONTINUOUS STRUCTURE AS LIST-----------------------------------------------------
# Testing this structure, there could be the next situations:
# The next two situation test initialization process
# 1. (test_1) Two elements are not annotated: the first because of sync process, the second because of filters inclusion (just to test two different situations)
# 2. (test_2) The first is not annotated, the second is
# The next situation test initialization process and write_into_comments function
# 3. (test_3) The first is annotated, the second is not

continuous_structure_list = [
    (
        os.path.join(rml_continuous_structure_path, "test_1.rml"),
        eppg_path,
        os.path.join(expected_continuous_structure_path, "test_1.txt"),
        os.path.join(out_continuous_structure_path, "test_1.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"SleepStages": ["NonREM1"]}},
    ),
    (
        os.path.join(rml_continuous_structure_path, "test_2.rml"),
        eppg_path,
        os.path.join(expected_continuous_structure_path, "test_2.txt"),
        os.path.join(out_continuous_structure_path, "test_2.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"SleepStages": ["NonREM2"]}},
    ),
    (
        os.path.join(rml_continuous_structure_path, "test_2.rml"),
        eppg_path,
        os.path.join(expected_continuous_structure_path, "test_3.txt"),
        os.path.join(out_continuous_structure_path, "test_3.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"SleepStages": ["NonREM1"]}},
    )
]


@pytest.mark.parametrize("rml,eppg,expected,output,filters", continuous_structure_list)
def test_continuous_structure_list_annotation(rml, eppg, expected, output, filters):
    run_annotation_test(rml, eppg, expected, output, filters)


# -----------------CONTINUOUS STRUCTURE AS ELEMENT-----------------------------------------------------
# Testing this structure, there could be the next situations:
# 1. (test_3) Element was skipped during initialization process
# 2. (test_4) The element was recorded

continuous_structure_list = [
    (
        os.path.join(rml_continuous_structure_path, "test_3.rml"),
        eppg_path,
        os.path.join(expected_continuous_structure_path, "test_3.txt"),
        os.path.join(out_continuous_structure_path, "test_3.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"SleepStages": ["NonREM1"]}},
    ),
    (
        os.path.join(rml_continuous_structure_path, "test_4.rml"),
        eppg_path,
        os.path.join(expected_continuous_structure_path, "test_4.txt"),
        os.path.join(out_continuous_structure_path, "test_4.txt"),
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"SleepStages": ["NonREM1"]}},
    ),
]


@pytest.mark.parametrize("rml,eppg,expected,output,filters", continuous_structure_list)
def test_continuous_structure_list_annotation(rml, eppg, expected, output, filters):
    run_annotation_test(rml, eppg, expected, output, filters)


# -------------------------------------GENERAL TESTING-----------------------------------------
# This section tests the synchronization between files, when ePPG is recorded earlier than PSG
# This test is applicable to all structures identically
rml_general_testing_eppg_earlier_path = os.path.join(rml_base_directory, "GeneralTesting",
                                                     "test_1_eppg_recorded_earlier.rml")
expected_general_testing_eppg_earlier_path = os.path.join(expected_out_base_directory, "GeneralTesting",
                                                          "test_1_eppg_recorded_earlier.txt")
out_general_testing_eppg_earlier_path = os.path.join(out_base_directory, "GeneralTesting",
                                                     "test_1_eppg_recorded_earlier.txt")

general_testing = [
    (
        rml_general_testing_eppg_earlier_path,
        eppg_path,
        expected_general_testing_eppg_earlier_path,
        out_general_testing_eppg_earlier_path,
        {KEY_IN_REQUEST_REQUIRED_FILTERS: {"SleepStages": ["NonREM1"]}},
    )
]


@pytest.mark.parametrize("rml,eppg,expected,output,filters", general_testing)
def test_general_testing_annotation(rml, eppg, expected, output, filters):
    run_annotation_test(rml, eppg, expected, output, filters)
