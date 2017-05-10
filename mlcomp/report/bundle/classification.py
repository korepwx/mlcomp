# -*- coding: utf-8 -*-
from ..components import *
from ..container import *
from ..elements import *

__all__ = ['classification_report']


def classification_report(y_true, y_pred, y_prob, title=None):
    """Classification report.

    This method will compose a standard classification report, including
    the summary, the result attachment, and the AUC curve if specified
    result is a binary classification result.

    Parameters
    ----------
    y_true : numpy.ndarray
        Ground truth (correct) target values.

    y_pred : numpy.ndarray
        Predicted target values.

    y_prob : numpy.ndarray
        Estimated probabilities for each target to be each class.

    title : str
        Optional title of this report.

        If specified, the resulting report will be a Section.
        Otherwise the resulting report will be a Group.
    """
    children = [
        classification_summary(y_true=y_true, y_pred=y_pred),
        classification_result_attachment(
            y_true=y_true, y_pred=y_pred, y_prob=y_prob,
            title='Classification Result'
        ),
    ]
    if (len(y_prob.shape) == 2 and y_prob.shape[1] in (1, 2)) or \
            len(y_prob.shape) == 1:
        children.append(binary_classification_auc_curve(
            y_true=y_true, y_prob=y_prob, title='Precision-Recall Curve'
        ))
    if title:
        return Section(title, children)
    return Group(children)
