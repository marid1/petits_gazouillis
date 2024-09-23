from flask import render_template, flash, redirect, request, url_for
from app import app, db
from app.formulaires import FormulaireEditerProfil, FormulaireEtablirSession, FormulaireEnregistrement, FormulaireVide
from app.modeles import Utilisateur
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont
import random
import base64
from io import BytesIO
from datetime import UTC, datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.dernier_acces = datetime.now(UTC)
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    utilisateurs = current_user
    publications = current_user.liste_publications_dont_je_suis_partisan().all()
    return render_template('index.html', titre='Acceuil', utilisateur=utilisateurs, publications=publications)

@app.route('/utilisateur/<nom>')
@login_required
def utilisateur(nom):
    utilisateur = Utilisateur.query.filter_by(nom=nom).first_or_404()
    publications = utilisateur.publications.all()
    formulaire = FormulaireVide()
    return render_template('utilisateur.html', utilisateur=utilisateur, publications=publications, formulaire=formulaire)

@app.route('/enregistrer', methods=['GET', 'POST'])
def enregistrer():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    formulaire = FormulaireEnregistrement()
    if formulaire.validate_on_submit():
        utilisateur = Utilisateur(nom=formulaire.nom.data, courriel=formulaire.courriel.data)
        utilisateur.enregister_mot_de_passe(formulaire.mot_de_passe.data)
        fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 15)
        image = Image.new('RGB', (128,128), color = 'black')
        for i in range(20):
            x = random.randint(0,128)
            y = random.randint(0,128)
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)
            h = random.randint(0,20)
            fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', h)
            d = ImageDraw.Draw(image)
            d.text((x,y), utilisateur.nom, font=fnt, fill=(r,g,g))

        tampon = BytesIO()
        image.save(tampon, format="JPEG")
        image_base64 = base64.b64encode(tampon.getvalue()).decode("utf-8")
        utilisateur.avatar = "data:image/jpg;base64," + image_base64
        print("data:image/jpg;base64," + image_base64)

        db.session.add(utilisateur)
        db.session.commit()
        flash("Felicitations, vous etes maintenant enregistrer!")
        return redirect(url_for('etablir_session'))
    return render_template('enregistrement.html', title='Enregistrer', formulaire=formulaire)

@app.route('/etablir_session', methods=['GET', 'POST'])
def etablir_session():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    formulaire = FormulaireEtablirSession()
    if formulaire.validate_on_submit():
        utilisateur = Utilisateur.query.filter_by(nom=formulaire.nom.data).first()
        if utilisateur is None or not utilisateur.valider_mot_de_passe(formulaire.mot_de_passe.data):
            flash('Nom utilisateur ou mot de passe invalide(s)')
            return redirect(url_for('etablir_session'))
        login_user(utilisateur, remember=formulaire.se_souvenir_de_moi.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            return redirect(url_for('index'))
        return redirect(next_page)
    return render_template('etablir_session.html', titre='Etablir une session', formulaire=formulaire)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/editer_profil', methods=['GET', 'POST'])
@login_required
def editer_profil():
    formulaire = FormulaireEditerProfil(current_user.nom)
    if formulaire.validate_on_submit():
        current_user.nom = formulaire.nom.data
        current_user.a_propos_de_moi = formulaire.a_propos_de_moi.data
        db.session.commit()
        flash('Vos modifications ont ete sauvegardees.')
        return redirect(url_for('editer_profil'))
    elif request.method == 'GET':
        formulaire.nom.data = current_user.nom
        formulaire.a_propos_de_moi.data = current_user.a_propos_de_moi
    return render_template('editer_profil.html', titre='Editer Profil', formulaire=formulaire)

@app.route('/suivre/<nom>', methods=['POST'])
@login_required
def suivre(nom):
    formulaire = FormulaireVide()
    if formulaire.validate_on_submit():
        utilisateur = Utilisateur.query.filter_by(nom=nom).first()
        if utilisateur is None:
            flash('Utilisateur {} n\'existe pas'.format(nom))
            return redirect(url_for('index'))
        if utilisateur == current_user:
            flash('Vous ne pouvez pas vous suivre vous-meme!')
            return redirect(url_for('utilisateur', nom=nom))
        current_user.devenir_partisan(utilisateur)
        db.session.commit()
        flash('Vous suivez maintenant {}!'.format(nom))
        return redirect(url_for('utilisateur', nom=nom))
    else:
        return redirect(url_for('index'))
    
@app.route('/ne_plus_suivre/<nom>', methods=['POST'])
@login_required
def ne_plus_suivre(nom):
    formulaire = FormulaireVide()
    if formulaire.validate_on_submit():
        utilisateur = Utilisateur.query.filter_by(nom=nom).first()
        if utilisateur is None:
            flash('Utilisateur {} n\'existe pas'.format(nom))
            return redirect(url_for('index'))
        if utilisateur == current_user:
            flash('Vous ne pouvez pas ne plus vous suivre!')
            return redirect(url_for('utilisateur', nom=nom))
        current_user.ne_plus_etre_partisan(utilisateur)
        db.session.commit()
        flash('Vous ne suivez plus {}.'.format(nom))
        return redirect(url_for('utilisateur', nom=nom))
    else:
        return redirect(url_for('index'))