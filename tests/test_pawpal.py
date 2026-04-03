from datetime import date, datetime
from pawpal_system import Pet, Task, Scheduler


TODAY = date.today()


def make_task(title="Morning Walk", hour=7, priority="high", frequency="once", pet_name="Mochi") -> Task:
    """Return a sample Task for reuse across tests."""
    return Task(
        task_title=title,
        description="Test task",
        scheduled_datetime=datetime(TODAY.year, TODAY.month, TODAY.day, hour, 0),
        priority=priority,
        frequency=frequency,
        pet_name=pet_name,
    )


# ---------------------------------------------------------------------------
# Existing tests (updated for new Task signature)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Scheduler.sort_by_time()
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order should come back sorted earliest to latest."""
    scheduler = Scheduler()
    t1 = make_task("Feeding",  hour=8)
    t2 = make_task("Grooming", hour=17)
    t3 = make_task("Walk",     hour=7)

    # Add deliberately out of order
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    scheduler.add_task(t3)

    sorted_tasks = scheduler.sort_by_time(scheduler.tasks)
    times = [t.scheduled_datetime.hour for t in sorted_tasks]
    assert times == [7, 8, 17]


def test_sort_by_time_single_task():
    """A single-task list should be returned unchanged."""
    scheduler = Scheduler()
    t = make_task(hour=10)
    result = scheduler.sort_by_time([t])
    assert result == [t]


def test_sort_by_time_empty_list():
    """An empty list should return an empty list without error."""
    scheduler = Scheduler()
    assert scheduler.sort_by_time([]) == []


def test_sort_by_time_preserves_all_tasks():
    """sort_by_time should not drop or duplicate any tasks."""
    scheduler = Scheduler()
    tasks = [make_task(f"Task{i}", hour=h) for i, h in enumerate([15, 9, 12, 6])]
    for t in tasks:
        scheduler.add_task(t)
    result = scheduler.sort_by_time(scheduler.tasks)
    assert len(result) == 4


# ---------------------------------------------------------------------------
# Scheduler.build_daily_schedule()
# ---------------------------------------------------------------------------

def test_build_daily_schedule_returns_only_target_date():
    """Tasks on other dates should be excluded from the schedule."""
    scheduler = Scheduler()
    today_task = make_task("Today Walk", hour=7)
    other_day = Task(
        task_title="Other Day Task",
        description="",
        scheduled_datetime=datetime(TODAY.year, TODAY.month, TODAY.day + 1, 9, 0),
        pet_name="Mochi",
    )
    scheduler.add_task(today_task)
    scheduler.add_task(other_day)

    schedule = scheduler.build_daily_schedule(pet_name="Mochi", target_date=TODAY)
    assert len(schedule) == 1
    assert schedule[0].task_title == "Today Walk"


def test_build_daily_schedule_returns_only_target_pet():
    """Tasks belonging to a different pet should not appear in the schedule."""
    scheduler = Scheduler()
    mochi_task = make_task("Mochi Walk", hour=7, pet_name="Mochi")
    luna_task  = make_task("Luna Nap",   hour=9, pet_name="Luna")
    scheduler.add_task(mochi_task)
    scheduler.add_task(luna_task)

    schedule = scheduler.build_daily_schedule(pet_name="Mochi", target_date=TODAY)
    assert all(t.pet_name == "Mochi" for t in schedule)
    assert len(schedule) == 1


def test_build_daily_schedule_priority_order():
    """High-priority tasks should appear before medium and low ones."""
    scheduler = Scheduler()
    low    = make_task("Playtime",  hour=7,  priority="low")
    medium = make_task("Grooming",  hour=8,  priority="medium")
    high   = make_task("Medication", hour=9, priority="high")

    # Add in reverse priority order
    scheduler.add_task(low)
    scheduler.add_task(medium)
    scheduler.add_task(high)

    schedule = scheduler.build_daily_schedule(pet_name="Mochi", target_date=TODAY)
    priorities = [t.priority for t in schedule]
    assert priorities == ["high", "medium", "low"]


def test_build_daily_schedule_same_priority_sorted_by_time():
    """Tasks with equal priority should be sorted by scheduled_datetime."""
    scheduler = Scheduler()
    t1 = make_task("Afternoon Feed", hour=14, priority="high")
    t2 = make_task("Morning Feed",   hour=8,  priority="high")
    t3 = make_task("Midday Feed",    hour=12, priority="high")

    scheduler.add_task(t1)
    scheduler.add_task(t2)
    scheduler.add_task(t3)

    schedule = scheduler.build_daily_schedule(pet_name="Mochi", target_date=TODAY)
    hours = [t.scheduled_datetime.hour for t in schedule]
    assert hours == [8, 12, 14]


def test_build_daily_schedule_empty_when_no_tasks():
    """Scheduler with no tasks should return an empty schedule."""
    scheduler = Scheduler()
    schedule = scheduler.build_daily_schedule(pet_name="Mochi", target_date=TODAY)
    assert schedule == []


# ---------------------------------------------------------------------------
# Scheduler.mark_task_complete()
# ---------------------------------------------------------------------------

def test_mark_task_complete_marks_original_done():
    """The original task should be marked completed after the call."""
    scheduler = Scheduler()
    task = make_task(frequency="once")
    scheduler.add_task(task)
    scheduler.mark_task_complete(task)
    assert task.completed is True


def test_mark_task_complete_once_returns_none():
    """A 'once' task should return None — no new task created."""
    scheduler = Scheduler()
    task = make_task(frequency="once")
    scheduler.add_task(task)
    result = scheduler.mark_task_complete(task)
    assert result is None


def test_mark_task_complete_once_does_not_add_task():
    """Completing a 'once' task should not grow the scheduler's task list."""
    scheduler = Scheduler()
    task = make_task(frequency="once")
    scheduler.add_task(task)
    scheduler.mark_task_complete(task)
    assert len(scheduler.tasks) == 1


