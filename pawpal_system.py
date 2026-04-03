from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List

_PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


# ---------------------------------------------------------------------------
# Appointment
# ---------------------------------------------------------------------------

@dataclass
class Appointment:
    appointment_title: str
    appointment_date_time: datetime
    place: str
    appointment_person: str          # e.g. vet name, groomer name
    pet_name: str = ""
    notes: str = ""
    completed: bool = False

    def get_appointment(self) -> dict:
        """Return all appointment details as a dictionary."""
        return {
            "title": self.appointment_title,
            "datetime": self.appointment_date_time,
            "place": self.place,
            "person": self.appointment_person,
            "pet": self.pet_name,
            "notes": self.notes,
            "completed": self.completed,
        }

    def update_appointment(self, **kwargs) -> None:
        """Update any appointment field by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self) -> None:
        """Mark this appointment as completed."""
        self.completed = True

    def remind_appointment(self) -> str:
        """Return a formatted reminder string showing status, time, person, and place."""
        status = "DONE" if self.completed else "UPCOMING"
        return (
            f"[{status}] '{self.appointment_title}' for {self.pet_name} "
            f"on {self.appointment_date_time.strftime('%Y-%m-%d at %H:%M')} "
            f"with {self.appointment_person} @ {self.place}"
        )

    @staticmethod
    def get_appointment_dates(appointments: List["Appointment"]) -> List[datetime]:
        """Return a list of datetimes for every appointment in the given list."""
        return [a.appointment_date_time for a in appointments]

    @staticmethod
    def get_by_pet(appointments: List["Appointment"], pet_name: str) -> List["Appointment"]:
        """Filter appointments to only those belonging to the named pet."""
        return [a for a in appointments if a.pet_name == pet_name]

    @staticmethod
    def get_upcoming(appointments: List["Appointment"], from_date: datetime) -> List["Appointment"]:
        """Return incomplete appointments on or after from_date, sorted by datetime."""
        upcoming = [
            a for a in appointments
            if not a.completed and a.appointment_date_time >= from_date
        ]
        return sorted(upcoming, key=lambda a: a.appointment_date_time)


# ---------------------------------------------------------------------------
# Task — a single care activity
# ---------------------------------------------------------------------------

@dataclass
class Task:
    task_title: str
    description: str
    scheduled_datetime: datetime
    pet_name: str = ""
    duration_minutes: int = 30
    priority: str = "medium"       # "low" | "medium" | "high"
    frequency: str = "once"        # "once" | "daily" | "weekly"
    completed: bool = False

    def get_task(self) -> dict:
        """Return all task fields as a dictionary."""
        return {
            "title": self.task_title,
            "description": self.description,
            "datetime": self.scheduled_datetime,
            "pet": self.pet_name,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "completed": self.completed,
        }

    def update_task(self, **kwargs) -> None:
        """Update any task field by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def remind_task(self) -> str:
        """Return a formatted reminder string showing status, time, and priority."""
        status = "DONE" if self.completed else "PENDING"
        return (
            f"[{status}] Reminder: '{self.task_title}' for {self.pet_name} "
            f"on {self.scheduled_datetime.strftime('%Y-%m-%d at %H:%M')} "
            f"({self.duration_minutes} min, {self.priority} priority)"
        )

    @staticmethod
    def get_task_by_date(tasks: List["Task"], target_date: date) -> List["Task"]:
        """Return only the tasks whose date matches target_date."""
        return [t for t in tasks if t.scheduled_datetime.date() == target_date]

    @staticmethod
    def get_task_by_pet(tasks: List["Task"], pet_name: str) -> List["Task"]:
        """Return only the tasks that belong to the named pet."""
        return [t for t in tasks if t.pet_name == pet_name]

    @staticmethod
    def group_similar_tasks(tasks: List["Task"]) -> dict:
        """Group tasks by normalised title, e.g. all 'walk' tasks together."""
        groups: dict = {}
        for task in tasks:
            key = task.task_title.strip().lower()
            groups.setdefault(key, []).append(task)
        return groups


