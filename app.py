import streamlit as st
import openai

# === 🔐 API Key Setup ===
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Set in Streamlit Cloud secrets OR use openai.api_key = "your-key" locally

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
    
                full_plan = response.choices[0].message.content
                st.success("✅ Your hybrid plan is ready!")
    
                # --- Split full plan into individual days ---
                plan_days = full_plan.split("Day ")[1:]
                plan_days = ["Day " + day.strip() for day in plan_days]
    
                # --- Day selector ---
                selected_day = st.selectbox("📅 Choose a day to view:", [f"Day {i+1}" for i in range(len(plan_days))])
                day_index = int(selected_day.split(" ")[1]) - 1
    
                st.markdown(f"### 📋 {selected_day} Plan")
                st.markdown(plan_days[day_index])
    
                # ✅ Ready for next step: feedback form right here
    
            except Exception as e:
                st.error(f"❌ Error generating plan: {e}")


# === Placeholder for other modes ===
else:
    st.header(f"{selected_mode} Mode")
    st.info("This mode will be added soon.")

# === Footer ===
st.markdown("---")
st.caption("Built with 💡 by [Pothen]")
