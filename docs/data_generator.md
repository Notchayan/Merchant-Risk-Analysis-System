# Data Generator Module Documentation

`src/data_generator.py` is a comprehensive module designed to generate realistic merchant and transaction data for testing and simulation purposes. This documentation provides an in-depth overview of the module's functionalities, classes, and functions, ensuring you can effectively utilize and extend it as needed.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Module Structure](#module-structure)
    - [Classes](#classes)
        - [`TransactionBase`](#transactionbase)
        - [`MerchantBase`](#merchantbase)
    - [Functions](#functions)
        - [`generate_merchant_id`](#generate_merchant_id)
        - [`generate_business_name`](#generate_business_name)
        - [`generate_random_date`](#generate_random_date)
        - [`generate_merchant_base`](#generate_merchant_base)
        - [`generate_transaction_id`](#generate_transaction_id)
        - [`generate_business_hour_timestamp`](#generate_business_hour_timestamp)
        - [`generate_normal_transactions`](#generate_normal_transactions)
        - [`inject_fraud_pattern`](#inject_fraud_pattern)
        - [`validate_merchant_data`](#validate_merchant_data)
        - [`validate_transaction_data`](#validate_transaction_data)
        - [`generate_dataset`](#generate_dataset)
5. [Example Usage](#example-usage)
6. [Error Handling](#error-handling)
7. [Logging](#logging)
8. [Customization](#customization)
9. [License](#license)

---

## Overview

The `data_generator.py` module is crafted to simulate realistic merchant and transaction data, incorporating various business types, payment methods, platforms, and potential fraud patterns. It leverages libraries such as `Faker` for generating fake data and `Pydantic` for data validation, ensuring the generated datasets adhere to predefined schemas.

---

## Installation

Before using the `data_generator.py` module, ensure you have the necessary dependencies installed. You can install them using `pip`:

```bash
pip install faker pydantic
```

---

## Usage

The module can be used to generate a dataset of merchants and transactions, with the ability to inject various fraud patterns. This is particularly useful for testing fraud detection systems, simulating transaction flows, or populating databases with sample data.

---

## Module Structure

### Classes

#### `TransactionBase`

```python:src/data_generator.py
class TransactionBase(BaseModel):
    transaction_id: str = Field(..., min_length=8, max_length=50)
    merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    receiver_merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    timestamp: datetime
    amount: float = Field(..., gt=0, lt=1000000)
    payment_method: str = Field(..., min_length=3, max_length=50)
    status: str = Field(..., pattern=f"^({'|'.join(TRANSACTION_STATUSES)})$")
    product_category: str
    platform: str
    customer_location: str = Field(..., min_length=2, max_length=100)
    customer_id: str = Field(..., min_length=8)
    device_id: str = Field(..., min_length=8)
    velocity_flag: bool = False
    amount_flag: bool = False
    time_flag: bool = False
    device_flag: bool = False
```

**Description:**

Defines the schema for a transaction using Pydantic's `BaseModel`. It includes various fields such as `transaction_id`, `merchant_id`, `amount`, `payment_method`, and flags for different fraud indicators.

**Fields:**

- `transaction_id`: Unique identifier for the transaction.
- `merchant_id`: ID of the merchant initiating the transaction.
- `receiver_merchant_id`: ID of the merchant receiving the transaction.
- `timestamp`: Date and time of the transaction.
- `amount`: Transaction amount.
- `payment_method`: Method used for payment.
- `status`: Current status of the transaction.
- `product_category`: Category of the product involved in the transaction.
- `platform`: Platform through which the transaction was made.
- `customer_location`: Location of the customer.
- `customer_id`: Unique identifier for the customer.
- `device_id`: Identifier for the device used.
- `velocity_flag`, `amount_flag`, `time_flag`, `device_flag`: Flags indicating potential fraud based on various criteria.

---

#### `MerchantBase`

```python:src/data_generator.py
class MerchantBase(BaseModel):
    merchant_id: str = Field(..., pattern="^M[0-9]{7}$")
    business_name: str = Field(..., min_length=5, max_length=100)
    business_type: str = Field(..., min_length=3)
    registration_date: datetime
    business_model: str = Field(..., pattern="^(Online|Offline|Hybrid)$")
    product_category: str
    average_ticket_size: float = Field(..., gt=0)
    gst_status: bool
    epfo_registered: bool
    registered_address: str = Field(..., min_length=10, max_length=200)
    city: str = Field(..., min_length=2, max_length=50)
    state: str = Field(..., min_length=2, max_length=50)
    reported_revenue: float = Field(..., gt=0)
    employee_count: int = Field(..., gt=0, lt=1000000)
    bank_account: str = Field(..., min_length=8, max_length=20)
```

**Description:**

Defines the schema for a merchant profile using Pydantic's `BaseModel`. It includes details such as `merchant_id`, `business_name`, `business_type`, and various financial and operational attributes.

**Fields:**

- `merchant_id`: Unique identifier for the merchant.
- `business_name`: Name of the business.
- `business_type`: Type/category of the business.
- `registration_date`: Date of business registration.
- `business_model`: Business model, e.g., Online, Offline, Hybrid.
- `product_category`: Category of products sold.
- `average_ticket_size`: Average transaction amount.
- `gst_status`: GST registration status.
- `epfo_registered`: EPFO registration status.
- `registered_address`: Address of the business.
- `city`: City where the business is located.
- `state`: State where the business is located.
- `reported_revenue`: Reported revenue of the business.
- `employee_count`: Number of employees.
- `bank_account`: Bank account number.

---

### Functions

#### `generate_merchant_id`

```python:src/data_generator.py
def generate_merchant_id(existing_ids=None):
    """Generate a unique merchant ID"""
    while True:
        merchant_id = f"M{random.randint(1000000, 9999999)}"
        if existing_ids is None or merchant_id not in existing_ids:
            return merchant_id
```

**Description:**

Generates a unique merchant ID following the pattern `MXXXXXXX`, where `X` is a digit. It ensures uniqueness by checking against an existing set of IDs if provided.

**Parameters:**

- `existing_ids` (set, optional): A set of existing merchant IDs to ensure uniqueness.

**Returns:**

- `str`: A unique merchant ID.

---

#### `generate_business_name`

```python:src/data_generator.py
def generate_business_name() -> str:
    """Generate business name between 5 and 100 characters"""
    return fake.company()[:100]
```

**Description:**

Generates a realistic business name using the `Faker` library, ensuring the name is between 5 and 100 characters.

**Returns:**

- `str`: A generated business name.

---

#### `generate_random_date`

```python:src/data_generator.py
def generate_random_date(start_year: int = 2018, end_year: int = 2024) -> datetime:
    """Generate a random registration date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    time_between_dates = end - start
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start + timedelta(days=random_number_of_days)
```

**Description:**

Generates a random date between the specified `start_year` and `end_year`.

**Parameters:**

- `start_year` (int, optional): The starting year for date generation. Defaults to `2018`.
- `end_year` (int, optional): The ending year for date generation. Defaults to `2024`.

**Returns:**

- `datetime`: A randomly generated date.

---

#### `generate_merchant_base`

```python:src/data_generator.py
def generate_merchant_base(count: int) -> List[Dict]:
    """Generate base merchant profiles"""
    merchants = []
    existing_ids = set()
    
    for i in range(count):
        merchant_id = generate_merchant_id(existing_ids)
        existing_ids.add(merchant_id)
        merchant = {
            "merchant_id": merchant_id,
            "business_name": generate_business_name(),
            "business_type": random.choice(BUSINESS_TYPES),
            "registration_date": fake.date_time_between(start_date='-5y'),
            "business_model": random.choice(["Online", "Offline", "Hybrid"]),
            "product_category": random.choice(BUSINESS_TYPES),
            "average_ticket_size": round(random.uniform(100, 10000), 2),
            "gst_status": random.choice([True, False]),
            "epfo_registered": random.choice([True, False]),
            "registered_address": fake.address(),
            "city": fake.city(),
            "state": fake.state(),
            "reported_revenue": round(random.uniform(100000, 10000000), 2),
            "employee_count": random.randint(1, 1000),
            "bank_account": str(random.randint(10000000, 99999999))
        }
        merchants.append(merchant)
    return merchants
```

**Description:**

Generates a list of merchant profiles based on the specified count. It ensures each merchant has a unique ID and realistic attributes.

**Parameters:**

- `count` (int): Number of merchant profiles to generate.

**Returns:**

- `List[Dict]`: A list of merchant dictionaries.

---

#### `generate_transaction_id`

```python:src/data_generator.py
def generate_transaction_id():
    """Generate a unique transaction ID"""
    return f"TXN{uuid.uuid4().hex[:12].upper()}"
```

**Description:**

Generates a unique transaction ID following the pattern `TXNXXXXXXXXXXXX`, where `X` is a hexadecimal digit.

**Returns:**

- `str`: A unique transaction ID.

---

#### `generate_business_hour_timestamp`

```python:src/data_generator.py
def generate_business_hour_timestamp() -> datetime:
    """Generate timestamp within business hours"""
    current_time = datetime.now()
    days_ago = random.randint(0, 30)
    business_hour = random.randint(9, 17)
    past_date = current_time - timedelta(days=days_ago)
    return past_date.replace(
        hour=business_hour,
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=0
    )
```

**Description:**

Generates a timestamp within typical business hours (9 AM to 5 PM) for a random date within the last 30 days.

**Returns:**

- `datetime`: A timestamp within business hours.

---

#### `generate_normal_transactions`

```python:src/data_generator.py
def generate_normal_transactions(
    merchants: List[Dict], 
    days: int = 30, 
    daily_volume: Tuple[int, int] = (10, 50),
    amount_range: Tuple[float, float] = (100, 10000)
) -> List[Dict]:
    """Generate normal transaction patterns between merchants"""
    all_transactions = []
    for _ in range(days):
        # Select merchants for this day's transactions
        daily_merchants = random.sample(merchants, random.randint(5, len(merchants)))
        
        for _ in range(random.randint(*daily_volume)):
            # Select sender and receiver merchants
            sender = random.choice(daily_merchants)
            receiver = random.choice([m for m in daily_merchants if m != sender])
            
            txn = {
                "transaction_id": generate_transaction_id(),
                "merchant_id": sender["merchant_id"],
                "receiver_merchant_id": receiver["merchant_id"],
                "timestamp": generate_business_hour_timestamp(),
                "amount": round(random.uniform(*amount_range), 2),
                "payment_method": random.choice(PAYMENT_METHODS),
                "status": random.choice(TRANSACTION_STATUSES),
                "product_category": sender["product_category"],
                "platform": random.choice(PLATFORMS),
                "customer_location": sender["city"],
                "customer_id": fake.uuid4(),
                "device_id": fake.uuid4(),
                
                # Risk flags
                "velocity_flag": False,
                "amount_flag": False,
                "time_flag": False,
                "device_flag": False
            }
            all_transactions.append(txn)
    
    transaction_ids = set()
    for txn in all_transactions:
        while True:
            txn_id = generate_transaction_id()
            if txn_id not in transaction_ids:
                transaction_ids.add(txn_id)
                txn["transaction_id"] = txn_id
                break
    
    return all_transactions
```

**Description:**

Generates a list of normal (non-fraudulent) transactions between merchants over a specified number of days. It ensures each transaction has a unique ID and realistic attributes.

**Parameters:**

- `merchants` (List[Dict]): List of merchant profiles.
- `days` (int, optional): Number of days to generate transactions for. Defaults to `30`.
- `daily_volume` (Tuple[int, int], optional): Range for the number of transactions per day. Defaults to `(10, 50)`.
- `amount_range` (Tuple[float, float], optional): Range for transaction amounts. Defaults to `(100, 10000)`.

**Returns:**

- `List[Dict]`: A list of transaction dictionaries.

---

#### `inject_fraud_pattern`

```python:src/data_generator.py
def inject_fraud_pattern(
    transactions: List[Dict],
    pattern_type: str,
    config: Dict
) -> List[Dict]:
    """Inject specific fraud patterns into transactions"""
    fraudulent_transactions = transactions.copy()
    
    if pattern_type == "late_night_trading":
        # Inject late-night transactions
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.1):
                txn["timestamp"] = txn["timestamp"].replace(
                    hour=random.randint(0, 5)
                )
                txn["time_flag"] = True
    
    elif pattern_type == "sudden_spike":
        # Create a sudden spike in transaction amounts
        spike_multiplier = config.get("multiplier", 5)
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.05):
                txn["amount"] *= spike_multiplier
                txn["amount_flag"] = True
    
    elif pattern_type == "customer_concentration":
        # Concentrate transactions from few customers
        concentrate_probability = config.get("probability", 0.2)
        few_customers = [fake.uuid4() for _ in range(3)]
        for txn in fraudulent_transactions:
            if random.random() < concentrate_probability:
                txn["customer_id"] = random.choice(few_customers)
                
    elif pattern_type == "velocity_abuse":
        # Multiple transactions in short time windows
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.15):
                txn["timestamp"] = txn["timestamp"] + timedelta(seconds=random.randint(30, 300))
                txn["velocity_flag"] = True
                
    elif pattern_type == "device_switching":
        # Rapid device switching for same customer
        device_pool = [fake.uuid4() for _ in range(3)]
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.1):
                txn["device_id"] = random.choice(device_pool)
                txn["device_flag"] = True
                
    elif pattern_type == "location_hopping":
        # Transactions from different locations in short time
        cities = [fake.city() for _ in range(5)]
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.1):
                txn["customer_location"] = random.choice(cities)
                
    elif pattern_type == "payment_method_cycling":
        # Cycling through different payment methods
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.15):
                txn["payment_method"] = random.choice(PAYMENT_METHODS)
                
    elif pattern_type == "round_amount":
        # Transactions with suspiciously round amounts
        for txn in fraudulent_transactions:
            if random.random() < config.get("probability", 0.1):
                txn["amount"] = float(round(txn["amount"], -2))  # Round to nearest 100
                txn["amount_flag"] = True

    return fraudulent_transactions
```

**Description:**

Injects specific fraud patterns into a list of transactions based on the `pattern_type` and configuration parameters provided.

**Parameters:**

- `transactions` (List[Dict]): List of transaction dictionaries.
- `pattern_type` (str): Type of fraud pattern to inject. Supported patterns include:
    - `late_night_trading`
    - `sudden_spike`
    - `customer_concentration`
    - `velocity_abuse`
    - `device_switching`
    - `location_hopping`
    - `payment_method_cycling`
    - `round_amount`
- `config` (Dict): Configuration parameters for the fraud pattern. Common keys:
    - `probability` (float): Probability of a transaction being affected by the fraud pattern.
    - Other keys specific to the pattern, e.g., `multiplier` for `sudden_spike`.

**Returns:**

- `List[Dict]`: A list of transactions with injected fraud patterns.

---

#### `validate_merchant_data`

```python:src/data_generator.py
def validate_merchant_data(merchant: Dict) -> Dict:
    try:
        MerchantBase(**merchant)
        return merchant
    except ValidationError as e:
        raise ValueError(f"Invalid merchant data: {str(e)}")
```

**Description:**

Validates a merchant dictionary against the `MerchantBase` schema. Raises an error if validation fails.

**Parameters:**

- `merchant` (Dict): Merchant data to validate.

**Returns:**

- `Dict`: Validated merchant data.

**Raises:**

- `ValueError`: If validation fails with details of the error.

---

#### `validate_transaction_data`

```python:src/data_generator.py
def validate_transaction_data(transaction: Dict) -> Dict:
    try:
        # Ensure status is one of the allowed values
        if transaction.get('status') == 'completed':
            transaction['status'] = 'success'
            
        # Validate against the schema
        TransactionBase(**transaction)
        return transaction
    except ValidationError as e:
        raise ValueError(f"Invalid transaction data: {str(e)}")
```

**Description:**

Validates a transaction dictionary against the `TransactionBase` schema. It also normalizes the `status` field if necessary.

**Parameters:**

- `transaction` (Dict): Transaction data to validate.

**Returns:**

- `Dict`: Validated transaction data.

**Raises:**

- `ValueError`: If validation fails with details of the error.

---

#### `generate_dataset`

```python:src/data_generator.py
def generate_dataset(merchant_count: int = 100, fraud_percentage: float = 0.1, fraud_patterns: List[str] = None):
    try:
        if fraud_patterns is None:
            fraud_patterns = [
                "late_night_trading", 
                "sudden_spike",
                "velocity_abuse",
                "device_switching",
                "location_hopping",
                "payment_method_cycling",
                "round_amount",
                "customer_concentration"
            ]
        if not 0 <= fraud_percentage <= 1:
            raise ValueError("fraud_percentage must be between 0 and 1")
        if merchant_count <= 0:
            raise ValueError("merchant_count must be positive")
        
        # Generate merchant base
        merchants = generate_merchant_base(merchant_count)
        
        # Generate normal transactions
        transactions = generate_normal_transactions(merchants)
        
        # Select merchants for fraud injection
        fraud_count = int(merchant_count * fraud_percentage)
        fraud_merchants = random.sample(merchants, fraud_count)
        
        # Inject fraud patterns
        for merchant in fraud_merchants:
            pattern = random.choice(fraud_patterns)
            fraud_config = {
                "probability": random.uniform(0.05, 0.2)
            }
            merchant_transactions = [
                txn for txn in transactions 
                if txn["merchant_id"] == merchant["merchant_id"]
            ]
            
            fraudulent_txns = inject_fraud_pattern(
                merchant_transactions, 
                pattern, 
                fraud_config
            )
            
            # Replace original transactions with fraudulent ones
            transactions = [
                txn for txn in transactions 
                if txn["merchant_id"] != merchant["merchant_id"]
            ] + fraudulent_txns
        
        return merchants, transactions
    except Exception as e:
        logger.error(f"Error generating dataset: {str(e)}")
        raise ValueError(f"Failed to generate dataset: {str(e)}")
```

**Description:**

Generates a complete dataset of merchants and transactions, with a specified percentage of merchants having fraudulent transactions injected using various fraud patterns.

**Parameters:**

- `merchant_count` (int, optional): Number of merchants to generate. Defaults to `100`.
- `fraud_percentage` (float, optional): Percentage of merchants to inject fraud patterns into (0 to 1). Defaults to `0.1` (10%).
- `fraud_patterns` (List[str], optional): List of fraud patterns to use. If `None`, all supported patterns are used.

**Returns:**

- `Tuple[List[Dict], List[Dict]]`: A tuple containing the list of merchants and the list of transactions.

**Raises:**

- `ValueError`: If input parameters are invalid or dataset generation fails.

---

## Example Usage

Here’s how you can utilize the `data_generator.py` module to generate a dataset of merchants and transactions:

```python:src/data_generator.py
if __name__ == "__main__":
    merchants, transactions = generate_dataset(
        merchant_count=1000, 
        fraud_percentage=0.2
    )
    
    print(f"Generated {len(merchants)} merchants")
    print(f"Generated {len(transactions)} transactions")
    print("\nSample Merchant:")
    print(merchants[0])
    print("\nSample Transaction:")
    print(transactions[0])
```

**Steps:**

1. **Generate Dataset:**
    - Generates `1000` merchants.
    - Injects fraud patterns into `20%` of these merchants.

2. **Output:**
    - Prints the total number of merchants and transactions generated.
    - Displays a sample merchant and a sample transaction for inspection.

**Running the Script:**

```bash
python src/data_generator.py
```

---

## Error Handling

The module incorporates robust error handling to ensure smooth dataset generation:

- **Validation Errors:**
    - Utilizes Pydantic's `ValidationError` to validate merchant and transaction data schemas.
    - Raises `ValueError` with detailed error messages if validation fails.

- **Dataset Generation Errors:**
    - Catches general exceptions during dataset generation.
    - Logs errors using Python's `logging` module.
    - Raises `ValueError` to notify of dataset generation failures.

**Example:**

```python:src/data_generator.py
try:
    merchants, transactions = generate_dataset(...)
except ValueError as e:
    print(f"An error occurred: {e}")
```

---

## Logging

The module uses Python's built-in `logging` library to log errors and important information.

```python:src/data_generator.py
import logging

logger = logging.getLogger(__name__)
```

**Configuration:**

You can configure the logging level and format as needed in your main application:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Customization

The module is highly customizable to fit various data generation needs:

- **Business Types, Payment Methods, Platforms:**
    - Modify the predefined lists (`BUSINESS_TYPES`, `PAYMENT_METHODS`, `PLATFORMS`) to include or exclude specific categories.

- **Fraud Patterns:**
    - Extend or modify the `inject_fraud_pattern` function to introduce new fraud patterns.
    - Adjust the `fraud_patterns` list in the `generate_dataset` function.

- **Data Ranges:**
    - Change parameters like `amount_range`, `daily_volume`, and `merchant_count` to generate datasets of different scales and scopes.

---

## License

This module is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements or bug fixes.

---

## Acknowledgements

- [Faker](https://faker.readthedocs.io/en/master/) for realistic fake data generation.
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation and settings management.

---
