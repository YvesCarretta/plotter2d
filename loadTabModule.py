#!/usr/bin/env python
# -*- coding: latin-1; -*- 

from PyQt4.QtCore import *
from PyQt4.QtGui  import *

from curveModule import *

import os

class LoadFileTab(QWidget):
        
    def __init__(self,openRep,plotter2D): # on met les arguments du constructeur ici
        super(LoadFileTab, self).__init__()   

        self.openRep     = openRep
        self.txtBrowser  = QTextBrowser()
        
        self.__plotter2D = plotter2D

        layout = QVBoxLayout()
        
        self.tabWidget        = QTabWidget(self)#self.tabWidgetLoadGen)
        
        # Chargement de fichiers .ascii
        self.qWid_loadAscii = LoadAsciiWidget(self.openRep,self.txtBrowser,\
                                              self.__plotter2D,self.refresh)
        self.tabWidget.addTab(self.qWid_loadAscii,"Load .ascii")      

        # Tracer d'une courbe en fonction de son expression analytique
        self.qWid_DrawAnaFun = DrawAnaFunWidget(self.txtBrowser,self.__plotter2D,\
                                                self.refresh)
        self.tabWidget.addTab(self.qWid_DrawAnaFun,'Draw y = f(x)')              

        # Chargement du contenu d'un fichier .m issu de lubri
        self.qWid_LoadMFile = LoadMFileWidget(self.openRep,self.txtBrowser,\
                                              self.__plotter2D,self.refresh)
        self.tabWidget.addTab(self.qWid_LoadMFile,'Load .m')   
        
        
        layout.addWidget(self.tabWidget)
        layout.addWidget(self.txtBrowser)
        
        self.setLayout(layout)
        self.txtBrowser.setFixedHeight(100)

    def refresh(self):
        self.__plotter2D.updCurveList()


class LoadFileWidget(QWidget):
    
    def __init__(self,openRep,txtBrowser,plotter2D,refresh):
        super(LoadFileWidget, self).__init__()
        self.openRep    = openRep
        self.txtBrowser = txtBrowser
        self.plotter2D  = plotter2D
        self.refresh    = refresh    # référence vers la fonction refresh du dialogue

    def selectFile(self, existingText):
        fDialog = QFileDialog()
        fDialog.setViewMode(QFileDialog.Detail)
        fDialog.setFileMode(QFileDialog.AnyFile) # on sélectionne un seul nom de fichier qu'il existe ou non

        if len(existingText) != 0:
            existingText = str(existingText.replace('/',os.sep) )
            repName = os.path.dirname(existingText.replace('/',os.sep) ) 
            # s'il y a déjà un fichier sélectionné
            #    -> on ouvre la boîte de dialogue dans le répertoire de ce fichier
            # sinon on ouvre la boite de dialogue dans le dernier répertoire sélectionné
            if os.path.isdir(repName):
                self.openRep = repName
        # Ouverture de la boîte de dialogue
        filename = str(QFileDialog.getOpenFileName(self, 'Open File', self.openRep))
        
        if not filename: # Si l'utilisateur a appuyé sur le bouton "annuler"
            return ''    # on sort proprement de la fonction 
        
        self.openRep = os.path.dirname(filename.replace('/',os.sep) ) 
        
        return filename           
        
