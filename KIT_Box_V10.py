#!/usr/bin/env /usr/bin/python3
# -*- coding: utf-8 -*-

from grove.gpio import GPIO
import time
import os
import sys
from datetime import datetime
import pygame
from pygame.locals import *
import glob
from random import *
from pymouse import PyMouse
import subprocess
import psutil
import pytesseract
from lirc import Lirc

#
# ===== Procedures de gestion de la télé =====
#    
def statut_tele (fichier_log) :
    # retourne 'standby' si OFF, 'on' si ON, ou "erreur"
    cmd = "echo 'pow 0' | cec-client RPI -s -d 1 | grep power | awk '{ print $3 }'"
    try :
        o = os.popen (cmd,'r')
        st = str(o.read())
        if ("on" or "in") in st:
            s = "on"
        else :
            if "standby" in st :
                s = "standby"
            else :
                s = "erreur"
        t = "Statut tele = " + s
        print_log (fichier_log,t)
        return s
    except :
        print_log (fichier_log, "Erreur Statut tele")
        return "erreur"

def allumer_tele (fichier_log) :
    if statut_tele(fichier_log) != "on" :
        print_log (fichier_log,"Allumage télé")
        try:
            os.system("echo 'on 0' | cec-client RPI -s -d 1")
            time.sleep(5)
            i = 1
            while statut_tele(fichier_log != "on") and (i <= 5) :
                time.sleep(5)
                i = i+1
            if i==6 :
                print_log (fichier_log, "Erreur allumage tele : 5 tentatives")
        except:
            print_log (fichier_log, "Erreur allumage télé : erreur inconnue")
            return

def eteindre_tele (fichier_log) :
    print_log(fichier_log,"Extinction télé")
    try:
        os.system("echo 'standby 0' | cec-client RPI -s -d 1")
        time.sleep(2)
    except:
        print_log (fichier_log,"Erreur extinction télé")
        return

def hdmi_tele_CEC (rasp,hdmi,fichier_log) :
    t = "Passage télé en HDMI" + str(hdmi) + " via CEC"
    print_log(fichier_log,t)
    try:
        cmd = "echo 'tx " + str(rasp) + "F:82:" + str(hdmi) + "0:00' | cec-client RPI -s -d 1"
        os.system(cmd)
        #time.sleep(2)
    except:
        print_log (fichier_log,"Erreur de passage en HDMI")
        return
    #os.system("echo 'as' | cec-client RPI -s -d 1")  # definir RPI actif
def hdmi_tele_IR (ir,telecommande,commandes,fichier_log) :
    t = "Passage télé en HDMI via IR : Telecommande = " + str(telecommande)
    print_log(fichier_log,t)
    i=0
    while i < len(commandes) :
        print_log (fichier_log,str(commandes[i]))
        ir.send_once(commandes[i],telecommande,1)
        time.sleep(1)
        i=i+1
        
def tv_tele_CEC (rasp,fichier_log) :
    print_log(fichier_log,"Passage télé en entree TV")
    try:
        os.system("echo 'as' | cec-client RPI -s -d 1")  #  RPI actif
        cmd = "echo 'tx " + str(rasp) + "0:9D:" + str(rasp) + "0:00' | cec-client RPI -s -d 1"
        os.system(cmd)
        time.sleep(0,5)
    except:
        print_log (fichier_log,"Erreur de passage en TV")
        return
def tv_tele_IR (ir,telecommande,commandes,fichier_log) :
    t = "Passage télé en entrée TV via IR : Telecommande = " + str(telecommande)
    print_log(fichier_log,t)
    i=0
    while i < len(commandes) :
        print_log (fichier_log,str(commandes[i]))
        ir.send_once(commandes[i],telecommande,1)
        time.sleep(1)
        i=i+1
#
# ===== Procédures de Gestion des Parametres =====
#
def lire_parametres (fichier) :
    with open(fichier,"r") as fic_param :
        params = fic_param.read().split("\n") 
    dico={}
    i=0
    while i<len(params) and params[i]!="" :
        intitule = params[i].strip()
        if intitule[0]!="#" : 
            valeur = params[i+1].strip()
            if "CommandeIR" in intitule :
                dico[intitule] = valeur.split(",")
            else :
                dico[intitule] = valeur
            i = i+2
        else :
            i = i+1
    return dico

def mode_JN(debut,fin) :
    now = datetime.now()
    h_m = int(now.strftime("%H%M"))
    if (h_m >= debut and h_m < fin):
        return "J"
    else :
        return "N"

