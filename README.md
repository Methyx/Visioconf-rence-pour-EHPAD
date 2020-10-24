# Visioconference-pour-EHPAD
Une Box pour faire des visioconférences avec des personnes âgées dépendantes.


=== Le principe :

Une box à base de Raspberry Pi qui se connecte sur une télé en HDMI dans la chambre d'une personne agée dépendante.
On peut alors l'appeler, via GoogleDuo, et elle n'a rien à faire pour décrocher.
L'appel est automatiquement accepté au bout d'une quizaine de secondes, sauf si un soignant présent dans la chambre refuse l'appel en appuyant sur le bouton rouge (une boite d'information apparait pendant ces 15 secondes).
Un soignant a également la possibilité de bloquer les appels pendant 15 min à 1 heure pour lui permettre d’intervenir tranquillement (par simple appui sur le bouton rouge), puis sélection de la durée de blocage (bouton bleu) et validation (bouton jaune).
La box est active dans une plage horaire paramétrable (par exemple de 10h00 à 19h00).
Elle peut également faire cadre photo.


=== Le matériel :

- Un Raspberry Pi V4B 2 Go, carte SD 32 Go
- Un plateforme Grove Base pour Raspberry : https://wiki.seeedstudio.com/Grove_Base_Hat_for_Raspberry_Pi/
- 3 boutons LED Grove : https://wiki.seeedstudio.com/Grove-LED_Button/
- 1 emetteur IR Grove : https://wiki.seeedstudio.com/Grove-Infrared_Emitter/
- 1 recepteur IR Grove : https://wiki.seeedstudio.com/Grove-Infrared_Receiver/
- 1 ventilateur 30x30 5V (j'ai choisi le SUNON 30x30x6 24 dBa) + 1 transistor NPN S8050
- 1 boitier imprimé 3D (6 faces emboitables) Merci à http://bastelstube.rocci.net/projects/MBS30_RasPi-Halter/RasPi-Halter.html pour son modèle ;-)
- 1 cable mini HDMI - HDMI  (attention à bien prendre un cable de qualité "vidéo" et pas "informatique", car tous les cables ne sont pas compatibles avec les signaux CEC pour commander la télé)
- 1 webcam USB


=== Le fonctionnement :

2 modes de fonctionnement sont possibles.

1) La Box est raccordée à une télé "dédiée" à la visio (petite télé ~20" que l'on peut trouver à ~ 100 EUR) : mode Cadre Photos

Ce mode est utile si la "vraie" TV de la personne ne possède pas de prise HDMI, ou si la fonction "Cadre Photos" vous intéresse.
La télé est automatiquement allumée à l'heure programmée, et lance un diaporama aléatoire des photos présentes dans un répertoire (paramétrable).
La durée de transition entre les photos est paramétrable.
Seules les photos .jpg  sont prises en compte. 
Les photos sont automatiquement mises à l'échelle si elles sont trop grandes, inutile de les redimensionner avant.
Pendant les heures de fonctionnement, lorsqu'un appel arrive (ou appui sur un bouton menu), la télé est automatiquement allumée si elle avait été éteinte manuellement.
Avant et après un appel, il est possible d'envoyer un signal IR de "MUTE" afin de couper / remettre le son de la "vraie" TV de la personne (souvent allumée et très fort ;-)), afin de couper le son de la TV pendant la visoconférence.
La télé est automatiquement éteinte à l'heure programmée de mise en veille.
 
2) La Box est raccordée à la télé principale de la personne : mode TV

Il n'y a alors pas de gestion ON/OFF de la TV aux heures programmées.
Par contre, si elle est éteinte, la TV sera allumée lors d'un appel (ou appui sur un bouton menu).
En cas d'appel (ou appui sur un bouton menu), la TV bascule automatiquement sur l'entrée HDMI du raspberry (paramétrable).
En fin d'appel, la TV est rebasculée automatiquement sur l'entrée TV.
Le diaporama est donc inutile dans ce mode. 

