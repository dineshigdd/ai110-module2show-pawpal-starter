import streamlit as st
from pawpal_system import Pet, Owner, Task, Scheduler, Appointment
from datetime import date, time, datetime

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "appointments" not in st.session_state:
    st.session_state.appointments = []

if "schedule" not in st.session_state:
    st.session_state.schedule = []

if "schedule_summary" not in st.session_state:
    st.session_state.schedule_summary = ""

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")

##Creating pet and owner objects with user input (UI only, no logic yet)
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Create pet and owner"):
    try:
        pet = Pet(name=pet_name, species=species)
        owner = Owner(name=owner_name, pets=[pet])
        st.session_state.owner = owner.get_owner_info()
        st.session_state.pet = pet.get_pet_info()
        if not st.session_state.tasks:
            default_task = Task(
                task_title="Morning walk",
                description="",
                scheduled_datetime=datetime.combine(date.today(), time(8, 0)),
                duration_minutes=20,
                priority="high",
            )
            st.session_state.tasks.append(
                {"task_title": default_task.task_title, "duration_minutes": default_task.duration_minutes, "priority": default_task.priority}
            )
        st.success(f"Created owner {owner.name} with pet {pet.name} ({pet.species})")
    except AttributeError as e:
        st.error(f"Failed to create owner/pet: {e}")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Owner and Pet Info")
    if st.session_state.owner and st.session_state.pet:
        st.write(f"Owner: {st.session_state.owner['name']}")
        pet_breed = st.session_state.pet['breed'] or "unknown breed"
        st.write(f"Pet: {st.session_state.pet['name']} ({pet_breed})")
    else:
        st.info("No owner/pet created yet.")


##Task input section (UI only, no logic yet)
st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    new_task = Task(
        task_title=task_title,
        description="",
        scheduled_datetime=datetime.combine(date.today(), time(0, 0)),
        duration_minutes=int(duration),
        priority=priority,
    )
    st.session_state.tasks.append(
        {"task_title": new_task.task_title, "duration_minutes": new_task.duration_minutes, "priority": new_task.priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

##Appointment scheduling section (UI only, no logic yet)
st.subheader("Appointments")
st.caption("Schedule an appointment for your pet.")

appt_col1, appt_col2 = st.columns(2)
with appt_col1:
    appt_title = st.text_input("Appointment title", value="Vet checkup")
    appt_place = st.text_input("Place", value="City Animal Clinic")
with appt_col2:
    appt_person = st.text_input("Person (vet, groomer, etc.)", value="Dr. Smith")
    appt_pet = st.text_input("Pet name", value=pet_name, key="appt_pet")

appt_date = st.date_input("Appointment date", value=date.today())
appt_time = st.time_input("Appointment time", value=time(10, 0))
appt_notes = st.text_area("Notes (optional)", value="")

if st.button("Add appointment"):
    new_appt = Appointment(
        appointment_title=appt_title,
        appointment_date_time=datetime.combine(appt_date, appt_time),
        place=appt_place,
        appointment_person=appt_person,
        pet_name=appt_pet,
        notes=appt_notes,
    )
    st.session_state.appointments.append(new_appt.get_appointment())

if st.session_state.appointments:
    st.write("Scheduled appointments:")
    st.table(st.session_state.appointments)
else:
    st.info("No appointments yet. Add one above.")

st.divider()

## Build schedule section (UI only, no logic yet)
st.subheader("Build Schedule")

sched_col1, sched_col2 = st.columns(2)
with sched_col1:
    sched_pet = st.text_input(
        "Pet name",
        value=st.session_state.pet["name"] if st.session_state.pet else "",
        key="sched_pet",
    )
with sched_col2:
    sched_date = st.date_input("Schedule date", value=date.today(), key="sched_date")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    elif not sched_pet:
        st.warning("Enter a pet name.")
    else:
        pet_species = st.session_state.pet["species"] if st.session_state.pet else "unknown"
        sched_pet_obj = Pet(name=sched_pet, species=pet_species)
        owner_name = st.session_state.owner["name"] if st.session_state.owner else "Owner"
        sched_owner = Owner(name=owner_name, pets=[sched_pet_obj])

        scheduler = Scheduler()
        scheduler.add_owner(sched_owner)
        scheduler.add_pet(sched_pet_obj)

        slot_hour, slot_min = 8, 0
        for task_dict in st.session_state.tasks:
            t = Task(
                task_title=task_dict["task_title"],
                description="",
                scheduled_datetime=datetime.combine(sched_date, time(slot_hour, slot_min)),
                duration_minutes=task_dict["duration_minutes"],
                priority=task_dict["priority"],
                pet_name=sched_pet,
            )
            scheduler.add_task(t)
            total = slot_hour * 60 + slot_min + task_dict["duration_minutes"]
            slot_hour, slot_min = total // 60, total % 60

        for appt_dict in st.session_state.appointments:
            if appt_dict["pet"] in (sched_pet, ""):
                scheduler.add_appointment(Appointment(
                    appointment_title=appt_dict["title"],
                    appointment_date_time=appt_dict["datetime"],
                    place=appt_dict["place"],
                    appointment_person=appt_dict["person"],
                    pet_name=sched_pet,
                    notes=appt_dict["notes"],
                ))

        schedule = scheduler.build_daily_schedule(pet_name=sched_pet, target_date=sched_date)
        st.session_state.schedule = [t.get_task() for t in schedule]
        st.session_state.schedule_summary = scheduler.explain_schedule(schedule)
        st.success(f"Schedule generated for {sched_pet} on {sched_date}!")

## Schedule output section
st.markdown("### Today's Schedule")

if st.session_state.schedule:
    st.text(st.session_state.get("schedule_summary", ""))
    st.table(st.session_state.schedule)
else:
    st.info("Schedule will appear here once generated.")