#
# ===== Procedures de Gestion des fichiers Journaux =====
#
def init_log(fic_log) :
    try :  # Copie le fichier precedent, si il existe, en .bak
        with open(fic_log,"r") as journal :
            log_prec = journal.read()
        prec = fic_log + ".bak"
        with open(prec,"w") as journal_prec :
            journal_prec.write(log_prec)
    except :
        a=1
    with open(fic_log,"w") as journal :
        t = str(datetime.now())+" - Initialisation du fichier journal" + "\n"
        journal.write(t)
    
def print_log(fic_log,log) :
    with open(fic_log,"a") as journal :
        t = str(datetime.now())+" - "+ log + "\n"
        journal.write(t)

# 
# ===== Procédure de gestion de menu =====
# 
def affiche_menu(image, liste_titre, liste_choix, duree) :
    # image sera positionnée à gauche de la fenetre
    # les textes des menus seront centrés dans la place restant à droite
    # sans activité pendant 'duree' secondes, le menu est quitté
    led_bleu = GPIO(22, GPIO.OUT)
    bouton_bleu = GPIO(23, GPIO.IN)
    led_jaune = GPIO(24, GPIO.OUT)
    bouton_jaune = GPIO(25, GPIO.IN)
    led_rouge = GPIO(16, GPIO.OUT)
    led_rouge.write(0)
    led_bleu.write(1)
    led_jaune.write(1)   
    # Preparation de la fenetre menu
    green=(0,255,0)
    blue=(0,0,180)
    yellow=(255,255,0)
    white=(255,255,255)
    black=(0,0,0)
    grey=(199,208,204)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
    pygame.init()
    fenetre_menu = pygame.display.set_mode((1280,720),RESIZABLE)
    pygame.display.set_caption("Menu")
    fenetre_menu.fill(grey)
    if image != '' :
        im = pygame.image.load(image).convert()
        largeur_image = im.get_size()[0]
        if im.get_size()[1] < 650 :
            pos_image_V = int((650-im.get_size()[1])/2)
        else :
            pos_image_V = 0
        fenetre_menu.blit(im,(0,pos_image_V))
    else :
        largeur_image = 0
    centre_texte = largeur_image + int((1280-largeur_image)/2)
    ligne = 0
    interligne = 25
    
    pygame.font.init()
    font_titre = pygame.font.Font('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',24)
    titre = []
    titre_rect = []
    index = 0
    while index < len(liste_titre) :
        titre.append (font_titre.render(liste_titre[index], True, blue))
        titre_rect.append (titre[index].get_rect())
        ligne = ligne + interligne
        titre_rect[index].center = (centre_texte,ligne)
        fenetre_menu.blit(titre[index], titre_rect[index])
        index = index + 1
    ligne = ligne + interligne  # ligne vide 
    font_menu = pygame.font.Font('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',20)
    menu=[]
    menu_rect=[]
    index=0
    while index < len(liste_choix) :
        if index == 0 :
            menu.append (font_menu.render(liste_choix[index],False,grey,black))
        else :
            menu.append (font_menu.render(liste_choix[index],False,black,grey))
        menu_rect.append (menu[index].get_rect())
        ligne = ligne + interligne
        menu_rect[index].center=(centre_texte,ligne)
        fenetre_menu.blit(menu[index],menu_rect[index])
        index=index+1   
    pygame.display.flip()   
    long_menu = len(menu)-1
    pos_menu = 0
    t0 = int(time.time())
    d = int(time.time())-t0
    choix = False
    naviguer = False
    while d <= duree and choix==False :
        for event in pygame.event.get() :
            if event.type==pygame.KEYDOWN :   # Fleche Bas pour naviguer
                if event.key==pygame.K_DOWN :
                    naviguer = True
                if event.key==pygame.K_RETURN :  # Entree pour valider
                    choix = True
        if bouton_bleu.read()==0 :  # bouton Naviguer appuyé
            naviguer= True
        if bouton_jaune.read()==0 :  # bouton Valider appuyé               
               choix = True
        if naviguer :
            t0 = int(time.time()) # réinitialisation de la tempo
            menu[pos_menu]=font_menu.render(liste_choix[pos_menu],False,black,grey)
            fenetre_menu.blit(menu[pos_menu],menu_rect[pos_menu])
            pos_menu = pos_menu + 1
            if pos_menu > long_menu :
                pos_menu = 0
            menu[pos_menu]=font_menu.render(liste_choix[pos_menu],False,grey,black)
            fenetre_menu.blit(menu[pos_menu],menu_rect[pos_menu])
            pygame.display.flip()
            naviguer = False                 
        time.sleep(0.2)
        d = int(time.time())-t0
    #sortie    
    led_bleu.write(0)
    led_jaune.write(0)
    pygame.quit()
    return choix,pos_menu    

