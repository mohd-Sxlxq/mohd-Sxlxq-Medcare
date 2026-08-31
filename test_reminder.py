from backend.reminder import (
    save_reminder,
    get_reminders_for_senior,
    mark_taken,
    mark_notified
)


senior = "medcare_test2"


print("Testing reminder save...")

result = save_reminder(
    medicine="Paracetamol",
    start_time="09:00:00",
    end_time="09:30:00",
    senior=senior
)

print("Save result:", result)


print("\nTesting reminder retrieval...")

reminders = get_reminders_for_senior(senior)

print(reminders)


if not reminders.empty:

    reminder_id = reminders.iloc[0]["id"]

    print("\nTesting mark as taken...")

    taken_result = mark_taken(reminder_id)

    print("Taken result:", taken_result)


    print("\nTesting mark as notified...")

    notified_result = mark_notified(reminder_id)

    print("Notified result:", notified_result)


print("\nTesting final reminder state...")

final_reminders = get_reminders_for_senior(senior)

print(final_reminders)