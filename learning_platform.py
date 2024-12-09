import streamlit as st
import streamlit_ace
import openai
import os
import subprocess
import tempfile
import json
import sys
from dotenv import load_dotenv

load_dotenv()

class ProgrammingLearningPlatform:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # define execution environments for different programming languages
        self.execution_environments = {
            "Python": {
                "runner": self.run_python_code,
                "ace_mode": "python",
                "file_extension": ".py"
            },
            "JavaScript": {
                "runner": self.run_javascript_code,
                "ace_mode": "javascript",
                "file_extension": ".js"
            },
            "Java": {
                "runner": self.run_java_code,
                "ace_mode": "java",
                "file_extension": ".java"
            },
            "C++": {
                "runner": self.run_cpp_code,
                "ace_mode": "c_cpp",
                "file_extension": ".cpp"
            }
        }

    # generate learning path for user based on their input
    def generate_learning_path(self, current_knowledge, learning_goals, language):
        try:
            prompt = f"""
                Create a learning path for a learner with the following details:
                - Language: {language}
                - Current Knowledge: {current_knowledge}
                - Learning Goals: {learning_goals}
                (If language is Java or C++, please provide main method in the example code. Note: double quotes are escaped in Java and C++ strings.)
                Provide a JSON response list of 3 programming lessons and their key is 'lessons', including:
                - title
                - objective
                - explanation
                - example_code
                - coding_exercise
                
                (Note: do not include lessson number in the title, it will be added by the system.)
                (Note: explanation should be helpful and provide details, and exercise will be related to it.)
                (Note: there is no need to provide backgound or installation lessons, all 3 lessions are related to coding.)
                """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a helpful assistant that help people learn programming languages."},
                          {"role": "user", "content": prompt}],
                max_tokens=1000
            )

            raw_response = response.choices[0].message.content
            return json.loads(raw_response)
        except Exception as e:
            st.error(f"Error generating learning path: {e}")
            st.error("Please try again.")
            return None

    # run code in different programming languages
    def run_python_code(self, code):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_name = temp_file.name

            result = subprocess.run(
                ["python3", temp_file_name], 
                capture_output=True, 
                text=True
            )
            return result.stdout, result.stderr
        except Exception as e:
            return None, str(e)

    def run_javascript_code(self, code):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_name = temp_file.name
            result = subprocess.run(
                ['node', temp_file_name], 
                capture_output=True, 
                text=True
            )

            return result.stdout, result.stderr
        except Exception as e:
            return None, str(e)
        
    def run_java_code(self, code):
        try:
            temp_dir = tempfile.mkdtemp()
            temp_file_name = os.path.join(temp_dir, "Main.java")
            with open(temp_file_name, "w") as temp_file:
                temp_file.write(code)

            compile_result = subprocess.run(
                ['javac', temp_file_name],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return None, compile_result.stderr

            run_result = subprocess.run(
                ['java', '-cp', temp_dir, 'Main'],
                capture_output=True,
                text=True
            )
            return run_result.stdout, run_result.stderr
        except Exception as e:
            return None, str(e)
        
    def run_cpp_code(self, code):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_name = temp_file.name

            output_file = temp_file_name.replace('.cpp', '')
            compile_result = subprocess.run(
                ['g++', temp_file_name, '-o', output_file],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                return None, compile_result.stderr

            run_result = subprocess.run(
                [output_file],
                capture_output=True,
                text=True
            )
            return run_result.stdout, run_result.stderr
        except Exception as e:
            return None, str(e)

    # get AI feedback for user code
    def get_ai_feedback(self, language, code, objective, exerise_question):
        try:
            if not code:
                return "No code submitted for feedback. Please write some code before requesting feedback."

            prompt = f"""
                Analyze this {language} code submission:
                Lesson Objective: {objective}
                Exercise Question: {exerise_question}

                Code:
                ```
                {code}
                ```

                Provide:
                1. Code correctness assessment
                2. Best practices feedback
                3. Improvement suggestions
                """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a helpful assistant that check code and provide feedback."},
                          {"role": "user", "content": prompt}],
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Feedback generation error: {e}"