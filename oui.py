from PIL import Image
import cv2
import numpy as np
from PIL import ImageGrab
import pickle

print("Laissez votre curseur sur l'item que vous allez switch le temps de l'initialisation")

#mettez le nom du chemin de votre script
nom_chemin_script = r'F:\Mes documents\Metin2\Wiki\programme\dm dc'

#ouverture image "moyen" et "tence"
image_moyen = Image.open(r'{0}\chiffres\moyen.png'.format(nom_chemin_script))
image_moyen_np = np.array(image_moyen)
image_tence = Image.open(r'{0}\chiffres\tence.png'.format(nom_chemin_script))
image_tence_np = np.array(image_tence)

#transformation des images en nuance de gris
image_moyen_gray = cv2.cvtColor(image_moyen_np, cv2.COLOR_BGR2GRAY)
image_tence_gray = cv2.cvtColor(image_tence_np, cv2.COLOR_BGR2GRAY)

#valeur associé à chaque modèle de chiffre 
valeur_chiffre=[[-20655,0],[-22440,1],[-19125,2],[-23460,3],[-26775,4],[-19635,5],[-17340,6],[-26520,7],[-19380,8],[-25755,9]]

#image de base du calque
image_base = np.array(Image.new('RGB',(3,7),(255,255,255)))

#repère l'emplacement de "moyen" dans une image
def RepereMoyen(img):
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_seuil = cv2.threshold(img_gray,0,255,cv2.THRESH_BINARY)[1]
    res = cv2.matchTemplate(image_moyen_gray,img_seuil,cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= 0.8)
    coord = [pt for pt in zip(*loc[::-1])]
    
    if coord == []:
        return [],[],[],[]
        
    else :
        res2 = cv2.matchTemplate(image_tence_gray,img_seuil,cv2.TM_CCOEFF_NORMED)
        loc2 = np.where(res2 >= 0.8)
        coord2 = [pt for pt in zip(*loc2[::-1])]
    
        #renvoie les coordonnées de "moyen", la couleur (vert ou rouge)
        return coord[0],img[coord[0][1]+1,coord[0][0]+1],coord2[0],img[coord2[0][1]+1,coord2[0][0]+1]

#associe un chiffre à une valeur calculé par uniqueValue
def bijection(img,couleur):
    
    valeur = uniqueValue(img,couleur)
    
    for i in range(10):
        if valeur == valeur_chiffre[i][0]:
            
            return valeur_chiffre[i][1]
            
    return 'error'

#calcul une valeur unique d'une image
def uniqueValue(img,couleur):
    
    img_s=spectre(img,couleur)
    a=0
    
    for i in range(6,-1,-1):
        
        for j in range(2,-1,-1):
            
            a+=(img_s[i,j][0])*(j+1-3*i)
            
    return a
    
#transforme l'image d'un chiffre en un calque noir et blanc
def spectre(img,couleur):  
 
    base = image_base.copy()
    mask = np.all(img == couleur,axis=-1)
    base[mask]=[0,0,0]
    
    return base

fichier_donnees = open(r"{0}\données dm dc.txt".format(nom_chemin_script), "a")

def ecrireFichier(dm,dc):
    fichier_donnees.write("\n" + "[" + str(dm) + "," + str(dc) + "]")
    
    
    
#renvoie les DC
def findDC(img,coord_tence,couleur):
    
    dc1, dc2 = 0,0
    
    if couleur[0] == 176:
            
        #cadre sur le premier chiffre des DC
        image_dc1 = img[coord_tence[1]+1 : coord_tence[1]+8, coord_tence[0]+28 : coord_tence[0]+31]
            
        #cadre sur le deuxième chiffre des DC
        image_dc2 = img[coord_tence[1]+1 : coord_tence[1]+8, coord_tence[0]+33 : coord_tence[0]+36]
        

        #valeur des 2 chiffres
        dc1 = bijection(image_dc1,couleur)
        dc2 = bijection(image_dc2,couleur)
            
        #si DC est composé d'un seul chiffre
        if dc2 == 'error':
                
            #DC réel
            dc = dc1
                
        else:
            #DC réel
            dc = 10*dc1+dc2
            
        return dc
               
    #idem si couleur rouge (DC négatif)
    elif couleur[0] == 229:
            
        image_dc1 = img[coord_tence[1]+1 : coord_tence[1]+8, coord_tence[0]+32 : coord_tence[0]+35]
        image_dc2 = img_cadre[coord_tence[1]+1 : coord_tence[1]+8, coord_tence[0]+37 : coord_tence[0]+40]
            
        dc1 = bijection(image_dc1,couleur)
        dc2 = bijection(image_dc2,couleur)
        
        if dc2 == 'error':
            dc = dc1
                
        else:
            dc = 10*dc1+dc2
        
        return -1*dc

        
