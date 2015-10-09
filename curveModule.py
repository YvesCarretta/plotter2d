#!/usr/bin/env python
# -*- coding: latin-1; -*- 


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os
from math  import *
import re

class Point:
    def __init__(self, x, y):
        self.x=x
        self.y=y    
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def __str__(self):
        return "(%f,%f)" % (self.x, self.y)        

class Curve:
    def __init__(self):
        self.pts    = []
        self.__name   = "Curve"
        self.__scaling = 1.0
        self.__scalingTot = 1.0
        self.__color  = QColor(Qt.blue)
        self.__lineW  = 2
        self.__lineS  = Qt.SolidLine
        self.__marker = Marker()
        self.__show = True    # si True on affiche la courbe dans le plotter
        self.__info = 'Empty' # chaine de caractères qui va contenir les infos sur la courbe
        # ex : si load d'un fichier _res.m de lubri -> contient nom du fichier + arborescence
        # ex : si courbe analytique : fonction utilisée + bornes min. et max. + nbre de points
        
    def setName(self,name):
        self.__name = name      
    def getName(self):
        return self.__name    
    
    def setScaling(self,scaleFactor):
        self.__scaling = scaleFactor      
    def getScaling(self):
        return self.__scaling 
        
    def setColor(self,color):
        self.__color = color
    def getColor(self):
        return self.__color
        
    def setLineW(self,lineW):        
        self.__lineW = lineW
    def getLineW(self):
        return self.__lineW
    
    def setLineS(self,lineS):        
        self.__lineS = lineS
    def getLineS(self):
        return self.__lineS
    
    def setMarker(self,type):
        if   type == '':
            self.__marker.type = Marker.NoMarker
        elif type == 's':
            self.__marker.type = Marker.Square
        elif type == 'd':
            self.__marker.type = Marker.Diamond            
        elif type == '>':
            self.__marker.type = Marker.RightTriangle         
        elif type == '<':
            self.__marker.type = Marker.LeftTriangle         
        elif type == '^':
            self.__marker.type = Marker.UpTriangle     
        elif type == 'v':
            self.__marker.type = Marker.LowTriangle                

    def getMarker(self):
        return self.__marker
        
    def getVisibility(self):
        return self.__show
    def show(self):
        self.__show = True
    def hide(self):
        self.__show = False
        
    def setInfo(self, info):
        self.__info = info
    def getInfo(self):
        return self.__info
        
    def addPoint(self,x,y):
        self.pts.append(Point(x,y))
        
    def computeRange(self):
        # Calcul des valeurs min max pour x et y
        # -> permet de centrer le graphe sur les données
        # computeRange() appelé lorsqu'on charge les données au format Matlab
        vecX = []
        vecY = []
        for pt in self.pts:
            vecX.append(pt.getX())
            vecY.append(pt.getY())
        self.__xMin = min(vecX)
        self.__xMax = max(vecX)
        self.__yMin = min(vecY)
        self.__yMax = max(vecY)   
    
    def scaling(self, scaleFactor):
        ''' Mise à l'échelle de la courbe'''
        # -> permet de comparer des courbes avec des ordres de grandeur très différents à un instant donné
        self.__scaling = scaleFactor
        self.__scalingTot *= scaleFactor
        vecX = []
        vecY = []
        for pt in self.pts:
            vecX.append(pt.getX())
            vecY.append(pt.getY()*scaleFactor)
        self.erase()
        self.fill(vecX,vecY)
        # Mise à jour des infos de la courbe
        s = str(self.getInfo()).splitlines()
        if 'Scale' in s[-1]:
            s2 = s[-1].replace(s[-1],('Scale factor = ' + str(self.__scalingTot)))
            s[-1] = s2
            self.__info = ''
            self.__info += s[0] 
            for lin in s[1:]:
                self.__info += '\n'+lin  
        else:
            self.__info+='\nScale factor = ' + str(self.__scalingTot)
        
    def erase(self):
        del self.pts[:]
        
    def fill(self, vecX, vecY):   # Permet de tracer une fonction à partir des couples de points (x,y)
        if len(vecX) != len(vecY):
            return False # Les vecteurs n'ont pas la même longueur
            #print "Afficher un message d'erreur : les vecteurs doivent etre de meme longueur"
        else:
            for i in range(len(vecX)):
                self.pts.append(Point(vecX[i],vecY[i]))
            self.__xMin = min(vecX)
            self.__xMax = max(vecX)
            self.__yMin = min(vecY)
            self.__yMax = max(vecY)            
            return True # Tout s'est bien passé
            
    def fill2(self, f, rng, n):
        x = float(rng[0])
        dx = (float(rng[1])-float(rng[0]))/n
        vecX = [] # variables temporaires 
        vecY = [] # calcul des valeurs min et max
        for i in range(n):
            self.pts.append(Point(x,f(x)))
            vecX.append(x)
            vecY.append(f(x))
            x += dx
        self.__xMin = min(vecX)
        self.__xMax = max(vecX)
        self.__yMin = min(vecY)
        self.__yMax = max(vecY)
        
    # A virer
    def loadData1(self, profil_name, cName = 'Empty Name'):
        f = open(profil_name,'r')
        txt = f.readline()
        vecX = []
        vecY = []
        while txt != '':
            a = txt.split()
            #print "a = ", a
            vecX.append(float(a[0]))
            vecY.append(float(a[1]))
            txt = f.readline()    
        # 
        #print "vecX = ", vecX
        #print "vecY = ", vecY
        f.close()
        self.fill(vecX,vecY)
        self.__name = cName
        self.__info = 'Curve loaded from : ' + os.path.abspath(profil_name)
        
    # A virer
    def loadData2(self, vecX_name, vecY_name, cName = 'Empty Name'):
        # 
        f = open(vecX_name,'r')
        vecX = []
        self.__readVector(f,vecX)
        f.close()
        # 
        f = open(vecY_name,'r')
        vecY = []
        self.__readVector(f,vecY)
        f.close()
        # 
        if len(vecX) == len(vecY):
            self.fill(vecX,vecY)
            self.__name = cName
            self.__info = 'Curve loaded from files \n' + \
                          'Vec. X = ' + os.path.abspath(vecX_name) + '\n' + \
                          'Vec. Y = ' + os.path.abspath(vecY_name)
            return True
        else:
            # les vecteurs n'ont pas la même longueur
            return False
    
    # Lit le fichier f ligne par ligne et ajoute le contenu de la ligne 
    # à la liste vector
    def __readVector(self,f,vector):
        txt = f.readline()
        while txt != '':
            txt = float(txt)
            vector.append(txt)
            txt = f.readline()     
            
    def __str__(self):
        s = ""
        for p in self.pts:
            s += str(p) + " "
        return s
    def __iter__(self):
        for p in self.pts:
            yield p        
    def getXmin(self):
        return self.__xMin
    def getXmax(self):
        return self.__xMax
    def getYmin(self):
        return self.__yMin
    def getYmax(self):
        return self.__yMax
        
