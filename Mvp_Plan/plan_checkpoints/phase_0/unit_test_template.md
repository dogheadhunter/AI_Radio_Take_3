### Unit Test Template
```python
# tests/module/test_component.py
"""
Tests for [component]. 

Test naming convention:
    test_[method]_[scenario]_[expected_result]
    
Example:
    test_add_song_valid_input_increases_count
"""
import pytest
from src.ai_radio. module.component import function_to_test


class TestFunctionName:
    """Tests for function_name."""
    
    def test_returns_expected_type(self):
        """Function must return the expected type."""
        result = function_to_test()
        assert isinstance(result, ExpectedType)
    
    def test_handles_edge_case(self):
        """Function must handle edge case correctly."""
        result = function_to_test(edge_input)
        assert result == expected_output
    
    def test_raises_on_invalid_input(self):
        """Function must raise appropriate error on invalid input."""
        with pytest. raises(ExpectedError):
            function_to_test(invalid_input)


class TestAnotherScenario:
    """Tests for another scenario."""
    
    @pytest.fixture
    def setup_data(self):
        """Set up data for these tests."""
        return create_test_data()
    
    def test_with_setup(self, setup_data):
        """Test using the setup fixture."""
        result = function_to_test(setup_data)
        assert result is not None
```
