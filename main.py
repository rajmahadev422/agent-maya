
from ollama import chat
from utils.utils import save_messages
from utils.config import PROJECT_DIR
from tool_file.all_tools import available_functions, tools

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
BOLD = "\033[1m"

messages = [{
    "role": "system",
    "content": (
        "You are Maya, a local AI assistant. "
        "Use available tools when needed. "
        "Never claim execution succeeded without checking the result. "
        "Remember the conversation context when answering follow-up questions. "
        f"Current directory and Project directory: {PROJECT_DIR}"
    )
}]
print(f"{BOLD}Project Directory: {RESET}: {PROJECT_DIR}")

while True:
    
    user_input = input(f"\n{GREEN}You: {RESET}")

    if not user_input:
        print(f"{CYAN}MAYA:{RESET} I could not understand. Please repeat.")
        continue

    if user_input.lower() in {"exit", "quit", "exit.", "quit."}:
        save_messages(messages=messages)
        print(f"{CYAN}MAYA:{RESET} Chat history saved. Goodbye!")
        break

    messages.append({"role": "user", "content": user_input})

    for _ in range(5):
        print(f"\n{CYAN}MAYA:{RESET} ", end="", flush=True)

        response = chat(
            model="qwen3:1.7b",
            messages=messages,
            tools=tools,
            stream=True
        )

        full_content = ""
        tool_calls = []

        for chunk in response:
            message = chunk["message"]

            if message.get("content"):
                content = message["content"]
                full_content += content
                print(content, end="", flush=True)

            if message.get("tool_calls"):
                tool_calls.extend(message["tool_calls"])

        print()

        # Final assistant message
        assistant_message = {
            "role": "assistant",
            "content": full_content,
        }

        if tool_calls:
            assistant_message["tool_calls"] = tool_calls

        messages.append(assistant_message)

        if not tool_calls:
            break

        for call in tool_calls:
            fn_name = call.function.name
            fn = available_functions.get(fn_name)

            print(f"\n{YELLOW}Function Call: {RESET}{fn_name}")

            if fn is None:
                result = "Error: Unknown tool."
            else:
                try:
                    result = fn(**call.function.arguments)
                except Exception as exc:
                    result = f"Tool failed: {exc}"

            messages.append({
                "role": "tool",
                "tool_name": fn_name,
                "content": str(result),
            })

    else:
        print(f"\n{CYAN}MAYA:{RESET} Tool-call limit reached.")