import gradio as gr
import json
import os
import numpy as np
import time
import random
import uuid
from openai import OpenAI

# ============================================
# OPENAI API CONFIGURATION
# ============================================
# TODO: Replace "your-openai-api-key-here" with your actual OpenAI API key
OPENAI_API_KEY = "your-openai-api-key-here"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# Simple function to load problems (replaces the custom load_problems)
def load_problems_simple(problems_dir):
    """Simple version that loads HTML files from directory"""
    problems = []

    # Get absolute path for debugging
    abs_path = os.path.abspath(problems_dir)
    print(f"Looking for cases in: {abs_path}")

    if not os.path.exists(problems_dir):
        print(f"Warning: Problems directory {problems_dir} does not exist")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir('.')}")
        return problems

    # List all files in directory for debugging
    all_files = os.listdir(problems_dir)
    print(f"All files in {problems_dir}: {all_files}")

    problem_files = [f for f in all_files if f.endswith('.html')]
    print(f"HTML files found: {problem_files}")
    problem_files.sort()

    for idx, problem_file in enumerate(problem_files):
        try:
            problem_path = os.path.join(problems_dir, problem_file)
            print(f"Loading file: {problem_path}")

            with open(problem_path, 'r', encoding='utf-8') as f:
                problem_text = f.read()

            print(f"Successfully loaded {problem_file} - Length: {len(problem_text)} characters")

            problems.append({
                "id": idx,
                "text": problem_text,
                "filename": problem_file
            })

        except Exception as e:
            print(f"Error loading problem file {problem_file}: {e}")
            import traceback
            traceback.print_exc()

    print(f"Total problems loaded: {len(problems)}")
    return problems


# Neura AI chatbot function using OpenAI API
def neura_chatbot(message, history, current_case_text):
    """Neura chatbot that uses OpenAI GPT for intelligent responses"""

    if not message.strip():
        return history, ""

    try:
        # Build conversation history for OpenAI API
        messages = [
            {
                "role": "system",
                "content": f"""You are Neura, an expert neurology AI assistant helping medical students analyze neurological cases. Your role is to guide students through systematic thinking about neurological problems without giving direct answers.

CURRENT CASE BEING ANALYZED:
{current_case_text}

GUIDELINES:
- Ask probing questions to help students think through the case
- Suggest diagnostic approaches and reasoning frameworks
- Help them understand neuroanatomy and pathophysiology
- Guide them toward the correct answers rather than providing them directly
- Be encouraging and educational
- Keep responses focused and concise (2-3 sentences typically)
- Use medical terminology appropriately but explain complex concepts

Remember: You're helping them learn to think like neurologists, not just giving them answers."""
            }
        ]

        # Add previous conversation history
        for chat in history:
            messages.append({
                "role": chat["role"],
                "content": chat["content"]
            })

        # Add current user message
        messages.append({"role": "user", "content": message})

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",  # You can change to "gpt-3.5-turbo" for faster/cheaper responses
            messages=messages,
            max_tokens=300,
            temperature=0.7,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )

        ai_response = response.choices[0].message.content

        # Update conversation history
        new_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": ai_response}
        ]

        return new_history, ""

    except Exception as e:
        # Fallback error handling
        error_message = "I apologize, but I'm having trouble connecting right now. Please try again in a moment."
        print(f"OpenAI API Error: {str(e)}")  # Log error for debugging

        new_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": error_message}
        ]
        return new_history, ""


# Global variables
unique_key = ""
start_time = time.time()
current_case = 0

print("=== NEUROLOGY CASE STUDY - LOADING CASES ===")

# Load problems from both Cases_Easy and Cases_Hard directories
easy_paths = [
    "./data/Cases_Easy/",
    "data/Cases_Easy/",
    "./Cases_Easy/",
    "Cases_Easy/",
    "../data/Cases_Easy/",
    "../Cases_Easy/"
]

hard_paths = [
    "./data/Cases_Hard/",
    "data/Cases_Hard/",
    "./Cases_Hard/",
    "Cases_Hard/",
    "../data/Cases_Hard/",
    "../Cases_Hard/"
]

