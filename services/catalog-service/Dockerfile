# Etape 1 : Build (On installe tout pour construire)
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# On lance les tests ici ou dans le pipeline
# RUN npm test 

# Etape 2 : Run (On ne garde que le strict minimum pour la prod)
FROM node:18-alpine
WORKDIR /app
# On copie seulement les fichiers nécessaires depuis l'étape 1
COPY --from=builder /app .
# On utilise un utilisateur non-root (Sécurité !)
USER node
EXPOSE 3000
CMD ["npm", "start"]