Dans les 2 modes :

Les commandes ON/OFF de la télé sur laquelle est branchée le Raspberry se font par les commandes CEC de l'HDMI.
*** Attention à vérifier que la télé est bien compatible avec le CEC (qui s'appelle différemment selon les marques de télé !) ***
Par contre, pour les passages en entrée HDMI ou TV, j'ai pu constater que toutes les télés ne sont pas complètement compatibles avec la norme CEC ... :-(
Il est donc possible d'envoyer des commandes infrarouges pour ces actions.
Il faudra alors enregistrer les commandes correspondantes avec la télécommande d'origine (via irrecord), et indiquer les commandes à lancer dans le fichier paramètres.

L'insertion d'une clé USB est détectée (pendant les heures de "réveil") pour ajouter des photos au diaporama. On peut alors choisir, à l'aide des boutons bleu (Navigation) et jaune (Validation) le répertoire de la clé qui contient les fichiers .jpg. Après validation, ils sont automatiquement copiés dans le répertoire correspondant du Raspberry.

Lors d'un appel, une boite de dialogue apparait pendant 15 secondes et permet, en appuyant sur le bouton rouge, de refuser un appel entrant.

Pendant les heures de "réveil", un appui sur le bouton rouge fait apparaitre un menu de "blocage des appels". A l'aide des boutons bleu (Navigation) et jaune (Validation), on peut choisir la durée de blocage (15, 30, 45 ou 60 minutes). Le Raspberry refusera alors tous les appels entrants pendant cette période. Le bouton rouge reste allumé pendant toute la durée du blocage.

Pendant les heures de "réveil", un appui sur le bouton bleu fait apparaitre un menu "système". Il est alors possible de choisir quelques commandes système : quitter, reboot, ...

Un journal d'appel est enregistré, et conservé, automatiquement : appels reçus, accepté / refusé, durée de l'appel

Un journal système est également créé. Il est réinitialisé à chaque démarrage du programme (mais la version précédente est sauvegardée).


=== Gestion à distance :

En cas d'accès au Raspberry via VNC à distance, il est possible de "simuler" des actions sur les boutons à l'aide du clavier :
"r" pour le bouton rouge  /  "b" pour le bouton bleu  /  "j" pour le bouton jaune
Dans les menus, il suffit d'utiliser la flèche vers le bas pour Naviguer et la touche Entrée pour Valider
L'appui sur la touche ESC permet de basculer en mode plein écran ou pas (utile pour accéder à des commandes du Raspberry)
L'appui sur la touche END permet de mettre fin au programme


=== Fichier "Parametres.txt"

Ce fichier (commenté) permet de régler différents paramètres du programme.
Attention à bien respecter les règles suivantes :
Les lignes commençant par "#" sont des commentaires, pour expliquer le paramètre qui suit. Elles sont ignorées par le programme
Sur la ligne suivante vient le nom du paramètre : Il ne faut PAS le modifier !!
Sur la ligne suivante vient la valeur du paramètre : Elle est précédée de plusieurs espaces (c'est juste pour la lisibilité, ils seront ignorés par le programme). La valeur est soit un chiffre, soit codifiée comme expliquée dans les commentaires qui précèdent. Attention de bien respecter la casse des valeurs attendues !!

Par exemple, le paramètre 'Demarrage' :
3 valeurs sont possibles : 'Raspberry'  ou  'Visio'  ou  'Photos'   (ne pas mettre les ' ')
Cela permet de fixer le comportement au démarrage du programme :
Raspberry : le programme est quitté immédiatement (utilse lorsque l'on a parametré le lancement automatique du programme au démarrage du Raspberry)
Visio : le cadre photos n'est pas activé
Photos : le cadre photos est activé

Si vous ne respectez pas exactement l'une de ces 3 valeurs, le paramètre ne sera pas compris

