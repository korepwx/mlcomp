# -*- coding: utf-8 -*-
from flask import Blueprint, current_app, send_from_directory, render_template

report_bp = Blueprint('report', __name__.rsplit('.')[1])


@report_bp.route('/')
def report_index():
    """Get the report index page."""
    return render_template('report.html')


@report_bp.route('/<path:path>')
def resources(path):
    """Get resources from the storage directory."""
    return send_from_directory(current_app.report_dir, path)
