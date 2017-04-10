# -*- coding: utf-8 -*-
import os
import time
from logging import getLogger

from PIL import Image as PILImage

from ..container import Report
from ..elements import *

__all__ = [
    'demo_report',
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
            )
        ]
    ))
    r.add(Section(
        title='Resource Elements',
        children=[
            ParagraphText('In this section we will demonstrate report '
                          'elements with resources.'),
            Image(
                mandelbrot(),
                title='Mandelbrot Set',
            ),
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
    r.add(Section(
        title='Dynamic Elements',
        children=[
            ParagraphText('In this section we will demonstrate various '
                          'dynamic elements.'),
            Section(
                title='Basic Dynamic Element',
                children=DynamicContent(
                    html='<p>Loading, please wait for 3 seconds ...</p>',
                    script='setTimeout(function(){$($el).html($data);}, 3000);',
                    data='hello, dynamic element!'
                )
            )
        ]
    ))
    return r
