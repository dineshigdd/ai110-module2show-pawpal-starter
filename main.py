from datetime import date, datetime
from pawpal_system import Appointment, Owner, Pet, Scheduler, Task

today = date.today()

# ---------------------------------------------------------------------------
# Test: Task class
# ---------------------------------------------------------------------------
print("=== Task ===")

morning_walk = Task(
    task_title="Morning Walk",
    description="30-minute walk around the park",
    scheduled_datetime=datetime(today.year, today.month, today.day, 7, 0),
    priority="high",
    frequency="daily",
    duration_minutes=30,
)

feeding = Task(
    task_title="Feeding",
    description="Serve 1 cup of dry kibble",
    scheduled_datetime=datetime(today.year, today.month, today.day, 8, 0),
    priority="high",
    frequency="daily",
    duration_minutes=10,
)

grooming = Task(
    task_title="Grooming",
    description="Brush coat and clean ears",
    scheduled_datetime=datetime(today.year, today.month, today.day, 17, 0),
    priority="medium",
    frequency="weekly",
    duration_minutes=20,
)

# Extra tasks added OUT OF ORDER (late afternoon and midday)
playtime = Task(
    task_title="Playtime",
    description="Fetch and tug-of-war in the backyard",
    scheduled_datetime=datetime(today.year, today.month, today.day, 15, 0),
    priority="low",
    frequency="daily",
    duration_minutes=25,
)

medication = Task(
    task_title="Medication",
    description="Administer heart medication with food",
    scheduled_datetime=datetime(today.year, today.month, today.day, 12, 0),
    priority="high",
    frequency="daily",
    duration_minutes=5,
)

print(morning_walk.remind_task())
print(feeding.remind_task())
print(grooming.remind_task())
print(playtime.remind_task())
print(medication.remind_task())

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

# Assign tasks to Mochi OUT OF ORDER: grooming, playtime, morning_walk, medication, feeding
mochi.add_task(grooming)
mochi.add_task(playtime)
mochi.add_task(morning_walk)
mochi.add_task(medication)
mochi.add_task(feeding)

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
# Test: Scheduler — sorting and filtering
# ---------------------------------------------------------------------------
print("\n=== Scheduler ===")

scheduler = Scheduler()
scheduler.add_owner(jordan)
scheduler.add_pet(mochi)
scheduler.add_pet(luna)

for task in mochi.tasks:
    scheduler.add_task(task)

scheduler.add_appointment(vet_visit)

# --- sort_by_time: tasks added out of order, sorted by HH:MM ---
print("\n--- sort_by_time() ---")
sorted_tasks = scheduler.sort_by_time(scheduler.tasks)
for t in sorted_tasks:
    print(f"  {t.scheduled_datetime.strftime('%H:%M')} [{t.priority.upper()}] {t.task_title}")

# --- get_task_by_date: filter to today only ---
print("\n--- get_task_by_date() ---")
todays_tasks = Task.get_task_by_date(scheduler.tasks, today)
print(f"  Tasks for {today}: {len(todays_tasks)}")
for t in todays_tasks:
    print(f"    - {t.task_title}")

# --- get_task_by_pet: filter to Mochi only ---
print("\n--- get_task_by_pet() ---")
mochi_tasks = Task.get_task_by_pet(scheduler.tasks, "Mochi")
print(f"  Tasks for Mochi: {len(mochi_tasks)}")
for t in mochi_tasks:
    print(f"    - {t.task_title}")

# --- group_similar_tasks ---
print("\n--- group_similar_tasks() ---")
groups = Task.group_similar_tasks(scheduler.tasks)
for group_name, group_tasks in groups.items():
    print(f"  '{group_name}': {len(group_tasks)} task(s)")

# --- build_daily_schedule: priority then time ---
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
