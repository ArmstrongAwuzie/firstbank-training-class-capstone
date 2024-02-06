from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import time

app = Dash(__name__)

# Function to generate image URL
def generate_image_from_prompt(prompt):
    try:
        load_dotenv()
        api_base = os.getenv("AZURE_OAI_ENDPOINT")
        api_key = os.getenv("AZURE_OAI_KEY")
        api_version = "2023-06-01-preview"

        url = f"{api_base}openai/images/generations:submit?api-version={api_version}"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        body = {"prompt": prompt, "n": 2, "size": "512x512"}
        submission = requests.post(url, headers=headers, json=body)

        operation_location = submission.headers["Operation-Location"]

        status = ""
        while status != "succeeded":
            time.sleep(3)
            response = requests.get(operation_location, headers=headers)
            status = response.json()["status"]

        image_url = response.json()["result"]["data"][0]["url"]
        return image_url

    except Exception as ex:
        print(ex)
        return None  # Indicate error by returning None

# Function to generate and refine prompt
def generate_prompt(value):
    load_dotenv()
    azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
    azure_oai_key = os.getenv("AZURE_OAI_KEY")
    azure_oai_model = os.getenv("AZURE_OAI_MODEL")

    client = AzureOpenAI(
        azure_endpoint=azure_oai_endpoint,
        api_key=azure_oai_key,
        api_version="2023-05-15",
    )

    response = client.chat.completions.create(
        model=azure_oai_model,
        temperature=0.7,
        max_tokens=120,
        messages=[
            {"role": "system", "content": "You are an expert at generating Dall-E prompts"},
            {"role": "user", "content": value},
        ],
    )

    refined_prompt = response.choices[0].message.content
    return refined_prompt
app.layout = html.Div(
    style={"backgroundColor": "#90EE90"},  # Set background color
    children=[
        html.H1(
            children="Almighty GroupB Image Generation App",
            style={"textAlign": "center", "margin-bottom": "20px"},
        ),
        html.Div(
            style={"display": "flex", "justify-content": "center", "align-items": "center"}
        ),
        dcc.Input(
            id="basic-prompt-input",
            type="text",
            placeholder="Type your basic prompt here",
            size="100",
            style={"margin-left": "20px", "margin-right": "20px"},
        ),
        html.Button(
            "Submit",
            id="submit-button",
            n_clicks=0,
            style={
                "backgroundColor": "#4CAF50",  # Set button color
                "color": "white",
                "padding": "10px 20px",
                "border": "none",
                "cursor": "pointer",
                "margin-left": "20px",
            },
        ),
        # Added the missing loading indicator element
        dcc.Loading(
            id="loading-output",
            type="default",
            children=[
                html.Div(id='Loading-indicator',children='', style={'font-weight':'bold','margin-bottom':'10px'}),
                html.Div(id="image-generation-output", children="Generated image will appear here.", style={"text-align": "center"}),
                html.Img(id="generated-image", style={"display": "block", "margin": "auto"}),
            ]
        )
    ],
)

# Callback for generating and displaying image
@callback(
    Output("generated-image", "src"),
    Output("Loading-indicator", "children"),
    Output("image-generation-output", "children"),
    Input("submit-button", "n_clicks"),
    State("basic-prompt-input", "value"),
)
def generate_image_and_update_ui(n_clicks, value):
    if n_clicks == 0:
        return None, None, None  # No clicks yet, do nothing

    # Show loading indicator
    loading_text = html.Div(
        [dcc.Loading(type="circle", color="#4CAF50"), html.H3("Generating image...")],
        style={"text-align": "center"},
    )

    # Generate refined prompt
    refined_prompt = generate_prompt(value)

    # Generate image
    image_url = generate_image_from_prompt(refined_prompt)

    # Update output
    if image_url:
        return image_url, None, f"Refined Prompt: {refined_prompt}"  # Image generated
    else:
        return None, None, "Error generating image. Please try again."  # Error

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
