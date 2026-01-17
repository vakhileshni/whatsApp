# Fixed: SQLAlchemy Reserved Attribute Error

## Problem
`Attribute name 'metadata' is reserved when using the Declarative API.`

SQLAlchemy uses `metadata` as a reserved attribute name for table metadata. We had a column named `metadata` in the `PaymentDB` model, which caused a conflict.

## Solution
Renamed the Python attribute from `metadata` to `payment_metadata`, but kept the database column name as `metadata` using SQLAlchemy's `name` parameter:

```python
payment_metadata = Column('metadata', Text, nullable=True)
```

This way:
- The database column is still named `metadata` (no migration needed)
- The Python attribute is `payment_metadata` (avoids conflict)
- The API response still returns `metadata` (via `to_dict()` method)

## Status
✅ Fixed - All models now load successfully!
