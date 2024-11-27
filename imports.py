from flask import Flask, render_template, flash, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float
import json
from datetime import date
from sqlalchemy import ForeignKey
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms import SelectMultipleField, widgets
from markupsafe import Markup
import os
matplotlib.use('agg')