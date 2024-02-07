from enum import Enum,auto

class communication_type(Enum):
    KAFKA = auto()
    FASTAPI = auto()

def get_communication_type(communication_type_option):
    if isinstance(communication_type_option, str):
        try:
            return communication_type[communication_type_option.upper()]  # Convert the string to enum member
        except KeyError:
            raise ValueError(f"Invalid _template: {communication_type_option}")
    elif isinstance(communication_type_option, communication_type):
        return communication_type_option  # Return the enum member directly
    else:
        raise TypeError("Input value must be a string or a dash_template enum member")
