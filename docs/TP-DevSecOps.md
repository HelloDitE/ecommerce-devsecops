# TP DevSecOps - Projet "BookStore Secure"

**Membres du groupe :** [Ton Nom], [Nom Camarade]
**Lien du dépôt :** [Lien GitHub]

---

## 1. Architecture Applicative

### Description Générale
L'application est une plateforme e-commerce simplifiée de vente de livres. Elle suit une architecture microservices conteneurisée, exposée via une API Gateway unique.

### Microservices et Rôles
Le système est composé de 3 services principaux communiquant en HTTP/REST :

1.  **Gateway (Port 80/443) :**
    * **Rôle :** Point d'entrée unique (Reverse Proxy). Gère le routage vers les services internes.
    * **Techno :** Nginx.
2.  **Auth Service (Interne : 3001) :**
    * **Rôle :** Gestion des utilisateurs (inscription/connexion) et délivrance des tokens JWT.
    * **Techno :** Node.js / Express.
3.  **Catalog Service (Interne : 3002) :**
    * **Rôle :** Gestion de l'inventaire des livres (Lecture seule publique, écriture admin).
    * **Techno :** Node.js / Express.
4.  **Order Service (Interne : 3003) :**
    * **Rôle :** Simulation de passage de commande (Validation panier).
    * **Techno :** Node.js / Express.

### Points d'entrée exposés (Surface d'attaque)
Seul le port de la Gateway est exposé à Internet.

| Route Publique | Méthode | Service Cible | Description | Auth Requise ? |
| :--- | :--- | :--- | :--- | :--- |
| `/api/auth/login` | POST | Auth Service | Connexion utilisateur | Non |
| `/api/books` | GET | Catalog Service | Liste des livres | Non |
| `/api/orders` | POST | Order Service | Créer une commande | Oui (Token JWT) |
| `/health` | GET | Tous | Vérification état | Non |

### Flux de Données Sensibles
* **Identifiants (Credentials) :** Transmis en HTTPS (idéalement) vers `/auth/login`. Stockés hachés dans la DB Auth.
* **Tokens (JWT) :** Transmis dans les headers HTTP `Authorization: Bearer ...` pour chaque requête authentifiée.
* **Données Personnelles (PII) :** Adresse de livraison envoyée au service Order lors de la commande.

### Dépendances Critiques
* **Images Docker de base :** `node:18-alpine` (OS minimal pour réduire la surface d'attaque), `nginx:alpine`.
* **Bibliothèques Tierces (Node.js) :**
    * `express` (Framework Web)
    * `jsonwebtoken` (Gestion Auth)
    * `pg` (Driver Base de données - *simulé pour ce TP*)
* **Infrastructure :** Docker & Docker Compose.

---