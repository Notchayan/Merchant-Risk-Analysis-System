# Testing Documentation

## Overview
The test suite covers various aspects of the merchant risk analysis system, including merchant validation, fraud pattern detection, and dataset balance verification.

## Test Setup

1. Install required packages:
```bash
pip install pytest pytest-cov requests
```

2. Create test configuration file `.env.test`:
```env
BASE_URL=https://winter-assignment.onrender.com
TEST_MERCHANT_ID=M1234567
```

3. Directory structure:
```
tests/
├── __init__.py
├── conftest.py
├── test_merchant_validation.py
├── test_fraud_patterns.py
└── test_dataset_balance.py
```

## Running Tests

Run all tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

Run specific test file:
```bash
pytest tests/test_merchant_validation.py
```

## Test Categories

### 1. Merchant Validation Tests
- Business hour distribution validation
- Amount distribution patterns
- Customer diversity checks

Reference implementation:
```python:tests/test_merchant_validation.py
startLine: 1
endLine: 50
```

### 2. Fraud Pattern Tests
- Late night trading patterns
- Transaction velocity abuse
- Device switching patterns
- Location hopping detection
- Payment method cycling
- Round amount transactions

Reference implementation:
```python:tests/test_fraud_patterns.py
startLine: 1
endLine: 70
```

### 3. Dataset Balance Tests
- Fraud/normal merchant ratio
- Pattern distribution verification
- Statistical measures validation

Reference implementation:
```python:tests/test_dataset_balance.py
startLine: 1
endLine: 60
```

## Test Data Generation

The tests use both real and synthetic data:

1. Real data from the production API
2. Synthetic data generated using the data generator:
```python:src/your_generator.py
startLine: 285
endLine: 339
```

## Risk Metrics Validation

Tests verify the accuracy of risk metrics calculation:
```python:src/risk_metrics.py
startLine: 42
endLine: 164
```

## Timeline Events Verification

Tests ensure proper detection of suspicious events:
```python:src/timeline_events.py
startLine: 43
endLine: 99
```

## Expected Test Coverage

- Unit Tests: >80% coverage
- Integration Tests: >70% coverage
- End-to-End Tests: >60% coverage

## Common Test Scenarios

1. Normal Merchant Validation
   - Check business hour distribution
   - Verify amount distributions
   - Validate customer diversity

2. Fraud Pattern Validation
   - Verify pattern characteristics
   - Check pattern timing
   - Validate pattern intensity

3. Dataset Balance
   - Check fraud/normal ratio
   - Verify pattern distribution
   - Validate overall statistics

## Continuous Integration

Tests are automatically run on:
- Pull request creation
- Merge to main branch
- Daily scheduled runs

## Troubleshooting

Common issues and solutions:

1. API Connection Issues
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

2. Test Database Setup
```bash
python scripts/setup_test_db.py
```

3. Rate Limiting
```python
import time
time.sleep(1)  # Add delay between API calls
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Include both positive and negative test cases
3. Add appropriate documentation
4. Ensure proper error handling
5. Verify coverage impact

## Test Maintenance

Regular maintenance tasks:

1. Update test data monthly
2. Verify API endpoints quarterly
3. Review and update test scenarios
4. Monitor test execution times
5. Update documentation as needed
