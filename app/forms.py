from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, SelectMultipleField, StringField, BooleanField
from wtforms.validators import DataRequired
import engine

class SearchForm(FlaskForm):
    exhibitionName = StringField('Exhibition name',render_kw={"placeholder": "Digital curator's choice"})
    searchedClassSelect = SelectMultipleField('Displayed objects',
                                              choices=engine.getDetectedObjectsList(),
                                              validators=[DataRequired('Select the objects that the artworks should display')]
                                              )
    comparisonActivationCheck = BooleanField('Compare with other artworks')
    comparisonClassSelect = SelectMultipleField('Displayed objects for comparison',
                                                choices=engine.getDetectedObjectsList())
    dateFrom = SelectField('From', choices=[(1300, '1300'), (1400, '1400'), (1500, '1500'), (1600, '1600'),(1700, '1700'), (1800, '1800'), (1900, '1900'), (2000, '2000')])
    dateTo = SelectField('To', coerce=int, choices=[(1400, '1400'),(1500, '1500'), (1600, '1600'), (1700, '1700'), (1800, '1800'),(1900, '1900'), (2000, '2000'),(2020, 'Today')])
    submit = SubmitField('Explore ' + str(engine.getGalleriesSum()['artworks count']) + ' artworks')