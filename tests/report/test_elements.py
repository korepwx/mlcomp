#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import unittest
from io import BytesIO
from hashlib import md5

from PIL import Image as PILImage

from mlcomp.report import ReportSaver
from mlcomp.report.elements import *
from mlcomp.utils import TemporaryDirectory


class ElementsTestCase(unittest.TestCase):

    def test_class_is_element(self):
        element_classes = [
            HTML, Text, ParagraphText, LineBreak, InlineMath, BlockMath,
            Image,
        ]
        for cls in element_classes:
            self.assertTrue(is_report_element(cls))

    def test_HTML(self):
        r = HTML(html='<span>text</span>', name='HTML element')
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "HTML", "html": "<span>text</span>", "name": "HTML element"}'
        )

    def test_Text(self):
        r = Text(text='text', name='Text element')
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "Text", "name": "Text element", "text": "text"}'
        )

    def test_ParagraphText(self):
        r = ParagraphText(text='paragraph text', name='ParagraphText element')
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "ParagraphText", "name": "ParagraphText element", "text": "paragraph text"}'
        )

    def test_LineBreak(self):
        r = LineBreak(name='LineBreak element')
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "LineBreak", "name": "LineBreak element"}'
        )

    def test_InlineMath(self):
        r = InlineMath(latex='x+1', name='InlineMath element')
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "InlineMath", "latex": "x+1", "name": "InlineMath element"}'
        )

    def test_BlockMath(self):
        r = BlockMath(latex='x+1', name='BlockMath element')
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "BlockMath", "latex": "x+1", "name": "BlockMath element"}'
        )

    def test_Image(self):
        image_data = gzip.decompress(
            b'\x1f\x8b\x08\x00y\\\xe8X\x02\xffs\xf2\xf5`\x80\x003 \xd6\x00b&'
            b'(fd\x90\x00\x8b\x0b\x01\xf1eS\x08\x86\x81\xffH,\x08\x1b\x00\x96'
            b'\x07?\xc0H\x00\x00\x00'
        )
        png_md5 = '6dcf131908cc639a95d11da701b2a059'
        image = PILImage.open(BytesIO(image_data))

        # test construct from PIL image
        r = Image(image)
        self.assertTrue(is_report_element(r))
        self.assertEqual(r.content_type, 'image/png')
        self.assertEqual(r.extension, '.png')
        self.assertEqual(md5(r.data).hexdigest(), png_md5)
        png_data = r.data

        with TemporaryDirectory() as tempdir:
            ReportSaver(tempdir).save(r)
            self.assertEqual(
                r.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "Image", "content_type": "image/png", "name_scope": "image", "path": "res/image.png"}'
            )

        # test construct from PNG bytes
        r = Image(png_data, content_type='image/png')
        self.assertEqual(r.content_type, 'image/png')
        self.assertEqual(r.extension, '.png')

        # test construct from JPG bytes
        with BytesIO() as buf:
            image.save(buf, format='JPEG')
            buf.seek(0)
            jpg_data = buf.read()
        r = Image(jpg_data, extension='.jpg')
        self.assertEqual(r.extension, '.jpg')
        if r.content_type is not None:
            content_type_s = '"content_type": "image/jpeg", '
        else:
            # might because 'python-magic' is not installed properly
            content_type_s = ''

        with TemporaryDirectory() as tempdir:
            ReportSaver(tempdir).save(r)
            self.assertEqual(
                r.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "Image", %s"extension": ".jpg", "name_scope": "image", "path": "res/image.jpg"}' % (content_type_s,)
            )

        # test detect content-type by python-magic
        try:
            import magic
            r = Image(jpg_data)
            self.assertEqual(r.content_type, 'image/jpeg')
        except ImportError:
            pass


if __name__ == '__main__':
    unittest.main()
