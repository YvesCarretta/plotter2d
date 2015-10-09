#!/usr/bin/env python
# -*- coding: latin-1; -*- 

import math
import sys
import os  # -> pour connaitre le chemin vers 
           # le répertoire que l'on propose à l'utilisateur
           # lorsqu'on sauvegarde une image
from PyQt4.QtGui  import *
from PyQt4.QtCore import *
from PyQt4.Qt     import *

from curveModule  import *

import qrc_resourcesPlot  #obtenu à l'aide de la commande : 
# D:\LibsVS2012\Python-2.7.5-tcl8.5\pyrcc4.exe -o qrc_resourcesPlot.py resourcesPlot.qrc
# téléchargement icones -> http://www.iconspedia.com/icon/copy--82-.html

import curvePropertiesDlg  
import treeModule

class Plotter(QWidget):
    def __init__(self, parent = None):
        super(QWidget, self).__init__(parent)

        # Couleur associée au widget
        self.setBackgroundRole(QPalette.Dark)# QPalette.Light)
                                             # QPalette.Midlight)
        
        self.setAutoFillBackground(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Def des boutons et des signaux associés
        self.__setButton() 

        # Attribus de la classe :
        self.__marginLR = 75 # marges cotés (Left and Right)
        self.__margin   = 50      
        
        self.curZoom    = 0
        self.rubberBandIsShown = False
        self.rubberBandRect    = QRect()

        self.zoomStack      = [] # Liste de PlotSettings()
        self.__plotSettings = PlotSettings()
        self.__setPlotSettings(self.__plotSettings);
                
        self.treeCurves = treeModule.QTreeWidgetCurve()
            
        self.__curveList = [] # Liste qui contient les objets curve à tracer
        
        # Label des axes
        self.__xlabel = 'axe X'
        self.__ylabel = 'axe Y'
        self.__fontsize = 14
        
        # Légende
        self.__legend = Legend()
        
        # Objet de dialogue pour définir les propriétés des courbes
        self.curvePropDlg = None

        # Fin de déclaration des attributs
        
    def __setButton(self):
        """Definition des boutons et des connections SIGNAL-SLOT correspondantes 
        """
        # Zoom In
        self.zoomInButton = QToolButton(self)
        self.zoomInButton.setIcon(QIcon(':/zoomin.png'))
        self.zoomInButton.adjustSize()
        self.zoomInButton.setToolTip("Zoom in")
        # Le bouton reste enfoncé quand on appuie dessus
        self.zoomInButton.setCheckable(True) 

        # Zoom Out
        self.zoomOutButton = QToolButton(self)
        self.zoomOutButton.setIcon(QIcon(':/zoomout.png'))
        self.zoomOutButton.adjustSize()
        self.zoomOutButton.setToolTip("Zoom out")
        self.zoomOutButton.setEnabled(False)
        self.connect(self.zoomOutButton, SIGNAL("clicked()"), self.__zoomOut)
        
        # Save
        self.saveButton = QToolButton(self)
        self.saveButton.setIcon(QIcon(':/filesaveas.png'))
        self.saveButton.adjustSize()
        self.saveButton.setToolTip("Save the graph in a .PNG format")
        self.connect(self.saveButton, SIGNAL("clicked()"), self.__saveImage)
        
        # Curves properties
        self.curveP = QToolButton(self)
        self.curveP.setIcon(QIcon(':/properties.png'))
        self.curveP.setToolTip("Display a dialog box allowing to modify graph properties")
        self.connect(self.curveP, SIGNAL("clicked()"), self.__setCurvesProperties)        
        
        # Copy
        self.curveCp = QToolButton(self)
        self.curveCp.setIcon(QIcon(':/copy.png'))
        self.curveCp.setToolTip("Copy the image in order to paste it in another program (word, powerpoint, etc.)")
        self.connect(self.curveCp, SIGNAL("clicked()"), self.__copyImage)          
        
        # liste des boutons à masquer lorsqu'on fait une copie du widget (copier-coller)
        self.__buttonToHide = [] 
        self.__buttonToHide.append(self.zoomOutButton)
        self.__buttonToHide.append(self.zoomInButton)
        self.__buttonToHide.append(self.saveButton)
        self.__buttonToHide.append(self.curveP)
        self.__buttonToHide.append(self.curveCp)        
        
        
    def getCurveList(self):
        return self.__curveList
        
    def getNewCurve(self):
        return Curve()
    
    def setXlabel(self,label):
        self.__xlabel = label
    def getXlabel(self):
        return self.__xlabel
        
    def setYlabel(self,label):
        self.__ylabel = label               
    def getYlabel(self):
        return self.__ylabel
        
    def setFontSize(self,size):  
        self.__fontsize = size
    def getFontSize(self):  
        return self.__fontsize
        
    def getLegend(self):
        return self.__legend
        
    def __setCurvesProperties(self):
        if self.curvePropDlg is not None:
            # on remet à jour le contenu de l'interface du CurvePropertiesDlg
            # si l'objet existe déjà
            self.curvePropDlg.getCurvePropWidget().refresh() 
        else : 
            self.curvePropDlg = curvePropertiesDlg.CurvePropertiesDlg(
                    self, self.update, self)
        
        self.curvePropDlg.show()
        self.curvePropDlg.raise_()
        self.curvePropDlg.activateWindow() 
        
    def __setPlotSettings(self,plotSettings):
        self.zoomStack.append(plotSettings)
        self.curZoom = 0
    def getPlotSettings(self):
        return self.zoomStack[-1]
    
    def addCurve(self, curve,setName='UserData'):
        ''' ajout de la curve dans le QTreeWidget "treeCurves"
        sous l'onglet "setName" -> "UserData" par défaut 
        '''
        self.treeCurves.addCurve(curve,setName)
        
    def appendCurveDict(self,dict,setName):
        ''' ajout d'un dictionnaire de courbes (dict) 
        dans le QTreeWidget "treeCurves" sous l'onglet "setName".
        Utile pour charger le contenu du _res.m de MetaLub
        '''
        for key in dict:
            curve = dict[key]
            curve.computeRange() # calcul xmin, xmax etc. 
            # pour ajuster le graphe autour des données via le GUI
            self.addCurve(curve,setName)        
        
    def updCurveList(self):
        ''' Mise à jour de self.__curveList en fonction des données contenues
        dans le dictionnaire self.curveDict
        '''
        del self.__curveList[:] # on efface le contenu de la liste
               
        it = QTreeWidgetItemIterator(self.treeCurves)
        while it.value():
            if isinstance(it.value(), treeModule.QTreeWidgetItemCurve):
                curve = it.value().getCurve()
                if curve.getVisibility():
                    self.__curveList.append(curve)
            it.__iadd__(1)         
        
        
    def __zoomOut(self):
        if (self.curZoom > 0):
            self.curZoom -= 1
            del self.zoomStack[-1] #on efface le dernier élément de la liste
            
            if self.curvePropDlg is not None:
                # on refraichit CurvePropertiesDlg si l'objet existe déjà -> 
                # label des xmin - xmax etc à remettre à jour dans le dialogue
                #self.curvePropDlg.setPlotSettings(self.zoomStack[self.curZoom]) # on met à jour le plotSettings
                self.curvePropDlg.getCurvePropWidget().refresh()   
                
            
            self.zoomOutButton.setEnabled(self.curZoom > 0)
            self.zoomInButton.setEnabled(True)
            self.update()

    def clearCurve(self, id): # a modifier
        del curveMap[id]
        self.update()

    def minimumSizeHint(self):
        # nb: the QSize class defines the size of a two-dimensional object using integer point precision.
        return QSize( 6 * self.__marginLR, 4 * self.__margin) 
    
    def sizeHint(self):
        return QSize(12 * self.__marginLR, 8 * self.__margin)
    
    def paintEvent(self, event): # QPaintEvent  
        painter = QPainter(self) 
        
        self.__drawAxisLabel(painter)
        
        self.__drawGrid(painter)
        self.__drawCurves(painter)    
        self.__drawMarker(painter)
        
        self.__legend.drawLegend(painter,self.__curveList,self.__fontsize,\
                                 self.__marginLR,self.__margin,\
                                 self.width(),self.height()) 
        
        if (self.rubberBandIsShown):
            pen = QPen()         
            pen.setColor(Qt.black)            
            pen.setWidth(1)
            painter.setPen(pen);        
            painter.drawRect(self.rubberBandRect)   
    

    def resizeEvent(self, event): # Positionner les boutons de zoom en haut à droite de la fenêtre
        x = self.width() - (self.zoomInButton.width() + self.zoomOutButton.width() + 10)
        xIcons = self.width() - 0.7*self.__marginLR
        yIcons = 48
        self.zoomInButton.move (xIcons, yIcons)
        self.zoomOutButton.move(xIcons, yIcons+30)

        self.saveButton.move(xIcons, yIcons+60)
        self.curveP.move    (xIcons, yIcons+90)
        self.curveCp.move   (xIcons, yIcons+120)        

        self.update()

    def __ax2win(self, ax, ay):
        t1 = self.zoomStack[self.curZoom] # variable temporaire
        wx = self.rect.left() + (ax-t1.getXmin())/(t1.getXmax()-t1.getXmin())*self.rect.width()
        wy = self.rect.bottom() - (ay-t1.getYmin())/(t1.getYmax()-t1.getYmin())*self.rect.height()
        return (wx, wy)   
        
    def __win2ax(self, wx, wy):
        t1 = self.zoomStack[self.curZoom] # variable temporaire
        ax = t1.getXmin() + (wx-self.rect.left())*(t1.getXmax()-t1.getXmin())/self.rect.width()
        ay = t1.getYmin() - (wy-self.rect.bottom())*(t1.getYmax()-t1.getYmin())/self.rect.height()
        return (ax, ay)       
    
    def mousePressEvent(self, event):
        t1 = self.zoomInButton.isChecked() # Le bouton zoom est activé
        if (t1 and (event.button() == Qt.LeftButton)):
            #print "Zoom button activated + left clicked!"
            rect = QRect(self.__marginLR, self.__margin, self.width() - 2 * self.__marginLR, self.height() - 2 * self.__margin)        
            if (rect.contains(event.pos())):
                self.rubberBandIsShown = True
                self.rubberBandRect.setTopLeft(event.pos())
                self.rubberBandRect.setBottomRight(event.pos())
                self.setCursor(Qt.CrossCursor) # Fait apparaitre un curseur en forme de croix   
                self.__updateRubberBandRegion(event)
 
        elif event.button() == Qt.LeftButton:
            #print "left clicked!";
            self.starttx = event.pos().x()
            self.startty = event.pos().y()
        elif event.button() == Qt.RightButton:
            #print "right clicked!";
            self.starttx = event.pos().x()
            self.startty = event.pos().y()
            
        if self.curvePropDlg is not None:
            # on refraichit CurvePropertiesDlg si l'objet existe déjà -> 
            # label des xmin - xmax etc à remettre à jour dans le dialogue   
            self.curvePropDlg.getCurvePropWidget().refresh()
    
    def mouseMoveEvent(self, event):
        #print "mouse moved!"
        if (self.rubberBandIsShown):
            #self.updateRubberBandRegion(event)
            self.rubberBandRect.setBottomRight(event.pos())
            self.update()
        elif event.buttons() & Qt.LeftButton:
            (x1,y1) = self.__win2ax(self.starttx, self.startty)
            (x2,y2) = self.__win2ax(event.pos().x(), event.pos().y())
            dx = x1-x2
            dy = y1-y2
            self.zoomStack[-1].setXmin(self.zoomStack[-1].getXmin()+dx)
            self.zoomStack[-1].setYmin(self.zoomStack[-1].getYmin()+dy)
            self.zoomStack[-1].setXmax(self.zoomStack[-1].getXmax()+dx)
            self.zoomStack[-1].setYmax(self.zoomStack[-1].getYmax()+dy)
            self.starttx = event.pos().x()
            self.startty = event.pos().y()            
            self.update() 
        elif event.buttons() & Qt.RightButton:
            dx = float(event.pos().x() - self.starttx)
            dy = float(event.pos().y() - self.startty)
            dz = math.sqrt(dx*dx+dy*dy)
            if dz>400.0: dz=400.0
            if dx<0: dz=-dz
            zoom = 1.+dz/400.0
            if zoom<0.: zoom=1. # normalement impossible
            #print "zoom=",zoom
            cx = (self.zoomStack[-1].getXmin()+self.zoomStack[-1].getXmax())/2.
            cy = (self.zoomStack[-1].getYmin()+self.zoomStack[-1].getYmax())/2.
            self.zoomStack[-1].setXmin( cx - (cx-self.zoomStack[-1].getXmin())*zoom )
            self.zoomStack[-1].setYmin( cy - (cy-self.zoomStack[-1].getYmin())*zoom )
            self.zoomStack[-1].setXmax( cx - (cx-self.zoomStack[-1].getXmax())*zoom )
            self.zoomStack[-1].setYmax( cy - (cy-self.zoomStack[-1].getYmax())*zoom )
            
            self.starttx = event.pos().x()
            self.startty = event.pos().y()
            
            self.update()
        
        if self.curvePropDlg is not None:
            # on refraichit CurvePropertiesDlg si l'objet existe déjà -> 
            # label des xmin - xmax etc à remettre à jour dans le dialogue   
            self.curvePropDlg.getCurvePropWidget().refresh()    
    
    def mouseReleaseEvent(self, event):
        if ((event.button() == Qt.LeftButton) and self.rubberBandIsShown):
            # On a appuyé sur le zoom - on a déplacé la souris - 
            # on vient de relacher le bouton gauche de la souris
            self.rubberBandIsShown = False
            self.__updateRubberBandRegion(event)
            self.unsetCursor()
    
            rect = QRect(self.rubberBandRect.normalized())
            if (rect.width() < 4 or rect.height() < 4):
                return
            rect.translate(-self.__marginLR, -self.__margin)

            prevSettings = self.zoomStack[self.curZoom]
            settings = PlotSettings()
            dx = prevSettings.spanX() / (self.width() - 2 * self.__marginLR)
            dy = prevSettings.spanY() / (self.height() - 2 * self.__margin)
            settings.setXmin( prevSettings.getXmin() + dx * rect.left()   )
            settings.setXmax( prevSettings.getXmin() + dx * rect.right()  )
            settings.setYmin( prevSettings.getYmax() - dy * rect.bottom() )
            settings.setYmax( prevSettings.getYmax() - dy * rect.top()    )
                     
            self.zoomStack.append(settings)
            self.curZoom += 1      
            self.zoomOutButton.setEnabled(True)
            self.update()

            if self.curvePropDlg is not None:
                # on refraichit CurvePropertiesDlg si l'objet existe déjà -> 
                # label des xmin - xmax etc à remettre à jour dans le dialogue
                #self.curvePropDlg.getCurvePropWidget().setPlotSettings(self.zoomStack[-1])
                self.curvePropDlg.getCurvePropWidget().refresh()                         
            
            return
       

    def __updateRubberBandRegion(self, event):
        self.rubberBandRect.setBottomRight(event.pos()) 
        self.update()
        return
        
    def __drawGrid(self,painter):
    
        painter.save()     
        font = painter.font()
        font.setPointSize(self.getFontSize() )
        painter.setFont(font)
        
        pen = QPen()
        pen.setColor(Qt.black)
        painter.setPen(pen)        

            
    
        rect = QRect(self.__marginLR, self.__margin, self.width() - 2 * self.__marginLR, self.height() - 2 * self.__margin);
        if (not rect.isValid()):
            return

        # On met un fond blanc au rectangle dans lequel on trace les courbes
        # à déplacer dans le paintEvent
        painter.fillRect(rect.adjusted(0, 0, -1, -1), Qt.white)
            
        # Calcul de la grille
        ( xminf, bdXf, yminf, bdYf ) = self.zoomStack[self.curZoom].updGrid()

        settings = self.zoomStack[self.curZoom]
        
        quiteDark = QPen(QPalette().dark().color().light())
        light = QPen(QPalette().light().color())
        i = 0
        
        pen = QPen()
        pen.setColor(Qt.black)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)        
        
        # axes x
        x = xminf
        while x<settings.getXmax():
            x1 = rect.left() + (x-settings.getXmin())/(settings.getXmax()-settings.getXmin())*rect.width()
            y1 = rect.bottom()
            x2 = x1
            y2 = rect.top()
            line = QLine(x1,y1,x2,y2)
            # Tracé des lignes verticales
            painter.drawLine(line)
            # Ecrit les labels
            label = x
            painter.drawText(x1 - 50, rect.bottom() + 2, 100, 25, # coord. point du rect + largeur et hauteur, Question y aura-t-il tjrs assez de place pour afficher le label
                              Qt.AlignHCenter | Qt.AlignTop,      # alignement
                              QString.number(label))              # texte à afficher            
            x+=bdXf
            
        # axes y
        y = yminf
        while y<settings.getYmax():
            x1 = rect.left()
            y1 = rect.bottom() - (y-settings.getYmin())/(settings.getYmax()-settings.getYmin())*rect.height()
            x2 = rect.right()
            y2 = y1
            line = QLine(x1,y1,x2,y2)
            # Tracé des lignes horizontales
            painter.drawLine(line)
            # Ecrit les labels
            label = y
            painter.drawText(rect.left() - self.__marginLR, y1 - 10, self.__marginLR - 5, 20,
                              Qt.AlignRight | Qt.AlignVCenter,
                              QString.number(label));            
            y+=bdYf        

        # Affiche un cadre autour de la zone dans laquelle
        # les courbes sont tracées      
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)  
        painter.drawRect(rect.adjusted(0, 0, -1, -1));
        
        painter.restore()   


    def __drawCurves(self,painter):
        painter.save()
        # Permet de donner un meilleur rendu aux courbes 
        # (pas de pixels apparents sur les courbes)
        painter.setRenderHint(QPainter.Antialiasing)        
        
        # rect = zone rectangulaire dans laquelle on trace les courbes
        settings = self.zoomStack[self.curZoom]
        rect = QRect(self.__marginLR, self.__margin,
                   self.width() - 2 * self.__marginLR, self.height() - 2 * self.__margin)
        self.rect = rect

        if (not rect.isValid()):
            return
        # on empêche le tracé en dehors de la zone rectangulaire
        painter.setClipRect(rect.adjusted(+1, +1, -1, -1)) 
        
        #print self.__curveList
        if self.__curveList == []: # si il n'y a pas de courbe à tracer on sort
            return
        
        for c in self.__curveList: 
            if c.getVisibility():
                poly = QPolygon(len(c.pts))
                i = 0
                for pt in c.pts: # On itère sur l'ensemble des points de la courbes
                    (x,y) = self.__ax2win(pt.x, pt.y)
                    poly[i] = QPoint(x,y)
                    i+=1
                    
                pen = QPen()         
                pen.setColor(c.getColor())        
                pen.setWidth(c.getLineW())
                pen.setStyle(c.getLineS())
                painter.setPen(pen);
                painter.drawPolyline(poly)
            
        painter.restore()
            
    def __drawMarker(self,painter):
        painter.save()
        painter.setClipRect(self.rect.adjusted(+1, +1, -1, -1)) 
        for c in self.__curveList:  
            if c.getVisibility():
                pen = QPen()         
                pen.setColor(c.getColor())
                pen.setWidth(c.getLineW())
                if c.getLineW() > 2 : 
                # pour eviter que les marker ne ressemblent à 
                # des cercles à cause de traits trop épais
                    pen.setWidth(2)                
                painter.setPen(pen);        
                if c.getMarker().fill:   
                    painter.setBrush(QBrush(c.getColor()))
                
                fctShape, theta = c.getMarker().getShape()
                
                for pt in c.pts: # On itère sur l'ensemble des points de la courbes
                    if c.getMarker().type == Marker.NoMarker :
                        break
                    (x,y) = self.__ax2win(pt.x, pt.y)
                    poly  = fctShape(x,y,theta)
                    painter.drawPolygon(poly) 
                
        painter.restore()    


 
                
    def __drawAxisLabel(self,painter):
        ''' Tracé du label des axes '''
        painter.save()

        font = painter.font()
        font.setPointSize(self.getFontSize())
        painter.setFont(font)
        
        pen = QPen()
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
    
        # Axe X  
        x_supG = self.__marginLR 
        y_supG = self.height() - self.__margin*0.55
        lx = self.width()  - 2 * self.__marginLR
        ly = self.__margin*0.5
        rectStringLabelX = QRectF(x_supG,y_supG,lx,ly)   
        #painter.drawRect(rectStringLabelX)        
        painter.drawText(rectStringLabelX,Qt.AlignCenter, self.__xlabel)    
        
        # Axe Y
        x_supG = self.__marginLR*0.7 
        y_supG = self.__margin*0.45    
        lx = self.width()  - 2 * self.__marginLR
        ly = self.__margin*0.5        
        rectStringLabelY = QRectF(x_supG,y_supG,lx,ly) 
        #painter.drawRect(rectStringLabelY)   
        painter.drawText(rectStringLabelY,Qt.AlignVCenter, self.__ylabel)   

        painter.restore()
        
        
        
    def __saveImage(self):       
        # 1.On récupère le nom du fichier que l'utilisateur veut créer
        fDialog = QFileDialog()
        fDialog.setDefaultSuffix('.png')
        fDialog.setViewMode(QFileDialog.Detail)
        fDialog.setFileMode(QFileDialog.AnyFile) # on sélectionne un seul nom de fichier qu'il existe ou non
        
        
        self.saveRep = os.getcwd()
        filename = fDialog.getSaveFileName(self, 'Save File', self.saveRep, "*.png" )

        # 2.Si l'utilisateur a appuyé sur le bouton "annuler"
        #   on sort proprement de la fonction saveImage
        if not filename:
            return
        
        # 3.On masque les boutons
        for b in self.__buttonToHide:
            b.setVisible(False);                      
        # 4.On met un fond blanc avant de sauver l'image (comme dans Matlab)
        self.setBackgroundRole(QPalette.Light)
        # 5.On sauve l'image
        sshot = QPixmap.grabWidget(self)       
        sshot.save(filename,'PNG',80) #la qualité est comprise entre 1 et 100 
        # (ne rien mettre si on veut la valeur par défaut)
        # 100 alourdit la taille du fichier et n'apporte rien. 80 semble un bon compromis
        # 6.On remet le fond gris
        self.setBackgroundRole(QPalette.Dark)# QPalette.Light)        
        # 7.On affiche les boutons
        for b in self.__buttonToHide:
            b.setVisible(True);
            
    def __copyImage(self):
    
        # 1.On masque les boutons
        for b in self.__buttonToHide:
            b.setVisible(False);                      
        # 2.On met un fond blanc avant de sauver l'image (comme dans Matlab)
        self.setBackgroundRole(QPalette.Light)
        # 3.On effectue une copie dans le clipboard 
        sshot = QPixmap.grabWidget(self)    
        clipBoard = QCoreApplication.instance().clipboard() # récuper le QApplication qui permet de gérer copy-paste
        clipBoard.setPixmap(sshot)
        # 4.On remet le fond gris
        self.setBackgroundRole(QPalette.Dark)# QPalette.Light)        
        # 5.On affiche les boutons
        for b in self.__buttonToHide:
            b.setVisible(True);      
            
            
    def loadMFile(self,fileName):
        ''' Fonction permettant d'importer les résultats d'un fichier _res.m
        obtenu avec MetaLub2.0
        '''
        # Nb: je laisse cette fonction dans la classe plotter  
        # pour pouvoir faire un load en ligne de commande 
        # via un objet de type plotter
        
        # Info à ajouter à chaque courbe
        info = fileName
        # -----
        curveDict = {}
        # Lecture du fichier _res.m
        f = open(fileName,'r') 
        txt = f.readline()
        while txt != '':
            a = txt.split('(')
            if len(a) != 1: # si len(a)=1 on ne lit pas la ligne d'un vecteur
                #print "a = ", a
                cName = a[0]
                b = a[1].split('[')
                #print "b = ", b
                c = b[1].split(';')
                #print "c = ", c
                x = float(c[0])
                # c[0] = 1er élément du vecteur
                d = c[1].split(']')
                #print 'd = ',d 
                y = float(d[0])
                # d[0] = 2è élément du vecteur            
                if cName not in curveDict :
                    curveDict[str(cName)] = Curve()
                    curveDict[str(cName)].setName(str(cName))
                    curveDict[str(cName)].setInfo(str(cName) + ' from ' + info)
                    curveDict[str(cName)].hide()
                curveDict[str(cName)].addPoint(x,y)
            txt = f.readline()    
        f.close()        
        return curveDict        
               
         
