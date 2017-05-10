# -*- coding: utf-8 -*-
import copy

import numpy as np
import pandas as pd

from ..elements import *

__all__ = [
    'dataframe_to_table',
]


def dataframe_to_table(df, title=None, name=None, name_scope=None):
    """Create a report Table from pandas DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe object.

    title : str
        Optional title of the table.

    name, name_scope : str
        Name and name scope of the table.

    Returns
    -------
    Table
        Table report object.
    """
    def to_str(v):
        return (
            '' if v is None else (
                '%.7g' % v if isinstance(v, (float, np.float)) else str(v)
            )
        )

    # inspect the index names
    if isinstance(df.index, pd.MultiIndex):
        index_names = df.index.names
    else:
        index_names = [df.index.name]

    # inspect the column names
    column_names = df.columns

    # compose the header rows
    headers = [
        TableRow(
            [TableCell(Text(''), colspan=len(index_names))] +
            [TableCell(Text(to_str(c))) for c in column_names]
        )
    ]
    if any(n is not None for n in index_names):
        headers.append(TableRow(
            [TableCell(Text(to_str(n))) for n in index_names] +
            [TableCell(Text(''), colspan=len(column_names))]
        ))

    # compose the body rows
    last_row_index = None
    last_index_cells = []

    body = []
    for row_index, row_data in df.iterrows():
        if not isinstance(row_index, tuple):
            row_index = (row_index,)
        if last_row_index is None:
            last_index_cells = [
                TableCell(Text(to_str(idx)))
                for idx in row_index
            ]
            cells = copy.copy(last_index_cells)
        else:
            cells = []
            for i, idx in enumerate(row_index):
                if idx != last_row_index[i]:
                    cell = TableCell(Text(to_str(idx)))
                    last_index_cells[i] = cell
                    cells.append(cell)
                else:
                    if last_index_cells[i].rowspan is None:
                        last_index_cells[i].rowspan = 2
                    else:
                        last_index_cells[i].rowspan += 1
        cells.extend(
            TableCell(Text(to_str(row_data[k])))
            for k in column_names
        )
        body.append(TableRow(cells))
        last_row_index = row_index

    return Table(rows=body, header=headers, title=title, name=name,
                 name_scope=name_scope)
