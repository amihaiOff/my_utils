from typing import Optional, Union

import pandas as pd


def safe_divide(a: Union[int, float],
                b: Union[int,float],
                div_zero: str = 'zero') -> Optional[float]:
    """
    Divide a by b and deal with 0 divisor according to div_zero
    :param a:
    :param b:
    :param div_zero: options - 'zero', 'none', 'error.
                    if zero - return zero
                    if none - return None
                    if error - raise ZeroDivisionError
    :return:
    """
    if b == 0:
        if div_zero == 'zero':
            return 0.0
        elif div_zero == 'none':
            return None
        elif div_zero == 'error':
            raise ZeroDivisionError
        else:
            raise ValueError(f'Unknown value for div_zero: {div_zero}')
    else:
        return a / b


def pd_float_format(digits=-1):
    """
    Change how numbers are displayed in a DataFrame:
        2.4321564e3 => 2432.1564

    :param digits: if >= 0, use a fixed number of digits,
                   if -1, use default python format,
                   if None, use pandas default format
    """
    if digits is None:
        fmt = None
    elif digits < 0:
        fmt = '{:}'.format
    else:
        fmt = ('{:,.%df}' % digits).format
    pd.options.display.float_format = fmt


def pd_df_num_rows(num_rows: int = 60):
    """
    Set the number of rows to display in a DataFrame.
    """
    pd.options.display.max_rows = num_rows


def col_by_kw(df: pd.DataFrame, kw: str):
    """
    Return list of columns in df that contain kw
    """
    return [col for col in df.columns if kw in col]
