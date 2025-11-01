from functions.call_function import call_function
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [--verbose] <your prompt here>")
        sys.exit(1)
    
    arguments = sys.argv[1:]
    verbose = False
    
    # Check for verbose flag
    if "--verbose" in arguments:
        verbose = True
        arguments.remove("--verbose")
    
    user_prompt = " ".join(arguments)
    
    MAX_ITERATIONS = 20
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]   

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    
    client = genai.Client(api_key=api_key)

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    model_name="gemini-2.5-flash"

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_run_python_file,
            schema_get_file_content,
            schema_write_file
        ]   
    )

    #response = client.models.generate_content(model='gemini-2.5-flash', contents=messages)

    for i in range(MAX_ITERATIONS):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt
                ),
            )

            # Add all candidate content to messages
            for candidate in response.candidates:
                for c in candidate.content:
                    if isinstance(c, types.Content):
                        messages.append(c)

            # Execute any function calls
            has_function_call = False
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "function_call") and part.function_call is not None:
                        has_function_call = True
                        function_call_result = call_function(part.function_call, verbose=verbose)

                        func_result_dict = function_call_result.parts[0].function_response.response
                        result_str = func_result_dict.get("result", func_result_dict)
                        if isinstance(result_str, (dict, list)):
                            result_str = str(result_str)

                        messages.append(types.Content(
                            role="user",
                            parts=[types.Part.from_function_response(
                                name=part.function_call.name,
                                response={"result": result_str}
                            )]
                        ))

                        if verbose:
                            print(f"-> {function_call_result.parts[0].function_response.response}")

            # Check for final text
            final_text_found = False
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"Final response:\n{part.text}")
                        final_text_found = True
                        break
                if final_text_found:
                    break

            if final_text_found:
                break

            if not has_function_call:
                print("No further actions produced.")
                break

        except Exception as e:
            print(f"Error during iteration {i+1}: {e}")
            break


if __name__ == "__main__":
    main()
