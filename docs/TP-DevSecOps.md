# TP DevSecOps - Projet "BookStore Secure"

**Membres du groupe :** Gautier Klara, Eloire Elodie
**Lien du dépôt :** https://github.com/HelloDitE/ecommerce-devsecops.git

---

## 1. Architecture Applicative

### Description Générale
L'application est une plateforme e-commerce de vente de livres. Elle repose sur une architecture **microservices** où chaque fonctionnalité métier est isolée.
Le service Catalog (Flask) agit comme point d'entrée principal.

### Microservices et Rôles
Le système complet est conçu autour de 3 services. Pour ce rendu, le développement actif est sur le Catalogue (Python).

1.  **Catalog Service (Interne : 5000) :**
    * **Rôle :** Point d'entrée de l'application et gestion de l'inventaire des livres.
    * **Techno :** **Python / Flask** (Choisi pour la démonstration des vulnérabilités SAST/DAST).
    * **Fonction Gateway :** Il expose directement les API REST aux clients et intègre la logique métier.
    * **Base de données :** SQLite (embarquée pour le prototypage).
2.  **Auth Service & Order Service (Architecture Cible) :**
    * **Rôle :** Services tiers (Authentification et Commandes).
    * **Techno :** Node.js

### Points d'entrée exposés (Surface d'attaque)
Le service Flask est exposé directement sur le port 5000.

| Route Publique | Méthode | Description | Auth Requise ? | Risque Identifié |
| :--- | :--- | :--- | :--- | :--- |
| `/health` | GET | Vérification de l'état du service (Healthcheck) | Non | Faible |
| `/search?q=...` | GET | Recherche de livres | Non | **Critique** (Injection SQL possible) |
| `/debug/run` | GET | Interface admin de debug | Non | **Critique** (RCE - Command Injection) |
| `/discount` | POST | Calcul de réduction | Non | Moyen (Bug logique / Déni de service) |

### Flux de Données Sensibles
* **Secrets d'API :** Tokens et clés (SECRET_KEY) présents en dur dans le code Flask.
* **Commandes Système :** Exécution arbitraire possible via la route /debug/run exposée publiquement par le service Flask.

### Dépendances Critiques
L'analyse des risques (SCA - Software Composition Analysis) se porte sur ces composants :

* **Image Docker de base :** `python:3.11-slim` (Version Debian allégée).
* **Bibliothèques Python (requirements.txt) :**
    * `flask` (Framework Web)
    * `requests` (Appels HTTP)
* **Infrastructure :** Docker Compose pour l'orchestration locale et Staging.

---

## 2. Description détaillée du pipeline CI/CD

Le pipeline est orchestré via **GitHub Actions** et se déclenche à chaque push. Il est conçu pour bloquer le déploiement si une faille de sécurité critique est détectée.

### Les Étapes (Jobs)
1.  **Tests Unitaires (`unit-tests`) :**
    * Installation des dépendances Python.
    * Exécution de `pytest` pour vérifier la logique métier (ex: calcul des réductions).
    * *Gate Quality :* Le pipeline s'arrête si le code plante.

2.  **Sécurité Statique (`security-static`) :**
    * **Gitleaks :** Scanne l'historique git pour trouver des secrets (mots de passe, clés API) committés par erreur.
    * **Semgrep (SAST) :** Analyse le code source Python pour détecter des patterns dangereux (Injections SQL, RCE, Shell=True).
    * *Gate Security :* Bloque le pipeline immédiatement si une faille est trouvée.

3.  **Build & Container Scan (`deploy-staging-and-scan`) :**
    * Construction de l'image Docker `catalog-service`.
    * **Trivy (SCA) :** Scanne l'image Docker pour trouver des vulnérabilités connues dans l'OS (Debian/Alpine) et les paquets système.
    * *Gate Security :* Bloque si une vulnérabilité "CRITICAL" ou "HIGH" est détectée.

4.  **Staging & DAST :**
    * Déploiement de l'environnement de staging via `docker compose`.
    * Exécution des scripts de supervision (`smoke.sh`).
    * **OWASP ZAP (DAST) :** Attaque l'application en cours d'exécution pour détecter des failles Web (Headers manquants, XSS...).

---

## 3. Preuve d'efficacité (Vuln-Demo)

Pour démontrer l'efficacité des gates de sécurité, nous maintenons deux branches :

| Branche | État du Code | Résultat Pipeline | Explication |
| :--- | :--- | :--- | :--- |
| **`vuln-demo`** | Contient des failles (Secret en dur, SQLi, RCE) | 🔴 **ÉCHEC** | Bloqué par Semgrep (RCE/SQLi) et Gitleaks (Secrets). Le code n'est pas déployé. |
| **`main`** | Code corrigé et sécurisé | 🟢 **SUCCÈS** | Toutes les failles sont corrigées. Le code passe en staging et les tests ZAP sont exécutés. |