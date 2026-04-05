import streamlit as st
from pawpal_system import Pet, Owner, Task, Scheduler, Appointment
from datetime import date, time, datetime

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Session state initialization ---
# owners: dict keyed by owner name, each holding pets, tasks, appointments, conflicts
if "owners" not in st.session_state:
    st.session_state.owners = {}

if "current_owner" not in st.session_state:
    st.session_state.current_owner = None

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

# --- Owner selection / creation ---
col_own1, col_own2 = st.columns([3, 1])
with col_own1:
    owner_name_input = st.text_input("Owner name", value="Jordan")
with col_own2:
    st.write("")
    st.write("")
    if st.button("Add / Switch owner"):
        name = owner_name_input.strip()
        if name:
            if name not in st.session_state.owners:
                st.session_state.owners[name] = {
                    "pets": [],
                    "tasks": [],
                    "appointments": [],
                    "conflicts": [],
                }
                st.success(f"Owner '{name}' created.")
            else:
                st.info(f"Switched to owner '{name}'.")
            st.session_state.current_owner = name
            st.rerun()

# If no owner yet, stop here
if not st.session_state.current_owner:
    st.info("Enter an owner name and click 'Add / Switch owner' to begin.")
    st.stop()

# Shorthand for current owner's data
cur = st.session_state.owners[st.session_state.current_owner]

# Show all owners as quick-switch buttons
if len(st.session_state.owners) > 1:
    st.markdown("**Switch owner:**")
    btn_cols = st.columns(len(st.session_state.owners))
    for idx, oname in enumerate(st.session_state.owners):
        label = f"{'→ ' if oname == st.session_state.current_owner else ''}{oname}"
        if btn_cols[idx].button(label, key=f"switch_{oname}"):
            st.session_state.current_owner = oname
            st.rerun()

st.markdown(f"### Working on: **{st.session_state.current_owner}**")
st.divider()

# --- Add pet ---
st.markdown("#### Add a pet")
pet_col1, pet_col2, pet_col3 = st.columns([2, 2, 1])
with pet_col1:
    pet_name_input = st.text_input("Pet name", value="Mochi")
with pet_col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with pet_col3:
    st.write("")
    st.write("")
    if st.button("Add pet"):
        pname = pet_name_input.strip()
        existing = [p["name"] for p in cur["pets"]]
        if pname in existing:
            st.warning(f"'{pname}' already exists for {st.session_state.current_owner}.")
        else:
            pet = Pet(name=pname, species=species)
            cur["pets"].append(pet.get_pet_info())
            st.success(f"Added pet '{pname}' to {st.session_state.current_owner}.")
            st.rerun()

# --- Owner & Pet Info display ---
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Owner and Pet Info")
    if cur["pets"]:
        st.write(f"Owner: {st.session_state.current_owner}")
        selected_pet_name = st.selectbox("Select pet", [p["name"] for p in cur["pets"]])
        selected_pet = next(p for p in cur["pets"] if p["name"] == selected_pet_name)
        pet_breed = selected_pet["breed"] or "unknown breed"
        st.write(f"Pet: {selected_pet_name} ({selected_pet['species']}, {pet_breed})")
        pet_name = selected_pet_name
    else:
        st.info("No pets yet. Add one above.")
        pet_name = ""

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if not cur["pets"]:
    st.info("Please add at least one pet before adding tasks.")
    st.stop()

if "task_conflicts" not in st.session_state:
    st.session_state.task_conflicts = []

def clear_conflicts():
    st.session_state.task_conflicts = []

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, on_change=clear_conflicts)
with col3:
    scheduled_time = st.time_input("Scheduled time", value=time(0, 0), on_change=clear_conflicts)
with col4:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
with col5:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=0)

scheduler = Scheduler()

if st.button("Add task"):
    st.session_state.task_conflicts = []   # reset before each attempt
    new_task = Task(
        task_title=task_title,
        description="",
        scheduled_datetime=datetime.combine(date.today(), scheduled_time),
        duration_minutes=int(duration),
        priority=priority,
        pet_name=pet_name,
        frequency=frequency
    )
    # Find only conflicts introduced by the new task (ignore pre-existing ones)
    scheduler.tasks = cur["tasks"]
    existing_conflicts = set(scheduler.detect_conflicts())
    scheduler.tasks = cur["tasks"] + [new_task]
    all_conflicts = set(scheduler.detect_conflicts())
    new_conflicts = list(all_conflicts - existing_conflicts)
    if new_conflicts:
        st.session_state.task_conflicts = new_conflicts
    else:
        cur["tasks"].append(new_task)
        st.success("Task added.")

if st.session_state.task_conflicts:
    for warning in st.session_state.task_conflicts:
        st.warning(warning)
    st.error("Task not added. Resolve the time conflict first (change the time or duration).")

