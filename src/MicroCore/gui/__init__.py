from .dash import get_dash_template_type, gui_factory

def launch_dash_ui(micro_core: str, template ="image_compare_sidebyside" , port: int = 8501) -> None:

    dash_template_type = get_dash_template_type(template)

    app = gui_factory(micro_core, dash_template_type)
    app.run_server(debug=False, port=port)