# ---------------------------------------------------------------------------
# Pet — stores pet details and owns a list of tasks
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    dob: date = field(default_factory=date.today)
    physical_characteristics: str = ""
    allergies: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    appointments: List[Appointment] = field(default_factory=list)

    def get_pet_info(self) -> dict:
        """Return core pet details and task/appointment counts as a dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "dob": self.dob,
            "physical_characteristics": self.physical_characteristics,
            "allergies": self.allergies,
            "task_count": len(self.tasks),
            "appointment_count": len(self.appointments),
        }

    def update_pet_info(self, **kwargs) -> None:
        """Update any pet field by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet and set its pet_name back-reference."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> None:
        """Remove all tasks whose title matches task_title."""
        self.tasks = [t for t in self.tasks if t.task_title != task_title]

    def add_appointment(self, appointment: Appointment) -> None:
        """Append an appointment to this pet and set its pet_name back-reference."""
        appointment.pet_name = self.name
        self.appointments.append(appointment)

    def remove_appointment(self, appointment_title: str) -> None:
        """Remove all appointments whose title matches appointment_title."""
        self.appointments = [
            a for a in self.appointments if a.appointment_title != appointment_title
        ]

    def create_report(self) -> str:
        """Return a formatted multi-line summary of the pet's details and task counts."""
        pending = [t for t in self.tasks if not t.completed]
        done = [t for t in self.tasks if t.completed]
        lines = [
            f"=== Pet Report: {self.name} ===",
            f"  Species    : {self.species}",
            f"  Breed      : {self.breed}",
            f"  DOB        : {self.dob}",
            f"  Physical   : {self.physical_characteristics}",
            f"  Allergies  : {', '.join(self.allergies) if self.allergies else 'None'}",
            f"  Tasks      : {len(self.tasks)} total | {len(pending)} pending | {len(done)} done",
            f"  Appointments: {len(self.appointments)}",
        ]
        return "\n".join(lines)

    @staticmethod
    def filter_by(pets: List["Pet"], criteria: dict) -> List["Pet"]:
        """Return pets where every key in criteria matches the pet's attribute."""
        result = pets
        for key, value in criteria.items():
            result = [p for p in result if getattr(p, key, None) == value]
        return result


# ---------------------------------------------------------------------------
# Owner — manages multiple pets and exposes all their tasks
# ---------------------------------------------------------------------------

