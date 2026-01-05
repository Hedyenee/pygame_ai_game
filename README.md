# Jeu Multi IA - Evite les obstacles

Petit jeu Python/Pygame où 1 ou 2 joueurs esquivent des blocs qui tombent. Chaque joueur peut être contrôlé manuellement ou par l'IA en un clic. Tir à distance, power-ups et difficulté progressive.

## Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python main.py
```

## Menu principal (cliquable)
- Bouton 1 Joueur / 2 Joueurs : choisit le nombre de joueurs (J2 désactivé en solo).
- Bouton IA auto : active l'IA pour tous au lancement.
- Bouton Musique : coupe/remet le son (musique + FX).
- Bouton Start : lance la partie après tes choix.
- Options (touche O) : remap touches, volumes Musique/FX, IA auto, mute.

## Commandes en jeu
- Joueur 1 : flèches. Tir : `Ctrl` droit.
- Joueur 2 : ZQSD. Tir : `E`.
- IA : `1` ou `2` pour basculer l'IA de chaque joueur; `TAB` ou `T` pour tous.
- Pause : `P`. Mute : `M`. Quitter : `Échap`.
- Game over : `Espace` pour relancer.

## Power-ups et tirs
- SPD : vitesse x2 (5s).
- SHD : bouclier (absorbe un choc).
- +50 : points bonus.
- SLOW : ralenti global temporaire.
- ZAP : supprime l'obstacle le plus proche.
- AMMO : +5 balles (munitions).
- Tirs : chaque joueur a 3 balles de base; un tir qui touche détruit l'obstacle et donne +1 point.

## IA : fonctionnement
- Priorise l'esquive des obstacles immédiats/proches, sinon se place au centre.
- Peut être forcée on/off par joueur (`1`/`2`) ou pour tous (`TAB`/`T`).
- Option IA auto (menu ou options) : active l'IA des deux joueurs au démarrage.
- Marge d'erreur IA : premier choc sans bouclier consomme un hit de grâce (affiche "Hits IA" dans le HUD).

## Gameplay et progression
- Obstacles plus rapides et nombreux au fil du temps; fonds de couleur cyclent par niveau.
- Joueurs deviennent circulaires à partir du niveau 2.
- Score par joueur + high score persistant (`highscore.json`).

## Fichiers importants
- `main.py` lance le jeu.
- `game.py` logique principale, menu, sons, particules, collisions.
- `player.py` déplacements, tirs, IA toggle, bouclier/vitesse.
- `ai.py` décisions de l'IA.
- `powerup.py` définitions des power-ups (dont AMMO).
- `assets/` sons et sprites (optionnels).

Bon jeu !
