from datetime import date, datetime, time
from pawpal_system import Appointment, Owner, Pet, Scheduler, Task

today = date.today()

# ---------------------------------------------------------------------------
# Test: Task class
# ---------------------------------------------------------------------------
print("=== Task ===")

morning_walk = Task(
    task_title="Morning Walk",
    description="30-minute walk around the park",
    date=today,
    scheduled_time=time(7, 0),
    priority="high",
    frequency="daily",
    duration_minutes=30,
)

feeding = Task(
    task_title="Feeding",
    description="Serve 1 cup of dry kibble",
    date=today,
    scheduled_time=time(8, 0),
    priority="high",
    frequency="daily",
    duration_minutes=10,
)

grooming = Task(
    task_title="Grooming",
    description="Brush coat and clean ears",
    date=today,
    scheduled_time=time(17, 0),
    priority="medium",
    frequency="weekly",
    duration_minutes=20,
)

print(morning_walk.remind_task())
print(feeding.remind_task())
print(grooming.remind_task())

# ---------------------------------------------------------------------------
# Test: Appointment class
# ---------------------------------------------------------------------------
print("\n=== Appointment ===")

vet_visit = Appointment(
    appointment_title="Annual Checkup",
    appointment_date_time=datetime(today.year, today.month, today.day, 10, 30),
    place="PawPal Veterinary Clinic",
    appointment_person="Dr. Rivera",
    notes="Bring vaccination records",
)

print(vet_visit.remind_appointment())
print(vet_visit.get_appointment())

# ---------------------------------------------------------------------------
# Test: Pet class
# ---------------------------------------------------------------------------
print("\n=== Pets ===")

mochi = Pet(
    name="Mochi",
    species="dog",
    breed="Shiba Inu",
    dob=date(2020, 3, 15),
    physical_characteristics="orange coat, curly tail",
    allergies=["chicken"],
)

luna = Pet(
    name="Luna",
    species="cat",
    breed="Domestic Shorthair",
    dob=date(2021, 7, 4),
    physical_characteristics="grey tabby, green eyes",
    allergies=[],
)

# Assign tasks to Mochi
mochi.add_task(morning_walk)
mochi.add_task(feeding)
mochi.add_task(grooming)

# Assign appointment to Mochi
mochi.add_appointment(vet_visit)

print(mochi.create_report())
print()
print(luna.create_report())

# ---------------------------------------------------------------------------
# Test: Owner class
# ---------------------------------------------------------------------------
print("\n=== Owner ===")

jordan = Owner(name="Jordan", email="jordan@email.com", phone_number="555-1234")
jordan.add_pet(mochi)
jordan.add_pet(luna)

print(jordan.get_owner_info())

all_tasks = jordan.get_all_tasks()
print(f"Total tasks across all pets: {len(all_tasks)}")

# ---------------------------------------------------------------------------
# Test: Scheduler class + Today's Schedule
# ---------------------------------------------------------------------------
print("\n=== Scheduler ===")

scheduler = Scheduler()
scheduler.add_owner(jordan)
scheduler.add_pet(mochi)
scheduler.add_pet(luna)

for task in mochi.tasks:
    scheduler.add_task(task)

scheduler.add_appointment(vet_visit)

schedule = scheduler.build_daily_schedule(pet_name="Mochi", target_date=today)

print("\n" + "=" * 45)
print("         TODAY'S SCHEDULE")
print("=" * 45)
print(scheduler.explain_schedule(schedule))
print("=" * 45)

# mark morning walk done and re-print
morning_walk.mark_complete()
print("\n[After completing Morning Walk]")
print(morning_walk.remind_task())

upcoming = Appointment.get_upcoming(mochi.appointments, from_date=datetime.now())
print(f"\nUpcoming appointments for {mochi.name}: {len(upcoming)}")
for appt in upcoming:
    print(f"  - {appt.remind_appointment()}")
