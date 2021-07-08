import os

"""
Directory which d++.py is placed
"""
DPP_HOME: str = os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
)
