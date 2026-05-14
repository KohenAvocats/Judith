# Conditions d'utilisation

Ce document précise le cadre légal et les obligations à respecter lors de l'utilisation du pack Judith et des données qu'il importe dans votre espace Notion. **La lecture intégrale est indispensable avant tout usage professionnel.**

## 1. Source des données

Les 41 955 décisions importées dans votre Notion sont issues de **Judilibre**, base officielle de la Cour de cassation, accessible via l'API publique [api.piste.gouv.fr](https://piste.gouv.fr) opérée par la Direction de l'information légale et administrative (DILA) pour le compte de la Cour de cassation.

Cadre légal de cette mise à disposition :
- Article **L. 111-13** du Code de l'organisation judiciaire
- Article **33** de la loi n° 2019-222 du 23 mars 2019 de programmation 2018-2022 et de réforme pour la justice
- Décret n° 2020-797 du 29 juin 2020 relatif à la mise à la disposition du public des décisions des juridictions judiciaires et administratives
- Décret n° 2021-1276 du 30 septembre 2021 fixant le calendrier de mise à disposition

## 2. Licence

Les données sont diffusées sous **Licence Ouverte Etalab 2.0** ([texte de la licence](https://www.etalab.gouv.fr/licence-ouverte-open-licence/)). Cette licence autorise la réutilisation libre et gratuite, y compris à des fins commerciales, sous réserve :

- de **mentionner la source** (« Données issues de la Cour de cassation, via l'API Judilibre, api.piste.gouv.fr »)
- d'indiquer la **date de la dernière mise à jour** des données utilisées (ici : avril 2026)
- de **respecter les restrictions légales** énoncées au point 3 ci-dessous

## 3. Restrictions impératives applicables aux décisions de justice

L'article **L. 111-13, alinéa 3 du Code de l'organisation judiciaire** énonce une **interdiction absolue, pénalement sanctionnée** :

> « Les données d'identité des magistrats et des membres du greffe ne peuvent faire l'objet d'une réutilisation ayant pour objet ou pour effet d'évaluer, d'analyser, de comparer ou de prédire leurs pratiques professionnelles réelles ou supposées. La violation de cette interdiction est punie des peines prévues aux articles 226-18, 226-24 et 226-31 du code pénal. »

Sanction : **5 ans d'emprisonnement et 300 000 € d'amende** (article 226-18 du code pénal).

**En pratique, vous ne pouvez pas** :
- Construire un profil ou un classement par magistrat (« le juge X statue dans tel sens dans Y % des cas »)
- Croiser les noms de magistrats / greffiers / avocats avec d'autres bases pour les identifier ou les évaluer
- Publier un classement comparatif de juridictions ou de magistrats fondé sur ces données
- Entraîner un modèle prédictif sur les pratiques individuelles de magistrats

## 4. Périmètre de l'occultation et responsabilité

L'article L. 111-13, alinéa 1 du Code de l'organisation judiciaire impose une occultation systématique des **nom et prénoms des personnes physiques** parties à l'instance et tiers mentionnés dans la décision, préalablement à sa mise à disposition publique.

En revanche, l'alinéa 2 du même article précise que l'occultation des éléments d'identification des **magistrats, membres du greffe, avocats, experts judiciaires, témoins, auxiliaires de justice** n'est **pas systématique** : elle reste **facultative** et n'intervient que sur demande motivée présentée à la Cour de cassation ou au Conseil d'État, lorsque la divulgation est de nature à porter atteinte à la sécurité ou au respect de la vie privée de l'intéressé.

**Concrètement**, le corpus que vous importez contient donc, dans la plupart des décisions :
- les nom et prénoms des magistrats ayant siégé
- les nom et prénoms des membres du greffe
- les nom et prénoms des avocats des parties
- parfois les nom et prénoms d'experts, témoins ou auxiliaires de justice

Ces mentions ne résultent pas d'une erreur d'anonymisation : elles correspondent au régime légal d'open data tel qu'il a été pensé par le législateur, qui a privilégié la transparence de l'institution judiciaire sur les professionnels du droit tout en protégeant les justiciables.

**En important ces décisions dans votre workspace Notion, vous devenez responsable du traitement** des données nominatives qu'elles contiennent au sens du Règlement général sur la protection des données (RGPD, règlement UE 2016/679).

À ce titre, vous devez :
- respecter l'interdiction de profilage des magistrats et membres du greffe énoncée au point 3 ci-dessus (art. L. 111-13, al. 3 COJ), sanctionnée pénalement
- ne pas tenter de réidentifier les parties ou tiers anonymisés
- ne pas croiser les données nominatives avec d'autres fichiers personnels susceptibles de constituer un profilage
- répondre aux demandes d'effacement ou de rectification que pourrait formuler une personne identifiée (articles 16, 17 et 21 du RGPD)
- ne pas conserver ces données au-delà du strict nécessaire à votre usage propre

## 5. Limitation de responsabilité du cabinet Kohen Avocats

Le cabinet Kohen Avocats publie ce projet **à titre purement informatif et collaboratif**, sans aucune garantie expresse ou implicite. En particulier :

- **Aucun conseil juridique** n'est délivré au travers de cet outil
- **Aucune relation client** ne naît du téléchargement ou de l'usage du projet
- **Aucune garantie d'exactitude, d'exhaustivité ou de mise à jour** des décisions importées n'est offerte ; toute citation dans un acte professionnel suppose une vérification préalable sur la source officielle : [www.courdecassation.fr](https://www.courdecassation.fr)
- **Aucune assistance** technique ou juridique n'est assurée par le cabinet sur ce projet
- Le cabinet ne saurait être tenu pour responsable d'un usage non conforme aux conditions énumérées dans le présent document, ni des conséquences d'un tel usage

## 6. Pour les avocats utilisateurs : implications déontologiques

Si vous êtes avocat et que vous utilisez ce corpus dans le cadre de votre activité professionnelle, vous restez seul responsable du respect de vos obligations déontologiques, notamment :

- **Devoir de compétence et de diligence** : vérification systématique de toute décision sur la source officielle avant citation dans un acte
- **Secret professionnel** : aucune donnée client ne doit être croisée avec ce corpus dans des conditions susceptibles de compromettre le secret
- **Indépendance** : aucune sollicitation ni démarchage automatisé ne peut être construit à partir de ces données
- **Devoir de prudence** : aucune communication, publication ou tribune ne peut s'appuyer sur un classement de magistrats ou une analyse comparative de juridictions issue de ces données

## 7. Acceptation

L'installation et l'utilisation du pack Judith **valent acceptation pleine et entière** des présentes conditions. En cas de désaccord, l'utilisateur doit s'abstenir de tout téléchargement, installation ou usage.

---

Texte mis à jour le 14 mai 2026. Version applicable à Judith v1.0.0.