# Load easy cases
easy_cases = []
print("=== LOADING EASY CASES ===")
for path in easy_paths:
    print(f"Trying path: {path}")
    easy_cases = load_problems_simple(path)
    if easy_cases:
        print(f"✓ Successfully loaded {len(easy_cases)} easy cases from: {path}")
        break
    else:
        print(f"✗ No easy cases found in: {path}")

# Load hard cases
hard_cases = []
print("\n=== LOADING HARD CASES ===")
for path in hard_paths:
    print(f"Trying path: {path}")
    hard_cases = load_problems_simple(path)
    if hard_cases:
        print(f"✓ Successfully loaded {len(hard_cases)} hard cases from: {path}")
        break
    else:
        print(f"✗ No hard cases found in: {path}")

print(f"\n=== SUMMARY ===")
print(f"Easy cases loaded: {len(easy_cases)}")
print(f"Hard cases loaded: {len(hard_cases)}")

# Print details of loaded cases
if easy_cases:
    print("\nEasy cases details:")
    for i, case in enumerate(easy_cases):
        print(f"  {i}: {case['filename']} (length: {len(case['text'])} chars)")

if hard_cases:
    print("\nHard cases details:")
    for i, case in enumerate(hard_cases):
        print(f"  {i}: {case['filename']} (length: {len(case['text'])} chars)")

# ============================================
# CASE ASSIGNMENT CONFIGURATION (1-BASED)
# ============================================
# Specify which case numbers you want for each condition
# Case numbers are 1-based (1 = first case, 2 = second case, etc.)
# This is more intuitive than 0-based indexing!

CASE_ASSIGNMENT_1_BASED = {
    "neura_easy": 1,  # Use the 1st easy case for Neura (Easy)
    "oxford_easy": 2,  # Use the 2nd easy case for Oxford (Easy)
    "neura_hard": 1,  # Use the 1st hard case for Neura (Hard)
    "oxford_hard": 2,  # Use the 2nd hard case for Oxford (Hard)
}

# Convert to 0-based indexing for internal use
CASE_ASSIGNMENT = {
    "neura_easy": CASE_ASSIGNMENT_1_BASED["neura_easy"] - 1,
    "oxford_easy": CASE_ASSIGNMENT_1_BASED["oxford_easy"] - 1,
    "neura_hard": CASE_ASSIGNMENT_1_BASED["neura_hard"] - 1,
    "oxford_hard": CASE_ASSIGNMENT_1_BASED["oxford_hard"] - 1,
}


# Validation: Check if specified case numbers exist
def validate_case_assignment():
    """Validate that the specified case numbers exist"""
    errors = []

    if CASE_ASSIGNMENT_1_BASED["neura_easy"] > len(easy_cases) or CASE_ASSIGNMENT_1_BASED["neura_easy"] < 1:
        errors.append(
            f"Neura Easy case #{CASE_ASSIGNMENT_1_BASED['neura_easy']} doesn't exist. Available: 1 to {len(easy_cases)}")

    if CASE_ASSIGNMENT_1_BASED["oxford_easy"] > len(easy_cases) or CASE_ASSIGNMENT_1_BASED["oxford_easy"] < 1:
        errors.append(
            f"Oxford Easy case #{CASE_ASSIGNMENT_1_BASED['oxford_easy']} doesn't exist. Available: 1 to {len(easy_cases)}")

    if CASE_ASSIGNMENT_1_BASED["neura_hard"] > len(hard_cases) or CASE_ASSIGNMENT_1_BASED["neura_hard"] < 1:
        errors.append(
            f"Neura Hard case #{CASE_ASSIGNMENT_1_BASED['neura_hard']} doesn't exist. Available: 1 to {len(hard_cases)}")

    if CASE_ASSIGNMENT_1_BASED["oxford_hard"] > len(hard_cases) or CASE_ASSIGNMENT_1_BASED["oxford_hard"] < 1:
        errors.append(
            f"Oxford Hard case #{CASE_ASSIGNMENT_1_BASED['oxford_hard']} doesn't exist. Available: 1 to {len(hard_cases)}")

    if errors:
        print("\n❌ CASE ASSIGNMENT ERRORS:")
        for error in errors:
            print(f"  - {error}")
        print("\nAvailable cases (1-based numbering):")
        print("Easy cases:")
        for i, case in enumerate(easy_cases):
            print(f"  {i + 1}: {case['filename']}")
        print("Hard cases:")
        for i, case in enumerate(hard_cases):
            print(f"  {i + 1}: {case['filename']}")
        exit(1)
    else:
        print("✅ Case assignment validation passed!")


