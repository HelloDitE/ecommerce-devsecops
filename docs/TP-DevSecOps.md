# TP DevSecOps - Projet "BookStore Secure"

**Membres du groupe :** Gautier Klara, Eloire Elodie
**Lien du dépôt :** https://github.com/HelloDitE/ecommerce-devsecops.git

---

## 1. Architecture Applicative

### Description Générale
L'application est une plateforme e-commerce de vente de livres. Elle repose sur une architecture **microservices** où chaque fonctionnalité métier est isolée.
Pour ce TP, conformément aux consignes, nous nous sommes concentrés sur l'implémentation technique et la sécurisation du service critique : le **Catalog Service**.

### Microservices et Rôles
Le système complet est conçu autour de 3 services. Pour ce rendu, le développement actif est sur le Catalogue (Python).

1.  **Gateway (Port 80/443) :**
    * **Rôle :** Point d'entrée unique (Reverse Proxy). Il route les requêtes vers les bons services et protège l'accès direct aux conteneurs.
    * **Techno :** Nginx.
2.  **Catalog Service (Interne : 5000) - *Focus du TP* :**
    * **Rôle :** Gestion de l'inventaire des livres et moteur de recherche.
    * **Techno :** **Python / Flask** (Choisi pour la démonstration des vulnérabilités SAST/DAST).
    * **Base de données :** SQLite (embarquée pour le prototypage).
3.  **Auth Service & Order Service (Architecture Cible) :**
    * **Rôle :** Gestion des utilisateurs (JWT) et des paniers.
    * **Techno :** Node.js (Prévus dans la roadmap, simulés pour l'instant).

### Points d'entrée exposés (Surface d'attaque)
Voici les routes API définies dans notre service Catalogue actuel, accessibles via la Gateway ou directement en interne :

| Route Publique | Méthode | Description | Auth Requise ? | Risque Identifié |
| :--- | :--- | :--- | :--- | :--- |
| `/health` | GET | Vérification de l'état du service (Healthcheck) | Non | Faible |
| `/search?q=...` | GET | Recherche de livres | Non | **Critique** (Injection SQL possible) |
| `/debug/run` | GET | Interface admin de debug | Non | **Critique** (RCE - Command Injection) |
| `/discount` | POST | Calcul de réduction | Non | Moyen (Bug logique / Déni de service) |

### Flux de Données Sensibles
* **Secrets d'API :** Des clés de configuration (`SECRET_KEY`) et des tokens d'administration (`ADMIN_TOKEN`) sont présents dans le code source (détectables par Secret Scanning).
* **Commandes Système :** Le service Catalogue expose par erreur une route (`/debug/run`) permettant d'exécuter des commandes arbitraires sur le serveur, créant un risque majeur de prise de contrôle du conteneur.
* **Données Métier :** Les informations produits (Prix, Titres) sont exposées publiquement.

### Dépendances Critiques
L'analyse des risques (SCA - Software Composition Analysis) se porte sur ces composants :

* **Image Docker de base :** `python:3.11-slim` (Version Debian allégée).
* **Bibliothèques Python (requirements.txt) :**
    * `flask` (Framework Web)
    * `requests` (Appels HTTP)
* **Infrastructure :** Docker Compose pour l'orchestration locale et Staging.

---