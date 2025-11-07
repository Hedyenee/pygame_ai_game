# 🎮 Jeu avec IA - Évite les Obstacles

Un jeu Python/Pygame où vous contrôlez un personnage qui doit éviter des obstacles tombants, avec une IA intelligente qui peut jouer automatiquement.

## 🚀 Fonctionnalités

- **🎯 Deux modes de jeu**: Manuel ou IA automatique
- **🤖 IA intelligente** qui évite les obstacles et chase les power-ups
- **⚡ Système de power-ups**: Vitesse, Bouclier, Points bonus
- **📈 Niveaux de difficulté** progressive
- **🏆 Système de score** en temps réel
- **🎨 Interface colorée** avec effets visuels

## 🎯 Contrôles

- **← → ↑ ↓**: Déplacer le joueur (mode manuel)
- **A**: Activer/désactiver le mode IA
- **ESPACE**: Redémarrer après Game Over
- **Q**: Quitter le jeu

## 🛠️ Installation

1. **Cloner ou télécharger** les fichiers du projet
2. **Installer les dépendances**:
   ```bash
   pip install pygame
   ```
3. **Lancer le jeu**:
   ```bash
   python main.py
   ```

## 📁 Structure du Projet

```
pygame_ai_game/
├── main.py          # Point d'entrée du jeu
├── game.py          # Logique principale du jeu
├── player.py        # Classe du joueur
├── obstacle.py      # Classe des obstacles
├── ai.py           # Intelligence artificielle
├── powerup.py      # Système de power-ups
└── requirements.txt # Dépendances
```

## 🎮 Comment Jouer

### Mode Manuel
- Utilisez les flèches pour déplacer le carré bleu
- Évitez les obstacles rouges qui tombent
- Attrapez les power-ups pour obtenir des bonus

### Mode IA
- Appuyez sur **A** pour activer l'IA
- Observez l'IA jouer intelligemment
- L'IA analyse les dangers et prend des décisions stratégiques

## 🎁 Power-ups

- **⚡ Vitesse** (Jaune): Double la vitesse du joueur pendant 5 secondes
- **🛡️ Bouclier** (Cyan): Protège des obstacles pendant 8 secondes
- **⭐ Points** (Vert): +50 points instantanés

## 🤖 Fonctionnalités de l'IA

L'IA améliorée possède:
- **Détection multi-niveaux** des dangers
- **Analyse de trajectoire** prédictive
- **Évaluation de sécurité** des mouvements
- **Gestion des priorités** intelligente
- **Planification stratégique** des déplacements

## 🎯 Objectif

- Survivre le plus longtemps possible
- Atteindre un score élevé
- Monter de niveau en évitant les obstacles
- Observer les performances de l'IA

## 🔧 Dépendances

- Python 3.6+
- Pygame 2.5.2

## 📊 Niveaux de Difficulté

La difficulté augmente automatiquement:
- **Niveau 1**: Vitesse normale
- **Niveau 2+**: Obstacles plus rapides et plus fréquents
- **Toutes les 30 secondes**: Nouveau niveau

## 🐛 Dépannage

Si vous rencontrez des erreurs:
1. Vérifiez que Pygame est installé: `pip list | grep pygame`
2. Assurez-vous que tous les fichiers sont dans le même dossier
3. Vérifiez que vous utilisez Python 3.6+

## 👨‍💻 Développement

Ce projet est développé en Python avec Pygame et présente:
- Architecture orientée objet
- Code modulaire et réutilisable
- IA avec algorithmes de décision
- Système de jeu équilibré

## 📝 Notes

- L'IA peut toujours perdre - c'est normal et montre que le jeu est bien équilibré
- Le bouclier vous protège temporairement des obstacles
- La vitesse boostée vous aide à éviter plus facilement
- Plus vous survivez longtemps, plus le jeu devient difficile

---
**Amusez-vous bien!** 🎮