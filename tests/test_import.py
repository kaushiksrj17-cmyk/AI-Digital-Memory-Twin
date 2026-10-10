import sys
import os

def test_app_import():
    if r"D:\ECHO" not in sys.path:
        sys.path.insert(0, r"D:\ECHO")
    import backend.app.main as m
    assert m.app.title is not None