# Run validation only if we have cases loaded
if easy_cases and hard_cases:
    validate_case_assignment()
elif not easy_cases:
    print(f"\nERROR: No easy cases found!")
    print("Please ensure Cases_Easy directory exists with HTML files")
    exit(1)
elif not hard_cases:
    print(f"\nERROR: No hard cases found!")
    print("Please ensure Cases_Hard directory exists with HTML files")
    exit(1)

# Create the case sequence: Easy Neura, Easy Oxford, Hard Neura, Hard Oxford
case_sequence = ["Neura", "Oxford", "Neura", "Oxford"]
difficulty_sequence = ["Easy", "Easy", "Hard", "Hard"]

# Prepare cases using specified case numbers
problem_texts = [
    easy_cases[CASE_ASSIGNMENT["neura_easy"]],  # Case 1: Neura (Easy)
    easy_cases[CASE_ASSIGNMENT["oxford_easy"]],  # Case 2: Oxford (Easy)
    hard_cases[CASE_ASSIGNMENT["neura_hard"]],  # Case 3: Neura (Hard)
    hard_cases[CASE_ASSIGNMENT["oxford_hard"]],  # Case 4: Oxford (Hard)
]

total_problems = len(problem_texts)
print(f"\n=== CONFIGURED CASE ASSIGNMENT (1-BASED) ===")
print(f"Total cases prepared for study: {total_problems}")
print("Case distribution:")
print(
    f"  Case 1: Neura (Easy) - {easy_cases[CASE_ASSIGNMENT['neura_easy']]['filename']} (case #{CASE_ASSIGNMENT_1_BASED['neura_easy']})")
print(
    f"  Case 2: Oxford (Easy) - {easy_cases[CASE_ASSIGNMENT['oxford_easy']]['filename']} (case #{CASE_ASSIGNMENT_1_BASED['oxford_easy']})")
print(
    f"  Case 3: Neura (Hard) - {hard_cases[CASE_ASSIGNMENT['neura_hard']]['filename']} (case #{CASE_ASSIGNMENT_1_BASED['neura_hard']})")
print(
    f"  Case 4: Oxford (Hard) - {hard_cases[CASE_ASSIGNMENT['oxford_hard']]['filename']} (case #{CASE_ASSIGNMENT_1_BASED['oxford_hard']})")

# Show mapping for clarity
print(f"\n=== CASE FILE MAPPING ===")
print("Easy cases (1-based numbering):")
for i, case in enumerate(easy_cases):
    marker = " ← SELECTED" if (i == CASE_ASSIGNMENT["neura_easy"] or i == CASE_ASSIGNMENT["oxford_easy"]) else ""
    print(f"  {i + 1}: {case['filename']}{marker}")
print("Hard cases (1-based numbering):")
for i, case in enumerate(hard_cases):
    marker = " ← SELECTED" if (i == CASE_ASSIGNMENT["neura_hard"] or i == CASE_ASSIGNMENT["oxford_hard"]) else ""
    print(f"  {i + 1}: {case['filename']}{marker}")

# Create saving directory
main_saving_path = "./saved_data/"
if not os.path.exists(main_saving_path):
    os.makedirs(main_saving_path)