#
# ===== Procédures liées à Google DUO =====
#
def google_duo(fichier) :  # lancer google duo s'il n'est pas déjà lancé
    liste = psutil.pids()
    trouve = False
    try :
        for p in liste :
            if "chromium" in (psutil.Process(p).name()):
                trouve = True
    except :
        print_log(fichier, "erreur dans la recherche de process chromium")
    if not trouve :
        print_log (fichier, "Process Chromium non trouvé : lancement de GoogleDuo")
        subprocess.Popen(["/usr/bin/chromium-browser", "--profile-directory=Default", "--app-id=imgohncinckhbblnlmaedahepnnpmdma"])
        time.sleep(5)
    else :
        print_log(fichier, "Process Chromium trouvé")
        
def capture(fichier,x,y,largeur,longueur) :
    #Capture de la zone definie dans le fichier defini
    adr_zone=str(x)+","+str(y)+","+str(largeur)+","+str(longueur)
    subprocess.call(["scrot", "-a"+adr_zone, fichier])

def surveillance_notif() :
    #Surveillance d'apparition de la notification Google Home
    alarme = False
    qui = ""
    type_notif = ""
    img_notif="/home/pi/Documents/Screenshots/notification.png"
    capture (img_notif,945,55,200,25)
    texte = pytesseract.image_to_string (img_notif)
    if "duo.google.com" in texte :
        alarme=True
        img_notif="/home/pi/Documents/Screenshots/appelant.png"
        capture (img_notif,915,80,230,25)
        qui = pytesseract.image_to_string (img_notif)
        for car in qui :  # enlève les caractères spéciaux
            if ord(car)<32 or ord(car)>175 :
                qui = qui.replace(car," ")
        img_notif="/home/pi/Documents/Screenshots/type_notif.png"
        capture (img_notif,915,100,230,25)
        texte = pytesseract.image_to_string (img_notif)
        if "entrant" in texte :
            type_notif = "entrant"
        else :
            type_notif = "manqué"
    return alarme, qui, type_notif

def verif_appel_en_cours() :
    # surveillance de l'intitulé de la fenetre GoogleDuo
    # "ENTRANT" : Appel en cours si intitulé est "Appel vidéo Duo"
    # "NON" : Detection de fin d'appel si l'intitulé est 'Démarrer un appel"
    # "OUI" : sinon (l'appel est en cours avec la vidéo)    
    img_duo = "/home/pi/Documents/Screenshots/EnTeteDuo.png"
    capture (img_duo,400,100,500,150)
    texte = pytesseract.image_to_string (img_duo)
    #Si la fenetre affiche Démarrer un appel, l'appel est fini
    if "Démarrer un appel" in texte :
        en_cours = "NON"
    #Si la fenetre affiche Appel vidéo Duo, l'appel est en attente d'acceptation / refus
    elif "Appel vidéo Duo" in texte :
        en_cours = "ENTRANT"
    else :
        en_cours = "OUI"
    return en_cours

def gestion_appel_duo(fic_log, fic_appels) :
    souris = PyMouse()
    led_rouge = GPIO(16, GPIO.OUT)
    bouton_rouge = GPIO(17, GPIO.IN)    
    # Preparation de la boite d'acceptation
    green=(0,255,0)
    blue=(0,0,180)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (200,250)
    pygame.init()
    boite = pygame.display.set_mode((850,300),RESIZABLE)
    im = pygame.image.load('/home/pi/Documents/Screens/Image_BoiteAttente.png').convert()
    boite.blit(im,(0,0))
    pygame.font.init()
    font_obj = pygame.font.Font('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',16)
    # Allume le bouton rouge
    led_rouge.write(1)
    #préparation du décompte de 15 secondes
    refus=False
    t0 = int(time.time())
    d = 0   

    # Gestion de l'acceptation
    while verif_appel_en_cours()=="ENTRANT" and refus==False and d<15 :
        d=int(time.time())-t0
        reste=15-d
        Decompte = "Connexion dans "+ str(reste) + " secondes  "
        texte_surface_obj2 = font_obj.render(Decompte, True, green, blue)
        boite.blit(texte_surface_obj2, (530,220))
        pygame.display.flip()
        for event in pygame.event.get() :
            if event.type==pygame.KEYDOWN :   # ESCAPE pour annuler
                if event.key==pygame.K_ESCAPE :
                    refus = True
        if bouton_rouge.read()==0: #bouton appuyé
            refus = True
    #fin du decompte
    pygame.quit()
    led_rouge.write(0)  # eteint le bouton rouge
    if refus :
        # L'appel a été refusé
        souris.click (550,645)  # clic sur le bouton "refuser"
        t="Appel refusé par appui sur le bouton"
        print_log(fic_log,t)
        print_log(fic_appels,t)
        time.sleep(1)
    else :
        # L'appel est accepté automatiquement
        souris.click(730,645)  #clic sur le bouton Accepter de Google Duo
        t="Appel accepté automatiquement"
        print_log(fic_log,t)
        print_log(fic_appels,t)
        time.sleep(6)
        # Attente fin appel
        d = 0
        ventilo = False
        while verif_appel_en_cours() == "OUI" :
            gestion_ventilo(65,70)
            time.sleep(5)
            d = d+5
        # Appel fini
        t="Appel terminé. Duree de l'appel = " + str(d) + " secondes"
        print_log(fic_log,t)
        print_log(fic_appels,t)
    return
