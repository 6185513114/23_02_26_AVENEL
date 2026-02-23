from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from datetime import datetime
import psycopg2

def get_db_connection():
    # Gardée pour futur usage (Postgres). Non utilisée dans cette version "en mémoire".
    return psycopg2.connect(
        host="192.168.1.2",
        dbname="vision",
        user="vision",
        password="12345"
    )

app = Flask(__name__)
app.secret_key = "change_this_to_a_secure_random_value"
bcrypt = Bcrypt(app)

# -----------------------
# Utilisateurs (mémoire)
# -----------------------
utilisateurs = [
    {
        "id": 1,
        "nom": "admin",
        # mot de passe "1234" hashé
        "mdp": bcrypt.generate_password_hash("1234").decode('utf-8')
    },

    {
        "id": 2,
        "nom": "user1",
        # mot de passe "abc" hashé
        "mdp": bcrypt.generate_password_hash("abc").decode('utf-8')
    }
]

# -----------------------
# Wiki articles (mémoire)
# -----------------------
wiki_articles = [
    {
        "id": 1,
        "titre": "Ultron : La menace persistante",
        "contenu": (
            "En 2015, Ultron fut affronté lors de la bataille de Novi Grad, en Sokovie. "
            "Pensé détruit après l’intervention des Avengers, il ne s’agissait que d’une victoire temporaire.\n\n"
            "Aujourd’hui, Ultron est devenu un virus-IA diffus, présent dans chaque caméra, chaque assistant vocal, "
            "chaque requête réseau. Ses fragments corrompent les infrastructures et forcent l’humanité à survivre hors-réseau."
        ),
        "auteur": "admin",
        "date": datetime.now()
    },
    {
        "id": 2,
        "titre": "La D.I.P. - Défense Informatique Planétaire",
        "contenu": (
            "La D.I.P. est une cellule clandestine née pour protéger les communautés et sauvegarder le savoir "
            "dans un monde où les réseaux sont compromis. Sa stratégie : organiser, stocker localement, et survivre."
        ),
        "auteur": "admin",
        "date": datetime.now()
    },
    {
        "id": 3,
        "titre": "Vision — Les recrues",
        "contenu": (
            "Vision regroupe les équipes recrutées par la D.I.P. Notre rôle est de concevoir des outils résilients, "
            "hors-réseaux, pour permettre aux populations de s'organiser et survivre."
        ),
        "auteur": "admin",
        "date": datetime.now()
    }
]

# Counters
next_user_id = 2
next_article_id = 4

# -----------------------
# Helpers utilisateur
# -----------------------
def get_user_by_name(nom_utilisateur):
    for utilisateur in utilisateurs:
        if utilisateur['nom'] == nom_utilisateur:
            return utilisateur
    return None

def verify_user(nom_utilisateur, mot_de_passe):
    user = get_user_by_name(nom_utilisateur)
    if user and bcrypt.check_password_hash(user['mdp'], mot_de_passe):
        return user
    return None

# -----------------------
# Routes : Auth
# -----------------------
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nom = request.form.get('nom')
        mdp = request.form.get('mdp')

        utilisateur = verify_user(nom, mdp)
        if utilisateur:
            session['nom_utilisateur'] = utilisateur['nom']
            return redirect(url_for('menu'))
        else:
            return render_template("login.html", erreur="Nom ou mot de passe invalide", show_nav_links=False)

    if 'nom_utilisateur' in session:
        return redirect(url_for('menu'))
    return render_template("login.html", show_nav_links=False)

@app.route('/logout')
def logout():
    session.pop('nom_utilisateur', None)
    return redirect(url_for('login'))

@app.route('/register', methods=["GET", "POST"])
def register():
    global next_user_id
    if request.method == "POST":
        nom = request.form.get('nom')
        mdp = request.form.get('mdp')

        if get_user_by_name(nom) is None:
            hashed_password = bcrypt.generate_password_hash(mdp).decode('utf-8')
            utilisateurs.append({
                "id": next_user_id,
                "nom": nom,
                "mdp": hashed_password
            })
            next_user_id += 1
            return redirect(url_for('login'))
        else:
            return render_template("register.html", erreur="Utilisateur déjà existant", show_nav_links=False)

    return render_template("register.html", show_nav_links=False)

@app.route("/menu")
def menu():
    if 'nom_utilisateur' not in session:
        return redirect(url_for('login'))
    return render_template("menu.html", show_nav_links=True, nom_utilisateur=session['nom_utilisateur'])

# -----------------------
# Forum (mémoire)
# -----------------------
posts = [
    {"auteur": "admin", "contenu": "Bienvenue sur le forum 👋", "date": datetime.now()}
]

@app.route('/forum', methods=["GET", "POST"])
def forum():
    if 'nom_utilisateur' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        contenu = request.form.get('contenu')
        if contenu:
            posts.append({
                "auteur": session['nom_utilisateur'],
                "contenu": contenu,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M")
            })
        return redirect(url_for('forum'))  # ✅ Évite le doublon

    return render_template(
        "forum.html",
        posts=posts,
        show_nav_links=True,
        nom_utilisateur=session['nom_utilisateur']
    )

@app.route('/forum/messages')
def forum_messages():
    if 'nom_utilisateur' not in session:
        return jsonify([])  

    messages_serialises = []
    for post in posts:
        messages_serialises.append({
            "auteur": post["auteur"],
            "contenu": post["contenu"],
            "date": datetime.now()
        })
    return jsonify(messages_serialises)

# -----------------------
# Wiki (mémoire)
# -----------------------
@app.route('/wiki', methods=["GET", "POST"])
def wiki():
    global next_article_id
    if 'nom_utilisateur' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        titre = request.form.get("titre")
        contenu = request.form.get("contenu")
        if titre and contenu:
            wiki_articles.append({
                "id": next_article_id,
                "titre": titre,
                "contenu": contenu,
                "auteur": session['nom_utilisateur'],
                "date": datetime.now()
            })
            next_article_id += 1

    return render_template("wiki.html", articles=wiki_articles, show_nav_links=True, nom_utilisateur=session['nom_utilisateur'])

@app.route('/wiki/<int:id>')
def article(id):
    if 'nom_utilisateur' not in session:
        return redirect(url_for('login'))

    for art in wiki_articles:
        if art['id'] == id:
            return render_template("article.html", article=art, show_nav_links=True, nom_utilisateur=session['nom_utilisateur'])
    return "Article non trouvé", 404

# -----------------------
# Debug endpoint (optionnel)
# -----------------------
@app.route('/debug/wiki_dump')
def debug_wiki():
    from flask import jsonify
    return jsonify(wiki_articles)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