def save_responses(case_num, condition, responses):
    """Save user responses to file"""
    try:
        filename = f"case_{case_num}_{condition}_{int(time.time())}.json"
        filepath = os.path.join(main_saving_path, filename)

        data = {
            "case_number": case_num,
            "condition": condition,
            "timestamp": time.time(),
            "responses": responses,
            "case_assignment": CASE_ASSIGNMENT  # Save which specific cases were used
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Responses saved to {filepath}")
    except Exception as e:
        print(f"Error saving responses: {e}")


def create_interface():
    with gr.Blocks(title="Neurology Case Study") as demo:

        # State variables
        case_counter = gr.State(0)
        all_responses = gr.State({})
        chat_history = gr.State([])

        # Welcome page
        with gr.Column(visible=True) as welcome_page:
            gr.Markdown("# Welcome to the Neurology Case Study")
            gr.Markdown(
                "You will be presented with 4 neurology cases, alternating between Neura AI assistance and Oxford Handbook reference.")
            gr.Markdown(
                "Please answer all sections (a, b, c) for each case and indicate whether the resource was helpful.")

            # Show current case assignment (without difficulty levels)
            case_info = f"""
**Current Case Assignment:**
- **Case 1:** Neura - {easy_cases[CASE_ASSIGNMENT['neura_easy']]['filename']} (#{CASE_ASSIGNMENT_1_BASED['neura_easy']})
- **Case 2:** Oxford - {easy_cases[CASE_ASSIGNMENT['oxford_easy']]['filename']} (#{CASE_ASSIGNMENT_1_BASED['oxford_easy']})
- **Case 3:** Neura - {hard_cases[CASE_ASSIGNMENT['neura_hard']]['filename']} (#{CASE_ASSIGNMENT_1_BASED['neura_hard']})
- **Case 4:** Oxford - {hard_cases[CASE_ASSIGNMENT['oxford_hard']]['filename']} (#{CASE_ASSIGNMENT_1_BASED['oxford_hard']})
"""
            gr.Markdown(case_info)

            start_button = gr.Button("Start Study", variant="primary")

        # Main study interface
        with gr.Column(visible=False) as study_interface:

            # Case header and display
            condition_display = gr.Markdown()
            case_display = gr.Markdown()

            # Neura chat interface (visible only for Neura cases)
            with gr.Column(visible=False) as neura_interface:
                gr.Markdown("### 💬 Interact with Neura AI")
                chatbot = gr.Chatbot([], label="Neura AI Assistant", height=300, type='messages')
                with gr.Row():
                    msg = gr.Textbox(label="Ask Neura about this case", placeholder="Type your question here...",
                                     scale=4)
                    send_btn = gr.Button("Send", scale=1, variant="primary")
                clear_chat = gr.Button("Clear Chat", variant="secondary")

            # Answer sections
            gr.Markdown("### 📝 Your Answers")

            with gr.Tab("Answer for Section A"):
                answer_a = gr.Textbox(label="Section A Answer", lines=4,
                                      placeholder="Enter your answer for section a...")
                helpful_a = gr.Radio(["Yes", "No"], label="Was the resource helpful to answer this?", value=None)

            with gr.Tab("Answer for Section B"):
                answer_b = gr.Textbox(label="Section B Answer", lines=4,
                                      placeholder="Enter your answer for section b...")
                helpful_b = gr.Radio(["Yes", "No"], label="Was the resource helpful to answer this?", value=None)

            with gr.Tab("Answer for Section C"):
                answer_c = gr.Textbox(label="Section C Answer", lines=4,
                                      placeholder="Enter your answer for section c...")
                helpful_c = gr.Radio(["Yes", "No"], label="Was the resource helpful to answer this?", value=None)

            # Navigation
            with gr.Row():
                next_button = gr.Button("Next Case", variant="primary")
                progress_display = gr.Markdown()

        # Completion page
        with gr.Column(visible=False) as completion_page:
            gr.Markdown("# 🎉 Study Complete!")
            gr.Markdown("Thank you for participating in the neurology case study. Your responses have been saved.")

            # Show completed case summary (without difficulty levels)
            completion_summary = f"""
**Cases Completed:**
- **Case 1:** Neura - {easy_cases[CASE_ASSIGNMENT['neura_easy']]['filename']} (#{CASE_ASSIGNMENT_1_BASED['neura_easy']})
- **Case 2:** Oxford - {easy_cases[CASE_ASSIGNMENT['oxford_easy']]['filename']} (#{CASE_ASSIGNMENT_1_BASED['oxford_easy']})
- **Case 3:** Neura - {hard_cases[CASE_ASSIGNMENT['neura_hard']]['filename']} (#{CASE_ASSIGNMENT_1_BASED['neura_hard']})
- **Case 4:** Oxford - {hard_cases[CASE_ASSIGNMENT['oxford_hard']]['filename']} (#{CASE_ASSIGNMENT_1_BASED['oxford_hard']})
"""
            gr.Markdown(completion_summary)

            restart_button = gr.Button("Start New Session", variant="secondary")

        def start_study():
            """Initialize the study"""
            case_results = load_case(0)
            return (
                gr.update(visible=False),  # welcome_page
                gr.update(visible=True),  # study_interface
                0,  # case_counter
                {},  # all_responses
                case_results[0],  # condition_display
                case_results[1],  # case_display
                case_results[2],  # neura_interface
                case_results[3],  # answer_a
                case_results[4],  # helpful_a
                case_results[5],  # answer_b
                case_results[6],  # helpful_b
                case_results[7],  # answer_c
                case_results[8],  # helpful_c
                case_results[9],  # progress_display
                case_results[10],  # chat_history
                case_results[11]  # chatbot
            )

        def load_case(case_num):
            """Load a specific case"""
            if case_num >= len(case_sequence):
                return show_completion()

            condition = case_sequence[case_num]
            difficulty = difficulty_sequence[case_num]
            case_data = problem_texts[case_num]

            # Create readable text from HTML by stripping tags for Markdown display
            import re
            case_text = case_data["text"]
            # Convert HTML to markdown-friendly format
            case_text = re.sub(r'<p><strong>(.*?)</strong>(.*?)</p>', r'**\1**\2\n\n', case_text)
            case_text = re.sub(r'<p>(.*?)</p>', r'\1\n\n', case_text)
            case_text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', case_text)
            case_text = re.sub(r'<br/?>', '\n', case_text)

            # Update displays - remove difficulty from header
            condition_markdown = f"## Case {case_num + 1}/4 - {condition}\n*File: {case_data['filename']}*"
            case_markdown = f"### Case Details\n\n{case_text}"
            progress_markdown = f"**Progress: Case {case_num + 1} of 4** | **Condition: {condition}** | **File: {case_data['filename']}**"

            # Show/hide Neura interface based on condition
            neura_visible = condition == "Neura"

            return (
                condition_markdown,  # condition_display
                case_markdown,  # case_display
                gr.update(visible=neura_visible),  # neura_interface
                "",  # answer_a
                None,  # helpful_a
                "",  # answer_b
                None,  # helpful_b
                "",  # answer_c
                None,  # helpful_c
                progress_markdown,  # progress_display
                [],  # chat_history (clear for new case)
                gr.update(value=[], visible=neura_visible)  # chatbot
            )

        def next_case_handler(case_num, responses_dict, ans_a, help_a, ans_b, help_b, ans_c, help_c):
            """Handle moving to next case"""
            # Save current responses
            condition = case_sequence[case_num]
            difficulty = difficulty_sequence[case_num]
            current_responses = {
                "answer_a": ans_a,
                "helpful_a": help_a,
                "answer_b": ans_b,
                "helpful_b": help_b,
                "answer_c": ans_c,
                "helpful_c": help_c,
                "case_filename": problem_texts[case_num]['filename']  # Include filename in responses
            }

            responses_dict[f"case_{case_num + 1}_{condition}_{difficulty}"] = current_responses
            save_responses(case_num + 1, f"{condition}_{difficulty}", current_responses)

            # Move to next case
            next_case_num = case_num + 1

            if next_case_num >= len(case_sequence):
                # Study complete - return all required outputs with proper values
                return (
                    gr.update(),  # condition_display - no change
                    gr.update(),  # case_display - no change
                    gr.update(),  # neura_interface - no change
                    gr.update(),  # answer_a - no change
                    gr.update(),  # helpful_a - no change
                    gr.update(),  # answer_b - no change
                    gr.update(),  # helpful_b - no change
                    gr.update(),  # answer_c - no change
                    gr.update(),  # helpful_c - no change
                    gr.update(),  # progress_display - no change
                    [],  # chat_history - clear
                    gr.update(value=[]),  # chatbot - clear
                    next_case_num,  # case_counter
                    responses_dict  # all_responses
                )
            else:
                case_results = load_case(next_case_num)
                return (
                    case_results[0],  # condition_display
                    case_results[1],  # case_display
                    case_results[2],  # neura_interface
                    case_results[3],  # answer_a
                    case_results[4],  # helpful_a
                    case_results[5],  # answer_b
                    case_results[6],  # helpful_b
                    case_results[7],  # answer_c
                    case_results[8],  # helpful_c
                    case_results[9],  # progress_display
                    case_results[10],  # chat_history
                    case_results[11],  # chatbot
                    next_case_num,
                    responses_dict
                )

        def handle_chat(message, history):
            """Handle chat with Neura AI"""
            # Get current case text for context
            current_case_num = case_counter.value if hasattr(case_counter, 'value') else 0
            if current_case_num < len(problem_texts):
                current_case_text = problem_texts[current_case_num]["text"]
            else:
                current_case_text = "No case currently loaded."

            return neura_chatbot(message, history, current_case_text)

        def clear_chat_history():
            """Clear the chat history"""
            return [], []

        def restart_study():
            """Restart the study"""
            return (
                gr.update(visible=True),  # welcome_page
                gr.update(visible=False),  # study_interface
                gr.update(visible=False),  # completion_page
                0,  # reset case_counter
                {}  # reset all_responses
            )

        # Event handlers
        start_button.click(
            start_study,
            outputs=[welcome_page, study_interface, case_counter, all_responses,
                     condition_display, case_display, neura_interface,
                     answer_a, helpful_a, answer_b, helpful_b, answer_c, helpful_c,
                     progress_display, chat_history, chatbot]
        )

        next_button.click(
            next_case_handler,
            inputs=[case_counter, all_responses, answer_a, helpful_a, answer_b, helpful_b, answer_c, helpful_c],
            outputs=[condition_display, case_display, neura_interface,
                     answer_a, helpful_a, answer_b, helpful_b, answer_c, helpful_c,
                     progress_display, chat_history, chatbot, case_counter, all_responses]
        )

        # Handle completion transition - separate event handlers for showing completion page
        next_button.click(
            lambda case_num: gr.update(visible=False) if case_num >= len(case_sequence) else gr.update(),
            inputs=[case_counter],
            outputs=[study_interface]
        )

        next_button.click(
            lambda case_num: gr.update(visible=True) if case_num >= len(case_sequence) else gr.update(),
            inputs=[case_counter],
            outputs=[completion_page]
        )

        # Chat functionality
        msg.submit(handle_chat, inputs=[msg, chat_history], outputs=[chatbot, msg])
        msg.submit(lambda: "", outputs=[msg])

        send_btn.click(handle_chat, inputs=[msg, chat_history], outputs=[chatbot, msg])
        send_btn.click(lambda: "", outputs=[msg])

        clear_chat.click(clear_chat_history, outputs=[chatbot, chat_history])

        restart_button.click(
            restart_study,
            outputs=[welcome_page, study_interface, completion_page, case_counter, all_responses]
        )

    return demo


# Create and launch the demo
if __name__ == "__main__":
    try:
        demo = create_interface()
        print("Launching Neurology Case Study interface...")
        demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
    except Exception as e:
        print(f"Error launching demo: {e}")
        import traceback

        traceback.print_exc()