class LoadMFileWidget(LoadFileWidget):

    def __init__(self,openRep,txtBrowser,plotter2D,refresh):
        super(LoadMFileWidget, self).__init__(openRep,txtBrowser,plotter2D,refresh)   
        # LineEdit et bouttons
        self.lEdit_mFile      = QLineEdit()
        self.repButton_mFile  = QToolButton()
        
        self.lEditTreeName_mFile = QLineEdit()
        self.loadButton_mFile    = QPushButton('Load to memory')
        
        # Layout
        loadMFile_gb = QGroupBox('File Selection')
        
        grid = QGridLayout()
        grid.addWidget(QLabel('File name') ,0,0)
        grid.addWidget(self.lEdit_mFile    ,0,1)
        grid.addWidget(self.repButton_mFile,0,2)    

        grid.addWidget(QLabel('Tree structure name') ,1,0)
        grid.addWidget(self.lEditTreeName_mFile      ,1,1)       
        
        grid.addWidget(self.loadButton_mFile,3,0)   
        
        loadMFile_gb.setLayout(grid)
        
        layout = QVBoxLayout()
        layout.addWidget(loadMFile_gb)
        layout.insertSpacing(-1, 160) # index négatif donc on ajoute l'espace à la fin
        
        self.setLayout(layout)
        
        # Signaux
        self.connect(self.repButton_mFile ,SIGNAL("clicked ()"), self.__selectMfile) 
        self.connect(self.loadButton_mFile,SIGNAL("clicked ()"), self.__loadMfile)     

    def __selectMfile(self):
        existingText = self.lEdit_mFile.text()
        filename     = self.selectFile(existingText)
        # On ne met à jour le contenu du QLineEdit que si 
        # on a sélectionné un fichier valide et si l'utilisateur 
        # n'a pas appuyé sur annuler
        if len(filename) != 0:
            self.lEdit_mFile.setText(filename)    
        
    def __loadMfile(self):
        fileName = self.lEdit_mFile.text()
        t1       = fileName
        # 1. Le contenu des lineEdit correspond à des fichiers ?
        if os.path.isfile(t1):
            # 2. Est-ce que c'est un fichier .ascii ?
            if (t1.split('.')[-1] == 'm'):                   
                # ---------------------------------------------
                # 3. Lecture du fichier
                cDict = self.plotter2D.loadMFile(fileName)
                if len(self.lEditTreeName_mFile.text()) == 0:
                    absP = os.path.abspath(fileName)
                    treeName = os.path.basename(absP.replace('/',os.sep))
                else:
                    treeName = self.lEditTreeName_mFile.text()
                self.plotter2D.appendCurveDict(cDict,treeName)   
                self.refresh()                
                # ---------------------------------------------
                self.txtBrowser.append('<font color=green> %s: <b>load successful !</b>' % fileName)
                return 
            else:
                self.txtBrowser.append('<font color=red>Selected file does not have a .m extension')
        else:
            self.txtBrowser.append('<font color=red> Selected path is not a file')
            
        self.txtBrowser.append('<font color=red> M file : %s '% t1)
        self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')  
        return           
        
