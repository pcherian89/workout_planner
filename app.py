# === Import Libraries ===
import streamlit as st
import openai
import re
import pandas as pd

# === API Key Setup ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === Custom Styling for Dark Theme ===
st.markdown("""
    <style>
    /* Fix dropdown background in dark mode */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #1e1e1e !important;
        color: #fff !important;
    }

    .stSlider, .stRadio, .stSelectbox, .stMultiSelect {
        color: #ffffff !important;
    }

    /* Style the data table */
    thead tr th {
        color: #ffffff !important;
        background-color: #262730 !important;
    }

    tbody tr td {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }

    .stDataFrame {
        border: 1px solid #333;
        border-radius: 10px;
        overflow: hidden;
    }

    /* General UI padding and contrast */
    .block-container {
        padding-top: 2rem;
    }

    </style>
""", unsafe_allow_html=True)

# === Sidebar Navigation ===
st.sidebar.title("🏋️ Workout Modes")
selected_mode = st.sidebar.radio("Choose Your Mode:", ["Bodybuilding", "HYROX", "CrossFit", "Hybrid"])

# === Header ===
st.title("💪 AI-Powered Training Platform")
st.markdown("Your intelligent coach for Bodybuilding, HYROX, and CrossFit — or a mix of all.")

# === MODE CONFIGURATIONS ===
mode_config = {
    "Bodybuilding": {
        "prompt_prefix": "Create a bodybuilding-focused training plan.",
        "goals": ["Build Muscle", "Increase Strength"],
    },
    "HYROX": {
        "prompt_prefix": "Create a HYROX-specific weekly training plan for competitive athletes.",
        "goals": ["Race Preparation", "Improve Time"],
    },
    "CrossFit": {
        "prompt_prefix": "Create a weekly CrossFit training plan for a performance-oriented athlete.",
        "goals": ["Boost Performance", "Increase Work Capacity"],
    },
    "Hybrid": {
        "prompt_prefix": "Create a hybrid training plan that combines bodybuilding, HYROX, and CrossFit.",
        "goals": ["Build Muscle", "Lose Fat", "Boost Endurance", "Hybrid Performance"],
    }
}