class Legend:
    # On définit une enum pour désigner la position de la légende
    NorthWest, NorthCenter, NorthEast, CenterWest, CenterEast, SouthWest, SouthCenter, SouthEast = range(0,8)
    def __init__(self):
        self.__vSpace     = 3  # Nbre de pixels entre deux lignes de la légende
        self.__hSpace     = 5  # Nbre de pixels entre deux éléments 
                               # successifs sur une même ligne
        self.__lMiniCurve = 30 # largeur du morceau de courbe tracé en vis-à-vis du label

        # Distance entre le coin sup. gauche du cadre 
        # de traçage des courbes et le coin supérieur gauche de la légende       
        self.__dxLeg   = 5    # selon X
        self.__dyLeg   = 5    # selon Y
        self.__display = True # Si True -> on affiche la légende
    
        self.__position = Legend.NorthWest
    
    def setPostion(self,pos):
        self.__position = pos
    def getPostion(self):
        return self.__position
        
    def setDisplay(self,disp):
        self.__display = disp
    def getDisplay(self):
        return self.__display
        
    # à mettre en argument self.getFontSize()
    def drawLegend(self, painter, curveList, fontSize,marginLR,margin,width,height):
        if not self.__display: # on ne trace pas la légende
            return
        # Rectangle contenant la légende
        curveToDraw = self.__drawLegBorder(painter, curveList, fontSize,marginLR,margin,width,height)
        if curveToDraw:
            # Ecriture du nom des courbes
            self.__writeCName(painter,curveList,fontSize)
            # Tracé d'une ligne en vis à vis du nom de la courbe
            self.__drawCItem(painter,curveList)
            
        painter.restore()
             
    def __drawLegBorder(self,painter, curveList, fontSize,marginLR,margin,widthWidg,heightWidg):
        '''Tracé du rectangle entourant la légende.
        Ses dimensions sont calculées sur base du nom de courbe le plus long
        '''    
        # On récupère la plus longue chaine de caractères du nom des courbes
        font = painter.font()
        font.setPointSize(fontSize)  

        lenText = []
        nCurveToShow = 0 # nombre de courbes affichées
        for c in curveList:        
            if c.getVisibility(): # uniquement si la courbe est affichée       
                lenText.append(len(c.getName()))
                nCurveToShow = nCurveToShow+1
            else:
                lenText.append(0)
            
        if len(lenText) == 0:
            return False # on ne trace pas de légende -> car pas de courbe dans la liste

        painter.save()
        ind = lenText.index(max(lenText))

        fm = QFontMetrics(font);
        self.__pixelsWide = fm.width(curveList[ind].getName());
        self.__pixelsHigh = fm.height();   
               
        # largeur du rectangle encadrant la légende
        self.__widthLeg  = self.__hSpace*3 + self.__lMiniCurve + self.__pixelsWide  
        # hauteur du rectangle encadrant la légende
        self.__heightLeg = nCurveToShow*self.__pixelsHigh + (nCurveToShow+1)*self.__vSpace      
        # coordonnées du coin sup gauche du rectangle autour de la légende
        xSupG, ySupG = self.__computeRCornerPos(marginLR,margin,widthWidg,heightWidg)
                
        pen = QPen()
        pen.setColor(Qt.black)
        painter.setFont(font)
        painter.setPen(pen)
        
        self.rectLegend = QRectF(xSupG,ySupG,self.__widthLeg,self.__heightLeg) 
        painter.setBrush(Qt.white)
        painter.drawRect(self.rectLegend)    
        return True  
        
    def __computeRCornerPos(self,marginLR,margin,widthWidg,heightWidg):
        ''' calcul des coordonnées du coin sup gauche 
        du rectangle autour de la légende '''        
        if (self.__position == Legend.NorthWest):
            self.__dxLeg = 5 
            self.__dyLeg = 5 
            xSupG = marginLR + self.__dxLeg 
            ySupG = margin   + self.__dyLeg

        elif (self.__position == Legend.NorthCenter):
            widthGraphe = widthWidg-2*marginLR
            self.__dxLeg = (widthGraphe - self.__widthLeg)/2.0
            self.__dyLeg = 5 
            xSupG = marginLR + self.__dxLeg 
            ySupG = margin   + self.__dyLeg      
            
        elif (self.__position == Legend.NorthEast):
            widthGraphe = widthWidg-2*marginLR
            self.__dxLeg = widthGraphe - self.__widthLeg - 5
            self.__dyLeg = 5 
            xSupG = marginLR + self.__dxLeg 
            ySupG = margin   + self.__dyLeg     

        elif (self.__position == Legend.CenterWest):
            heightGraphe = heightWidg-2*margin
            self.__dxLeg = 5 
            self.__dyLeg = (heightGraphe - self.__heightLeg)/2.0
            xSupG = marginLR + self.__dxLeg 
            ySupG = margin   + self.__dyLeg            

        elif (self.__position == Legend.CenterEast):
            widthGraphe = widthWidg-2*marginLR
            heightGraphe = heightWidg-2*margin
            self.__dxLeg = widthGraphe - self.__widthLeg - 5
            self.__dyLeg = (heightGraphe - self.__heightLeg)/2.0
            xSupG = marginLR + self.__dxLeg 
            ySupG = margin   + self.__dyLeg            

        elif (self.__position == Legend.SouthWest):
            heightGraphe = heightWidg-2*margin
            self.__dxLeg = 5
            self.__dyLeg = (heightGraphe - self.__heightLeg) -5
            xSupG = marginLR + self.__dxLeg 
            ySupG = margin   + self.__dyLeg                   
            
        elif (self.__position == Legend.SouthCenter):
            widthGraphe = widthWidg-2*marginLR            
            heightGraphe = heightWidg-2*margin
            self.__dxLeg = (widthGraphe - self.__widthLeg)/2.0
            self.__dyLeg = (heightGraphe - self.__heightLeg) -5
            xSupG = marginLR + self.__dxLeg 
            ySupG = margin   + self.__dyLeg                 
            
        elif (self.__position == Legend.SouthEast):
            widthGraphe = widthWidg-2*marginLR
            heightGraphe = heightWidg-2*margin
            self.__dxLeg = widthGraphe - self.__widthLeg - 5
            self.__dyLeg = (heightGraphe - self.__heightLeg) -5
            xSupG = marginLR + self.__dxLeg 
            ySupG = margin   + self.__dyLeg                

        return xSupG,ySupG        

    def __writeCName(self,painter,curveList,fontSize):
        '''Ecriture du nom des courbes dans la légende
        '''
        pSupG = self.rectLegend.topLeft()
        xSupG = pSupG.x()
        ySupG = pSupG.y()
        i = 1
        for c in curveList:   
            if c.getVisibility(): # uniquement si la courbe est affichée       
                x = xSupG+2*self.__hSpace+self.__lMiniCurve
                y = ySupG+i*self.__vSpace+(i-1)*self.__pixelsHigh
                #painter.drawRect(QRectF(x,y,pixelsWide,pixelsHigh))
                pen = QPen()
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.drawText(QRectF(x,y,self.__pixelsWide,self.__pixelsHigh),Qt.AlignVCenter,c.getName())           
                i=i+1        
        
    def __drawCItem(self,painter,curveList):
        '''Tracé d'un trait en vis a vis du nom de la courbe
        '''
        pSupG = self.rectLegend.topLeft()
        xSupG = pSupG.x()
        ySupG = pSupG.y()        
        
        i = 1
        for c in curveList:  
            if c.getVisibility(): # uniquement si la courbe est affichée               
                x1 = xSupG + self.__hSpace
                y1 = ySupG + i*self.__vSpace+(i-1)*self.__pixelsHigh/2.0+i*self.__pixelsHigh/2.0
                
                poly    = QPolygon(2) #2 points à relier
                poly[0] = QPoint(x1             , y1)
                poly[1] = QPoint(x1 + self.__lMiniCurve, y1)
                # Tracé de la ligne
                pen = QPen()
                pen.setColor(c.getColor())        
                pen.setWidth(c.getLineW())
                pen.setStyle(c.getLineS())
                painter.setPen(pen);        
                painter.drawPolyline(poly)

                # Tracé du marker éventuel    
                if c.getMarker().fill:   
                    painter.setBrush(QBrush(c.getColor()))
                else:
                    painter.setBrush(QBrush(Qt.transparent))
                
                fctShape, theta = c.getMarker().getShape()
                if c.getMarker().type != Marker.NoMarker :               
                    pen = QPen()         
                    pen.setColor(c.getColor())
                    pen.setWidth(2)
                    painter.setPen(pen)              
                    poly  = fctShape(x1 + self.__lMiniCurve/2.0,y1,theta)
                    painter.drawPolygon(poly)             
                
                i = i+1               

    
