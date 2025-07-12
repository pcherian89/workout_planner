import streamlit as st
import openai

# === 🔐 API Key Setup ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === Sidebar Navigation ===
st.sidebar.title("🏋️ Workout Modes")
selected_mode = st.sidebar.radio("Choose Your Mode:", ["Bodybuilding", "HYROX", "CrossFit", "Hybrid"])

# === Header ===
st.title("💪 AI-Powered Training Platform")
st.markdown("Your intelligent coach for Bodybuilding, HYROX, and CrossFit — or a mix of all.")

# === HYBRID MODE: Weekly Plan Generator ===
if selected_mode == "Hybrid":
    st.header("🔀 Hybrid Plan Generator")

    with st.form("hybrid_form"):
        st.subheader("Customize Your Weekly Plan")
        goal = st.selectbox("Your Goal", ["Build Muscle", "Lose Fat", "Boost Endurance", "Hybrid Performance"])
        experience = st.radio("Experience Level", ["Beginner", "Intermediate", "Advanced"])
        days = st.slider("Training Days per Week", 3, 7, 5)
        equipment = st.multiselect(
            "Available Equipment", 
            ["Dumbbells", "Barbell", "Rower", "Sled", "Kettlebells", "Pull-up Bar", "Bodyweight Only"]
        )
        submit = st.form_submit_button("Generate My Weekly Plan")

    # ========== SUBMIT BUTTON ========== #
    if submit:
        with st.spinner("🧠 Generating your hybrid training plan..."):
            try:
                equipment_str = ", ".join(equipment) if equipment else "bodyweight only"
                prompt = (
                    f"Create a hybrid training plan that combines bodybuilding, HYROX, and CrossFit. "
                    f"The user is a {experience.lower()} athlete with a goal to {goal.lower()} and can train {days} days per week. "
                    f"Available equipment includes: {equipment_str}. "
                    f"Only generate {days} training days — do NOT include rest or recovery days. "
                    f"Each training day should include a name, the main focus (e.g. push, pull, engine, power), and a detailed, advanced workout. "
                    f"Use professional formatting: exercises, sets/reps, time-based intervals. Include compound lifts, metcons, and movement variety. "
                    f"Use terms like EMOM, AMRAP, zone pacing, or split times when appropriate. This should feel like elite training, not general advice."
                )
    
                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
    
                # Save to session_state
                st.session_state["full_plan"] = response.choices[0].message.content
                plan_days = st.session_state["full_plan"].split("Day ")[1:]
                st.session_state["plan_days"] = ["Day " + day.strip() for day in plan_days]
                st.success("✅ Your hybrid plan is ready!")
    
            except Exception as e:
                st.error(f"❌ Error generating plan: {e}")

    # ======== SHOW PLAN IF STORED ========
    if "plan_days" in st.session_state:
        plan_days = st.session_state["plan_days"]

        selected_day = st.selectbox("📅 Choose a day to view:", [f"Day {i+1}" for i in range(len(plan_days))])
        day_index = int(selected_day.split(" ")[1]) - 1

        st.markdown(f"### 📋 {selected_day} Plan")
        st.markdown(
            f"<div style='margin-bottom: -25px; padding-bottom: 0;'>{plan_days[day_index].strip().rstrip('*')}</div>",
            unsafe_allow_html=True
        )

        # No empty "###", no awkward line
        # No st.markdown("---") above Check-In
        st.markdown("<div style='margin-top: -10px;'></div>", unsafe_allow_html=True)

        # ======== DAILY FEEDBACK FORM ========
        st.subheader("🧠 Daily Check-In")

        col1, col2 = st.columns([1, 2])
        with col1:
            energy = st.slider("Energy", 1, 10, 7, help="How energetic do you feel today?")
        with col2:
            soreness = st.selectbox("Soreness Level", ["None", "Mild", "Moderate", "Severe"])

        injury_note = st.text_input("Injury / Pain Notes", placeholder="Describe any pain or injuries...")

        if st.button("🔁 Adjust Today’s Workout if Needed"):
            if energy <= 4 or soreness in ["Moderate", "Severe"] or injury_note.strip():
                st.warning("⚠️ Adjusting your workout based on your feedback...")

                feedback_prompt = (
                    f"Here is today's original workout:\n\n{plan_days[day_index]}\n\n"
                    f"The user reports: Energy = {energy}/10, Soreness = {soreness}, Notes = '{injury_note}'.\n\n"
                    f"Please modify this workout to reduce strain, avoid aggravating injuries, and maintain a productive session. "
                    f"Keep the structure but swap high-intensity or affected movements with gentler alternatives."
                )

                try:
                    adjustment_response = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": feedback_prompt}]
                    )
                    adjusted_plan = adjustment_response.choices[0].message.content
                    st.success("✅ Adjusted Workout Plan:")
                    st.markdown(adjusted_plan)

                except Exception as e:
                    st.error(f"Error adjusting workout: {e}")
            else:
                st.info("✅ You’re good to go! No need to modify today’s plan.")

    # === Placeholder for other modes ===
    else:
        st.header(f"{selected_mode} Mode")
        st.info("This mode will be added soon.")

    # === Footer ===
    st.caption("Built with 💡 by [Pothen]")

