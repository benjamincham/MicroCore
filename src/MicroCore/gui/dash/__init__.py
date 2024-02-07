from enum import Enum,auto
from .template_image_compare_slider import template_image_compare_slider
from .template_image_compare_sidebyside import template_image_compare_sidebyside
from ...core import MicroCore
import dash

class dash_template(Enum):
    image_compare_sidebyside = auto()
    image_compare_slider = auto()

def get_dash_template_type(template_option):
    if isinstance(template_option, str):
        try:
            return dash_template[template_option.lower()]  # Convert the string to enum member
        except KeyError:
            raise ValueError(f"Invalid _template: {template_option}")
    elif isinstance(template_option, dash_template):
        return template_option  # Return the enum member directly
    else:
        raise TypeError("Input value must be a string or a dash_template enum member")

def gui_factory(micro_core:MicroCore, dash_template_type):

    app = init_dash_app(micro_core)
    dash_template_function = dash_templates[dash_template_type]
    dash_template_function(micro_core,app)
    
    return app

def init_dash_app(micro_core: MicroCore):
    service_name = micro_core.name
    dash_app = dash.Dash(service_name)
    
    return dash_app

dash_templates = {
    dash_template.image_compare_sidebyside : template_image_compare_sidebyside,
    dash_template.image_compare_slider : template_image_compare_slider,
}