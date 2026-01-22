### Integration Test Template
```python
# tests/integration/test_feature.py
"""
Integration tests for [feature].

These tests verify multiple components working together. 
They may require external services and take longer to run. 

Run with: pytest -m integration
"""
import pytest


@pytest.mark. integration
class TestFeatureIntegration: 
    """Integration tests for feature."""
    
    @pytest.fixture
    def configured_system(self):
        """Set up a fully configured system."""
        system = create_system()
        yield system
        system. cleanup()
    
    def test_end_to_end_flow(self, configured_system):
        """Test complete flow from input to output."""
        input_data = create_input()
        result = configured_system.process(input_data)
        assert result. is_valid
    
    @pytest.mark.slow
    def test_performance_under_load(self, configured_system):
        """Test system handles load correctly."""
        # This test may take a while
        for _ in range(100):
            configured_system.process(create_input())
        assert configured_system. is_healthy
```
