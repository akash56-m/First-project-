from flask_wtf import FlaskForm
from wtforms import FileField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class ComplaintForm(FlaskForm):
    department_id = SelectField("Department", coerce=int, validators=[DataRequired()])
    service_id = SelectField("Service", coerce=int, validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=20)])
    evidence = FileField("Evidence")
    submit = SubmitField("Submit complaint")


class TrackForm(FlaskForm):
    tracking_id = StringField("Tracking ID", validators=[DataRequired(), Length(min=11, max=11)])
    submit = SubmitField("Track")


class UpdateStatusForm(FlaskForm):
    status = SelectField(
        "Status",
        choices=[("Under Review", "Under Review"), ("Action Taken", "Action Taken"), ("Closed", "Closed")],
        validators=[DataRequired()],
    )
    notes = TextAreaField("Investigation Notes", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Update status")