if cur["tasks"]:
    st.write("Current tasks:")
    h0, h1, h2, h3, h4, h5, h6 = st.columns([2.5, 1, 1, 1.5, 1, 1.5, 2])
    h0.markdown("**Task**")
    h1.markdown("**Pet**")
    h2.markdown("**Time**")
    h3.markdown("**Duration**")
    h4.markdown("**Priority**")
    h5.markdown("**Frequency**")
    h6.markdown("**Action**")
    st.divider()
    for i, t in enumerate(cur["tasks"]):
        col_title,col_pet_name ,col_time, col_dur, col_pri, col_freq, col_chk = st.columns([2.5,1, 1, 1, 1, 1.5, 2])
        col_title.write(t.task_title)
        col_pet_name.write(t.pet_name)
        col_time.write(t.scheduled_datetime.strftime("%H:%M"))
        col_dur.write(f"{t.duration_minutes} min")
        col_pri.write(t.priority)
        col_freq.write(t.frequency)
        if not t.completed:
            if col_chk.checkbox("Mark complete", key=f"complete_{st.session_state.current_owner}_{i}"):
                scheduler.tasks = cur["tasks"]
                new_task = scheduler.mark_task_complete(t)
                if new_task:
                    cur["tasks"].append(new_task)
                # Sync completed status into the schedule snapshot
                for sched_task in st.session_state.schedule:
                    if sched_task["title"] == t.task_title:
                        sched_task["completed"] = True
                st.rerun()
        else:
            col_chk.write("✅")

if not cur["tasks"]:
    st.info("No tasks yet. Add one above.")
elif len(cur["tasks"]) > 1:
    if st.button("Sort tasks by time"):
        cur["tasks"] = scheduler.sort_by_time(cur["tasks"])
        st.rerun()
    if st.button("Sort tasks by priority"):
        scheduler.tasks = cur["tasks"]
        cur["tasks"] = scheduler.build_daily_schedule(
            pet_name=pet_name,
            target_date=date.today()
        )
        st.rerun()

st.divider()

##Appointment scheduling section
st.subheader("Appointments")
st.caption("Schedule an appointment for your pet.")

appt_col1, appt_col2 = st.columns(2)
with appt_col1:
    appt_title = st.text_input("Appointment title", value="Vet checkup")
    appt_place = st.text_input("Place", value="City Animal Clinic")
with appt_col2:
    appt_person = st.text_input("Person (vet, groomer, etc.)", value="Dr. Smith")
    appt_pet = st.selectbox("Pet for appointment", [p["name"] for p in cur["pets"]], key="appt_pet")

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
    cur["appointments"].append(new_appt.get_appointment())

if cur["appointments"]:
    st.write("Scheduled appointments:")
    st.table(cur["appointments"])
else:
    st.info("No appointments yet. Add one above.")

st.divider()

## Build schedule section
st.subheader("Build Schedule")

sched_col1, sched_col2 = st.columns(2)
with sched_col1:
    sched_pet = st.selectbox("Pet name", [p["name"] for p in cur["pets"]], key="sched_pet")
with sched_col2:
    sched_date = st.date_input("Schedule date", value=date.today(), key="sched_date")

if st.button("Generate schedule"):
    if not cur["tasks"]:
        st.warning("Add at least one task before generating a schedule.")
    else:
        pet_species = next((p["species"] for p in cur["pets"] if p["name"] == sched_pet), "unknown")
        sched_pet_obj = Pet(name=sched_pet, species=pet_species)
        sched_owner = Owner(name=st.session_state.current_owner, pets=[sched_pet_obj])

        scheduler.add_owner(sched_owner)
        scheduler.add_pet(sched_pet_obj)

        slot_hour, slot_min = 8, 0
        for t in cur["tasks"]:
            task = Task(
                task_title=t.task_title,
                description="",
                scheduled_datetime=datetime.combine(sched_date, time(slot_hour, slot_min)),
                duration_minutes=t.duration_minutes,
                priority=t.priority,
                pet_name=sched_pet,
                frequency=t.frequency,
                completed=t.completed,
            )
            scheduler.add_task(task)
            total = slot_hour * 60 + slot_min + t.duration_minutes
            slot_hour, slot_min = total // 60, total % 60

        for appt_dict in cur["appointments"]:
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
    schedule_display = []
    for t in st.session_state.schedule:
        schedule_display.append({
            "Title": t["title"],
            "Time": t["datetime"].strftime("%H:%M") if hasattr(t["datetime"], "strftime") else t["datetime"],
            "Pet": t["pet"],
            "Duration(min)": t["duration_minutes"],
            "Priority": t["priority"],
            "Frequency": t["frequency"],
            "Status": "Completed" if t["completed"] else "",
        })
    st.table(schedule_display)
else:
    st.info("Schedule will appear here once generated.")
