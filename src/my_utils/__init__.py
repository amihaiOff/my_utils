from my_utils.jup_nb.nb_utils import *
from my_utils.utils import *
from my_utils.readers import *

from IPython.display import Markdown, display

import my_utils.jup_nb.pandas_utils  # sets pandas DataFrame methods

try:
    from icecream import install
    install()
except ImportError:
    print('Icecream not installed')

def doc():
    """
    Make sure the there is no newline after the first triple quotes,
    and that the following lines are flush with the left margin.
    """
    docstring = """ # MyPackage Documentation
Welcome to the **MyUtils** guide! Here's what you can find in this package:
## Readers
* **[load\save]_[json\yaml]**: Read and save JSON and YAML files, doesn't support cloud
* **pretty_print_dict_with_filter**: - Pretty print a dictionary with a dict key filter. Supports S3 paths.

## Utils
* **pd_float_format**: Change how numbers are displayed in a DataFrame
* **pd_df_num_rows**: Set the number of rows to display in a DataFrame
* **col_by_kw**: Return list of columns in df that contain a keyword
* **grouped**: Return an iterator that produces n-tuples by grouping elements from the input iterable
* **DictViewer:** - Display dict values according to dropdown of keys. Useful for dicts of dataframes
* **GBViewer:** - Group-by viewer - nice display for pandas GroupBy objects in jupyter notebook.
* **OutputWrapper:** - Useful for converting dataframes to ipywidgets that can be displayed inside a VBox, etc.
* **catboost_feature_importance**: Return a DataFrame with feature importance from a CatBoost model

## DataFrame
* **col_intersect**: Return the intersection of two cols
* **sub_dfs**: Stack pandas dataframes side by side with as many rows as needed based on
* **subplots**: Create a subplot figure from a list of figures with two columns

## DataFrame\Series custom methods
* **vc**: value_counts alias
* **vcn**: value_counts with normalize=True
* **flatten_column_multi_index**: Flatten column multi-index
* **merge_left_with_indicator**: Merge two dataframes with a left join and indicator column
* **df_min_max**: Return the min and max values of a column in a DataFrame

#### main_ext.py - Jupyter Notebook Extension

"""
    return display(Markdown(docstring))
