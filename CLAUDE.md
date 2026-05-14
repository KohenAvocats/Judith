# CLAUDE.md — Contexte pour assistance IA

Ce fichier est destiné à être copié-collé dans une conversation **Claude** ou **ChatGPT** par un utilisateur qui rencontre une difficulté avec ce projet. Il donne à l'IA tout le contexte nécessaire pour aider efficacement, sans avoir à expliquer le projet à zéro.

---

## Comment utiliser ce fichier

1. Vous avez un souci avec l'installation ou l'usage du pack Jurisprudence Avril 2026
2. Ouvrez Claude (https://claude.ai) ou ChatGPT (https://chatgpt.com), peu importe
3. Collez le contenu de ce fichier dans la conversation
4. Décrivez votre problème en quelques phrases : ce que vous avez fait, ce que vous attendez, ce qui se passe
5. L'IA aura tout le contexte pour vous guider pas à pas

---

## Présentation du projet

Le projet `Judith` est un outil gratuit publié par le cabinet **Kohen Avocats** qui permet à n'importe quel utilisateur (avocat, juriste, étudiant) d'importer dans son propre espace Notion un corpus de **41 955 décisions de justice françaises rendues en avril 2026** (Cour de cassation, cours d'appel, tribunaux judiciaires, tribunaux de commerce).

L'objectif : permettre à chacun de construire localement une base de jurisprudence interrogeable en langage naturel via l'IA native de Notion.

## Architecture technique

- **Source des données** : API Judilibre officielle (api.piste.gouv.fr), endpoint `/export`, sous Licence Ouverte Etalab 2.0
- **Format livré** : ZIP contenant un dossier `decisions_json/` (les 41 955 fichiers JSON) + le script Python + des wrappers shell
- **Authentification Notion** : OAuth 2.0 Public Integration. Le client_id et client_secret de l'intégration "Créateur de RAG" sont embarqués dans `import.py`. Une page de redirection HTTPS hébergée sur https://kohenavocats.github.io/notion-callback/ relaie le code OAuth vers un serveur HTTP local lancé temporairement par le script (port 127.0.0.1:53682)
- **Création de la base Notion** : via l'API `POST /v1/databases` avec parent = page partagée par l'utilisateur lors de l'OAuth
- **Import des décisions** : pour chaque décision, `POST /v1/pages` avec propriétés (Décision/Juridiction/Date/Numéro/Chambre) + children blocks. Si la décision est très longue, les blocs au-delà des 100 premiers sont ajoutés via `PATCH /v1/blocks/{id}/children`
- **Parallélisme** : ThreadPoolExecutor avec 10 workers, contrôlé par un token bucket global à 8 req/s pour respecter le rate limit Notion documenté à ~3 req/s tout en exploitant le burst toléré
- **Idempotence** : fichier `~/.kohen-jurisprudence/progress.jsonl` qui enregistre chaque décision importée. En cas de relance après crash, le script recharge ce fichier et ne réimporte pas les pages déjà créées

## Fichiers du projet

- `import.py` — moteur Python principal (450 lignes environ)
- `taxonomies.py` — mappings location → libellé français pour les cours d'appel (36), tribunaux judiciaires (174), tribunaux de commerce (141), extraits de la taxonomie Judilibre
- `Importer-dans-Notion.command` — wrapper bash pour Mac (double-clic). Crée un venv local si nécessaire, lance `python3 import.py`
- `Importer-dans-Notion.bat` — wrapper Windows équivalent
- `decisions_json/` — 41 955 fichiers JSON Judilibre, organisés par juridiction (cc, ca, tj, tcom)
- `README.md` — guide utilisateur complet
- `CLAUDE.md` — ce fichier
- `demo.mp4` — vidéo de présentation du cabinet

## Pannes connues et résolutions

### "Aucune page partagée avec l'application"
Cause : l'utilisateur n'a coché aucune page lors du flow OAuth Notion.
Résolution : créer une page Notion (barre latérale → "+"), puis sur cette page cliquer "..." → "Connexions" → ajouter "Créateur de RAG". Puis revenir au terminal et appuyer sur Entrée.

### "Python 3 n'est pas installé"
Cause : Python absent du système (fréquent sur Windows).
Résolution : télécharger depuis https://www.python.org/downloads/. Sur Windows, **cocher impérativement "Add Python to PATH"** pendant l'installation.

### Mac refuse d'ouvrir `Importer-dans-Notion.command`
Cause : Gatekeeper bloque les scripts non signés.
Résolution : clic droit sur le fichier → Ouvrir → confirmer Ouvrir dans la dialog. Nécessaire seulement la première fois.

### "Erreur 429 Too Many Requests" en boucle
Cause : Notion a tagué le compte comme dépassant le rate limit (peu probable, le script gère normalement).
Résolution : attendre 15-30 minutes, puis relancer. Le script reprendra automatiquement.

### "Erreur 401 Unauthorized"
Cause : token OAuth expiré ou invalide.
Résolution : supprimer le fichier `~/.kohen-jurisprudence/token.json` puis relancer. Un nouveau flow OAuth démarre.

### Le script semble bloqué sans progression
Cause : connexion réseau lente ou Notion qui temporise.
Résolution : laisser tourner 5 minutes supplémentaires. Si toujours bloqué, Ctrl+C pour arrêter, puis relancer.

### "ModuleNotFoundError: requests" (rare car le script n'utilise que la stdlib Python)
Résolution : depuis le terminal, dans le dossier du projet, taper `python3 -m pip install requests`.

### La database est créée mais vide
Cause : le script a planté avant l'import des décisions.
Résolution : vérifier la sortie du terminal pour identifier l'erreur. Si nécessaire, supprimer la database dans Notion et relancer.

## Limitations

- **Rate limit Notion** : ~8 req/s sustained. Pour 41 955 décisions, l'import dure environ 1h30 à 2h. Pas plus rapide possible sans risquer un ban temporaire de l'API.
- **OAuth Public Integration** : limitée à 100 utilisateurs distincts tant qu'elle n'est pas soumise et approuvée au Marketplace Notion. Au-delà, un message d'erreur s'affichera lors de l'OAuth.
- **Pas de mise à jour automatique** : ce pack est statique sur avril 2026. Une nouvelle version sera publiée pour les mois suivants.
- **Occultation Judilibre limitée aux parties** : l'art. L. 111-13, al. 1 COJ n'impose l'occultation que des nom et prénoms des personnes physiques parties et tiers. Les magistrats, greffiers, avocats, experts et témoins **ne sont pas anonymisés par défaut** (al. 2 : occultation facultative sur demande). Ce n'est pas une erreur résiduelle, c'est le régime légal. L'utilisateur reste responsable du traitement RGPD et doit en particulier respecter l'interdiction de profilage de l'al. 3 (sanctionnée par l'art. 226-18 CP).

## Comment aider un utilisateur

Quand un utilisateur vous demande de l'aide :

1. **Demandez-lui sa plateforme** : Mac ou Windows ? Plan Notion gratuit ou payant ?
2. **Demandez-lui ce qui s'affiche dans le terminal** ou le navigateur au moment où ça plante
3. **Référez-vous aux pannes connues ci-dessus** avant de proposer des corrections
4. **Soyez pédagogue** : l'utilisateur peut être totalement novice en informatique. Donnez des instructions très concrètes ("ouvre cette application Y", "tape ceci", "clique là")
5. **Ne proposez jamais** à l'utilisateur de partager ses identifiants Notion ou son token OAuth avec vous

---

## Assistance

Aucune assistance humaine n'est assurée par le cabinet Kohen Avocats sur ce projet. Le code et la documentation sont fournis "as is". L'utilisateur s'appuie sur ce fichier CLAUDE.md et sur Claude/ChatGPT pour résoudre ses difficultés.
