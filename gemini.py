
import os
from dotenv import load_dotenv
import google.generativeai as genai



load_dotenv()
APP_KEY = os.getenv("APP_KEY")
def get_nutrition(text):
    genai.configure(api_key=APP_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
   # response = model.generate_content(f"calorieee vlue of {qty} {text} with percentage of content with out explaination")
    refined_query = (
        f"Provide the calorie value and percentage composition of {text}. "
        "Include only numerical values with the units. Present the result as: "
        "calories: [value] kcal, protein: [value] g, carbohydrates: [value] g, fats: [value] g."
    )
    response = model.generate_content(refined_query)
    text = response.text
    print(text)
    return response.text

def main():
    get_nutrition("1","slice", "pizza" )

if __name__ == "__main__":
    main()