def test_mark_task_complete_daily_creates_next_task():
    """Completing a 'daily' task should add one new task to the scheduler."""
    scheduler = Scheduler()
    task = make_task(frequency="daily")
    scheduler.add_task(task)
    scheduler.mark_task_complete(task)
    assert len(scheduler.tasks) == 2


def test_mark_task_complete_daily_advances_one_day():
    """The next daily task should be scheduled exactly one day later."""
    from datetime import timedelta
    scheduler = Scheduler()
    task = make_task(frequency="daily", hour=7)
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task.scheduled_datetime == task.scheduled_datetime + timedelta(days=1)


def test_mark_task_complete_weekly_advances_seven_days():
    """The next weekly task should be scheduled exactly seven days later."""
    from datetime import timedelta
    scheduler = Scheduler()
    task = make_task(frequency="weekly", hour=10)
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task.scheduled_datetime == task.scheduled_datetime + timedelta(weeks=1)


def test_mark_task_complete_new_task_not_completed():
    """The auto-created recurring task should start as not completed."""
    scheduler = Scheduler()
    task = make_task(frequency="daily")
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task.completed is False


def test_mark_task_complete_new_task_copies_fields():
    """The new task should inherit title, priority, duration, and frequency."""
    scheduler = Scheduler()
    task = make_task(title="Medication", hour=12, priority="high", frequency="daily")
    task.duration_minutes = 15
    scheduler.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task.task_title == "Medication"
    assert next_task.priority == "high"
    assert next_task.duration_minutes == 15
    assert next_task.frequency == "daily"


def test_mark_task_complete_daily_added_to_pet_tasks():
    """The new recurring task should also be appended to the pet's task list."""
    scheduler = Scheduler()
    pet = Pet(name="Mochi", species="dog")
    task = make_task(frequency="daily", pet_name="Mochi")
    pet.add_task(task)
    scheduler.add_pet(pet)
    scheduler.add_task(task)
    scheduler.mark_task_complete(task)
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Scheduler.detect_conflicts()
# ---------------------------------------------------------------------------

def test_detect_conflicts_no_tasks_returns_empty():
    """No tasks means no conflicts."""
    scheduler = Scheduler()
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_single_task_returns_empty():
    """A single task can never conflict with itself."""
    scheduler = Scheduler()
    scheduler.add_task(make_task(hour=8))
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_non_overlapping_returns_empty():
    """Tasks that end before the next one starts should not conflict."""
    scheduler = Scheduler()
    # 07:00-07:30, then 08:00-08:10 — gap between them
    t1 = make_task("Walk",    hour=7, pet_name="Mochi")   # 30 min default
    t2 = make_task("Feeding", hour=8, pet_name="Mochi")
    t2.duration_minutes = 10
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_exact_same_time_same_pet():
    """Two tasks at the exact same time for the same pet should conflict."""
    scheduler = Scheduler()
    t1 = make_task("Walk",    hour=8, pet_name="Mochi")
    t2 = make_task("Feeding", hour=8, pet_name="Mochi")
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "same pet" in conflicts[0]


def test_detect_conflicts_exact_same_time_different_pets():
    """Two tasks at the exact same time for different pets should conflict."""
    scheduler = Scheduler()
    t1 = make_task("Mochi Walk", hour=9, pet_name="Mochi")
    t2 = make_task("Luna Nap",   hour=9, pet_name="Luna")
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "different pets" in conflicts[0]


def test_detect_conflicts_partial_overlap():
    """A task starting mid-way through another should be detected as a conflict."""
    scheduler = Scheduler()
    # 08:00-08:30, second starts at 08:15 — overlaps by 15 min
    t1 = make_task("Grooming", hour=8, pet_name="Mochi")
    t1.duration_minutes = 30
    t2 = Task(
        task_title="Teeth Brushing",
        description="",
        scheduled_datetime=datetime(TODAY.year, TODAY.month, TODAY.day, 8, 15),
        duration_minutes=20,
        pet_name="Mochi",
    )
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert len(scheduler.detect_conflicts()) == 1


