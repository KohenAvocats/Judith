# Recherche jurisprudentielle dans Notion

Présentation du projet : **41 955 décisions de justice rendues en avril 2026** (Cour de cassation, cours d'appel, tribunaux judiciaires, tribunaux de commerce), importables dans votre Notion en deux clics. Texte intégral, métadonnées structurées, recherche par l'IA Notion native.

**Ce pack est volontairement limité au mois d'avril 2026** : il sert de démonstration du projet. L'objectif est de montrer aux confrères avocats et aux juristes ce qu'on peut faire avec un corpus de jurisprudence française importé dans un workspace Notion personnel.

Mis à disposition par le cabinet **[Kohen Avocats](https://www.kohenavocats.fr)**.

> **Avant tout téléchargement, lisez impérativement le fichier [CONDITIONS.md](CONDITIONS.md).** L'installation vaut acceptation des conditions d'usage (Licence Ouverte Etalab 2.0, restrictions de l'article L. 111-13 du Code de l'organisation judiciaire sur le profilage des magistrats, obligations RGPD, limitation de responsabilité du cabinet).

---

## À qui ça s'adresse

À tout avocat, juriste, magistrat, étudiant ou universitaire qui veut un corpus de jurisprudence française récent, structuré et exploitable par une IA conversationnelle. Une fois importé dans votre espace Notion, vous pouvez interroger les 41 955 décisions en langage naturel via l'IA intégrée à Notion : *« Trouve-moi les décisions sur la garde alternée d'un animal de compagnie »*, *« Décisions en matière de cyberharcèlement scolaire en avril 2026 »*, etc.

---

## Si vous êtes un débutant total en informatique

Suivez les étapes dans l'ordre. Ne sautez rien. L'installation prend moins de 10 minutes, puis l'import dans Notion tourne tout seul pendant 1 à 2 heures.

### Étape 1 — Créer un compte Notion (si vous n'en avez pas)

1. Allez sur https://www.notion.so
2. Cliquez sur **"S'inscrire gratuitement"**
3. Renseignez votre adresse e-mail et un mot de passe, puis suivez le parcours d'inscription
4. Une fois connecté, vous arrivez sur votre espace de travail. Notez visuellement à quoi ressemble la barre latérale gauche, c'est là qu'on va créer une page tout à l'heure

### Étape 2 — Python (installation automatique sur Mac)

Le script a besoin de Python 3. La plupart des Mac l'ont déjà. Si ce n'est pas votre cas, **rien à faire vous-même** : le lanceur Mac détecte l'absence et déclenche automatiquement l'installation des outils Apple (~5 min, un seul dialog à valider).

**Sur Windows uniquement** : Python n'est pas pré-installé. Allez sur https://www.python.org/downloads/, téléchargez l'installateur, lancez-le, et **cochez impérativement la case "Add Python to PATH"** au début de l'installation avant de cliquer "Install Now".

### Étape 3 — Télécharger le pack jurisprudence

Allez sur la page Releases du projet : https://github.com/KohenAvocats/Judith/releases

Téléchargez le fichier `Jurisprudence-Avril-2026.zip` (environ 200 Mo).

Décompressez-le là où vous voulez : sur votre Bureau, dans Téléchargements, peu importe. Vous obtenez un dossier `Jurisprudence-Avril-2026/` qui contient plusieurs fichiers et un sous-dossier `decisions_json/`.

### Étape 4 — Lancer l'import

**Sur Mac**

Double-cliquez sur **`Importer-dans-Notion.command`** dans le dossier décompressé.

La première fois, macOS peut refuser de l'ouvrir pour des raisons de sécurité ("ce fichier ne peut pas être ouvert car son auteur n'a pas pu être vérifié"). Si c'est le cas : **clic droit** sur le fichier → **Ouvrir** → confirmez **Ouvrir** dans la boîte de dialogue. C'est nécessaire seulement la première fois.

Une fenêtre noire (Terminal) s'ouvre. Laissez-la ouverte, c'est là que tout se passe.

**Sur Windows**

Double-cliquez sur **`Importer-dans-Notion.bat`** dans le dossier décompressé. Une fenêtre noire (Invite de commandes) s'ouvre, laissez-la ouverte.

### Étape 5 — Autoriser dans Notion

Le script va ouvrir automatiquement votre navigateur sur une page Notion qui demande votre autorisation.

1. Si vous n'êtes pas connecté à Notion, **connectez-vous** avec votre compte
2. Sur la page d'autorisation, Notion vous demande de **sélectionner les pages** auxquelles l'application aura accès. Cliquez sur **"Sélectionner les pages"** ou **"Select pages"**
3. **Cochez UNE SEULE page** de votre choix. Si vous n'en avez aucune, créez-en une depuis Notion (barre de gauche → "+" → tapez un titre comme "Jurisprudence Avril 2026" → revenez au flow d'autorisation)
4. Cliquez sur **"Autoriser"** ou **"Allow"**

Votre navigateur affiche un message "Authentification réussie" et vous demande de revenir au Terminal.

### Étape 6 — Laisser tourner

Le script crée une nouvelle base de données dans Notion appelée "Jurisprudence Avril 2026", puis commence à importer les 41 955 décisions. Vous voyez la progression dans le Terminal :

```
[250/41955] 8.2/s  ETA 85 min
[500/41955] 8.4/s  ETA 82 min
```

Comptez environ 1h30 à 2h. Vous pouvez fermer le Terminal et le relancer plus tard, le script reprend automatiquement là où il s'était arrêté.

### Étape 7 — Utiliser le corpus

Une fois l'import terminé, ouvrez Notion. Vous trouverez sur la page que vous aviez créée une nouvelle base de données "Jurisprudence Avril 2026" avec 41 955 entrées. Vous pouvez :

- **Filtrer** par Juridiction (Cour de cassation, cours d'appel, etc.), Date, Chambre, Numéro
- **Cliquer** sur une décision pour voir le texte intégral
- **Interroger l'IA Notion** : ouvrez l'IA Notion (icône AI en haut à droite ou raccourci `cmd+J` / `ctrl+J`), choisissez "Discuter avec cette page" sur la base de données, et posez des questions en langage naturel

---

## En cas de problème

### Le script s'arrête en cours

Relancez-le simplement. Il reprend automatiquement où il s'était arrêté grâce à un fichier de progression caché dans votre dossier personnel (`~/.kohen-jurisprudence/`).

### "Python 3 n'est pas installé"

Retournez à l'Étape 2 et installez Python depuis https://www.python.org. Sur Windows, n'oubliez pas de cocher **"Add Python to PATH"**.

### "Aucune page partagée avec l'application"

C'est que vous n'avez pas coché de page lors de l'autorisation Notion. Le script vous indique la marche à suivre. En résumé : créez une page dans Notion, cliquez sur les "..." en haut à droite de cette page, puis "Connexions" / "Connections", cherchez "Créateur de RAG" et confirmez. Revenez au Terminal et appuyez sur Entrée.

### "ERR_NETWORK" ou autres erreurs réseau

Vérifiez votre connexion internet. Si OK, attendez 5 minutes et relancez.

### Mac : "ne peut pas être ouvert car son auteur n'a pas pu être vérifié"

Clic droit sur `Importer-dans-Notion.command` → **Ouvrir** → confirmez **Ouvrir**. C'est nécessaire seulement la première fois.

### Besoin d'aide

Copiez le fichier `CLAUDE.md` du projet dans une conversation Claude (https://claude.ai) ou ChatGPT (https://chatgpt.com), expliquez votre problème, l'IA aura tout le contexte pour vous guider.

Aucune assistance humaine n'est assurée par le cabinet sur ce projet. Le code et la documentation sont fournis "as is".

---

## Données et responsabilité

Les décisions sont issues de **Judilibre**, base officielle de la Cour de cassation, accessible via l'API publique [api.piste.gouv.fr](https://piste.gouv.fr) sous **Licence Ouverte Etalab 2.0**.

Cadre légal : article L. 111-13 du Code de l'organisation judiciaire, article 33 de la loi n° 2019-222 du 23 mars 2019, décrets n° 2020-797 et n° 2021-1276.

Une fois importées dans votre espace Notion, **vous devenez responsable du traitement RGPD** de ces données. Sont notamment interdits :

- toute tentative de réidentification des personnes physiques mentionnées
- tout profilage, classement, évaluation ou comparaison des magistrats et membres du greffe (sanctionné par l'art. 226-18 du Code pénal : 5 ans d'emprisonnement et 300 000 € d'amende)
- tout recoupement avec d'autres bases nominatives
- toute revente sans valeur ajoutée substantielle

Cet outil ne fournit **aucun conseil juridique** et ne remplace pas une vérification sur la source officielle : [www.courdecassation.fr](https://www.courdecassation.fr). Vérifiez systématiquement le texte officiel avant tout usage professionnel.

**L'intégralité des conditions est dans [CONDITIONS.md](CONDITIONS.md). Son acceptation est requise pour utiliser le projet.**

---

## Sous le capot

- **Source** : API Judilibre / piste.gouv.fr, endpoint `/export`
- **Volume** : 41 955 décisions distinctes, environ 130 Mo de texte brut
- **Période** : du 1ᵉʳ au 30 avril 2026 (date d'indexation Judilibre, couvre l'essentiel des décisions rendues sur la période)
- **Juridictions** : Cour de cassation (1 111), cours d'appel (8 627), tribunaux judiciaires (25 812), tribunaux de commerce (6 405)
- **Authentification Notion** : OAuth 2.0 via redirection HTTPS vers GitHub Pages, aucune donnée ne transite par le cabinet
- **Parallélisme** : 10 workers, token bucket à 8 req/s pour respecter le rate limit Notion
- **Reprise** : fichier `progress.jsonl` local, idempotent

Le code source est ouvert et auditable : tout est dans `import.py`.

---

## Licence

Code sous licence MIT. Données sous Licence Ouverte Etalab 2.0 (origine Cour de cassation / DILA).
