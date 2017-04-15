# -*- coding: utf-8 -*-
from ..components import *
from ..container import *
from ..elements import *

__all__ = ['regression_report']


def regression_report(truth, predict, label=None, per_target=True,
                       target_names=None, title=None):
    """Regression report.
    
    This method will compose a standard regression report, including
    the summary and the result attachment.

    Parameters
    ----------
    truth : np.ndarray
        Ground truth (correct) target values.

    predict : np.ndarray
        Predicted target values.

    label : np.ndarray | list
        If specified, will compute the regression scores for each label class.

    per_target : bool
        Whether or not to compute the regression score for each dimension?
        (default True)

    target_names : np.ndarray | list
        Name of each dimension in regression results.

        If not specified, will use the coordinate of each dimension, e.g.,
        "(0,0,0)".

    title : str
        Optional title of this regression summary table.
    """
    children = [
        regression_summary(
            truth=truth, predict=predict, label=label, per_target=per_target,
            target_names=target_names
        ),
        regression_result_attachment(
            truth=truth, predict=predict, title='Regression Result'
        )
    ]
    if title:
        return Section(title, children)
    return Group(children)
