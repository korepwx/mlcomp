# -*- coding: utf-8 -*-
import os
import time
from logging import getLogger

import numpy as np
import pandas as pd
from PIL import Image as PILImage

from ..bundle import *
from ..container import *
from ..elements import *
from ..components import *

__all__ = [
    'demo_report', 'demo_loss_accuracy_curve',
]


def mandelbrot():
    """Generate a Mandelbrot image.

    Returns
    -------
    PILImage
        The generated image.
    """
    save_path = os.path.join(os.path.split(__file__)[0], 'mandelbrot.png')
    if os.path.exists(save_path):
        return PILImage.open(save_path)

    import pyximport
    pyximport.install()
    from .mandelbrot import Mandelbrot
    width, height = 1200, 800
    m = Mandelbrot(width, height, super_sampling=False)
    start_time = time.time()
    ret = PILImage.frombuffer(
        'RGB', (width, height), m.make_image(), 'raw', 'RGB', 0, 1)
    end_time = time.time()
    getLogger(__name__).info(
        'Mandelbrot image generated in %.2f seconds.', end_time - start_time)
    ret.save(save_path, format='PNG')
    return ret


def source_code():
    """Get the source code of this script."""
    with open(__file__, 'rb') as f:
        return f.read()


def make_table():
    """Make a demonstration table."""
    return Table(
        rows=[
            TableRow([
                TableCell(Text('1')),
                TableCell(Text('2')),
                TableCell(Text('3')),
                TableCell(Text('4')),
            ]),
            TableRow([
                TableCell(Text('5')),
                TableCell(Text('6')),
                TableCell(Text('7')),
                TableCell(Text('8')),
            ])
        ],
        header=[
            TableRow([
                TableCell(Text('a'), rowspan=2),
                TableCell(Text('b'), colspan=3),
            ]),
            TableRow([
                TableCell(Text('c')),
                TableCell(Text('d')),
                TableCell(Text('e')),
            ])
        ],
        footer=[
            TableRow([
                TableCell(Text('w')),
                TableCell(Text('x')),
                TableCell(Text('y')),
                TableCell(Text('z')),
            ])
        ],
        title='Demo Table'
    )


def make_dataframe_table():
    """Get a table object from dataframe."""
    arrays = [
        ['bar', 'bar', 'baz', 'baz', 'foo', 'foo', 'qux', 'qux'],
        ['one', 'two', 'one', 'two', 'one', 'two', 'one', 'two']
    ]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=['first', 'second'])
    df = pd.DataFrame(
        np.arange(16).reshape([8, 2]), index=index, columns=['A', 'B'])
    return data_frame_to_table(df, name='the-table')


