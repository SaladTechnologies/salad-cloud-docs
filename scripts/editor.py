from openai import OpenAI
import sys
import os
from datetime import datetime
import re
import time

filename = sys.argv[1]
with open(filename, "r") as file:
    file_content = file.read()


client = OpenAI()

start = time.time()
response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "system",
            "content": [
                {
                    "type": "input_text",
                    "text": "Task: review technical documentation for clarity, and return a version that has as few changes as possible, while improving clarity as much as possible. strive to maintain the tone and writing style of the original. Respond with only the new file content, in .mdx format. at the very end of the response include `>>>COMMIT`and a newline and a commit message"
                },

            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": file_content
                }
            ]
        },

    ],
    text={
        "format": {
            "type": "text"
        }
    },
    reasoning={},
    tools=[],
    temperature=1,
    max_output_tokens=8192,
    top_p=1,
    store=False
)
end = time.time()
print(f"OpenAI Response Time: {end - start} seconds")
input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
print(f"Input Tokens: {input_tokens} | Output Tokens: {output_tokens}")

new_content = response.output[0].content[0].text
new_content, commit_message = new_content.split(">>>COMMIT")
commit_message = commit_message.strip()
today = datetime.now().strftime("%B %d, %Y")
new_content = re.sub(r"_Last Updated: .*?_",
                     f"_Last Updated: {today}_", new_content)

# Save the response to the same file
with open(filename, "w") as file:
    file.write(new_content)

print("File updated successfully, running prettier...")
os.system(f"npx prettier --write {filename}")

# Commit the changes
os.system(f"git add {filename}")
os.system(f"git commit -m '{commit_message}'")