#
# ===== Procédures Systeme =====
#
def gestion_ventilo(temp_marche,temp_arret) :
    ventilateur = GPIO(18, GPIO.OUT)
    # vérifier la température et gérer le ventilo
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ftemp:
        current_temp = int(ftemp.read()) / 1000
    if current_temp > temp_marche :
        ventilateur.write(1)  # demarrer ventilateur
    if current_temp < temp_arret :
        ventilateur.write(0)  # arreter ventilo
    return
  
def detecte_cle_usb(dossier_usb_prec) :
    dossier_usb = []
    for dossier in os.listdir('/media/pi/'):
        dossier_usb.append(dossier)
    nouveau = list(set(dossier_usb) - set(dossier_usb_prec))
    if len(nouveau) > 0 :
        cle_usb = "/media/pi/" + str(nouveau[0])
        liste_rep = []
        for fic in os.listdir(cle_usb):
            f = os.path.join(cle_usb,fic)
            if os.path.isdir(f) :
                liste_rep.append("/"+fic)
    else :
        cle_usb = ""
        liste_rep=[]
    return dossier_usb, cle_usb, liste_rep  
#
# ===== Procédures de Gestion du Cadre Photo =====
#
def init_photos(rep) :
    #Initilisation de la liste de fichiers photo
    liste=glob.glob(rep+"*.jpg")
    complement=(glob.glob(rep+"*.JPG"))
    i=0
    while i<len(complement) :
        liste.append(complement[i])
        i=i+1
    return liste

def change_photo(master, x_max, y_max, photo) :
    # Change la photo qui va etre affichee en fond d'ecran dans la fenetre master
    
    # efface la photo precedente
    im = pygame.image.load('/home/pi/Documents/Screens/fond_noir_1280x768.jpg').convert()
    master.blit(im,(0,0))
    pygame.display.flip()
    
    im = pygame.image.load(photo).convert()
    rect = im.get_rect()
    #définir les coefficients de mise à l'echelle
    if rect.width > x_max :
        coef1 = x_max/rect.width
    else :
        coef1 = 1
    if rect.height > y_max :
        coef2 = y_max/rect.height
    else :
        coef2 = 1
    coef=min(coef1,coef2)
    #redimensionnement de la photo
    new_larg = int(rect.width*coef)
    new_haut = int(rect.height*coef)
    im = pygame.transform.scale(im,(new_larg,new_haut))
    #definir les decalages x et y pour centrer la photo
    if new_larg < x_max :
        new_x = int((x_max-new_larg)/2)
    else :
        new_x = 0
    if new_haut < y_max :
        new_y = int(y_max-new_haut)/2
    else :
        new_y = 0
    #afficher la photo
    master.blit(im,(new_x,new_y))
    pygame.display.flip()  # affiche la photo
    souris = PyMouse()
    souris.move(0,y_max)  # fait disparaitre la souris
    

#
# ===== Programme Principal =====
#

# Lecture du fichier des parametres
fichier_parametres = "/home/pi/Documents/Parametres.txt"
parametres = lire_parametres (fichier_parametres)

# si le démarrage est "Raspberry", on quitte directement
if parametres["Demarrage"] == "Raspberry" :
    sys.exit()
    
# Initialisation du fichier Journal systeme
fic_log = parametres["Journal_Systeme"]
init_log(fic_log)
#Initialisation du fichier Journal d'appels
fic_appels = parametres["Journal_Appels"]

# Initialisation des E/S GPIO
led_rouge = GPIO(16, GPIO.OUT)
bouton_rouge = GPIO(17, GPIO.IN) 
led_bleu = GPIO(22, GPIO.OUT)
bouton_bleu = GPIO(23, GPIO.IN)
led_jaune = GPIO(24, GPIO.OUT)
bouton_jaune = GPIO(25, GPIO.IN)
ventilateur = GPIO(18, GPIO.OUT)
led_rouge.write(0)
led_bleu.write(0)
led_jaune.write(0)

