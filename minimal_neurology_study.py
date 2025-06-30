import gradio as gr
import json
import os
import numpy as np
import time
import random
import uuid


# Simple function to load problems (replaces the custom load_problems)
def load_problems_simple(problems_dir):
    """Simple version that loads HTML files from directory"""
    problems = []

    if not os.path.exists(problems_dir):
        print(f"Warning: Problems directory {problems_dir} does not exist")
        return problems

    problem_files = [f for f in os.listdir(problems_dir) if f.endswith('.html')]
    problem_files.sort()

    for idx, problem_file in enumerate(problem_files):
        try:
            problem_path = os.path.join(problems_dir, problem_file)

            with open(problem_path, 'r', encoding='utf-8') as f:
                problem_text = f.read()

            problems.append({
                "id": idx,
                "text": problem_text,
                "filename": problem_file
            })

        except Exception as e:
            print(f"Error loading problem file {problem_file}: {e}")

    return problems


# Simple chatbot function for Neura
def simple_chatbot(message, history):
    """Simple chatbot that gives basic responses for Neura"""

    if not message.strip():
        return history, ""

    # Simple AI response
    responses = [
        "I understand you're asking about this neurology case. Let me help you think through this systematically.",
        "Based on the symptoms you've described, what are the key clinical features you notice?",
        "Consider the anatomical location and potential differential diagnoses.",
        "What additional tests or examinations might be helpful here?",
        "Let's work through this step by step. What's your initial assessment?",
        "Think about the neuroanatomy involved here. What structures could be affected?",
        "What would be your next diagnostic step in this case?",
        "Consider both common and rare causes for these symptoms."
    ]

    response = random.choice(responses)

    # Convert to messages format for new Gradio
    new_history = history + [{"role": "user", "content": message}, {"role": "assistant", "content": response}]

    return new_history, ""


# Global variables
unique_key = ""
start_time = time.time()
current_case = 0
case_sequence = ["Neura", "Oxford", "Neura", "Oxford"]  # 4 cases alternating

# Load problems
problem_texts = load_problems_simple("./data/Cases/")
total_problems = len(problem_texts)
print(f"Total neurology cases loaded: {total_problems}")

if total_problems == 0:
    print("No cases found! Make sure your ./data/Cases/ directory exists and contains HTML files.")
    # Create sample cases for demo
    problem_texts = [
        {"id": 0,
         "text": "<p><strong>Case 1:</strong> A 65-year-old man presents with sudden onset of weakness on the right side of his body and difficulty speaking.</p>",
         "filename": "case1.html"},
        {"id": 1,
         "text": "<p><strong>Case 2:</strong> A 28-year-old woman complains of episodes of visual disturbances followed by severe headache.</p>",
         "filename": "case2.html"},
        {"id": 2,
         "text": "<p><strong>Case 3:</strong> A 45-year-old man has progressive memory loss and behavioral changes over the past year.</p>",
         "filename": "case3.html"},
        {"id": 3,
         "text": "<p><strong>Case 4:</strong> A 22-year-old student presents with tremor, muscle rigidity, and slow movements.</p>",
         "filename": "case4.html"},
    ]
    total_problems = len(problem_texts)

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
            "responses": responses
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Responses saved to {filepath}")
    except Exception as e:
        print(f"Error saving responses: {e}")


