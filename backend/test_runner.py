import sys
import pytest

def run_all_tests():
    print("Running NirikshanX Backend Test Suite...")
    exit_code = pytest.main(["-v", "tests"])
    sys.exit(exit_code)

if __name__ == "__main__":
    run_all_tests()
