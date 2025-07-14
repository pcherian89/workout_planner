# === Import Libraries ===
import streamlit as st
import openai
import re
import pandas as pd

# === API Key Setup ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
        st.subheader("Customize Your Weekly Plan")
        goal = st.selectbox("Your Goal", mode_config[selected_mode]["goals"])
        experience = st.radio("Experience Level", ["Beginner", "Intermediate", "Advanced"])
        days = st.slider("Training Days per Week", 3, 7, 5)
        equipment = st.multiselect(
            "Available Equipment",
            ["Dumbbells", "Barbell", "Rower", "Sled", "Kettlebells", "Pull-up Bar", "Bodyweight Only"]
        )
        submit = st.form_submit_button("Generate My Weekly Plan")

    # === SUBMIT LOGIC ===
    if submit:
        with st.spinner(f"🧠 Generating your {selected_mode.lower()} training plan..."):
            try:
                equipment_str = ", ".join(equipment) if equipment else "bodyweight only"
                base_prompt = mode_config[selected_mode]["prompt_prefix"]
                prompt = (
                f"{base_prompt} "
                f"The user is a {experience.lower()} level athlete with a primary goal to {goal.lower()}. "
                f"They can train {days} days per week using the following equipment: {equipment_str}. "
                f"\n\nGenerate exactly {days} advanced, structured workout days. Do NOT include rest or recovery days. "
                f"Each training day should include:\n"
                f"- A unique title\n"
                f"- Main training focus (e.g. Push Strength, Pull Power, Engine Conditioning)\n"
                f"- Detailed warm-up section (include dynamic movements or mobility drills)\n"
                f"- Primary workout segment (e.g., barbell or compound lift with sets/reps)\n"
                f"- Conditioning or metcon (e.g., EMOM, AMRAP, interval sprints)\n"
                f"- Optional accessory or core work (e.g., 3 sets of 15 glute bridges)\n"
                f"- Cooldown or mobility finish (e.g., stretching or foam rolling)\n\n"
                f"Ensure the workouts feel purposeful and challenging, suitable for the user's level. "
                f"Use proper formatting and variety across days."
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

    st.markdown("### \U0001F4CA Weekly Overview Summary")
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

    selected_day = st.selectbox("\U0001F4C5 Choose a day to view:", [f"Day {i+1}" for i in range(len(plan_days))])
    day_index = int(selected_day.split(" ")[1]) - 1

    st.markdown(f"### \U0001F4CB {selected_day} Plan")
    workout_text = plan_days[day_index].strip()

    if len(workout_text) > 50:
        st.markdown(workout_text)
    else:
        st.warning("⚠️ This day's workout plan is missing or malformed. Please regenerate it.")

    # === Daily Check-In ===
    st.subheader("\U0001F9E0 Daily Check-In")
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






