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
            equipment_str = ", ".join(equipment) if equipment else "bodyweight only"
            prompt = (
                f"Create a 7-day hybrid training plan that combines bodybuilding, HYROX, and CrossFit elements. "
                f"The user is a {experience.lower()} athlete with a goal to {goal.lower()} and can train {days} days per week. "
                f"Available equipment includes: {equipment_str}. "
                f"Each day should include a workout name, main focus, and a brief description."
            )

            try:
                response = openai.chat.completions.create(
                    model="gpt-4o",  # or use "gpt-4-turbo" if you're not on GPT-4o
                    messages=[{"role": "user", "content": prompt}]
                )

                output = response['choices'][0]['message']['content']
                st.success("Here’s your custom hybrid plan:")
                st.markdown(output)
            except Exception as e:
                st.error(f"❌ Error generating plan: {e}")


# === Placeholder for other modes ===
else:
    st.header(f"{selected_mode} Mode")
    st.info("This mode will be added soon.")

# === Footer ===
st.markdown("---")
st.caption("Built with 💡 by [Pothen]")
