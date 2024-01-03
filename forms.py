# Imports
from flask_wtf import FlaskForm
from wtforms import StringField
from flask import request

# Forms
class SearchForm(FlaskForm):
    """Form for making queries to database"""
    search = StringField('search')
    