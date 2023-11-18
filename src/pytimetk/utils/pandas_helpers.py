import pandas as pd
import pandas_flavor as pf
import polars as pl

from pytimetk.utils.checks import check_dataframe_or_groupby


@pf.register_dataframe_method
def glimpse(
    data: pd.DataFrame, 
    max_width: int = 76,
    engine: str = 'pandas'
) -> None:
    '''
    Takes a pandas DataFrame and prints a summary of its dimensions, column 
    names, data types, and the first few values of each column.
    
    Parameters
    ----------
    data : pd.DataFrame
        The `data` parameter is a pandas DataFrame that contains the data you 
        want to glimpse at. It is the main input to the `glimpse` function.
    max_width : int, optional
        The `max_width` parameter is an optional parameter that specifies the 
        maximum width of each line when printing the glimpse of the DataFrame. 
        If not provided, the default value is set to 76.
    engine : str, optional
        The `engine` parameter is used to specify the engine to use for 
        generating a glimpse. It can be either "pandas" or "polars". 
        
        - The default value is "pandas".
        
        - When "polars", the function will internally use the `polars` library 
          for generating the glimpse. 
    
    Examples
    --------
    ```{python}
    import pytimetk as tk
    import pandas as pd
    
    df = tk.load_dataset('walmart_sales_weekly', parse_dates=['Date'])
    
    df.glimpse()
    ```
    
    '''

    # Common checks 
    check_dataframe_or_groupby(data)
    
    if engine == 'pandas':
        return _glimpse_pandas(data, max_width)
    elif engine == 'polars':
        return _glimpse_polars(data, max_width)
    else:
        raise ValueError("Invalid engine. Use 'pandas' or 'polars'.")

def _glimpse_pandas(
    data: pd.DataFrame, max_width: int = 76
) -> None:
    df = data.copy()

    # find the max string lengths of the column names and dtypes for formatting
    _max_len = len(max(df.columns, key=len))
    _max_dtype_label_len = 15

    # print the dimensions of the dataframe
    print(f"{type(df)}: {df.shape[0]} rows of {df.shape[1]} columns")

    # print the name, dtype and first few values of each column
    for _column in df:
        
        _col_vals = df[_column].head(max_width).to_list()
        _col_type = str(df[_column].dtype)
        
        output_col = f"{_column}:".ljust(_max_len+1, ' ')
        output_dtype = f" {_col_type}".ljust(_max_dtype_label_len+3, ' ')

        output_combined = f"{output_col} {output_dtype} {_col_vals}"
    
        # trim the output if too long
        if len(output_combined) > max_width:
            output_combined = output_combined[0:(max_width-4)] + " ..."
        
        print(output_combined)
    
    return None

def _glimpse_polars(df, max_width=76):
    
    _max_len = len(max(df.columns, key=len))
    
    final_df = (
        ((pl.DataFrame(df.columns.to_list()).rename({'column_0': ''}))
    .hstack(pl.DataFrame((pd.Series(df.dtypes.to_list())).astype('string').to_frame()))
    .hstack(pl.DataFrame(df).select(pl.all().head(15).implode()).transpose())
    ).to_pandas()
    ).rename(columns={'0': ' ', 'column_0': '  '})
    
    final_df['  '] = final_df['  '].astype(str).str.slice(stop=(max_width-_max_len-15)).fillna('') + '...'

    def make_lalign_formatter(df, cols=None):
        if cols is None:
            cols = df.columns[df.dtypes == 'object'] 
        return {col: f'{{:<{df[col].str.len().max()}s}}'.format for col in cols}

    print(f"{type(df)}: {len(df)} rows of {len(df.columns)} columns", end="")
    print(final_df.to_string(formatters=make_lalign_formatter(final_df), index=False, justify='left'))
    
    return None

@pf.register_dataframe_method
def flatten_multiindex_column_names(data: pd.DataFrame, sep = '_') -> pd.DataFrame:
    '''Takes a DataFrame as input and flattens the column
    names if they are in a multi-index format.
    
    Parameters
    ----------
    data : pd.DataFrame
        The parameter "data" is expected to be a pandas DataFrame object.
    
    Returns
    -------
    pd.DataFrame
        The input data with flattened multiindex column names.
        
    Examples
    --------
    ```{python}
    import pandas as pd
    import pytimetk as tk
    
    date_rng = pd.date_range(start='2023-01-01', end='2023-01-03', freq='D')

    data = {
        'date': date_rng,
        ('values', 'value1'): [1, 4, 7],
        ('values', 'value2'): [2, 5, 8],
        ('metrics', 'metric1'): [3, 6, 9],
        ('metrics', 'metric2'): [3, 6, 9],
    }
    df = pd.DataFrame(data)
    
    df.flatten_multiindex_column_names()
    
    ```
    '''
    # Common checks
    check_dataframe_or_groupby(data)
    
    # Check if data is a Pandas MultiIndex
    data.columns = [sep.join(col).strip() if isinstance(col, tuple) else col for col in data.columns.values]
                
    return data


def pd_quantile(**kwargs):
    """Generates configuration for the rolling quantile function in Polars."""
    # Designate this function as a 'configurable' type - this helps 'augment_expanding' recognize and process it appropriately
    func_type = 'configurable'
    # Specify the Polars rolling function to be called, `rolling_<func_name>`
    func_name = 'quantile'
    # Initial parameters for Polars' rolling quantile function
    # Many will be updated by **kwargs or inferred externally based on the dataframe
    default_kwargs = {
        'q' : None,
        'interpolation' : 'midpoint',
        'numeric_only' : False, 
    }
    
    return func_type, func_name, default_kwargs, kwargs


def update_dict(d1, d2):
    """
    Update values in dictionary `d1` based on matching keys from dictionary `d2`.
    
    This function will only update the values of existing keys in `d1`.
    New keys present in `d2` but not in `d1` will be ignored. 
    """
    for key in d1.keys():
        if key in d2:
            d1[key] = d2[key]
    return d1

