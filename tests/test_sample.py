"""
Sample Test
"""

import pytest
import onion.main


@pytest.fixture
def sample_fixture():
    """Setup test fixture"""
    return 1


def test_func(sample_fixture):
    """Test the sample function"""
    assert onion.main.sample_func(1) == 2


def test_negative(sample_fixture):
    """Negative test of sample function"""
    assert onion.main.sample_func(-2) == -1
