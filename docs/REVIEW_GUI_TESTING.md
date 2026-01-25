# Review GUI Testing Documentation

This document describes the testing infrastructure for the AI Radio Review GUI feature.

## Test Files

### `tests/test_review_gui.py`
Tests for the main Review GUI module (`review_gui.py`).

**Coverage:**
- Content scanning and discovery
- ReviewItem class and version management
- Filtering and pagination logic
- Review status persistence (load/save)
- Audit status retrieval
- Regeneration queue management
- CSV export functionality
- Failure reason categories
- Outro naming convention handling

**Tests (10 total):**
1. `test_scan_generated_content` - Verifies content discovery
2. `test_review_item_version_paths` - Tests version path retrieval
3. `test_filter_items` - Tests filtering by type, DJ, status, search
4. `test_load_save_review_status` - Tests review status persistence
5. `test_get_audit_status` - Tests audit status lookup
6. `test_regeneration_queue` - Tests queue operations
7. `test_export_reviews_to_csv` - Tests CSV export
8. `test_failure_reason_categories` - Validates predefined categories
9. `test_outro_naming_convention` - Tests outro file naming
10. `test_review_status_persistence` - Tests status updates

### `tests/test_regen_queue_processor.py`
Tests for the regeneration queue processor (`scripts/process_regen_queue.py`).

**Coverage:**
- Version number calculation for all content types
- Folder name parsing (songs, time slots)
- Naming convention differences (intros vs outros)
- Queue file structure validation

**Tests (6 total):**
1. `test_get_next_version_number_intros` - Version incrementing for intros
2. `test_get_next_version_number_outros` - Version incrementing for outros
3. `test_parse_song_info_from_folder` - Artist/title extraction
4. `test_parse_time_info_from_folder` - Hour/minute extraction
5. `test_queue_file_structure` - Queue JSON validation
6. `test_version_increment_logic` - Naming pattern verification

## Running Tests

### Run All Review GUI Tests
```bash
pytest tests/test_review_gui.py tests/test_regen_queue_processor.py -v
```

### Run Specific Test File
```bash
# Review GUI tests only
pytest tests/test_review_gui.py -v

# Queue processor tests only
pytest tests/test_regen_queue_processor.py -v
```

### Run Specific Test
```bash
pytest tests/test_review_gui.py::test_scan_generated_content -v
```

### Run with Coverage
```bash
pytest tests/test_review_gui.py tests/test_regen_queue_processor.py --cov=review_gui --cov=scripts.process_regen_queue --cov-report=html
```

## Test Modes

The project uses a dual testing mode system (mock/integration). All Review GUI tests use **mock mode** for fast execution without requiring external services.

### Mock Mode (Default)
```bash
pytest tests/test_review_gui.py -v
# or explicitly:
TEST_MODE=mock pytest tests/test_review_gui.py -v
```

Mock tests use fixtures from `tests/conftest.py`:
- `mock_services` - Mocks LLM and TTS for pipeline tests
- `tmp_path` - Pytest's temporary directory fixture

## Test Structure

### Fixtures Used
- **`tmp_path`** (pytest built-in) - Temporary directories for isolated tests
- **`sample_generated_content`** - Creates sample file structure with all content types
- **`monkeypatch`** (pytest built-in) - For patching module-level constants

### Sample Data Structure
Tests create realistic sample data:
```
tmp_path/data/
├── generated/
│   ├── intros/julie/Test_Artist-Test_Song/
│   │   ├── julie_0.txt
│   │   └── julie_0.wav
│   ├── outros/mr_new_vegas/Other_Artist-Other_Song/
│   │   ├── mr_new_vegas_outro.txt
│   │   └── mr_new_vegas_outro.wav
│   ├── time/julie/12-00/
│   │   ├── julie_0.txt
│   │   └── julie_0.wav
│   └── weather/mr_new_vegas/06-00/
│       ├── mr_new_vegas_0.txt
│       ├── mr_new_vegas_0.wav
│       ├── mr_new_vegas_1.txt
│       └── mr_new_vegas_1.wav
├── audit/
│   └── julie/
│       ├── passed/Test_Artist-Test_Song_intro_audit.json
│       └── failed/12-00_time_audit.json
└── regeneration_queue.json
```

## Integration Testing

For full end-to-end testing with the Review GUI:

### Manual Testing Steps
1. **Create sample data:**
   ```bash
   python scripts/create_sample_data_for_review.py
   ```

2. **Launch Review GUI:**
   ```bash
   python run_review_gui.py
   ```

3. **Test scenarios:**
   - Filter by content type, DJ, status
   - Review and approve/reject items
   - Select failure reasons
   - Add notes
   - Queue regeneration requests
   - Export to CSV
   - Compare versions

4. **Test queue processor:**
   ```bash
   # Queue some items via GUI first
   python scripts/process_regen_queue.py
   # Verify new versions created
   ```

## Test Coverage Goals

- **Unit tests**: 100% coverage of core logic (filtering, status management, queue ops)
- **Integration tests**: Key workflows tested via manual GUI testing
- **Edge cases**: Malformed data, missing files, different naming conventions

## Continuous Integration

Tests run automatically in CI/CD pipeline:
- All mock tests execute in <1 second
- No external service dependencies
- Isolated tmp directories prevent test contamination

## Adding New Tests

When adding features to the Review GUI:

1. **Add unit tests** to `test_review_gui.py` for:
   - New functions/methods
   - New filtering logic
   - New status types

2. **Add processor tests** to `test_regen_queue_processor.py` for:
   - New regeneration types
   - New parsing logic
   - New queue operations

3. **Follow existing patterns**:
   ```python
   @pytest.mark.mock
   def test_my_new_feature(sample_generated_content, monkeypatch):
       """Test description."""
       # Setup
       import review_gui
       monkeypatch.setattr(review_gui, 'GENERATED_DIR', sample_generated_content['generated_dir'])
       
       # Test
       result = my_function()
       
       # Assert
       assert result == expected
   ```

## Troubleshooting

### Tests fail with ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Tests fail with import errors
Ensure you're running from project root:
```bash
cd /path/to/AI_Radio_Take_3
pytest tests/test_review_gui.py -v
```

### Tests fail with path issues
Check that `conftest.py` is setting up paths correctly:
```python
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
```

## Future Enhancements

Potential test additions:
- [ ] Streamlit UI component tests (using `streamlit.testing`)
- [ ] Performance tests for large datasets (1000+ items)
- [ ] Concurrent queue processing tests
- [ ] CSV export format validation
- [ ] Audio file validation tests