class LoadAsciiWidget(LoadFileWidget):

    def __init__(self,openRep,txtBrowser,plotter2D,refresh):
        super(LoadAsciiWidget, self).__init__(openRep,txtBrowser,plotter2D,refresh)   

        self.matrix1 = None
        self.matrix2 = None
                
        loadMatrixLayout = QVBoxLayout()
        
        # Sélection des fichiers
        # -----------------------
        loadFile_gb = QGroupBox('File Selection')
        grid = QGridLayout()
        self.lEdit_mat1       = QLineEdit()
        self.repButton_mat1   = QToolButton()
        self.loadButton_mat1  = QPushButton('Load')

        self.lEdit_mat2       = QLineEdit()
        self.repButton_mat2   = QToolButton()    
        self.loadButton_mat2  = QPushButton('Load')        
        
        grid.addWidget(QLabel('File 1')     ,0,0)
        grid.addWidget(self.lEdit_mat1      ,0,1)
        grid.addWidget(self.repButton_mat1  ,0,2)    
        grid.addWidget(self.loadButton_mat1 ,0,3)

        grid.addWidget(QLabel('File 2')     ,1,0)
        grid.addWidget(self.lEdit_mat2      ,1,1)
        grid.addWidget(self.repButton_mat2  ,1,2)
        grid.addWidget(self.loadButton_mat2 ,1,3)     

        loadFile_gb.setLayout(grid)
        loadMatrixLayout.addWidget(loadFile_gb)
        
        # Affichage des informations sur les fichiers loadés
        # ----------------------------------------------------
        infoFile_gb = QGroupBox('Info. on loaded files')
        
        self.labX_mat1 = QLabel('File 1 : has not been loaded yet')        

        self.labX_mat2 = QLabel('File 2 : has not been loaded yet')        
        
        grid = QGridLayout()
        grid.addWidget(self.labX_mat1,0,0)

        grid.addWidget(self.labX_mat2,1,0)

        infoFile_gb.setLayout(grid)
        loadMatrixLayout.addWidget(infoFile_gb)

        # Sélection des vecteurs X et Y dans les fichiers loadés
        # -------------------------------------------------------
        vecXvecY_gb = QGroupBox('Slection of vec. X and vec. Y')
        
        grid = QGridLayout()    

        self.xFile_cbox = QComboBox()
        self.xFile_cbox.addItem('File 1')
        self.xFile_cbox.addItem('File 2')
                
        self.xLorC_cbox = QComboBox()
        self.xLorC_cbox.addItem('Column')
        self.xLorC_cbox.addItem('Line')
        self.xLorCNbr_lEdit = QLineEdit('1')
        self.xLorCNbr_lEdit.setValidator(QIntValidator())

        grid.addWidget(QLabel('Vec. X')   ,0,0)
        grid.addWidget(self.xFile_cbox    ,0,1)
        grid.addWidget(self.xLorC_cbox    ,0,2)
        grid.addWidget(self.xLorCNbr_lEdit,0,3)

        self.yFile_cbox = QComboBox()
        self.yFile_cbox.addItem('File 1')
        self.yFile_cbox.addItem('File 2')
        
        self.yLorC_cbox = QComboBox()
        self.yLorC_cbox.addItem('Column')
        self.yLorC_cbox.addItem('Line')
        self.yLorCNbr_lEdit = QLineEdit('2')
        self.yLorCNbr_lEdit.setValidator(QIntValidator())

        grid.addWidget(QLabel('Vec. Y')   ,1,0)
        grid.addWidget(self.yFile_cbox    ,1,1)
        grid.addWidget(self.yLorC_cbox    ,1,2)
        grid.addWidget(self.yLorCNbr_lEdit,1,3)   

        vecXvecY_gb.setLayout(grid)
        
        loadMatrixLayout.addWidget(vecXvecY_gb)
   
        # Nom de la courbe
        horButton = QHBoxLayout()
        horButton.setSpacing(5)
        
        self.lEdit_curveName   = QLineEdit()
        self.buttonDrawFromMat = QPushButton('Draw')                
        
        horButton.addWidget(QLabel('Curve Name'))        
        horButton.addWidget(self.lEdit_curveName)
        horButton.addWidget(self.buttonDrawFromMat) 

        loadMatrixLayout.addItem(horButton)
        self.setLayout(loadMatrixLayout)             

        # Signaux associés
        self.connect(self.repButton_mat1 ,SIGNAL("clicked ()"), self.__selectXfile) 
        self.connect(self.loadButton_mat1,SIGNAL("clicked ()"), self.__loadMatrixFile1) 
        
        self.connect(self.repButton_mat2 ,SIGNAL("clicked ()"), self.__selectYfile) 
        self.connect(self.loadButton_mat2,SIGNAL("clicked ()"), self.__loadMatrixFile2)   
        
        self.connect(self.buttonDrawFromMat,SIGNAL("clicked ()"), self.__drawFromMatrix)           

   
    def __selectXfile(self):
        existingText = self.lEdit_mat1.text()
        filename     = self.selectFile(existingText)
        # On ne met à jour le contenu du QLineEdit que si 
        # on a sélectionné un fichier valide et si l'utilisateur 
        # n'a pas appuyé sur annuler
        if len(filename) != 0:
            self.lEdit_mat1.setText(filename)   

    def __loadMatrixFile1(self):
        fileName = self.lEdit_mat1.text()
        self.matrix1, self.nC1, self.nL1 = self.__loadMatrix(fileName)
        
        self.labX_mat1.setText('File 1 : contains'+str(self.nL1) + ' lines and ' + str(self.nC1) + ' columns')

    def __selectYfile(self):
        existingText = self.lEdit_mat2.text()
        filename     = self.selectFile(existingText)
        # On ne met à jour le contenu du QLineEdit que si 
        # on a sélectionné un fichier valide et si l'utilisateur 
        # n'a pas appuyé sur annuler
        if len(filename) != 0:
            self.lEdit_mat2.setText(filename)     

    def __loadMatrixFile2(self):
        fileName = self.lEdit_mat2.text()
        self.matrix2, self.nC2, self.nL2 = self.__loadMatrix(fileName)
        
        self.labX_mat2.setText('File 2 : contains'+str(self.nL2) + ' lines and ' + str(self.nC2) + ' columns')
            
    def __drawFromMatrix(self):
        vecX=[]
        vecY=[]        
        
        # 1. Abscisses de la courbe (vecX) :
        # -----------------------------------
        if self.xFile_cbox.currentIndex() == 0 :
            # 1.1 Si c'est File 1 qui est sélectionné
            #     -> on vérifie que self.matrix1 a bien été loadé
            if self.matrix1 != None:
                matrix = self.matrix1
                vecXFname = self.lEdit_mat1.text()
            else:
                self.txtBrowser.append('<font color=red> Matrix 1 has not been loaded !</b>')   
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')  
                return
        elif self.xFile_cbox.currentIndex() == 1 :
            # 1.2 Si c'est File 2 qui est sélectionné
            #     -> on vérifie que self.matrix2 a bien été loadé            
            if self.matrix2 != None:
                matrix = self.matrix2
                vecXFname = self.lEdit_mat2.text()
            else:
                self.txtBrowser.append('<font color=red> Matrix 2 has not been loaded !</b>')   
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')  
                return
        
        if self.xLorC_cbox.currentIndex() == 0: # Colonne
            col = int(self.xLorCNbr_lEdit.text())       
            if col>len(matrix[0]):
                self.txtBrowser.append('<font color=red> File selected for vec. X \
                                         does not contain %s columns !</b>' % str(col))   
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')    
                return
            else:
                col=col-1 # -1 pour que la colonne 1 dans l'interface 
                # graphique corresponde à la colonne 0 de la matrice
                for i in range(0,len(matrix)):
                    vecX.append(matrix[i][col])     
                info = 'Vec. X = column ' + str(col+1) + ' from file :' + vecXFname + '\n'
        elif self.xLorC_cbox.currentIndex() == 1: # Ligne
            line = int(self.xLorCNbr_lEdit.text()) 
            if line>len(matrix):
                self.txtBrowser.append('<font color=red> File selected for vec. X \
                                         does not contain %s lines !</b>' % str(line))   
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')   
                return
            else:
                line=line-1
                # -1 pour que la colonne 1 dans l'interface graphique
                # corresponde à la colonne 0 de la matrice
                vecX = matrix[line][:]
                info = 'Vec. X = line ' + str(line+1) + ' from file :' + vecXFname + '\n'
            
        
        # 2.  Ordonnées de la courbe (vecY) :
        # ------------------------------------
        if self.yFile_cbox.currentIndex() == 0 : 
            # 2.1 C'est File 1 qui est sélectionné
            #     -> on vérifie que self.matrix1 a bien été loadé
            if self.matrix1 != None:
                matrix    = self.matrix1
                vecYFname = self.lEdit_mat1.text()
            else: 
                self.txtBrowser.append('<font color=red> Matrix 1 has not been loaded !</b>')   
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')  
                return             
        elif self.yFile_cbox.currentIndex() == 1 : 
            # 2.2 C'est File 2 qui est sélectionné
            #     -> on vérifie que self.matrix2 a bien été loadé                
            if self.matrix2 != None:
                matrix = self.matrix2
                vecYFname = self.lEdit_mat2.text()
            else: 
                self.txtBrowser.append('<font color=red> Matrix 2 has not been loaded !</b>')   
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')  
                return            
        
        
        if self.yLorC_cbox.currentIndex() == 0: 
            # 2.3 VecY est une colonne de la matrice
            col = int(self.yLorCNbr_lEdit.text())
            if col>len(matrix[0]):
                self.txtBrowser.append('<font color=red> File selected for vec. Y \
                                         does not contain %s columns !</b>' % str(col))   
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')  
                return                
            else:
                col=col-1 # -1 pour que la colonne 1 dans l'interface             
                # graphique corresponde à la colonne 0 de la matrice
                for i in range(0,len(matrix)):
                    vecY.append(matrix[i][col])   
                info = info+'Vec. Y = column ' + str(col+1) + ' from file : ' + vecYFname
        elif self.yLorC_cbox.currentIndex() == 1:
            # 2.4 VecY est une ligne de la matrice
            line = int(self.yLorCNbr_lEdit.text())
            if line>len(matrix):
                self.txtBrowser.append('<font color=red> File selected for vec. Y \
                                         does not contain %s lines !</b>' % str(line))   
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')  
                return
            else:
                line=line-1 # -1 pour que la colonne 1 dans l'interface graphique
                # corresponde à la colonne 0 de la matrice
                vecY = matrix[line][:]       
                info = info+'Vec. Y = column ' + str(line+1) + ' from file : ' + vecYFname                
                
        curve = Curve()  
        if not curve.fill(vecX,vecY):
            self.txtBrowser.append('<font color=red> Vec. X and Vec. Y must be the same length !</b>')          
            return    
        curve.show()
        
        if len(self.lEdit_curveName.text()) == 0:
            cName = "Curve From ascii"
        else:
            cName = self.lEdit_curveName.text()
            
        curve.setName(cName)
        curve.setInfo(info)        
        
        self.plotter2D.addCurve(curve) 
        self.refresh()
                
                
    def __loadMatrix(self,fileName):   
        t1  = fileName
        # 1. Le contenu des lineEdit correspond à des fichiers ?
        if os.path.isfile(t1):
            # 2. Est-ce que c'est un fichier .ascii ?
            if (t1.split('.')[-1] == 'ascii'):                   
                # ---------------------------------------------
                # 3. Lecture du fichier
                f = open(fileName,'r')
                txt = f.readline()
                a = txt.split()
                matrix = []
                nC = len(a) # nombre de colonne
                nL = 1      # nombre de lignes
                while txt != '':
                    a = txt.split()
                    aFloat = [float(i) for i in a]
                    matrix.append(aFloat)
                    #print "a = ", a
                    txt = f.readline()    
                    nL = nL+1
                f.close()
                # ---------------------------------------------
                self.txtBrowser.append('<font color=green> %s: <b>load successful !</b>' % fileName)
                #print "matrix = ", matrix
                #print "len(matrix) = ", len(matrix)
                return matrix, nC, nL
            else:
                self.txtBrowser.append('<font color=red>Selected file does not have a .ascii extension')
        else:
            self.txtBrowser.append('<font color=red> Selected path is not a file')
            
        self.txtBrowser.append('<font color=red> Matrix XY : %s '% t1)
        self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')  
        return 0,0,0
                        
    def __selectMatrixfile(self): # PIPO
        # Matrix 1:
        existingText = self.lEdit_mat1.text()
        filename     = self.selectFile(existingText)
        # Matrix 2:
        existingText = self.lEdit_mat2.text()
        if len(existingText) > 0:
            filename     = self.selectFile(existingText)        

