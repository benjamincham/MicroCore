import base64
import io
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import numpy as np
from PIL import Image
import dash_mantine_components as dmc
from dash_extensions import BeforeAfter


def template_image_compare_slider(micro_core,app):

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
                            html.P("Enhance Your Images", className="header-subtitle"),
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

        original_img = decode_b64str_to_image(img_str)
        original_img_array = np.array(original_img)
        enhanced_image = Image.fromarray(
            LLE_model.predict(original_img_array)[0]["enhanced"]
        )
        sr_str = encode_image_to_b64str(enhanced_image)

        return make_before_after(sr_str, img_str)
    
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

def make_before_after(after, before):
    return html.Div(
        [
            dmc.Space(h=40),
            dmc.Group(
                [
                    dmc.Text("Original Image"),
                    dmc.Space(w=300),  # Add space to separate the texts
                    dmc.Text("Enhanced Image"),
                ],
                position="start",  # Adjust positioning to start
                style={
                    "maxWidth": 800,
                    "text-align": "center",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",  # Center horizontally
                    "margin": "0 auto",  # Center using auto margins
                },
            ),
            BeforeAfter(before={"src": before}, after={"src": after}),
        ],
    )

def image_element(src_before, src_after):
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    make_before_after(src_after, src_before),
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