class PlotSettings():
    def __init__(self):
        self.__xmin =  0.0
        self.__xmax = 10.0
        self.__numXTicks = 8
    
        self.__ymin =  0.0
        self.__ymax = 10.0
        self.__numYTicks = 5
    
    def spanX(self):
        return self.__xmax - self.__xmin   
    def spanY(self):
        return self.__ymax - self.__ymin    
    def updGrid(self):
        # axes
        (xminf, bdXf) = self.__computegrid(self.__xmin, self.__xmax, self.__numXTicks)
        (yminf, bdYf) = self.__computegrid(self.__ymin, self.__ymax, self.__numYTicks)
        '''
        if 1: # debug grid
            print '-----------------'
            print "self.xmin,xmax =", self.xmin, self.xmax
            print "self.ymin,ymax =", self.ymin, self.ymax
            print "xminf =", xminf
            print "bdXf =" , bdXf
            
            print "yminf =", yminf
            print "bdYf =" , bdYf        
            print '-----------------'
        '''
        return ( xminf, bdXf, yminf, bdYf )   
    def __computegrid(self, xmin, xmax, gridX):
        # find best step
        dx  = xmax-xmin  # print "dX=" , dx
        dgX = dx/gridX   # print "dgX=", dgX      # wanted dX
        
        # step in [0,10]        
        expo   = math.floor(math.log(dgX,10)) # print "expo=", expo
        factor = math.pow(10.0, expo)         # print "factor=", factor
        dgX3   = dgX/factor                   # print "dgX3=", dgX3
        
        # best integer increment
        if dgX3<1.5:
            bdXi=1
        elif dgX3<3.5:
            bdXi=2
        elif dgX3<7.5:
            bdXi=5
        else:
            bdXi=10

        bdXf =  bdXi*factor       
                   
        # find first grid pos.
        xminf = xmin/factor
        xmini = math.floor(xminf)
        
        while 1:
            if xmini%bdXi==0 and xmini>=xminf: break
            xmini+=1
        xminf = xmini*factor
        
        return (xminf, bdXf)       
    
    def setXmin(self,xmin):
        self.__xmin = xmin
    def getXmin(self):
        return self.__xmin

    def setXmax(self,xmax):
        self.__xmax = xmax
    def getXmax(self):
        return self.__xmax
        
    def setYmin(self,ymin):
        self.__ymin = ymin
    def getYmin(self):
        return self.__ymin        

    def setYmax(self,ymax):
        self.__ymax = ymax    
    def getYmax(self):
        return self.__ymax              


