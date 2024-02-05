import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def main(value):
    load_dotenv()
    azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
    azure_oai_key = os.getenv("AZURE_OAI_KEY")
    azure_oai_model = os.getenv("AZURE_OAI_MODEL")

    client = AzureOpenAI(
        azure_endpoint = azure_oai_endpoint, 
        api_key=azure_oai_key,  
        api_version="2023-05-15"
    )

    response = client.chat.completions.create(
        model=azure_oai_model,
        temperature=0.3,
        max_tokens=120,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": value}
        ]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print(main("A DALL-E prompt for a mystic dog"))