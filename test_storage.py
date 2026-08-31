from backend.storage import (
    save_health_record,
    get_latest_health,
    get_last_7_records,
    get_all_records,
    get_latest_risk
)

senior = "medcare_test2"

print("Testing health record save...")

result = save_health_record(
    senior=senior,
    bp=120,
    sugar=95,
    hr=72,
    risk="Low"
)

print("Save result:", result)


print("\nTesting latest health...")

latest = get_latest_health(senior)

print("Latest health:", latest)


print("\nTesting latest risk...")

risk = get_latest_risk(senior)

print("Latest risk:", risk)


print("\nTesting last 7 records...")

records = get_last_7_records(senior)

print(records)


print("\nTesting full history...")

history = get_all_records(senior)

print(history)