# === PLAN GENERATOR SECTION ===
if selected_mode:
    st.header(f"{selected_mode} Plan Generator")

    with st.form(f"{selected_mode.lower()}_form"):
        st.subheader("⚙️ Customize Your Weekly Plan")
        goal = st.selectbox("🎯 Your Goal", mode_config[selected_mode]["goals"])
        experience = st.radio("📈 Experience Level", ["Beginner", "Intermediate", "Advanced"])
        days = st.slider("📅 Training Days per Week", 3, 7, 5)
        equipment = st.multiselect(
            "🏋️ Available Equipment",
            ["Dumbbells", "Barbell", "Rower", "Sled", "Kettlebells", "Pull-up Bar", "Bodyweight Only"]
        )
        submit = st.form_submit_button("🚀 Generate My Weekly Plan")

    if submit:
        with st.spinner(f"🧠 Generating your {selected_mode.lower()} training plan..."):
            try:
                equipment_str = ", ".join(equipment) if equipment else "bodyweight only"
                base_prompt = mode_config[selected_mode]["prompt_prefix"]
                # Dynamic prompt builder based on selected mode
                if selected_mode == "Bodybuilding":
                    prompt = (
                        f"{base_prompt} "
                        f"The user is a {experience.lower()} level bodybuilder aiming to {goal.lower()}. "
                        f"They train {days} days/week and have access to: {equipment_str}. "
                        f"Only use listed equipment. No cardio machines unless specified.\n\n"
                        f"Generate exactly {days} detailed lifting workouts. No rest days.\n"
                        f"Each day should include:\n"
                        f"- A unique title (e.g., Chest Domination, Arm Annihilation)\n"
                        f"- Target muscle groups (e.g., Chest/Triceps)\n"
                        f"- Warm-up (mobility, light reps)\n"
                        f"- Main hypertrophy-focused workout (compound + isolation exercises with sets/reps)\n"
                        f"- Optional finisher (drop sets, supersets, pump work)\n"
                        f"- Cooldown (stretching, foam rolling)\n\n"
                        f"Use bodybuilding-specific language and progressive overload concepts. Avoid generic functional training."
                    )
                
                elif selected_mode == "HYROX":
                    prompt = (
                        f"{base_prompt} "
                        f"The user is a {experience.lower()} level HYROX athlete with a goal to {goal.lower()}. "
                        f"They can train {days} days/week using: {equipment_str}.\n\n"
                        f"Create exactly {days} competitive HYROX-style training days (no recovery days).\n"
                        f"Each day must include:\n"
                        f"- A unique title (e.g., Wall Ball Blitz, Row-Sled Crusher)\n"
                        f"- HYROX movement focus (e.g., sled push/pull, farmer’s carry, wall balls)\n"
                        f"- Functional warm-up (hips, posterior chain, shoulder prep)\n"
                        f"- Workout block with race-specific stations (e.g., Run 1km → Sled Push → Burpee Broad Jumps)\n"
                        f"- Pacing & breathing strategies\n"
                        f"- Optional mobility or zone-2 cool down\n\n"
                        f"Make it feel like actual race simulation and prep. Use real HYROX-style movements. Avoid bodybuilding style."
                    )
                
                elif selected_mode == "CrossFit":
                    prompt = (
                        f"{base_prompt} "
                        f"The user is a {experience.lower()} level CrossFit athlete aiming to {goal.lower()}. "
                        f"They train {days} days/week using the following equipment: {equipment_str}.\n\n"
                        f"Generate exactly {days} challenging WODs. No rest days.\n"
                        f"Each day should follow this format:\n"
                        f"- WOD Title (e.g., 'The Engine', 'Barbell Hell')\n"
                        f"- Focus (e.g., Gymnastics, Olympic Lifting, Mixed Modal)\n"
                        f"- Warm-up (functional/dynamic, specific to the WOD)\n"
                        f"- Strength or Skill segment (e.g., 5x3 Clean & Jerk)\n"
                        f"- Metcon or EMOM/AMRAP (clearly defined time/reps)\n"
                        f"- Optional accessory/core (GHD, kettlebells, etc.)\n"
                        f"- Cooldown or ROMWOD-style finish\n\n"
                        f"Make it read like a real CrossFit box programming. Include Rx scaling options if needed."
                    )
                
                elif selected_mode == "Hybrid":
                    prompt = (
                        f"{base_prompt} "
                        f"The user is a {experience.lower()} hybrid athlete with a primary goal to {goal.lower()}. "
                        f"They can train {days} days/week using: {equipment_str}.\n\n"
                        f"Create exactly {days} hybrid-style sessions that combine strength, conditioning, and endurance. "
                        f"No recovery days.\n"
                        f"Each day should include:\n"
                        f"- Title (e.g., Full Body Grinder, Engine + Pull)\n"
                        f"- Hybrid Focus (e.g., Strength + HIIT, Tempo Lifting + Endurance)\n"
                        f"- Warm-up (blended mobility + activation)\n"
                        f"- Primary lift or compound movement (e.g., Deadlift 5x5)\n"
                        f"- Functional circuit or run-based metcon (e.g., 3 rounds: 800m run, DB thrusters, burpees)\n"
                        f"- Optional finisher or EMOM/core work\n"
                        f"- Stretching or cooldown\n\n"
                        f"Ensure blend of CrossFit, HYROX and bodybuilding elements. Do not stick to one style per day. Mix smartly."
                    )

                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )

                full_text = response.choices[0].message.content
                st.session_state["full_plan"] = full_text
                st.session_state["plan_days"] = re.findall(r"(Day \d+[\s\S]*?)(?=Day \d+|$)", full_text)
                st.success("✅ Your plan is ready!")

            except Exception as e:
                st.error(f"❌ Error generating plan: {e}")

# === PLAN VIEWER & CHECK-IN ===
if "plan_days" in st.session_state:
    plan_days = st.session_state["plan_days"]

    st.markdown("### 🗓️ Weekly Overview")
    weekly_summary = []
    for i, day in enumerate(plan_days):
        lines = day.strip().split("\n")
        title = lines[0] if len(lines) > 0 else f"Day {i+1}"
        focus_line = next((line for line in lines if "focus" in line.lower()), "")
        weekly_summary.append({
            "Day": f"Day {i+1}",
            "Title": title.replace("Day", "").strip(": "),
            "Focus": focus_line.replace("Focus:", "").strip() if focus_line else "—"
        })

    summary_df = pd.DataFrame(weekly_summary)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    selected_day = st.selectbox("📌 Choose a Day", [f"Day {i+1}" for i in range(len(plan_days))])
    day_index = int(selected_day.split(" ")[1]) - 1

    st.markdown(f"### 🏋️ {selected_day} Plan")
    workout_text = plan_days[day_index].strip()

    if len(workout_text) > 50:
        st.markdown(workout_text)
    else:
        st.warning("⚠️ This day's workout plan is missing or malformed. Please regenerate it.")

    # === Daily Check-In ===
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
                f"Here is today's original workout:\n\n{workout_text}\n\n"
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

# === Footer ===
st.caption("Built with 💡 by [Pothen]")