class Marker:
    # On définit une enum pour désigner les marker
    NoMarker, Square, Diamond, RightTriangle, LeftTriangle, UpTriangle, LowTriangle = range(0,7)
    def __init__(self):
        self.type = Marker.NoMarker
        self.size = 5
        self.fill = True # si True : on remplit le marker  
    def getShape(self):
        fctShape = None
        theta    = 0.0
        if self.type == Marker.Square:
            fctShape = self.getSquare    
            theta    = 0.0
        elif self.type == Marker.Diamond:
            fctShape = self.getDiamond
            theta    = 0.0
        elif self.type == Marker.RightTriangle:
            fctShape = self.getTriangle    
            theta    = 0.0
        elif self.type == Marker.LeftTriangle:
            fctShape = self.getTriangle    
            theta    = pi
        elif self.type == Marker.UpTriangle:
            fctShape = self.getTriangle    
            theta    = -pi/2.0
        elif self.type == Marker.LowTriangle:
            fctShape = self.getTriangle    
            theta    = pi/2.0      
        return fctShape, theta
                
    def getSquare(self,x0,y0,theta):
        sinus   = sin(pi/4.)
        cosinus = cos(pi/4.)
        r = self.size  
        polyMarker = QPolygon(4)
        polyMarker[0] = QPoint(x0+r*cosinus,y0+r*sinus)
        polyMarker[1] = QPoint(x0-r*cosinus,y0+r*sinus)
        polyMarker[2] = QPoint(x0-r*cosinus,y0-r*sinus)
        polyMarker[3] = QPoint(x0+r*cosinus,y0-r*sinus)
        return polyMarker            
    def getDiamond(self,x0,y0,theta):
        r  = self.size
        polyMarker = QPolygon(4)
        polyMarker[0] = QPoint(x0+r , y0)
        polyMarker[1] = QPoint(x0   , y0+r)
        polyMarker[2] = QPoint(x0-r , y0)
        polyMarker[3] = QPoint(x0   , y0-r)
        return polyMarker        
    def getTriangle(self,x0,y0,theta):
        r  = self.size
        polyMarker = QPolygon(3)
        polyMarker[0] = QPoint(x0+r*cos(theta)              ,y0+r*sin(theta))
        polyMarker[1] = QPoint(x0+r*cos(theta+pi*2./3.),y0+r*sin(theta+pi*2./3.))
        polyMarker[2] = QPoint(x0+r*cos(theta-pi*2./3.),y0+r*sin(theta-pi*2./3.))
        return polyMarker             
        