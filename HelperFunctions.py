"""
file: HelperFunctions.py
description: Helper function for p100d.py
language: python3
author: Evan Prizel (emp4506)
"""


def in_to_m(value):
    """
    This converts unit inches to meters.
    :param value: The value wishing to be converted.
    :return: The converted value.
    """
    return value * .0254


def mps_to_mph(value):
    """
    This converts unit meters per second to miles per hour.
    :param value: The value wishing to be converted.
    :return: The converted value.
    """
    return value * 2.2369

