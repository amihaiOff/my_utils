from my_utils.utils import *
from my_utils.readers import *

tools_info = {
    "DictViewer": "Display dict values according to dropdown of keys.",
    "GBViewer": "Group-by viewer - nice display for pandas GroupBy objects in jupyter notebook.",
    "OutputWrapper": "Useful for converting dataframes to ipywidgets that can be displayed inside a VBox, etc.",
    "subplots": "Create a subplot figure from a list of figures with two columns.",
    "sub_dfs": "Stack pandas dataframes side by side with as many rows as needed based on len(dfs).",
    "add_diagonal": "Add diagonal line (x = y) to a plotly figure.",
    "square_fig": "Make a plotly figure square to have the same scale on both axes.",
    "col_intersection": "Return a series with the intersection of two series.",
    "df_sneak_peak": "Display a sneak peak of a dataframe.",
    "load_file_to_dict": "Loads a JSON or YAML file (local or S3) into a dictionary.",
    "pretty_print_dict_with_filter": "Pretty prints a dictionary in a Jupyter Lab notebook with optional key filtering."
}

def get_tools_info():
    info_lines = [f"{tool} - {desc}" for tool, desc in tools_info.items()]
    return "\n".join(info_lines)

def help():
    print(get_tools_info())
