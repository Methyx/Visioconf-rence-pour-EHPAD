# Visioconference-pour-EHPAD
Une Box à base de Raspberry Pi pour faire des visioconférences avec des personnes âgées dépendantes

Le principe :
Une box qui se connecte sur une télé en HDMI (écran télé dédié pour la visio, ou télé "normale" de la personne)
En cas de télé dédiée, il y a possibilité d'activer un diaporama de photos.
Lorsqu'un appel est reçu, la télé s'allume (si éteinte) et bascule automatiquement sur l'entrée HDMI du Raspberry.
Une boite de dialogue apparait pendant 15 secondes et permet à un soignant présent dans la chambre de refuser l'appel en appuyant sur le bouton rouge
Sinon, l'appel est accepté automatiquement (sans aucune intervention de la personne agée) au bout de 15 secondes environ.
En fin d'appel, la télé est automatiquement remise sur l'entrée TV, ou le diaporama photo reprend.
Il y a aussi la possibilité de bloquer les appels pendant 15 min à 1 heure pour permettre à un soignant d’intervenir tranquillement (par simple appui sur le bouton rouge), puis sélection de la durée de blocage (bouton bleu) et validation (bouton jaune)

Les principales fonctions :
- Programmation des heures de "veille" : par exemple de 10h00 à 19h00
- Diaporama photos possible (dans le cas ou le Raspberry est branché sur une télé dédié)
- Commande de la télé via CEC (HDMI) ou Infrarouge (un enregistrement de la télécommande via "irrecord" est nécessaire). Le CEC est toujours nécessaire pour la gestion ON/OFF de la télé (car il est impossible de connaitre l'état de la télé en cas de commande IR), mais la commande IR est possible pour le passage HDMI / TV, car j'ai pu constater que les commandes CEC de changement de source ne sont pas compatibles avec toutes les télés, contrairement au ON/OFF
- Pendant un appel, envoi d'une commande "Mute" à la télé (via IR), dans le cas d'un fonctionnement sur un écran dédié (car la "vraie" télé est souvent allumée, et le son souvent fort ;-)). Evidement, à la fin de l'appel, la commande "Mute" est renvoyée pour remettre le son de la télé.
- Détection de l'insertion d’une clé USB pour gérer le chargement de photos du cadre photos (via un menu, toujours avec les boutons bleu (navigation) et jaune (validation))
- Un menu "systeme" accessible par appui direct sur le bouton bleu
- Un journal d'appels
- Un journal système, réinitialisé à chaque démarrage
