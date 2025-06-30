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

# Simple chatbot function (replaces model_generate)
def simple_chatbot(message, history, model_state):
    """Simple chatbot that gives basic responses"""
    
    # Add user message to history
    history.append([message, None])
    
    # Simple AI response
    responses = [
        "I understand you're asking about this neurology case. Let me help you think through this systematically.",
        "Based on the symptoms you've described, what are the key clinical features you notice?",
        "Consider the anatomical location and potential differential diagnoses.",
        "What additional tests or examinations might be helpful here?",
        "Let's work through this step by step. What's your initial assessment?"
    ]
    
    response = random.choice(responses)
    history[-1][1] = response
    
    return history, history, ""

# Global variables
unique_key = ""
start_time = time.time()
case_difficulties = ["Easy", "Hard"]
study_conditions = ["Neura", "Oxford Handbook"]

# Load problems
problem_texts = load_problems_simple("./data/Cases/")
total_problems = len(problem_texts)
print(f"Total neurology cases loaded: {total_problems}")

if total_problems == 0:
    print("No cases found! Make sure your ./data/Cases/ directory exists and contains HTML files.")
    exit()

# Create simple problem distribution
half_point = max(1, total_problems // 2)
problems_per_difficulty = {
    "Easy": list(range(min(half_point, total_problems))),
    "Hard": list(range(half_point, total_problems)) if half_point < total_problems else [0]
}

# Simple demo with just one condition
main_saving_path = "./saved_data/"
if not os.path.exists(main_saving_path):
    os.makedirs(main_saving_path)

def create_simple_interface():
    with gr.Blocks(title="Neurology Case Study") as demo:
        
        # Welcome page
        with gr.Column() as welcome_page:
            gr.HTML("<h2>Welcome to the Neurology Case Study</h2>")
            gr.HTML("<p>This is a test version. Click Start to begin.</p>")
            start_button = gr.Button("Start Study")
        
        # Main interface
        with gr.Column(visible=False) as main_interface:
            # Show a sample case
            if problem_texts:
                case_text = problem_texts[0]["text"]
                gr.HTML(f"<h3>Sample Neurology Case</h3>")
                gr.HTML(f'<div style="background-color: #f0f0f0; padding: 10px;">{case_text}</div>')
            
            # Simple chatbot interface
            chatbot = gr.Chatbot([], label="Neura AI Assistant")
            msg = gr.Textbox(label="Your message", placeholder="Ask about the case...")
            clear = gr.Button("Clear")
            
            # Simple state management
            chat_history = gr.State([])
            
            def respond(message, history):
                return simple_chatbot(message, history, "neura")
            
            msg.submit(respond, [msg, chat_history], [chatbot, chat_history])
            clear.click(lambda: ([], []), outputs=[chatbot, chat_history])
        
        # Start button functionality
        def show_main():
            return gr.update(visible=False), gr.update(visible=True)
        
        start_button.click(show_main, outputs=[welcome_page, main_interface])
    
    return demo

# Create and launch the demo
if __name__ == "__main__":
    try:
        demo = create_simple_interface()
        print("Launching Gradio interface...")
        demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
    except Exception as e:
        print(f"Error launching demo: {e}")
        import traceback
        traceback.print_exc()