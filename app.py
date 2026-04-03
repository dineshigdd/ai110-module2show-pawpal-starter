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
                date=date.today(),
                scheduled_time=time(8, 0),
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
        date=date.today(),
        scheduled_time=time(0, 0),
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

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )

## Schedule output section (UI only, no logic yet)
st.markdown("### Today's Schedule")
st.caption("Once you have scheduling logic, display the generated schedule here.")

if st.session_state.schedule:
    st.table(st.session_state.schedule)
else:
    st.info("Schedule will appear here after you implement the scheduling logic and connect it to this app.")
