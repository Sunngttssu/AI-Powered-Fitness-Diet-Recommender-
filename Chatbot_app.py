import streamlit as st
import cohere
import json

# Temporary storage to save user progress
session_data = {}


# Function to display a welcome message
def display_welcome_message():
    st.markdown("<h1 style='color:blue;'>Welcome to the Enhanced Fitness and Diet Recommender!</h1>",
                unsafe_allow_html=True)
    st.write("We are here to help you create a personalized fitness and diet plan based on your goals.")

# Function to calculate daily caloric needs based on user input
def calculate_calories(weight, height, age, gender):
    if gender == 'Male':
        # BMR calculation for men
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        # BMR calculation for women
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return bmr


# Function to generate a detailed diet plan based on caloric needs and user goal
def get_diet_plan(user_data):
    bmr = calculate_calories(user_data['weight'], user_data['height'], user_data['age'], user_data['gender'])

    # Adjust calorie intake based on goal
    if user_data['fitness_goal'] == "Weight Loss":
        daily_calories = bmr - 500  # Caloric deficit for weight loss
    elif user_data['fitness_goal'] == "Muscle Gain":
        daily_calories = bmr + 300  # Caloric surplus for muscle gain
    else:
        daily_calories = bmr  # Maintenance for endurance or general fitness

    # Macronutrient distribution based on goals
    if user_data['fitness_goal'] == "Weight Loss":
        protein = 1.8 * user_data['weight']  # High protein intake to preserve muscle
        carbs = 0.4 * daily_calories / 4
        fats = (daily_calories - (protein * 4 + carbs * 4)) / 9
    elif user_data['fitness_goal'] == "Muscle Gain":
        protein = 2.0 * user_data['weight']  # Higher protein for muscle growth
        carbs = 0.55 * daily_calories / 4
        fats = (daily_calories - (protein * 4 + carbs * 4)) / 9
    elif user_data['fitness_goal'] == "Endurance":
        protein = 1.2 * user_data['weight']  # Moderate protein, more carbs for energy
        carbs = 0.6 * daily_calories / 4
        fats = (daily_calories - (protein * 4 + carbs * 4)) / 9
    else:  # General fitness
        protein = 1.5 * user_data['weight']  # Balanced intake for general fitness
        carbs = 0.5 * daily_calories / 4
        fats = (daily_calories - (protein * 4 + carbs * 4)) / 9

    # Return a diet plan
    return f"""
    **Your daily calorie intake should be approximately:** {daily_calories:.2f} kcal.
    **Macronutrient breakdown:**
    - **Protein:** {protein:.2f} grams/day
    - **Carbohydrates:** {carbs:.2f} grams/day
    - **Fats:** {fats:.2f} grams/day
    """


# Function to collect user data using Streamlit
def get_user_data():
    age = st.selectbox('Age:', [str(i) for i in range(18, 81)])
    gender = st.selectbox('Gender:', ['Male', 'Female'])
    weight = st.number_input('Weight (kg):', value=70.0)
    height = st.number_input('Height (cm):', value=170.0)
    fitness_goal = st.selectbox('Goal:', ['Weight Loss', 'Muscle Gain', 'Endurance', 'General Fitness'])
    diet_preference = st.selectbox('Dietary Preference:', ['None', 'Vegetarian', 'Non-Vegetarian', 'Eggetarian'])
    medical_conditions = st.text_area('Medical Conditions:', placeholder="Eg: Diabetes, Gluten Allergy, etc.")

    submit_button = st.button("Submit")

    if submit_button:
        session_data['age'] = int(age)
        session_data['gender'] = gender
        session_data['weight'] = float(weight)
        session_data['height'] = float(height)
        session_data['fitness_goal'] = fitness_goal
        session_data['diet_preference'] = diet_preference
        session_data['medical_conditions'] = medical_conditions

        generate_recommendations(session_data)


# Function to generate a workout plan based on user fitness goal
def get_workout_plan(fitness_goal):
    if fitness_goal == "Weight Loss":
        return [
            "30 min of cardio",
            "Strength training 3x per week",
            "HIT 2x per week"
        ]
    elif fitness_goal == "Muscle Gain":
        return [
            "Strength training 5x per week",
            "Compound lifts (e.g., squats, deadlifts)",
            "Progressive overload"
        ]
    elif fitness_goal == "Endurance":
        return [
            "Long-distance running",
            "Cycling",
            "Swimming"
        ]
    else:
        return [
            "General Fitness: A mix of cardio and strength training",
            "Flexibility exercises like yoga"
        ]


# Function to generate a response from the LLM
def generate_llm_response(user_data, workout_plan, diet_plan):
    co = cohere.Client('#Any desirable API key#')
    prompt = f"""
    User data: {json.dumps(user_data, indent=2)}
    Workout plan: {', '.join(workout_plan)}
    Diet plan: {diet_plan}
    Generate a detailed and personalized exercise and diet plan based on the user's data. Consider the user's medical conditions, fitness goals, dietary preferences, and other relevant factors to provide specific and accurate recommendations.
    """
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=3000,
        temperature=0.7
    )
    return response.generations[0].text.strip()


# Function to generate the recommendations
def generate_recommendations(user_data):
    diet_plan = get_diet_plan(user_data)
    workout_plan = get_workout_plan(user_data['fitness_goal'])
    llm_response = generate_llm_response(user_data, workout_plan, diet_plan)

    st.markdown("### Your Recommended Diet Plan")
    st.write(diet_plan)

    st.markdown("### Your Recommended Workout Plan")
    st.write("\n".join(workout_plan))

    st.markdown("### Personalized Advice from Expert")
    st.write(llm_response)


# Main function
if __name__ == "__main__":
    display_welcome_message()
    get_user_data()

