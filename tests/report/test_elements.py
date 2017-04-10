#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import json
import unittest
from io import BytesIO

from magic import Magic
from PIL import Image as PILImage

from mlcomp.report import ReportSaver, Report
from mlcomp.report.elements import *
from mlcomp.report.elements import _ResourceWithTitle
from mlcomp.utils import TemporaryDirectory


class ElementsTestCase(unittest.TestCase):

    def test_class_is_element(self):
        element_classes = [
            HTML, Text, ParagraphText, LineBreak, InlineMath, BlockMath,
            Image, Attachment,
            TableCell, TableRow, Table,
            Block, Section,
            DynamicContent,
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

    def test_ResourceWithTitle(self):
        R = _ResourceWithTitle

        # test title
        self.assertIsNone(R(data=b'').title)
        self.assertIsNone(R(data=b'', content_type='image/png').title)
        self.assertIsNone(R(data=b'', extension='.txt').title)
        self.assertEqual(
            R(data=b'', name='Hello World').title,
            'Hello World'
        )

        with TemporaryDirectory() as tempdir:
            r = Report([R(b''), R(b'', extension='.txt')])
            ReportSaver(tempdir).save(r)
            self.assertEqual(
                r.children[1].title,
                'resource_with_title_1.txt'
            )

    def test_Image(self):
        image = PILImage.frombytes(
            'RGB',
            (2, 2),
            b'\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00'
        )

        # test construct from PIL image
        r = Image(image)
        self.assertTrue(is_report_element(r))
        self.assertEqual(r.content_type, 'image/png')
        self.assertEqual(r.extension, '.png')
        self.assertEqual(Magic(mime=True).from_buffer(r.data), 'image/png')
        with PILImage.open(BytesIO(r.data)) as im:
            self.assertEqual(
                im.tobytes(),
                b'\xff\x00\x00\x00\xff\x00\x00\x00\xff\x00\x00\x00'
            )
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
        self.assertEqual(r.content_type, 'image/jpeg')
        self.assertEqual(r.extension, '.jpg')

        with TemporaryDirectory() as tempdir:
            ReportSaver(tempdir).save(r)
            self.assertEqual(
                r.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "Image", "content_type": "image/jpeg", "extension": ".jpg", "name_scope": "image", "path": "res/image.jpg"}'
            )

    def test_Attachment(self):
        # test ordinary attachment
        r = Attachment(data=b'1', title='my attach', content_type='image/png',
                       extension='.txt', name='the_attach')
        self.assertTrue(is_report_element(r))
        self.assertEqual(r.title, 'my attach')

        with TemporaryDirectory() as tempdir:
            ReportSaver(tempdir).save(r)
            self.assertEqual(
                r.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "Attachment", "content_type": "image/png", "extension": ".txt", "link_only": false, "name": "the_attach", "name_scope": "attach", "path": "res/attach.txt", "title": "my attach"}'
            )

    def test_Table(self):
        # test construct table cell
        r = TableCell(Text('text'), rowspan=1, colspan=2, name='Table Cell')
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "TableCell", "children": [{"__id__": 1, "__type__": "Text", "text": "text"}], "colspan": 2, "name": "Table Cell", "rowspan": 1}'
        )

        # test construct table row
        r = TableRow([
            TableCell(Text('text1')),
            TableCell(Text('text2'))
        ])
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "TableRow", "cells": [{"__id__": 1, "__type__": "TableCell", "children": [{"__id__": 2, "__type__": "Text", "text": "text1"}]}, {"__id__": 3, "__type__": "TableCell", "children": [{"__id__": 4, "__type__": "Text", "text": "text2"}]}]}'
        )
        self.assertEqual(
            repr(Report.from_json(r.to_json(sort_keys=True))),
            repr(r)
        )

        # test construct table row with non-cell element
        with self.assertRaises(TypeError):
            TableRow([Text('text')])

        # test construct table
        r = Table(TableRow(TableCell(Text('row'))))
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "Table", "rows": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "text": "row"}]}]}]}'
        )
        self.assertEqual(
            repr(Report.from_json(r.to_json(sort_keys=True))),
            repr(r)
        )

        # test construct table with header and footer
        r = Table(
            rows=[
                TableRow(TableCell(Text('row1'))),
                TableRow(TableCell(Text('row2'))),
            ],
            header=TableRow(TableCell(Text('header'))),
            footer=[
                TableRow(TableCell(Text('footer1'))),
                TableRow(TableCell(Text('footer2'))),
            ],
            title='My Table Title',
            name='My Table'
        )
        r.assign_name_scopes()
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "Table", "footer": [{"__id__": 1, "__type__": "TableRow", "cells": [{"__id__": 2, "__type__": "TableCell", "children": [{"__id__": 3, "__type__": "Text", "name_scope": "my_table/table_row_3/table_cell/text", "text": "footer1"}], "name_scope": "my_table/table_row_3/table_cell"}], "name_scope": "my_table/table_row_3"}, {"__id__": 4, "__type__": "TableRow", "cells": [{"__id__": 5, "__type__": "TableCell", "children": [{"__id__": 6, "__type__": "Text", "name_scope": "my_table/table_row_4/table_cell/text", "text": "footer2"}], "name_scope": "my_table/table_row_4/table_cell"}], "name_scope": "my_table/table_row_4"}], "header": [{"__id__": 7, "__type__": "TableRow", "cells": [{"__id__": 8, "__type__": "TableCell", "children": [{"__id__": 9, "__type__": "Text", "name_scope": "my_table/table_row_2/table_cell/text", "text": "header"}], "name_scope": "my_table/table_row_2/table_cell"}], "name_scope": "my_table/table_row_2"}], "name": "My Table", "name_scope": "my_table", "rows": [{"__id__": 10, "__type__": "TableRow", "cells": [{"__id__": 11, "__type__": "TableCell", "children": [{"__id__": 12, "__type__": "Text", "name_scope": "my_table/table_row/table_cell/text", "text": "row1"}], "name_scope": "my_table/table_row/table_cell"}], "name_scope": "my_table/table_row"}, {"__id__": 13, "__type__": "TableRow", "cells": [{"__id__": 14, "__type__": "TableCell", "children": [{"__id__": 15, "__type__": "Text", "name_scope": "my_table/table_row_1/table_cell/text", "text": "row2"}], "name_scope": "my_table/table_row_1/table_cell"}], "name_scope": "my_table/table_row_1"}], "title": "My Table Title"}'
        )
        self.assertEqual(
            repr(Report.from_json(r.to_json(sort_keys=True))),
            repr(r)
        )

    def test_Block(self):
        r = Block([Text('text')], name='Block element')
        r.assign_name_scopes()
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "Block", "children": [{"__id__": 1, "__type__": "Text", "name_scope": "block_element/text", "text": "text"}], "name": "Block element", "name_scope": "block_element"}'
        )

    def test_Section(self):
        r = Section('Section 1', [Text('text')], name='Section element')
        r.assign_name_scopes()
        self.assertTrue(is_report_element(r))
        self.assertEqual(
            r.to_json(sort_keys=True),
            '{"__id__": 0, "__type__": "Section", "children": [{"__id__": 1, "__type__": "Text", "name_scope": "section_element/text", "text": "text"}], "name": "Section element", "name_scope": "section_element", "title": "Section 1"}'
        )
        self.assertEqual(
            repr(Report.from_json(r.to_json(sort_keys=True))),
            repr(r)
        )

    def test_DynamicContent(self):
        with self.assertRaises(ValueError):
            DynamicContent()

        with TemporaryDirectory() as tempdir:
            # test HTML only element
            r = DynamicContent('HTML only')
            ReportSaver(tempdir + '/1').save(r)
            self.assertTrue(is_report_element(r))
            self.assertEqual(
                r.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "DynamicContent", "element_id": "%s", "html": "HTML only", "name_scope": "dynamic_content"}' % (r.element_id,)
            )

            # test JavaScript only element
            r = DynamicContent(script='alert($data);')
            ReportSaver(tempdir + '/2').save(r)
            self.assertTrue(is_report_element(r))
            self.assertEqual(
                r.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "DynamicContent", "element_id": "%s", "name_scope": "dynamic_content", "script": {"__id__": 1, "__type__": "Resource", "extension": ".js", "name": "Script", "name_scope": "dynamic_content/script", "path": "res/dynamic_content/script.js"}}' % (r.element_id,)
            )

            # test HTML, JavaScript and data
            r = DynamicContent(html='html content', script='alert($data);',
                               data=[1, 2, 3])
            ReportSaver(tempdir + '/3').save(r)
            self.assertTrue(is_report_element(r))
            self.assertEqual(
                r.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "DynamicContent", "data": {"__id__": 1, "__type__": "Resource", "extension": ".json", "name": "Data", "name_scope": "dynamic_content/data", "path": "res/dynamic_content/data.json"}, "element_id": "%s", "html": "html content", "name_scope": "dynamic_content", "script": {"__id__": 2, "__type__": "Resource", "extension": ".js", "name": "Script", "name_scope": "dynamic_content/script", "path": "res/dynamic_content/script.js"}}' % (r.element_id,)
            )
            with codecs.open(tempdir + '/3/res/dynamic_content/script.js') as f:
                self.assertEqual(
                    f.read(),
                    '(function(){var el=document.getElementById("%s");var data=el.getAttribute("dynamic-content-data");try{(function($,$el,$data){alert($data);})(window.jQuery,el,data);}catch(e){el.innerHTML="Failed to execute script: "+e;}})();' % (r.element_id,)
                )
            with codecs.open(tempdir + '/3/res/dynamic_content/data.json') as f:
                self.assertEqual(f.read(), '[1, 2, 3]')

    def test_CanvasJS(self):
        with TemporaryDirectory() as tempdir:
            r = CanvasJS({'data': [{
                'type': 'column',
                'dataPoints': [
                    {'label': 'a', 'y': 1},
                    {'label': 'b', 'y': 3},
                    {'label': 'c', 'y': 2},
                ]
            }]})
            ReportSaver(tempdir).save(r)
            self.assertTrue(is_report_element(r))
            self.assertEqual(
                r.to_json(sort_keys=True),
                '{"__id__": 0, "__type__": "CanvasJS", "container_id": "%s", "data": {"__id__": 1, "__type__": "Resource", "extension": ".json", "name": "Data", "name_scope": "canvas_js/data", "path": "res/canvas_js/data.json"}, "name_scope": "canvas_js"}' % (r.container_id,)
            )
            with codecs.open(tempdir + '/res/canvas_js/data.json') as f:
                self.assertEqual(
                    json.loads(f.read()),
                    {"data": [{"type": "column", "dataPoints": [{"y": 1, "label": "a"}, {"y": 3, "label": "b"}, {"y": 2, "label": "c"}]}]}
                )

if __name__ == '__main__':
    unittest.main()
