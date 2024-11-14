
import openai


# optional; defaults to `os.environ['OPENAI_API_KEY']`
openai.api_key = 'sk-rc-eTOQ3hihhmJZj-ovlJDRpA'

# all client options can be configured just like the `OpenAI` instantiation counterpart
openai.base_url = "http://148.187.108.173:8080"
openai.default_headers = {"x-foo": "true"}

completion = openai.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.choices[0].message.content)