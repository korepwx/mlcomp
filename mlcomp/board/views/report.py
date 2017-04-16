# -*- coding: utf-8 -*-
import json
import os

from flask import Blueprint, current_app, render_template

from .utils import send_from_directory_ex

report_bp = Blueprint('report', __name__.rsplit('.')[1])


@report_bp.route('/')
def report_index():
    """Get the report index page."""
    report_dir_name = os.path.split(current_app.report_dir)[1]
    return render_template(
        'report.html',
        report_dir_name=json.dumps(report_dir_name)
    )


@report_bp.route('/<path:path>')
def resources(path):
    """Get resources from the storage directory."""
    return send_from_directory_ex(current_app.report_dir, path)