class DrawAnaFunWidget(QWidget):

    def __init__(self, txtBrowser,plotter2D,refresh):
        super(DrawAnaFunWidget, self).__init__()        
        
        self.txtBrowser = txtBrowser
        self.plotter2D  = plotter2D
        self.refresh    = refresh
               
        grid = QGridLayout()

        self.lEditFunc_name = QLineEdit()
        grid.addWidget(QLabel('Curve name') ,0,0)
        grid.addWidget(self.lEditFunc_name  ,0,1)   
        
        self.lEditFunc_expr = QLineEdit()
        grid.addWidget(QLabel('f(x)')      ,1,0)        
        grid.addWidget(self.lEditFunc_expr ,1,1)

        
        self.lEditFunc_xMin = QLineEdit()
        self.lEditFunc_xMin.setValidator(QDoubleValidator())
        grid.addWidget(QLabel('x min.')    ,2,0)        
        grid.addWidget(self.lEditFunc_xMin ,2,1)        

        self.lEditFunc_xMax = QLineEdit()
        self.lEditFunc_xMax.setValidator(QDoubleValidator())
        grid.addWidget(QLabel('x max.')    ,3,0)        
        grid.addWidget(self.lEditFunc_xMax ,3,1)                
        
        self.lEditFunc_nbPoints = QLineEdit()
        self.lEditFunc_nbPoints.setValidator(QIntValidator())
        grid.addWidget(QLabel('Nb. points')    ,4,0)        
        grid.addWidget(self.lEditFunc_nbPoints ,4,1)            
        
        self.buttonLoadFun = QPushButton('Draw')
        grid.addWidget(self.buttonLoadFun,5,0)     

        
        gboxAnaFun = QGroupBox(self)
        gboxAnaFun.setLayout(grid)        
        
        
        vertLayout = QVBoxLayout()
        vertLayout.addWidget(gboxAnaFun)
        vertLayout.insertSpacing(-1, 100) # index négatif donc on ajoute l'espace à la fin
        
        self.setLayout(vertLayout)
        
        # Générer la courbe sur base d'une expression analytique
        self.connect(self.buttonLoadFun,SIGNAL("clicked()"), self.__genAnaFun)                

    def __genAnaFun(self):

        listLabel = [self.lEditFunc_expr,self.lEditFunc_xMin,self.lEditFunc_xMax,self.lEditFunc_nbPoints]
        for elem in listLabel:
            if len(elem.text()) == 0:
                # on vérifie qu'on a rempli tous les labels
                self.txtBrowser.append('<font color=red> Missing at least one parameter !')
                self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')
                return

        xMin = float(self.lEditFunc_xMin.text())
        xMax = float(self.lEditFunc_xMax.text())       
        if ( xMin > xMax ):
            self.txtBrowser.append('<font color=red> x min larger than x max !')
            self.txtBrowser.append("<font color=red>%s is not larger than %s</b>" % (str(xMin), str(xMax) ))
            self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')
            return
            
        nbPoints = int(self.lEditFunc_nbPoints.text())  
        if (nbPoints < 2 ):
            self.txtBrowser.append('<font color=red> You must use at least two sampling points!')
            self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')
            return            
    
        name = self.lEditFunc_name.text()
        if len(name) == 0:
            name = 'Curve num. ' + str(len(self.plotter2D.getCurveList()))    
    
        # On vérifie que la fonction est valide
        # c'est un peu foireux -> voir à l'usage       
        testFunc = isinstance(self.fctAna(xMin), (int, long, float))
        if not testFunc :
            self.txtBrowser.append('<font color=red> Check your function : \n \
                                    you must use y = f(x)! \n \
                                    for instance : sin(2*x)')
            self.txtBrowser.append('<font color=red><b>Load aborted</b>\n')
            return
    
        curve = Curve()
        curve.fill2(self.fctAna, (xMin,xMax), nbPoints)    
        curve.setName(name)
        
        info = 'f(x) = ' + self.lEditFunc_expr.text() + '\n' + \
               'x min = ' + str(xMin) + '\n' +\
               'x max = ' + str(xMax) + '\n' +\
               str(nbPoints) + ' sampling points'
                
        curve.setInfo(info) # fonction à déplacer dans la classe curve 
        # pour être cohérent avec les autres opérations du même type (setInfo)
        
        self.plotter2D.addCurve(curve) 
        self.refresh()
        self.txtBrowser.append('<font color=green> Analytical function %s drawn from \
                                x min. = %s to x max. = %s with %s sampling points!' \
                                %(self.lEditFunc_expr.text(), str(xMin),str(xMax),str(nbPoints) ))
        self.txtBrowser.append('<font color=green> %s: <b>load successful !</b>' % name)                                
    
    def fctAna(self,x):
        return eval(unicode(self.lEditFunc_expr.text()))     