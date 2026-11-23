import os
from flask import Flask, render_template, request
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db = mysql.connector.connect(user=os.getenv("DB_USER"),
                             host=os.getenv("DB_HOST"),
                            password=os.getenv("DB_PASSWORD"),
                             port=int(os.getenv("DB_PORT")),
                             database=os.getenv("DB_NAME"))



@app.route('/')
def index():
    curseur = db.cursor(dictionary=True)
    curseur.execute("SELECT * FROM croutes")
    croutes = curseur.fetchall()
    curseur.execute("SELECT * FROM sauces")
    sauces = curseur.fetchall()
    curseur.execute("SELECT * FROM garnitures")
    garnitures = curseur.fetchall()
    curseur.close()
    return render_template("index.html", croutes=croutes, sauces=sauces, garnitures=garnitures)

@app.route('/ajouter', methods=['POST'])
def ajouter():
    nom = request.form['nom']
    telephone = request.form['telephone']
    adresse = request.form['adresse']
    id_croute = request.form['croute']
    id_sauce = request.form['sauce']
    garnitures = request.form.getlist('garnitures')

    curseur = db.cursor()
    try:
        requete = """
        INSERT INTO clients (nom, telephone, adresse_livraison)
        VALUES(%(nom)s, %(telephone)s, %(adresse)s)
        """
        parametres = {
            "nom": nom, 
            "telephone": telephone, 
            "adresse": adresse
            }
        curseur.execute(requete, parametres)
        id_client = curseur.lastrowid

        requete = """
        INSERT INTO commandes (id_client, date_commande)
        VALUES(%(id_client)s, NOW())
        """
        parametres = {
            "id_client": id_client
            }
        curseur.execute(requete, parametres)
        id_commande = curseur.lastrowid

        requete = """
        INSERT INTO pizza (id_commande, id_croute, id_sauce)
        VALUES(%(id_commande)s, %(id_croute)s, %(id_sauce)s)
        """
        parametres = {"id_commande": id_commande, "id_croute": id_croute, "id_sauce": id_sauce}
        curseur.execute(requete, parametres)
        id_pizza = curseur.lastrowid

        for id_garniture in garnitures:
            requete = """
            INSERT INTO pizza_garniture (id_pizza, id_garniture)
            VALUES(%(id_pizza)s, %(id_garniture)s)
            """
            parametres = {"id_pizza": id_pizza, "id_garniture": id_garniture}
            curseur.execute(requete, parametres)

        db.commit()
        curseur.close()
        return render_template("ajout.html")
    except mysql.connector.Error as erreur:
        db.rollback()
        curseur.close()
        return render_template("erreur.html", erreur=erreur.msg)
    
@app.route('/resume', methods=['POST'])
def resume():
    nom = request.form['nom']
    telephone = request.form['telephone']
    adresse = request.form['adresse']
    id_croute = request.form['croute']
    id_sauce = request.form['sauce']
    garnitures = request.form.getlist('garnitures')

    curseur = db.cursor(dictionary=True)

    curseur.execute("SELECT nom_croute FROM croutes WHERE id = %(id)s", {"id": id_croute})
    nom_croute = curseur.fetchone()["nom_croute"]

    curseur.execute("SELECT nom_sauce FROM sauces WHERE id = %(id)s", {"id": id_sauce})
    nom_sauce = curseur.fetchone()["nom_sauce"]

    noms_garnitures = []
    for id_garniture in garnitures:
        curseur.execute("SELECT nom_garniture FROM garnitures WHERE id = %(id)s", {"id": id_garniture})
        noms_garnitures.append(curseur.fetchone()["nom_garniture"])

    curseur.close()

    return render_template("resume.html",
                           nom=nom, telephone=telephone, adresse=adresse,
                           id_croute=id_croute, id_sauce=id_sauce,
                           nom_croute=nom_croute, nom_sauce=nom_sauce,
                           garnitures=garnitures, noms_garnitures=noms_garnitures)

@app.route('/livraisons')
def livraisons():
    curseur = db.cursor(dictionary=True)
    requete = """
    SELECT ce.id AS id_attente, c.id AS id_commande, c.date_commande,
           cl.nom, cl.telephone, cl.adresse_livraison,
           cr.nom_croute, s.nom_sauce,
           GROUP_CONCAT(g.nom_garniture SEPARATOR ', ') AS garnitures
    FROM commandes_en_attente ce
    JOIN commandes c ON c.id = ce.id_commande
    JOIN clients cl ON cl.id = c.id_client
    JOIN pizza p ON p.id_commande = c.id
    JOIN croutes cr ON cr.id = p.id_croute
    JOIN sauces s ON s.id = p.id_sauce
    LEFT JOIN pizza_garniture pg ON pg.id_pizza = p.id
    LEFT JOIN garnitures g ON g.id = pg.id_garniture
    GROUP BY ce.id, c.id, c.date_commande, cl.nom, cl.telephone,
             cl.adresse_livraison, cr.nom_croute, s.nom_sauce
    ORDER BY c.date_commande
    """
   
    curseur.execute(requete)
    donnees = curseur.fetchall()
    curseur.close()
    return render_template("livraisons.html", data=donnees)
    


@app.route('/livrer/<int:id_attente>', methods=['POST'])
def livrer(id_attente):
    requete = "DELETE FROM commandes_en_attente WHERE id = %(id_attente)s"
    parametres = {"id_attente": id_attente}

    curseur = db.cursor()
    try:
        curseur.execute(requete, parametres)
        db.commit()
        curseur.close()
        return render_template("livre.html")
    except mysql.connector.Error as erreur:
        db.rollback()
        curseur.close()
        return render_template("erreur.html", erreur=erreur.msg)

if __name__ == '__main__':
    app.run(debug=True)