@dataclass
class Owner:
    name: str
    email: str=""
    phone_number: str=""
    pets: List[Pet] = field(default_factory=list)

    def get_owner_info(self) -> dict:
        """Return owner contact details and a list of pet names as a dictionary."""
        return {
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "pets": [p.name for p in self.pets],
        }

    def update_owner_info(self, **kwargs) -> None:
        """Update any owner field by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name from this owner's pet list."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self) -> List[Task]:
        """Flatten tasks from every owned pet into a single list."""
        return [task for pet in self.pets for task in pet.tasks]


# ---------------------------------------------------------------------------
# Scheduler — the "brain" that organises and manages tasks across all pets
# ---------------------------------------------------------------------------

class Scheduler:
    """Central store and manager for owners, pets, tasks, and appointments."""

    def __init__(self) -> None:
        """Initialize the Scheduler with empty lists for owners, pets, tasks, and appointments."""
        self.owners: List[Owner] = []
        self.pets: List[Pet] = []
        self.tasks: List[Task] = []
        self.appointments: List[Appointment] = []

    # --- Owner management ---
    def add_owner(self, owner: Owner) -> None:
        """Register an owner with the scheduler."""
        self.owners.append(owner)

    def delete_owner(self, name: str) -> None:
        """Remove the owner with the given name from the scheduler."""
        self.owners = [o for o in self.owners if o.name != name]

    # --- Pet management ---
    def add_pet(self, pet: Pet) -> None:
        """Register a pet with the scheduler."""
        self.pets.append(pet)

    def delete_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name from the scheduler."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    # --- Task management ---
    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler's central task list."""
        self.tasks.append(task)

    def delete_task(self, task_title: str, pet_name: str) -> None:
        """Remove tasks matching both title and pet name from the scheduler."""
        self.tasks = [
            t for t in self.tasks
            if not (t.task_title == task_title and t.pet_name == pet_name)
        ]

    # --- Appointment management ---
    def add_appointment(self, appointment: Appointment) -> None:
        """Add an appointment to the scheduler's central appointment list."""
        self.appointments.append(appointment)

    def delete_appointment(self, title: str, pet_name: str) -> None:
        """Remove appointments matching both title and pet name from the scheduler."""
        self.appointments = [
            a for a in self.appointments
            if not (a.appointment_title == title and a.pet_name == pet_name)
        ]

    # --- Scheduling (core logic) ---
    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by scheduled_datetime using 'HH:MM' string comparison."""
        return sorted(tasks, key=lambda t: t.scheduled_datetime.strftime("%H:%M"))

    def build_daily_schedule(self, pet_name: str, target_date: date) -> List[Task]:
        """Return tasks for a pet on a given day, sorted by priority then time."""
        pet_tasks = Task.get_task_by_pet(
            Task.get_task_by_date(self.tasks, target_date), pet_name
        )
        return sorted(
            pet_tasks,
            key=lambda t: (_PRIORITY_ORDER.get(t.priority, 1), t.scheduled_datetime),
        )

    def explain_schedule(self, schedule: List[Task]) -> str:
        """Return a human-readable summary of a schedule."""
        if not schedule:
            return "No tasks scheduled."
        pet = schedule[0].pet_name
        lines = [f"Daily schedule for {pet} ({schedule[0].scheduled_datetime.date()}):"]
        for task in schedule:
            status = "[X]" if task.completed else "[ ]"
            lines.append(
                f"  {status} {task.scheduled_datetime.strftime('%H:%M')} "
                f"[{task.priority.upper()}] {task.task_title} "
                f"({task.duration_minutes} min) - {task.description}"
            )
        return "\n".join(lines)

    def mark_task_complete(self, task: Task) -> "Task | None":
        """Mark a task complete and, for recurring tasks, schedule the next occurrence.

        Returns the newly created Task if the frequency is 'daily' or 'weekly',
        otherwise returns None.
        """
        task.mark_complete()

        if task.frequency == "daily":
            delta = timedelta(days=1)
        elif task.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None

        new_task = Task(
            task_title=task.task_title,
            description=task.description,
            scheduled_datetime=task.scheduled_datetime + delta,
            pet_name=task.pet_name,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            frequency=task.frequency,
            completed=False,
        )

        self.tasks.append(new_task)

        for pet in self.pets:
            if pet.name == task.pet_name:
                pet.tasks.append(new_task)
                break

        return new_task

    def detect_conflicts(self) -> List[str]:
        """Check all tasks for time overlaps and return a list of warning messages.

        Two tasks conflict when their time windows overlap:
            task_a.start < task_b.end  AND  task_b.start < task_a.end
        Completed tasks are skipped. Returns an empty list if no conflicts found.
        """
        warnings = []
        active = [t for t in self.tasks if not t.completed]

        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a = active[i]
                b = active[j]
                a_start = a.scheduled_datetime
                a_end = a_start + timedelta(minutes=a.duration_minutes)
                b_start = b.scheduled_datetime
                b_end = b_start + timedelta(minutes=b.duration_minutes)

                if a_start < b_end and b_start < a_end:
                    same_pet = a.pet_name == b.pet_name
                    scope = "same pet" if same_pet else "different pets"
                    warnings.append(
                        f"CONFLICT ({scope}): '{a.task_title}' ({a.pet_name}, "
                        f"{a_start.strftime('%H:%M')}-{a_end.strftime('%H:%M')}) "
                        f"overlaps with '{b.task_title}' ({b.pet_name}, "
                        f"{b_start.strftime('%H:%M')}-{b_end.strftime('%H:%M')})"
                    )

        return warnings
