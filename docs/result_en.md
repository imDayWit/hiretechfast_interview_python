# Project Updates

## Key Enhancements

1. **Added Celery and Celery Beat**:
   - Integrated Celery with Celery Beat to schedule a periodic task for inserting logs into ClickHouse.

2. **Implemented Celery Task for Batch Insertion**:
   - The task performs batch insertions of up to 100,000 records at a time.
   - Runs every minute by default. It is recommended to adjust the timing based on RPS for further optimization.

3. **Added Buffer Table in `init.sql`**:
   - Log insertions now go into a buffer table in ClickHouse for improved performance and optimization.

---

## Fixes and Testing

1. **Test Fixes**:
   - Adjusted tests to account for the creation of a `UserEventLog` object when a user is created.
   - Added a Use Case for user creation in the admin interface, as the method for creating users was not specified in the requirements.

2. **New Tests**:
   - Test to verify the creation of a `UserEventLog` object when a user is created.
   - Test to ensure data is inserted into the ClickHouse buffer table when the Celery task is triggered.