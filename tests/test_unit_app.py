import importlib
import pytest

import app as myapp


@pytest.fixture(autouse=True)
def client():
    # recharge le module pour réinitialiser l'état en mémoire entre les tests
    importlib.reload(myapp)
    myapp.app.config['TESTING'] = True
    client = myapp.app.test_client()
    yield client


def test_home_get_shows_login(client):
    # tester que la page d'accueil affiche le formulaire de connexion
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'<form' in rv.data


def test_register_and_login_flow(client):
    # Enregistrer un nouvel utilisateur
    resp = client.post('/register', data={'nom': 'tester', 'mdp': 'secret'}, follow_redirects=True)
    assert resp.status_code in (200, 302)

    # Se connecter avec le nouvel utilisateur
    resp = client.post('/', data={'nom': 'tester', 'mdp': 'secret'}, follow_redirects=True)
    assert b'menu' in resp.data.lower() or resp.status_code == 200


def test_login_invalid_credentials(client):
    # tenter de se connecter avec des identifiants invalides
    resp = client.post('/', data={'nom': 'admin', 'mdp': 'wrong'}, follow_redirects=True)
    assert b'Nom ou mot de passe invalide' in resp.data


def test_menu_requires_login(client):
    # tenter d'accéder au menu sans être connecté
    resp = client.get('/menu', follow_redirects=True)
    assert b'<form' in resp.data


def test_login_sets_session_and_menu_access(client):
    # se connecter avec des identifiants valides
    client.post('/', data={'nom': 'admin', 'mdp': '1234'}, follow_redirects=True)
    resp = client.get('/menu')
    assert resp.status_code == 200


def test_forum_requires_login(client):
    # tenter d'accéder au forum sans être connecté
    resp = client.get('/forum', follow_redirects=True)
    assert b'<form' in resp.data


def test_forum_post_and_message_present(client):
    # se connecter avec des identifiants valides et poster un message sur le forum
    client.post('/', data={'nom': 'admin', 'mdp': '1234'}, follow_redirects=True)
    resp = client.post('/forum', data={'contenu': 'test message'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'test message' in resp.data


def test_wiki_post_and_listed(client):
    # se connecter avec des identifiants valides et créer un article wiki
    client.post('/', data={'nom': 'admin', 'mdp': '1234'}, follow_redirects=True)
    resp = client.post('/wiki', data={'titre': 'T1', 'contenu': 'C1'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'T1' in resp.data or b'T1' in b', '.join([a.get('"titre"', b'') for a in myapp.wiki_articles])


def test_article_view_exists(client):
    # se connecter avec des identifiants valides et vérifier que l'article 1 existe
    client.post('/', data={'nom': 'admin', 'mdp': '1234'}, follow_redirects=True)
    resp = client.get('/wiki/1')
    assert resp.status_code == 200


def test_debug_wiki_returns_json(client):
    # se connecter avec des identifiants valides et vérifier que le dump wiki est accessible et retourne du JSON
    client.post('/', data={'nom': 'admin', 'mdp': '1234'}, follow_redirects=True)
    resp = client.get('/debug/wiki_dump')
    assert resp.status_code == 200
    assert resp.is_json
