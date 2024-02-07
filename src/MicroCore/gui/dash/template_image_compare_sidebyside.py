import base64,io,json
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import numpy as np
from PIL import Image
from ...core import MicroCore
from pydantic import parse_obj_as
from typing import Any
from io import BytesIO

def template_image_compare_sidebyside(micro_core: MicroCore,app):

    app_description = micro_core.name

    controls = [
    dcc.Upload(
        dbc.Card(
            [
                html.Div(
                    "Click to upload an Image", style={"marginBottom": "5px"}
                ),  # Adding some margin at the bottom
                html.Br(),  # Line break
                "Or Drag and Drop here",
            ],
            body=True,
            style={
                "textAlign": "center",
                "borderStyle": "dashed",
                "borderColor": "black",
                "background-color": "#f0f2f6",
                "color": "black",
                "padding": "20px",
            },
        ),
        id="img-upload",
        multiple=False,
    )
]


    app.layout = dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.Div(
                        [
                            html.H1("Image Comparison", className="header-title"),
                            html.P(f"{app_description}", className="header-subtitle"),
                        ],
                        className="header",
                        style={
                            "background-color": "#5c068c",
                            "color": "white",
                            "text-align": "center",
                            "padding": "20px",
                        },
                    ),
                    width=12,
                ),
                className="mb-4",
            ),
            html.Hr(),
            dbc.Row([dbc.Col(c) for c in controls]),
            html.Br(),
            dbc.Spinner(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    id="images-container",
                                    style={
                                        "whiteSpace": "nowrap",
                                        "text-align": "center",
                                        "margin": "0 auto",
                                    },
                                )
                            ],
                            width="auto",
                        )
                    ]
                )
            ),
        ],
        fluid=True,
        className="p-5",  # Add padding to the container
        style={"margin": "5%"},  # Add margin around the whole page
    )

    @app.callback(
        Output("images-container", "children"),
        [Input("img-upload", "contents")],
        [State("img-upload", "filename")],
    )
    def enhance_image(img_str, filename):
        if img_str is None:
            return dash.no_update

        # original_img = decode_b64str_to_image(img_str)
        data_start = img_str.find(',') + 1
        input_base64 = img_str[data_start:]

        input_type = micro_core.input_type
        output_type =micro_core.output_type

        input_dict = {"image_file": input_base64}
        input_obj = parse_obj_as(input_type, input_dict)
        
        output_obj = micro_core(input_obj)
        # Convert output to base64 string
        enhanced_image_bytes = BytesIO(output_obj.output_image_file.as_bytes())
        enhanced_image = Image.open(enhanced_image_bytes)

        sr_str = encode_image_to_b64str(enhanced_image)

        lr_img = html.Div(
            image_element(img_str, "Original Image"),
            style={"display": "inline-block", "margin": "10px"},
        )
        sr_img = html.Div(
            image_element(sr_str, "Enhanced Image"),
            style={"display": "inline-block", "margin": "10px"},
        )

        return lr_img, sr_img
    
    def predict(input: micro_core.input_type) -> Any:  # type: ignore
        """Executes this micro_core."""
        return micro_core(input).output_type
    
    return app



def decode_b64str_to_image(contents):
    content_type, content_string = contents.split(",")
    image_bytes = base64.b64decode(content_string)
    image = Image.open(io.BytesIO(image_bytes))
    return image


def encode_image_to_b64str(image, ext="jpeg"):
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=ext)  # Choose the appropriate format

    b64_string = base64.b64encode(image_bytes.getvalue()).decode("utf-8")
    return f"data:image/{ext};base64, {b64_string}"

def image_element(src, label):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Img(src=src, style={"width": "100%"}),
                    html.P(label, className="text-center mt-2"),  # Add label text
                ]
            ),
        ],
        style={"display": "inline-block", "margin": "10px"},
    )


def image_card(src, header=None):
    return dbc.Card(
        [
            dbc.CardHeader(header),
            dbc.CardBody(html.Img(src=src, style={"width": "100%"})),
        ]
    )