def fct(x):
    return math.sin(2*x)+math.cos(4*x)        

def fct2(x):
    return 1.0 + 0.25*math.sin(2*x)     
    
def main():   
    # Partie relative à l'interface graphique :
    app = QApplication(sys.argv)
    form = Plotter()
    form.setXlabel("Position dans l'emprise [mm]")
    form.setYlabel("Pression [MPa]")

    # Lecture de 2 fichiers .ascii contenant les points à tracer
    curve1 = Curve()
    curve1.loadData2('vectors/p_x.ascii','vectors/p_y.ascii',"Pression d'interface")   
    
    form.addCurve(curve1) # ajout de la courbe à tracer dans le plotter
    form.updCurveList()       
    
    # Lecture d'un fichier .ascii contenant 2 colonnes
    curve2 = Curve()
    curve2.loadData1('vectors/p_f.ascii','Pression du lubrifiant')
    curve2.setColor(Qt.red)
    form.addCurve(curve2) 
    form.updCurveList()    

    # Lecture d'un fichier res.m contenant les résultats calculés avec MetaLub
    cDict = form.loadMFile('vectors/A11_FL_CylRigc_res.m')
    form.appendCurveDict(cDict,'A11_FL_CylRigc_res.m')   

    # Intervalle sur lequel on affiche les courbes
    form.getPlotSettings().setXmin(-9.)
    form.getPlotSettings().setXmax( 2.)
    
    form.getPlotSettings().setYmin(  0.)
    form.getPlotSettings().setYmax(400.)

    # Tracé d'une fonction sur base de son expression analytique
    c3 = Curve()
    c3.fill2(fct, (-1.5,10), 150)    
    c3.setName('Courbe 1')
    c3.hide()  # la courbe est en mémoire mais on choisit de ne pas l'afficher
    form.addCurve(c3)
        
    c4 = Curve()
    c4.fill2(fct2, (-1.5,10), 150)  
    c4.setName('1+0.25 * sinus(2x)')
    c4.hide()  # la courbe est en mémoire mais on choisit de ne pas l'afficher
    form.addCurve(c4)
    
    
    form.show()
    app.exec_()    
    
if __name__=="__main__":
    main()
  