#screen l'écran jusqu'à que "moyen" apparaisse
while True:
    
    img_grab = np.array(ImageGrab.grab())
    moyen_info = RepereMoyen(img_grab)[0]
    
    if moyen_info != []:
        coord_moyen = moyen_info
        
        print('-----------------------------------------------')
        print("L'initialisation est terminée, vous pouvez switch")
        print('-----------------------------------------------')
        print("Ne pas changez l'emplacement de l'item pendant une exécution")
        print("Faire en sorte d'avoir toujours la fenêtre de l'item qui s'affiche soit vers le haut, soit vers le bas")
        
        break
        
L, M = [0], [0]
colonne1, ligne1 = coord_moyen[1]-50, coord_moyen[0]-50
colonne2, ligne2 = colonne1+220, ligne1+200


#screen et renvoie les dm lorsqu'ils changent d'une image à l'autre
while True:
    
    img_grab = np.array(ImageGrab.grab())
    
    #cadre le screen sur un petit carré autour du "moyen" d'origine
    img_cadre = img_grab[colonne1 : colonne2, ligne1 : ligne2]
    
    #coordonnées et couleur du "moyen"
    coord_moyen, couleur, coord_tence, couleur2 = RepereMoyen(img_cadre)
    
    #si la souris est sur un item
    if coord_moyen != []:

        dm1, dm2 = 0, 0
        
        #si la couleur est verte (DM positif)
        if couleur[0] == 176:
            
            #cadre sur le premier chiffre des DM
            image_dm1 = img_cadre[coord_moyen[1]-1 : coord_moyen[1]+6, coord_moyen[0]+45 : coord_moyen[0]+48]
            
            #cadre sur le deuxième chiffre des DM
            image_dm2 = img_cadre[coord_moyen[1]-1 : coord_moyen[1]+6, coord_moyen[0]+50 : coord_moyen[0]+53]
            
            #valeur des 2 chiffres
            dm1 = bijection(image_dm1,couleur)
            dm2 = bijection(image_dm2,couleur)
            
            #si DM est composé d'un seul chiffre
            if dm2 == 'error':
                
                #DM réel
                dm = dm1
                
            else:
                #DM réel
                dm = 10*dm1+dm2
                
            dc = findDC(img_cadre,coord_tence,couleur2)
            
            #si le DM est différent du précédent
            if (dm != L[0] or dc != M[0]):
                L.pop(0)
                L.append(dm)
                M.pop(0)
                M.append(dc)
                ecrireFichier(dm,dc)
                print("DM :",dm,", DC :",dc)
               
        #idem si couleur rouge (DM négatif)
        elif couleur[0] == 229:
            
            image_dm1 = img_cadre[coord_moyen[1]-1 : coord_moyen[1]+6, coord_moyen[0]+49 : coord_moyen[0]+52]
            image_dm2 = img_cadre[coord_moyen[1]-1 : coord_moyen[1]+6, coord_moyen[0]+54 : coord_moyen[0]+57]
            
            dm1 = bijection(image_dm1,couleur)
            dm2 = bijection(image_dm2,couleur)
            
            if dm2 == 'error':
                dm = dm1
                
            else:
                dm = 10*dm1+dm2

            dc = findDC(img_cadre,coord_tence,couleur2)
            
            if (dm != L[0] or dc != M[0]):
                L.pop(0)
                L.append(dm)
                M.pop(0)
                M.append(dc)
                ecrireFichier(dm,dc)
                print("DM :",-1*dm,", DC :",dc)


fichier_donnees.close()



    
        
        