def demo_report():
    """Create a report object with demonstration contents."""
    r = Report(title='Demontration Report')
    html_block = HTML('This is an <i>HTML</i> block.')
    r.add(Section(
        title='Basic Elements',
        children=[
            ParagraphText('In this section we will demonstrate basic '
                          'report elements.'),
            Section(
                title='Text Elements',
                children=[
                    ParagraphText('This is a paragraph text.'),
                    Block([
                        Text('This is an inline text followed by an equation:'),
                        InlineMath(r'x^2 + 1'),
                        Text(', and now we will have a line break.'),
                        LineBreak(),
                        Text('This is now the second line.')
                    ]),
                    Text('And this is a text followed by a block equation.'),
                    BlockMath(
                        r'\frac{1}{\sqrt{2\pi\sigma^2}}'
                        r'\exp\left\{'
                        r'-\frac{(x-\mu)^2}{2\sigma^2}'
                        r'\right\}'
                    ),
                    html_block,
                    ParagraphText('Above HTML block will be repeated below.'),
                    html_block,
                ]
            ),
            Section(
                title='Structured Elements',
                children=[
                    make_table(),
                    ParagraphText('The below table is created from DataFrame.'),
                    make_dataframe_table(),
                ]
            )
        ]
    ))
    mandelbrot_image = mandelbrot()
    mandelbrot_thumbail = mandelbrot_image.copy()
    mandelbrot_thumbail.thumbnail((300, 300))
    r.add(Section(
        title='Resource Elements',
        children=[
            ParagraphText('In this section we will demonstrate report '
                          'elements with resources.'),
            Image(
                mandelbrot_image,
                title='Mandelbrot Set',
            ),
            ParagraphText('And its thumbnail without title:'),
            Image(mandelbrot_thumbail),
            Attachment(
                source_code(),
                title='Script Source Code',
                extension='.py'
            ),
            Block([
                Text('This is a source code link: '),
                Attachment(
                    source_code(),
                    title='Script Source Code with Only Link',
                    extension='.py',
                    link_only=True,
                )
            ])
        ]
    ))
    chart_data = {
        'title': {
            'text': 'Columns Figure',
        },
        'data': [{
            'type': 'column',
            'dataPoints': [
                {'label': 'a', 'y': 1},
                {'label': 'b', 'y': 3},
                {'label': 'c', 'y': 2},
            ]
        }]
    }
    r.add(Section(
        title='JavaScript Elements',
        children=[
            ParagraphText('In this section we will demonstrate various '
                          'JavaScript enabled elements.'),
            Section(
                title='CanvasJS Figure',
                children=[
                    CanvasJS(title='Figure Caption', data=chart_data),
                    ParagraphText('And chart without title:'),
                    CanvasJS(data=chart_data)
                ]
            ),
            Section(
                title='Dynamic Element',
                children=DynamicContent(
                    html='<p>Loading, please wait for 3 seconds ...</p>',
                    script='setTimeout(function(){$($el).html($data);}, 3000);',
                    data='hello, dynamic element!'
                )
            ),
        ]
    ))
    r.add(Section(
        title='Report Components',
        children=[
            ParagraphText('In this section we will demonstrate some '
                          'experiment report components.'),
            demo_loss_accuracy_curve(),
            demo_classification_report(),
            demo_regression_report(),
        ]
    ))
    return r


def demo_loss_accuracy_curve():
    """Make a demo loss-accuracy curve figure."""
    steps = np.arange(101)
    loss = np.exp(-steps * 0.1) * 20. + np.random.normal(size=101) * 2.
    loss = loss - np.min(loss) + .2
    valid_steps = np.arange(0, 101, 10)
    valid_loss = (np.exp(-valid_steps * 0.1) * 25. +
                  np.random.normal(size=11) * 0.5)
    valid_loss = valid_loss - np.min(valid_loss)
    valid_acc = np.exp(-valid_loss * 0.1)
    return Section(
        'Training Metrics',
        loss_accuracy_curve(
            metrics=[
                {'name': 'loss', 'steps': steps, 'values': loss},
                {'name': 'valid loss', 'steps': valid_steps,
                 'values': valid_loss},
            ],
            secondary_metrics=[
                {'name': 'valid acc', 'steps': valid_steps,
                 'values': valid_acc},
            ],
            title='Training Loss & Validation Loss / Accuracy'
        )
    )


def demo_classification_report():
    """Make a demo classification report."""
    y_true = np.random.binomial(n=1, p=.4, size=200)
    x = (
        (1 - y_true) * np.random.normal(-1., scale=1., size=y_true.shape) +
        y_true * np.random.normal(1., scale=1., size=y_true.shape)
    )
    y_prob = 1. / (1 + np.exp(-x))
    y_pred = (y_prob >= 0.5).astype(np.int32)

    return classification_report(
        y_true=y_true, y_pred=y_pred, y_prob=y_prob,
        title='Classification Report'
    )


def demo_regression_report():
    """Make a demo regression report."""
    x = np.linspace(0, np.pi * 4, 1001)
    truth = np.stack([np.sin(x), np.cos(x)], axis=-1)
    label = np.random.binomial(1, .2, size=x.shape)
    predict = np.stack([
        truth[:, 0] + (
            (1 - label) * np.random.normal(0., scale=.1, size=x.shape) +
            label * np.random.normal(0., scale=1., size=x.shape)
        ),
        truth[:, 1] + (
            (1 - label) * np.random.normal(0, scale=1., size=x.shape) +
            label * np.random.normal(0., scale=.1, size=x.shape)
        )
    ], axis=-1)

    return regression_report(
        truth=truth, predict=predict, label=label, per_target=True,
        target_names=['cos(x)', 'sin(x)'], title='Regression Report'
    )
