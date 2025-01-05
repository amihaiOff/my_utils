import pandas as pd

def vc(self, *args, **kwargs):
    return self.value_counts(*args, **kwargs)

def vcn(self, *args, **kwargs):
    return self.value_counts(normalize=True, *args, **kwargs)

def flatten_column_multi_index(self, sep: str = "_") -> pd.DataFrame:
    self.columns = [sep.join(col).strip(sep) for col in self.columns.values]

pd.DataFrame.vc = vc
pd.DataFrame.vcn = vcn
pd.DataFrame.flatten_column_multi_index = flatten_column_multi_index