def create_interface():
    with gr.Blocks(title="Neurology Case Study", css="""
        .case-container { 
            background-color: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            margin: 10px 0; 
        }
        .condition-header {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }
    """) as demo:

        # State variables
        case_counter = gr.State(0)
        all_responses = gr.State({})

        # Welcome page
        with gr.Column() as welcome_page:
            gr.HTML("<h1>Welcome to the Neurology Case Study</h1>")
            gr.HTML(
                "<p>You will be presented with 4 neurology cases, alternating between Neura AI assistance and Oxford Handbook reference.</p>")
            gr.HTML(
                "<p>Please answer all sections (a, b, c) for each case and indicate whether the resource was helpful.</p>")
            start_button = gr.Button("Start Study", variant="primary")

        # Main study interface
        with gr.Column(visible=False) as study_interface:

            # Case display
            condition_display = gr.HTML()
            case_display = gr.HTML()

            # Neura interface (visible only for Neura cases)
            with gr.Column(visible=False) as neura_interface:
                gr.HTML("<h3>💬 Interact with Neura AI</h3>")
                chatbot = gr.Chatbot([], label="Neura AI Assistant", height=300, type='messages')
                with gr.Row():
                    msg = gr.Textbox(label="Ask Neura about this case", placeholder="Type your question here...",
                                     scale=4)
                    send_btn = gr.Button("Send", scale=1, variant="primary")
                clear_chat = gr.Button("Clear Chat", variant="secondary")

            # Answer sections (visible for both conditions)
            with gr.Column() as answer_sections:
                gr.HTML("<h3>📝 Your Answers</h3>")

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
                progress_display = gr.HTML()

        # Completion page
        with gr.Column(visible=False) as completion_page:
            gr.HTML("<h1>🎉 Study Complete!</h1>")
            gr.HTML("<p>Thank you for participating in the neurology case study. Your responses have been saved.</p>")
            restart_button = gr.Button("Start New Session", variant="secondary")

        # Chat state for Neura
        chat_history = gr.State([])

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
            case_data = problem_texts[case_num % len(problem_texts)]

            # Update displays
            condition_html = f'<div class="condition-header">Case {case_num + 1}/4 - {condition}</div>'
            case_html = f'<div class="case-container">{case_data["text"]}</div>'
            progress_html = f"<p>Progress: Case {case_num + 1} of 4</p>"

            # Show/hide Neura interface based on condition
            neura_visible = condition == "Neura"

            return (
                condition_html,  # condition_display
                case_html,  # case_display
                gr.update(visible=neura_visible),  # neura_interface
                "",  # answer_a
                None,  # helpful_a
                "",  # answer_b
                None,  # helpful_b
                "",  # answer_c
                None,  # helpful_c
                progress_html,  # progress_display
                [],  # chat_history (clear for new case)
                gr.update(value=[], visible=neura_visible),  # chatbot
                gr.update(),  # study_interface (no change)
                gr.update(),  # completion_page (no change)
            )

        def next_case_handler(case_num, responses_dict, ans_a, help_a, ans_b, help_b, ans_c, help_c):
            """Handle moving to next case"""
            # Save current responses
            condition = case_sequence[case_num]
            current_responses = {
                "answer_a": ans_a,
                "helpful_a": help_a,
                "answer_b": ans_b,
                "helpful_b": help_b,
                "answer_c": ans_c,
                "helpful_c": help_c
            }

            responses_dict[f"case_{case_num + 1}_{condition}"] = current_responses
            save_responses(case_num + 1, condition, current_responses)

            # Move to next case
            next_case_num = case_num + 1

            if next_case_num >= len(case_sequence):
                completion_results = show_completion()
                return completion_results + (next_case_num, responses_dict)
            else:
                case_results = load_case(next_case_num)
                return case_results + (next_case_num, responses_dict)

        def show_completion():
            """Show completion page"""
            return (
                gr.update(),  # condition_display (unchanged)
                gr.update(),  # case_display (unchanged)
                gr.update(visible=False),  # neura_interface
                gr.update(),  # answer_a (unchanged)
                gr.update(),  # helpful_a (unchanged)
                gr.update(),  # answer_b (unchanged)
                gr.update(),  # helpful_b (unchanged)
                gr.update(),  # answer_c (unchanged)
                gr.update(),  # helpful_c (unchanged)
                gr.update(),  # progress_display (unchanged)
                [],  # chat_history (clear)
                gr.update(value=[]),  # chatbot (clear)
                gr.update(visible=False),  # study_interface
                gr.update(visible=True),  # completion_page
            )

        def restart_study():
            """Restart the study"""
            return (
                gr.update(visible=True),  # welcome_page
                gr.update(visible=False),  # study_interface
                gr.update(visible=False),  # completion_page
                0,  # reset case_counter
                {}  # reset all_responses
            )

        def handle_chat(message, history):
            """Handle chat with Neura"""
            return simple_chatbot(message, history)

        def clear_chat_history():
            """Clear the chat history"""
            return [], []

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
                     progress_display, chat_history, chatbot, study_interface, completion_page, case_counter,
                     all_responses]
        )

        # Chat functionality
        msg.submit(handle_chat, inputs=[msg, chat_history], outputs=[chatbot, msg])
        msg.submit(lambda: gr.update(value=""), outputs=[msg])

        send_btn.click(handle_chat, inputs=[msg, chat_history], outputs=[chatbot, msg])
        send_btn.click(lambda: gr.update(value=""), outputs=[msg])

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
