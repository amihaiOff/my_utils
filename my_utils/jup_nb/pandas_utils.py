import pandas as pd

def vc(self, *args, **kwargs):
    return self.value_counts(*args, **kwargs)

def vcn(self, *args, **kwargs):
    return self.value_counts(normalize=True, *args, **kwargs)

def flatten_column_multi_index(self, sep: str = "_") -> pd.DataFrame:
    self.columns = [sep.join(col).strip(sep) for col in self.columns.values]

def merge_left_with_indicator(self, right, drop_ind_col=True, *args, **kwargs):
    merged = self.merge(right, how='left', indicator=True, *args, **kwargs)
    if drop_ind_col:
        print(merged['_merge'].value_counts())
        return merged.drop(columns='_merge')
    return merged

def df_min_max(self, col):
    return self[col].min(), self[col].max()

def series_min_max(self):
    return self.min(), self.max()

pd.Series.vc = vc
pd.Series.vcn = vcn
pd.Series.merge_left_with_indicator = merge_left_with_indicator
pd.Series.min_max = series_min_max

pd.DataFrame.merge_left_with_indicator = merge_left_with_indicator
pd.DataFrame.flatten_column_multi_index = flatten_column_multi_index
pd.DataFrame.min_max = df_min_max
pd.DataFrame.vc = vc
pd.DataFrame.vcn = vcn