ir = Lirc()

# initialisation de la tele
hdmi_rasp = int(parametres["HDMI_Raspberry"])
mode_ecran = parametres["Mode_TV"]  # "TV" si le Rasp est branché sur une télé, "Ecran" si le Rasp est un écran dédié
if mode_ecran == "TV" :
    print_log(fic_log,"Mode TV")
    if statut_tele(fic_log) == "on" :  # en mode TV, on repasse la télé sur "TV" si elle est allumée
        if parametres["Commande_tele"]=="CEC" :  
            tv_tele_CEC (hdmi_rasp, fic_log)
        else :
            tv_tele_IR (ir,parametres["Telecommande_tele"],parametres["CommandeIR_tele_TV"],fic_log)
else :
    print_log(fic_log,"Mode Ecran")
    allumer_tele(fic_log)  # en mode Ecran, on allume la tele si elle est eteinte

# initialisation ventilo
ventilo = False
with open('/sys/class/thermal/thermal_zone0/temp', 'r') as ftemp:
    current_temp = int(ftemp.read()) / 1000
t="Température = "+str(current_temp)+" °C"
print_log(fic_log,t)

# Lancement de Google Duo
print_log(fic_log,"Vérification de Google Duo")
google_duo(fic_log)

# initialisation des repertoires USB
dossier_usb_prec = []
for dossier in os.listdir('/media/pi/'):
    dossier_usb_prec.append(dossier)
liste_rep_cle=[]
cle_usb = ""

# initialisation des parametres de fenetre
largeur_fenetre = 1280
hauteur_fenetre = 720
if parametres["Plein_Ecran"]=="OUI" :
    type_fenetre = FULLSCREEN
else :
    type_fenetre = RESIZABLE

# initialisation de la liste de photos
liste_photos = init_photos(parametres["Dossier_Photos"])
t = "Chargement de " + str(len(liste_photos)) + " photos"
print_log(fic_log,t)

# initialisation de le fenetre principale
if parametres["Demarrage"]=="Photos" :
    cadre_photos = True
else :
    cadre_photos = False
    type_fenetre = RESIZABLE  # on force en RESIZABLE si pas de cadre photos  
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
pygame.init()
master = pygame.display.set_mode((largeur_fenetre,hauteur_fenetre),type_fenetre)

# initialisation mode jour / nuit à un mode bidon
mode = "Z"

# initialisation du mode REFUS
mode_refus = False

# initialisation des tempos
flag_notif = True
t0_notif = int(time.time())
flag_photo = True
t0_photo = int(time.time())

#initialisation des simulateurs de bouton
simul_rouge = False
simul_bleu = False

souris = PyMouse()

