# Visioconference-pour-EHPAD
Une Box pour faire des visioconférences avec des personnes âgées dépendantes.

Le principe :

Une box à base de Raspberry Pi qui se connecte sur une télé en HDMI dans la chambre d'une personne agée dépendante.
On peut alors l'appeler, via GoogleDuo, et elle n'a rien à faire pour décrocher.
L'appel est automatiquement accepté au bout d'une quizaine de secondes, sauf si un soignant présent dans la chambre refuse l'appel en appuyant sur le bouton rouge (une boite d'information apparait pendant ces 15 secondes).
Un soignant a également la possibilité de bloquer les appels pendant 15 min à 1 heure pour lui permettre d’intervenir tranquillement (par simple appui sur le bouton rouge), puis sélection de la durée de blocage (bouton bleu) et validation (bouton jaune).
La box est active dans une plage horaire paramétrable (par exemple de 10h00 à 19h00).
Elle peut également faire cadre photo.

Le matériel :

- Un Raspberry Pi V4B 2 Go, carte SD 32 Go
- Un plateforme Grove Base pour Raspberry : https://wiki.seeedstudio.com/Grove_Base_Hat_for_Raspberry_Pi/
- 3 boutons LED Grove : https://wiki.seeedstudio.com/Grove-LED_Button/
- 1 emetteur IR Grove : https://wiki.seeedstudio.com/Grove-Infrared_Emitter/
- 1 recepteur IR Grove : https://wiki.seeedstudio.com/Grove-Infrared_Receiver/
- 1 ventilateur 30x30 5V (j'ai choisi le SUNON 30x30x6 24 dBa) + 1 transistor NPN S8050
- 1 boitier imprimé 3D (6 faces emboitables) Merci à http://bastelstube.rocci.net/projects/MBS30_RasPi-Halter/RasPi-Halter.html pour son modèle ;-)
- 1 cable mini HDMI - HDMI  (attention à bien prendre un cable de qualité "vidéo" et pas "informatique", car tous les cables ne sont pas compatibles avec les signaux CEC pour commander la télé)
- 1 webcam USB

Le fonctionnement :

2 modes de fonctionnement sont possibles.

1) La Box est raccordée à une télé "dédiée" à la visio (petite télé ~20" que l'on peut trouver à ~ 100 EUR) : mode Cadre Photos
La télé est automatiquement allumée à l'heure programmée, et lance un diaporama aléatoire des photos présentes dans un répertoire (paramétrable).
La durée de transition entre les photos est paramétrable.
Seules les photos .jpg  sont prises en compte. 
Les photos sont automatiquement mises à l'échelle si elles sont trop grandes, inutile de les redimensionner avant.
Pendant les heures de fonctionnement, lorsqu'un appel arrive (ou appui sur un bouton menu), la télé est automatiquement allumée si elle avait été éteinte manuellement.
Avant et après un appel, il est possible d'envoyer un signal IR de "MUTE" afin de couper / remettre le son de la "vraie" TV de la personne (souvent allumée et très fort ;-)), afin de couper le son de la TV pendant la visoconférence.
La télé est automatiquement éteinte à l'heure programmée de mise en veille.
 
2) La Box est raccordée à la télé principale de la personne : mode TV
Il n'y a alors pas de gestion ON/OFF de la TV aux heures programmées.
Par contre la TV sera allumée, si elle est éteinte, lors d'un appel (ou appui sur un bouton menu).
En cas d'appel (ou appui sur un bouton menu), la TV bascule automatiquement sur l'entrée HDMI du raspberry (paramétrable).
En fin d'appel, la TV est rebasculée automatiquement sur l'entrée TV.
Le diaporama est inutile dans ce mode. 


En cas de télé dédiée, il y a possibilité d'activer un diaporama de photos.
Lorsqu'un appel est reçu, la télé s'allume (si éteinte) et bascule automatiquement sur l'entrée HDMI du Raspberry.
Une boite de dialogue apparait pendant 15 secondes et permet à un soignant présent dans la chambre de refuser l'appel en appuyant sur le bouton rouge
Sinon, l'appel est accepté automatiquement (sans aucune intervention de la personne agée) au bout de 15 secondes environ.
En fin d'appel, la télé est automatiquement remise sur l'entrée TV, ou le diaporama photo reprend.
Il y a aussi la possibilité de 

Les principales fonctions :
- Programmation des heures de "veille" : par exemple de 10h00 à 19h00
- Diaporama photos possible (dans le cas ou le Raspberry est branché sur une télé dédié)
- Commande de la télé via CEC (HDMI) ou Infrarouge (un enregistrement de la télécommande via "irrecord" est nécessaire). Le CEC est toujours nécessaire pour la gestion ON/OFF de la télé (car il est impossible de connaitre l'état de la télé en cas de commande IR), mais la commande IR est possible pour le passage HDMI / TV, car j'ai pu constater que les commandes CEC de changement de source ne sont pas compatibles avec toutes les télés, contrairement au ON/OFF
- Pendant un appel, envoi d'une commande "Mute" à la télé (via IR), dans le cas d'un fonctionnement sur un écran dédié (car la "vraie" télé est souvent allumée, et le son souvent fort ;-)). Evidement, à la fin de l'appel, la commande "Mute" est renvoyée pour remettre le son de la télé.
- Détection de l'insertion d’une clé USB pour gérer le chargement de photos du cadre photos (via un menu, toujours avec les boutons bleu (navigation) et jaune (validation))
- Un menu "systeme" accessible par appui direct sur le bouton bleu
- Un journal d'appels
- Un journal système, réinitialisé à chaque démarrage
