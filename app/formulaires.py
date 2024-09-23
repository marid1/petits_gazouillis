from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.modeles import Utilisateur

class FormulaireEtablirSession(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(message="Nom est un champ obligatoire")])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired(message="Mot de passe est un champ obligatoire")])
    se_souvenir_de_moi = BooleanField('Se souvenir de moi')
    soumettre = SubmitField('Etablir une session')

class FormulaireEnregistrement(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    courriel = StringField('Courriel', validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired()])
    mot_de_passe2 = PasswordField('Mot de passe (entrer a nouveau)', validators=[DataRequired(), EqualTo('mot_de_passe')])
    soumettre = SubmitField('Enregistrer')

    def validate_nom(self, nom):
        utilisateur = Utilisateur.query.filter_by(nom=nom.data).first()
        if utilisateur is not None:
            raise ValidationError('Ce nom existe deja')
        
    def validate_courriel(self, courriel):
        utilisateur = Utilisateur.query.filter_by(courriel=courriel.data).first()
        if utilisateur is not None:
            raise ValidationError('Ce courriel existe deja')
        
class FormulaireEditerProfil(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    a_propos_de_moi = TextAreaField('A propos de moi', validators=[Length(min=0, max=140)])
    soumettre = SubmitField('Enregistrer')

    def __init__(self, nom_original, *args, **kwargs):
        super(FormulaireEditerProfil, self).__init__(*args, **kwargs)
        self.nom_original = nom_original

    def validate_nom(self, nom):
        if nom.data != self.nom_original:
            utilisateur = Utilisateur.query.filter_by(nom=self.nom.data).first()
            if utilisateur is not None:
                raise ValidationError('Ce nom existe deja dans la base de donnees.')
            
class FormulaireVide(FlaskForm):
    soumettre = SubmitField('Enregistrer')