def test_detect_conflicts_completed_tasks_ignored():
    """Completed tasks should not be included in conflict detection."""
    scheduler = Scheduler()
    t1 = make_task("Walk",    hour=8, pet_name="Mochi")
    t2 = make_task("Feeding", hour=8, pet_name="Mochi")
    t1.mark_complete()
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_multiple_conflicts_detected():
    """All overlapping pairs should each produce a separate warning."""
    scheduler = Scheduler()
    # All three start at 09:00 — three pairs: (1,2), (1,3), (2,3)
    t1 = make_task("Task A", hour=9, pet_name="Mochi")
    t2 = make_task("Task B", hour=9, pet_name="Mochi")
    t3 = make_task("Task C", hour=9, pet_name="Luna")
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    scheduler.add_task(t3)
    assert len(scheduler.detect_conflicts()) == 3


def test_detect_conflicts_warning_contains_task_titles():
    """Each warning message should include both conflicting task titles."""
    scheduler = Scheduler()
    t1 = make_task("Morning Walk", hour=7, pet_name="Mochi")
    t2 = make_task("Morning Walk", hour=7, pet_name="Mochi")
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    warning = scheduler.detect_conflicts()[0]
    assert "Morning Walk" in warning


# ---------------------------------------------------------------------------
# Edge cases — sort_by_time
# ---------------------------------------------------------------------------

def test_sort_by_time_tasks_at_same_time_no_crash():
    """Two tasks at the exact same hour should not raise an error."""
    scheduler = Scheduler()
    t1 = make_task("Walk",    hour=8)
    t2 = make_task("Feeding", hour=8)
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    result = scheduler.sort_by_time(scheduler.tasks)
    assert len(result) == 2


def test_sort_by_time_does_not_mutate_original_list():
    """sort_by_time should return a new list, not modify the input in place."""
    scheduler = Scheduler()
    tasks = [make_task(f"T{i}", hour=h) for i, h in enumerate([14, 7, 11])]
    original_order = [t.task_title for t in tasks]
    scheduler.sort_by_time(tasks)
    assert [t.task_title for t in tasks] == original_order


# ---------------------------------------------------------------------------
# Edge cases — build_daily_schedule
# ---------------------------------------------------------------------------

def test_build_daily_schedule_unknown_pet_returns_empty():
    """Requesting a schedule for a pet that has no tasks should return empty."""
    scheduler = Scheduler()
    scheduler.add_task(make_task(pet_name="Mochi"))
    schedule = scheduler.build_daily_schedule(pet_name="Ghost", target_date=TODAY)
    assert schedule == []


def test_build_daily_schedule_includes_completed_tasks():
    """build_daily_schedule does not filter out completed tasks — all are returned."""
    scheduler = Scheduler()
    t = make_task(hour=7)
    t.mark_complete()
    scheduler.add_task(t)
    schedule = scheduler.build_daily_schedule(pet_name="Mochi", target_date=TODAY)
    assert len(schedule) == 1
    assert schedule[0].completed is True


# ---------------------------------------------------------------------------
# Edge cases — mark_task_complete
# ---------------------------------------------------------------------------

def test_mark_task_complete_daily_chained_twice():
    """Completing the auto-created daily task should produce a third occurrence."""
    from datetime import timedelta
    scheduler = Scheduler()
    task = make_task(frequency="daily", hour=7)
    scheduler.add_task(task)
    next1 = scheduler.mark_task_complete(task)
    next2 = scheduler.mark_task_complete(next1)
    assert len(scheduler.tasks) == 3
    assert next2.scheduled_datetime == task.scheduled_datetime + timedelta(days=2)


def test_mark_task_complete_pet_not_in_scheduler_no_crash():
    """If the pet is not registered in the scheduler, no exception should be raised."""
    scheduler = Scheduler()
    task = make_task(frequency="daily", pet_name="UnknownPet")
    scheduler.add_task(task)
    try:
        scheduler.mark_task_complete(task)
    except Exception as e:
        assert False, f"mark_task_complete raised unexpectedly: {e}"


# ---------------------------------------------------------------------------
# Edge cases — detect_conflicts
# ---------------------------------------------------------------------------

def test_detect_conflicts_back_to_back_tasks_no_conflict():
    """Tasks where one ends exactly when the next begins should NOT conflict."""
    scheduler = Scheduler()
    # 08:00-08:30, then 08:30-09:00 — adjacent, not overlapping
    t1 = make_task("Walk",    hour=8, pet_name="Mochi")
    t1.duration_minutes = 30
    t2 = Task(
        task_title="Feeding",
        description="",
        scheduled_datetime=datetime(TODAY.year, TODAY.month, TODAY.day, 8, 30),
        duration_minutes=30,
        pet_name="Mochi",
    )
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_all_completed_returns_empty():
    """All completed tasks should produce no conflicts."""
    scheduler = Scheduler()
    t1 = make_task("Walk",    hour=8, pet_name="Mochi")
    t2 = make_task("Feeding", hour=8, pet_name="Mochi")
    t1.mark_complete()
    t2.mark_complete()
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    assert scheduler.detect_conflicts() == []
