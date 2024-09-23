from datetime import UTC, datetime, timedelta
import unittest
from app import app, db
from app.modeles import Utilisateur, Publication

class CasModeleUtilisateur(unittest.TestCase):
    def setUp(self):        
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' 
        self.app_context = app.app_context()
        self.app_context.push() 

        with self.app_context: 
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_mot_de_passe_hashing(self):
        u = Utilisateur(nom='patate')
        u.enregister_mot_de_passe('Password1')
        self.assertFalse(u.valider_mot_de_passe('MotDePasseInvalide'))
        self.assertTrue(u.valider_mot_de_passe('Password1'))

    def test_partisans(self):
        u1 = Utilisateur(nom='patate', courriel='p@info.cgg')
        u2 = Utilisateur(nom='tomate', courriel='t@info.cgg')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertEqual(u1.les_partisans.all(), [])
        self.assertEqual(u1.partisans.all(), [])

        u1.devenir_partisan(u2)
        db.session.commit()

        self.assertTrue(u1.est_partisan(u2))
        self.assertEqual(u1.les_partisans.count(), 1)
        self.assertEqual(u1.les_partisans.first().nom, 'tomate')
        self.assertEqual(u2.partisans.count(), 1)
        self.assertEqual(u2.partisans.first().nom, 'patate')

        u1.ne_plus_etre_partisan(u2)
        db.session.commit()
        self.assertFalse(u1.est_partisan(u2))
        self.assertEqual(u1.les_partisans.count(), 0)
        self.assertEqual(u2.partisans.count(), 0)

    def test_publications_suivies(self):
        u1 = Utilisateur(nom='patate', courriel='p@info.cgg')
        u2 = Utilisateur(nom='tomate', courriel='t@info.cgg')
        u3 = Utilisateur(nom='salade', courriel='s@info.cgg')
        u4 = Utilisateur(nom='radis', courriel='r@info.cgg')
        db.session.add_all([u1,u2,u3,u4])

        maintenant = datetime.now(UTC)
        p1 = Publication(corps="publication de patate", auteur=u1, horodatage=maintenant + timedelta(seconds=1))
        p2 = Publication(corps="publication de tomate", auteur=u2, horodatage=maintenant + timedelta(seconds=4))
        p3 = Publication(corps="publication de salade", auteur=u3, horodatage=maintenant + timedelta(seconds=3))
        p4 = Publication(corps="publication de radis", auteur=u4, horodatage=maintenant + timedelta(seconds=2))
        db.session.add_all([p1,p2,p3,p4])
        db.session.commit()

        u1.devenir_partisan(u2)
        u1.devenir_partisan(u4)
        u2.devenir_partisan(u3)
        u3.devenir_partisan(u4)
        db.session.commit()

        f1 = u1.liste_publications_dont_je_suis_partisan().all()
        f2 = u2.liste_publications_dont_je_suis_partisan().all()
        f3 = u3.liste_publications_dont_je_suis_partisan().all()
        f4 = u4.liste_publications_dont_je_suis_partisan().all()

        self.assertEqual(f1, [p2,p4,p1])
        self.assertEqual(f2, [p2,p3])
        self.assertEqual(f3, [p3,p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)