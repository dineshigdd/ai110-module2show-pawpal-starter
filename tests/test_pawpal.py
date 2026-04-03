from datetime import date, time
from pawpal_system import Pet, Task


def make_task() -> Task:
    """Return a sample task for reuse across tests."""
    return Task(
        task_title="Morning Walk",
        description="Walk around the park",
        date=date.today(),
        scheduled_time=time(7, 0),
        priority="high",
    )


def test_mark_complete_changes_status():
    """mark_complete() should flip completed from False to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(
        name="Mochi",
        breed="Shiba Inu",
        dob=date(2020, 3, 15),
        physical_characteristics="orange coat",
    )
    assert len(pet.tasks) == 0
    pet.add_task(make_task())
    assert len(pet.tasks) == 1