# Boucle 'automate'
boucle = True
while boucle :
    # vérifier la température et gérer le ventilo
    gestion_ventilo(70,65)

    # vérifier l'insertion d'une clé USB
    dossier_usb_prec, cle_usb, liste_rep_cle = detecte_cle_usb(dossier_usb_prec)
    if cle_usb != "" :
        allumer_tele(fic_log)
        t = "Nouvelle clé USB insérée : " + cle_usb
        print_log(fic_log, t)
        pygame.quit()
        if mode_ecran == "TV" :
            if parametres["Commande_tele"]=="CEC" :
                hdmi_tele_CEC (hdmi_rasp, hdmi_rasp, fic_log)
            else :
                hdmi_tele_IR (ir,parametres["Telecommande_tele"],parametres["CommandeIR_tele_HDMI"],fic_log)
        rep_courant = cle_usb
        liste_rep = liste_rep_cle
        choix = 2 # init bidon pour rentrer dans la boucle
        while choix!=0 and choix !=1 :
            nb_photos_rep = len(init_photos(rep_courant+"/"))
            image = "/home/pi/Documents/Screens/Image_menu_usb.png"
            titre1 = str(nb_photos_rep)+ " photos trouvées dans le dossier"
            titre_menu = ["Chargement de photos",rep_courant,titre1,""]
            choix_menu = ["Charger ce dossier", "Annuler"] + liste_rep
            valid, choix = affiche_menu (image,titre_menu,choix_menu,15)
            if not valid :
                choix = 1  # Annuler
            if choix!=0 and choix!=1 :
                if choix_menu[choix]=="..." :
                    rep_courant = cle_usb
                else :
                    rep_courant=rep_courant + choix_menu[choix]
                liste_rep = ['...']
                for fic in os.listdir(rep_courant):
                    f = os.path.join(rep_courant,fic)
                    if os.path.isdir(f) :
                        liste_rep.append("/"+fic)
        if choix == 1 :
            print_log(fic_log,"Annulation du chargement de photos")
            nb_photos_rep = 0
        else :
            if nb_photos_rep!=0 :
                print_log(fic_log,"Copie des photos de "+rep_courant)
                commande = "cp '" + rep_courant + "/'*.jpg " + parametres["Dossier_Photos"]
                os.system (commande)
                commande = "cp '" + rep_courant + "/'*.JPG " + parametres["Dossier_Photos"]
                os.system (commande)
        os.system("sudo eject " + cle_usb) 
        liste_photos = init_photos(parametres["Dossier_Photos"])       
        # Message d'information
        image = ""
        titre1 = "====  " + str(nb_photos_rep) + " photos ont été copiées  ===="
        titre2 = "---> Retirez la clé USB"
        titre_menu = ["","","",titre1,"","", titre2]
        choix_menu = ["OK"]
        valid, choix = affiche_menu(image, titre_menu, choix_menu, 10)
        # reinitialisation de la fenetre principale
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
        pygame.init()
        master = pygame.display.set_mode((largeur_fenetre,hauteur_fenetre),type_fenetre)
        mode = "Z"  # mode bidon pour réinitialisation de l'image
        
    # vérifier les touches ESC ou Fin
    for event in pygame.event.get() :
        if event.type==pygame.KEYDOWN :   # ESCAPE pour changer le mode fenetre
            if event.key==pygame.K_ESCAPE :
                print_log(fic_log,"Touche ESC appuyée : changement du mode fenetre")
                if type_fenetre == RESIZABLE :
                    type_fenetre = FULLSCREEN
                else :  
                    type_fenetre = RESIZABLE
                pygame.quit()
                os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
                pygame.init()
                master = pygame.display.set_mode((largeur_fenetre,hauteur_fenetre),type_fenetre)
                mode = "Z"  # mode bidon pour réinitialisation de l'image
            if event.key==pygame.K_END :  # END pour terminer le programme
                print_log(fic_log,"Touche End appuyée : quitter le programme")
                # quitter
                boucle=False    
            if event.key==pygame.K_r :  # R pour simuler un appui sur le bouton rouge
                simul_rouge = True
            if event.key==pygame.K_b :  # B pour simuler un appui sur le bouton bleu
                simul_bleu = True
                
    # vérifier Appui sur le bouton Bleu
    if mode=="J" and (bouton_bleu.read()==0 or simul_bleu) :  # bouton appuyé pour rentrer dans le Menu
        led_bleu.write(1)
        simul_bleu = False
        print_log(fic_log,"Bouton Bleu appuyé : Menu demandé")
        pygame.quit()
        allumer_tele(fic_log)
        if mode_ecran == "TV" :
            if parametres["Commande_tele"]=="CEC" :
                hdmi_tele_CEC (hdmi_rasp, hdmi_rasp, fic_log)
            else :
                hdmi_tele_IR (ir,parametres["Telecommande_tele"],parametres["CommandeIR_tele_HDMI"],fic_log)
        image = "/home/pi/Documents/Screens/Image_menu_systeme.png"
        titre_menu = ["Menu Système", ""]
        choix_menu = ["Annuler","Eteindre la télé","Passer la télé sur entrée TV","Quitter le programme","Reboot"]
        valid, choix = affiche_menu(image, titre_menu, choix_menu, 15)
        if valid :
            if choix == 1 :
                print_log (fic_log, "Choix Menu = Eteindre la télé")
                if parametres["Commande_tele"]=="CEC" :  # en mode TV, on repasse la télé sur "TV" si elle est allumée
                    tv_tele_CEC (hdmi_rasp, fic_log)
                else :
                    tv_tele_IR (ir,parametres["Telecommande_tele"],parametres["CommandeIR_tele_TV"],fic_log)
                eteindre_tele(fic_log)
            if choix == 2 :
                print_log (fic_log, "Choix Menu = Passer en entrée TV")
                if parametres["Commande_tele"]=="CEC" :  # en mode TV, on repasse la télé sur "TV" si elle est allumée
                    tv_tele_CEC (hdmi_rasp, fic_log)
                else :
                    tv_tele_IR (ir,parametres["Telecommande_tele"],parametres["CommandeIR_tele_TV"],fic_log)
            if choix == 3 :
                print_log (fic_log, "Choix Menu = Quitter")
                boucle = False  # quitter
            if choix == 4 :
                print_log (fic_log, "Choix Menu = Reboot")
                os.system ("sudo reboot")  # Reboot systeme
        if mode_refus and (mode_ecran == "Ecran") :
                eteindre_tele(fic_log)    
        # reinitialisation de la fenetre principale
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
        pygame.init()
        master = pygame.display.set_mode((largeur_fenetre,hauteur_fenetre),type_fenetre)
        mode = "Z"  # mode bidon pour réinitialisation de l'image
        
    # vérifier appui sur le bouton Rouge
    if mode=="J" and (bouton_rouge.read()==0 or simul_rouge):  # bouton appuyé pour demander un blocage d'appel
        led_rouge.write(1)
        simul_rouge = False
        print_log(fic_log,"Bouton Rouge appuyé : Demande de blocage")
        pygame.quit()
        allumer_tele(fic_log)
        if mode_ecran == "TV" :
            if parametres["Commande_tele"]=="CEC" :
                hdmi_tele_CEC (hdmi_rasp, hdmi_rasp, fic_log)
            else :
                hdmi_tele_IR (ir,parametres["Telecommande_tele"],parametres["CommandeIR_tele_HDMI"],fic_log)
        image = "/home/pi/Documents/Screens/Image_menu_refus.png"
        titre_menu = ["Refus automatique des Appels", "", "Choisissez une durée"]
        choix_menu = ["15 minutes","30 minutes","45 minutes","60 minutes", "Annuler"]
        valid, choix = affiche_menu(image, titre_menu, choix_menu, 20)
        if valid :
            if choix == 0 :
                temps_blocage = 900  # 15 minutes
            if choix == 1 :
                temps_blocage = 1800  # 30 minutes
            if choix == 2 :
                temps_blocage = 2700  # 45 minutes
            if choix == 3 :
                temps_blocage = 3600  # 1 heure
            if choix == 4 :
                temps_blocage = 0
                print_log(fic_log,"Annulation du Blocage")
                image = ""
                titre1 = "==== Annulation du Blocage ===="
                titre2 = "La surveillance des appels est active"
                titre_menu = ["","","",titre1,"","", titre2]
                choix_menu = ["OK"]
                valid, choix = affiche_menu(image, titre_menu, choix_menu, 10)
            else :
                t = "Blocage demandé pour "+str(temps_blocage)+" secondes"
                print_log(fic_log,t)
                image = ""
                titre1 = "==== Blocage des appels entrants ===="
                titre2 = "==== Les appels seront bloqués pendant " + str(int(temps_blocage/60)) +" minutes ===="
                titre_menu = ["","","",titre1,"","", titre2]
                choix_menu = ["OK"]
                valid, choix = affiche_menu(image, titre_menu, choix_menu, 10)
                t0_blocage = int(time.time())
                mode_refus = True
                led_rouge.write(1)
                if mode_ecran == "Ecran" :
                    eteindre_tele(fic_log)
        else :
            if mode_refus and (mode_ecran == "Ecran") :
                eteindre_tele(fic_log)
        # reinitialisation de la fenetre principale
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
        pygame.init()
        master = pygame.display.set_mode((largeur_fenetre,hauteur_fenetre),type_fenetre)
        mode = "Z"  # mode bidon pour réinitialisation de l'image
           
    # verification de la tempo du mode refus
    if mode_refus :
        t_blocage = int(time.time()) - t0_blocage
        if t_blocage >= temps_blocage :
            print_log(fic_log,"Fin du mode Blocage")
            mode_refus = False
            led_rouge.write(0)
            mode = "Z" # mode bidon pour réinitialisation de l'image
            
    # Vérification du changement de Mode Jour / Nuit
    if mode != mode_JN(int(parametres["Heure_Reveil"]),int(parametres["Heure_Sommeil"])) :
        #changement de mode jour / nuit détecté
        mode = mode_JN(int(parametres["Heure_Reveil"]),int(parametres["Heure_Sommeil"]))
        if mode == "J" :
            # Passage en mode Jour
            print_log(fic_log,"Passage en mode Jour")
            # verification de notification apparues pendant le mode nuit
            notif, appelant, type_notif = surveillance_notif()
            while notif :
                t = "Notification détectée pendant le mode nuit : Appel manqué de " + appelant
                print_log(fic_log,t)
                print_log(fic_appels,t)
                souris.click (1255,60) # clic sur la croix d'acquittement de la notif
                time.sleep(0.5)
                notif, appelant, type_notif = surveillance_notif()
            if not cadre_photos :
                photo_aff = "/home/pi/Documents/Screens/fond_cadrephotos_nonactif.jpg"
                change_photo (master,largeur_fenetre,hauteur_fenetre,photo_aff)
            else :
                photo_aff = liste_photos[randint(0,len(liste_photos)-1)]
                change_photo (master,largeur_fenetre,hauteur_fenetre,photo_aff)
            if mode_refus :
                photo_aff = "/home/pi/Documents/Screens/fond_mode_refus.jpg"
                change_photo (master,largeur_fenetre,hauteur_fenetre,photo_aff)
            elif mode_ecran == "Ecran" :
                allumer_tele(fic_log)
            if mode_ecran == "TV" :
                if statut_tele(fic_log) == "on" :
                    if parametres["Commande_tele"]=="CEC" :  # en mode TV, on repasse la télé sur "TV" si elle est allumée
                        tv_tele_CEC (hdmi_rasp, fic_log)
                    else :
                        tv_tele_IR (ir,parametres["Telecommande_tele"],parametres["CommandeIR_tele_TV"],fic_log)
        else :
            # Passage en mode Nuit
            print_log(fic_log,"Passage en mode Nuit")
            photo_sommeil = "/home/pi/Documents/Screens/En_Sommeil.jpg"
            change_photo (master,largeur_fenetre,hauteur_fenetre,photo_sommeil)
            if mode_ecran == "Ecran" :
                eteindre_tele(fic_log)
            
    # Déclenchement d'evenements toutes les x secondes
    if mode == "J" :
        if (int(time.time()) - t0_notif) >= 3 : # toutes les 3 secondes pour les notif
            flag_notif = True
        if flag_notif :
            notif, appelant, type_notif = surveillance_notif()
            if notif :
                pygame.quit()  # supprimer la fenetre principale
                if type_notif == "entrant" :
                    t = "Notification détectée : Appel de " + appelant
                    print_log(fic_log,t)
                    print_log(fic_appels,t)
                    souris.click(1240,95) #cliquer sur la notification Google Duo
                    time.sleep(0.2)
                    if mode_refus :
                        souris.click (550,645)  # clic sur le bouton "refuser"
                        time.sleep(0.5)
                        t="Appel refusé car mode REFUS actif"
                        print_log(fic_log,t)
                        print_log(fic_appels,t)
                    else :
                        allumer_tele(fic_log)
                        if mode_ecran == "TV" :
                            if parametres["Commande_tele"]=="CEC" :
                                hdmi_tele_CEC (hdmi_rasp, hdmi_rasp, fic_log)
                            else :
                                hdmi_tele_IR (ir,parametres["Telecommande_tele"],parametres["CommandeIR_tele_HDMI"],fic_log)
                        else :
                            # Passer la télé en MUTE (première commande uniquement)
                            telec = parametres["Telecommande_tele"]
                            com = parametres["CommandeIR_tele_MUTE"][0]
                            print_log (fic_log,"Passage de la télé en MUTE")
                            ir.send_once(com,telec,1)
                        gestion_appel_duo(fic_log, fic_appels)
                        if mode_ecran == "Ecran" :
                            # Enlever MUTE de la télé
                            telec = parametres["Telecommande_tele"]
                            com = parametres["CommandeIR_tele_MUTE"][0]
                            print_log (fic_log,"Enlever le MUTE de la télé")
                            ir.send_once(com,telec,1)
                        # verification de notification apparues pendant l'appel
                        notif, appelant, type_notif = surveillance_notif()
                        while notif :
                            t = "Notification détectée pendant l'appel : Appel manqué de " + appelant
                            print_log(fic_log,t)
                            print_log(fic_appels,t)
                            souris.click (1255,60) # clic sur la croix d'acquittement de la notif
                            time.sleep(0.5)
                            notif, appelant, type_notif = surveillance_notif()
                else :
                    t = "Notification détectée : Appel manqué de " + appelant
                    print_log(fic_log,t)
                    print_log(fic_appels,t)
                    souris.click (1255,60) # clic sur la croix d'acquittement de la notif
                    time.sleep(0.5)
                # reinitialisation de la fenetre principale
                os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
                pygame.init()
                master = pygame.display.set_mode((largeur_fenetre,hauteur_fenetre),type_fenetre)
                mode = "Z"  # mode bidon pour réinitialisation de l'image
                flag_photo = True  # forcer le changement de photo  
            #reinitialisation du chrono de surveillance notif
            t0_notif = int(time.time())
            flag_notif = False
        if (int(time.time()) - t0_photo) >= int(parametres["Duree_Diapo"]) :
            flag_photo = True
        if  flag_photo :
            # Changement de la photo
            if cadre_photos and not mode_refus:
                #print_log(fic_log,"Changement de photo")
                photo_aff = liste_photos[randint(0,len(liste_photos)-1)]
                change_photo (master,largeur_fenetre,hauteur_fenetre,photo_aff)
            #reinitialisation du chrono de changement de photo
            t0_photo = int(time.time())
            flag_photo = False
    time.sleep(0.2)            
    
pygame.quit()
led_rouge.write(0)
led_jaune.write(0)
led_bleu.write(0)
ventilateur.write(0)
print_log(fic_log,"Sortie du Programme")
