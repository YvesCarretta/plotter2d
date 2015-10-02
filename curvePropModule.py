#!/usr/bin/env python
# -*- coding: latin-1; -*-     

from PyQt4.QtCore import *
from PyQt4.QtGui import *    

import treeModule

class CurvePropWidget(QWidget):

    def __init__(self, plotter2D, callback):
        super(CurvePropWidget, self).__init__()
        
        # Liste des courbes -> permet d'accéder aux propriétés 
        # des courbes pour mettre à jour les widget et modifier les
        # propriétés des courbes
        self.plotter2D   = plotter2D
        self.__curveList = plotter2D.getCurveList()
        
        self.__plotSettings = plotter2D.getPlotSettings()
        
        self.__currentItem  = None
        self.__currentCurve = None
        
        # Propriétés des lignes
        # ----------------------
        self.lineLab = QLabel('Line')
        
        # QComboBox permettant de définir le style de tracé de courbe
        self.cbox_Cstyle = QComboBox()       
        self.cbox_Cstyle.addItem("Solid"        , Qt.SolidLine  )
        self.cbox_Cstyle.addItem("Dashed"       , Qt.DashLine      )
        self.cbox_Cstyle.addItem("Dotted"       , Qt.DotLine       )
        self.cbox_Cstyle.addItem("DashDotted"   , Qt.DashDotLine   )
        self.cbox_Cstyle.addItem("DashDotDotted", Qt.DashDotDotLine)

        self.sbox_Cwidth = QSpinBox()   
        
        self.label_Ccolor  = QLabel("Color")
        self.label_Ccolor.setAutoFillBackground(True)        
        
        # Bouton permettant de choisir la couleur de la courbe
        self.button_Ccolor = QPushButton('Color')   
        self.connect(self.button_Ccolor, SIGNAL("clicked()"),
                     self.__getColor)     
       
        # "callback" fait référence à la fonction update()
        # qui met à jour le plotter
        self.callback = callback
        
        # Propriétés des marker
        # ----------------------        
        self.markLab       = QLabel('Marker')
        self.cbox_MarkType = QComboBox()
        
        self.cbox_MarkType.addItem("None"            , 1 )
        self.cbox_MarkType.addItem("square"          , 2 )
        self.cbox_MarkType.addItem("diamond"         , 3 )
        self.cbox_MarkType.addItem("triangle right >", 4 )
        self.cbox_MarkType.addItem("triangle left <" , 5 )
        self.cbox_MarkType.addItem("triangle up ^"   , 6 )
        self.cbox_MarkType.addItem("triangle down v" , 7 )
        
        
        self.cbox_MarkSize = QSpinBox() # Taille des marker
        self.checkBox_MarkFill = QCheckBox("Fill")
        
        # Modification du nom des courbes
        labNameEdit    = QLabel('Name')
        self.cNameEdit = QLineEdit()
        
        # Mise à l'échelle des courbes (si nécessaire)
        labScalingEdit    = QLabel('Scale')
        self.cScalingEdit = QLineEdit()
        self.cScalingEdit.setValidator(QDoubleValidator())
        self.cScalingEdit.setAlignment(Qt.AlignLeft)
        self.cScalingEdit.setFixedWidth(80)
        
        # Layout des différents widgets
        
        # GroupBox des courbes
        # ---------------------
        self.gbCurve        = QGroupBox("Curves")
        self.layout_gbCurve = QVBoxLayout()       

        grid = QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(self.lineLab      , 0, 0) # ligne 0
        grid.addWidget(self.cbox_Cstyle  , 0, 1)
        grid.addWidget(self.sbox_Cwidth  , 0, 2)
        grid.addWidget(self.label_Ccolor , 0, 3)
        grid.addWidget(self.button_Ccolor, 0, 4)
        
        grid.addWidget(self.markLab      , 1, 0) # ligne 1
        grid.addWidget(self.cbox_MarkType, 1, 1)
        grid.addWidget(self.cbox_MarkSize, 1, 2)
        grid.addWidget(self.checkBox_MarkFill, 1, 3)
               
        
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.addWidget(labNameEdit    )
        layout.addWidget(self.cNameEdit )
        layout.addWidget(labScalingEdit    )
        layout.addWidget(self.cScalingEdit )
        grid.addLayout(layout,2,0,2,5)
        
        self.layout_gbCurve.addItem(grid)
        self.gbCurve.setLayout(self.layout_gbCurve)

        
        # GroupBox des axes
        # ------------------   
        xlabel = QLabel("X Label")
        self.xLedit = QLineEdit()
                
        xlimLabel1     = QLabel("X Limits")
        self.xMinLedit = QLineEdit()
        self.xMinLedit.setValidator(QDoubleValidator())
        self.xMinLedit.setAlignment(Qt.AlignLeft)
        self.xMinLedit.setFixedWidth(80)
        xlimLabel2     = QLabel("to")
        self.xMaxLedit = QLineEdit()
        self.xMaxLedit.setValidator(QDoubleValidator())
        self.xMaxLedit.setFixedWidth(80)
        self.xAdjustButton = QPushButton('Adjust')
        
        layoutXLim = QHBoxLayout()
        layoutXLim.setSpacing(15)
        layoutXLim.addWidget(xlimLabel1    )
        layoutXLim.addWidget(self.xMinLedit ) 
        layoutXLim.addWidget(xlimLabel2    )
        layoutXLim.addWidget(self.xMaxLedit ) 
        layoutXLim.addWidget(self.xAdjustButton)
      
        ylabel = QLabel("Y Label")
        self.yLedit = QLineEdit()

        ylimLabel1     = QLabel("Y Limits")
        self.yMinLedit = QLineEdit()
        self.yMinLedit.setValidator(QDoubleValidator())
        self.yMinLedit.setFixedWidth(80)
        ylimLabel2     = QLabel("to")
        self.yMaxLedit = QLineEdit()
        self.yMaxLedit.setValidator(QDoubleValidator())
        self.yMaxLedit.setFixedWidth(80)
        self.yAdjustButton = QPushButton('Adjust')
        
        layoutYLim = QHBoxLayout()
        layoutYLim.setSpacing(15)
        layoutYLim.addWidget(ylimLabel1    )
        layoutYLim.addWidget(self.yMinLedit ) 
        layoutYLim.addWidget(ylimLabel2    )
        layoutYLim.addWidget(self.yMaxLedit ) 
        layoutYLim.addWidget(self.yAdjustButton)        
        
        fontLabel = QLabel("Font Size")
        self.fontSpinBox = QSpinBox()

        # Layout de la partie Axes
        #--------------------------
        self.gbAxes = QGroupBox("Axes")
        grid = QGridLayout()
        grid.addWidget(xlabel     ,0,0)
        grid.addWidget(self.xLedit,0,1)

        grid.addLayout(layoutXLim,1,0,1,2)  
        
        grid.addWidget(ylabel     ,2,0)
        grid.addWidget(self.yLedit,2,1)
        
        grid.addLayout(layoutYLim,3,0,1,2)  
        
        grid.addWidget(fontLabel       ,4,0)
        grid.addWidget(self.fontSpinBox,4,1)
        
        self.gbAxes.setLayout(grid)
        
        # GroupBox de la légende
        # ------------------------     
        legendLab        = QLabel('Show')
        self.legendShow  = QCheckBox()
        
        self.nw_legendCb = QCheckBox()
        self.nc_legendCb = QCheckBox()
        self.ne_legendCb = QCheckBox()

        self.cw_legendCb = QCheckBox()
        self.ce_legendCb = QCheckBox()
        
        self.sw_legendCb = QCheckBox()
        self.sc_legendCb = QCheckBox()
        self.se_legendCb = QCheckBox()
        
        # On rend les boutons de position de la légende exclusifs
        exclCB = QButtonGroup(self)
        exclCB.addButton(self.nw_legendCb)
        exclCB.addButton(self.nc_legendCb)
        exclCB.addButton(self.ne_legendCb)
        
        exclCB.addButton(self.cw_legendCb)
        exclCB.addButton(self.ce_legendCb)
        
        exclCB.addButton(self.sw_legendCb)
        exclCB.addButton(self.sc_legendCb)
        exclCB.addButton(self.se_legendCb)
        # ------
        
        self.gbLegend = QGroupBox("Legend")
        grid = QGridLayout()
        grid.addWidget(legendLab      ,0,0)
        grid.addWidget(self.legendShow,0,1)

        grid.addWidget(QLabel('North-West')  ,1,0)
        grid.addWidget(self.nw_legendCb      ,1,1)
        grid.addWidget(QLabel('North-Center'),1,2)
        grid.addWidget(self.nc_legendCb      ,1,3)
        grid.addWidget(QLabel('North-East')  ,1,4)
        grid.addWidget(self.ne_legendCb      ,1,5)   
        
        grid.addWidget(QLabel('Center-West')  ,2,0)
        grid.addWidget(self.cw_legendCb       ,2,1)
        grid.addWidget(QLabel('Center-East')  ,2,4)
        grid.addWidget(self.ce_legendCb       ,2,5)   
        
        grid.addWidget(QLabel('South-West')  ,3,0)
        grid.addWidget(self.sw_legendCb      ,3,1)
        grid.addWidget(QLabel('South-Center'),3,2)
        grid.addWidget(self.sc_legendCb      ,3,3)
        grid.addWidget(QLabel('South-East')  ,3,4)
        grid.addWidget(self.se_legendCb      ,3,5)           
        self.gbLegend.setLayout(grid)
        

        # Layout global
        # --------------
        self.layoutGlobal = QVBoxLayout()
        self.layoutGlobal.addWidget(self.gbCurve)
        self.layoutGlobal.addWidget(self.gbAxes)
        self.layoutGlobal.addWidget(self.gbLegend)
        
        self.setLayout(self.layoutGlobal)
  
        # Signaux associés aux courbes    
        self.connect(self.cbox_Cstyle, SIGNAL("currentIndexChanged(int)"), self.__updLineStyle)
        self.connect(self.sbox_Cwidth, SIGNAL("valueChanged(int)")       , self.__updWidth)
        
        # Signaux associés aux Marker
        self.connect(self.cbox_MarkType, SIGNAL("currentIndexChanged(int)"), self.__updMarkType)
        self.connect(self.cbox_MarkSize, SIGNAL("valueChanged(int)")       , self.__updMarkerSize)
        self.connect(self.checkBox_MarkFill, SIGNAL("stateChanged(int)"), self.__updMarkerFill)
        
        # Signal Edit du nom des courbes
        self.connect(self.cNameEdit, SIGNAL("editingFinished()"), self.__emitEditingFinishedSignal)
        
        # Signal Edit du facteur d'échelle
        self.connect(self.cScalingEdit, SIGNAL("editingFinished()"), self.__updScaling)
        #self.connect(self.cScalingEdit, SIGNAL("editingFinished()"), self.__emitEditingFinishedSignal)
        
        # Signal Edit du nom des axes
        self.connect(self.xLedit, SIGNAL("editingFinished()"), self.__upd_AxesName)
        self.connect(self.yLedit, SIGNAL("editingFinished()"), self.__upd_AxesName)
        
        self.connect(self.fontSpinBox, SIGNAL("valueChanged(int)")       , self.__updFontSize)
        
        # Signal Edit des valeurs min. et max. des axes
        self.connect(self.xMinLedit, SIGNAL("editingFinished()"), self.__upd_AxesLimits)
        self.connect(self.xMaxLedit, SIGNAL("editingFinished()"), self.__upd_AxesLimits)
        self.connect(self.xAdjustButton, SIGNAL("clicked()")    , self.__autoAdjustX)
        

        self.connect(self.yMinLedit, SIGNAL("editingFinished()"), self.__upd_AxesLimits)
        self.connect(self.yMaxLedit, SIGNAL("editingFinished()"), self.__upd_AxesLimits)
        self.connect(self.yAdjustButton, SIGNAL("clicked()")    , self.__autoAdjustY)        
        
        # Signaux liés à la légende
        self.connect(self.legendShow, SIGNAL("stateChanged(int)"), self.__updLegend)
        
        self.connect(self.nw_legendCb, SIGNAL("stateChanged(int)"), self.__updLegend)
        self.connect(self.nc_legendCb, SIGNAL("stateChanged(int)"), self.__updLegend)
        self.connect(self.ne_legendCb, SIGNAL("stateChanged(int)"), self.__updLegend)
        self.connect(self.cw_legendCb, SIGNAL("stateChanged(int)"), self.__updLegend)
        self.connect(self.ce_legendCb, SIGNAL("stateChanged(int)"), self.__updLegend)
        self.connect(self.sw_legendCb, SIGNAL("stateChanged(int)"), self.__updLegend)
        self.connect(self.sc_legendCb, SIGNAL("stateChanged(int)"), self.__updLegend)
        self.connect(self.se_legendCb, SIGNAL("stateChanged(int)"), self.__updLegend)
        
        self.setWindowTitle("Set Curves Properties (Modeless)")
        
        # Rempli le contenu des différents widgets en fonction 
        # propriétés de la courbe sélectionné
        self.refresh()
        
    def editItem(self,item):
        self.__currentItem  = item
        #self.__currentCurve = None
        if isinstance(item,treeModule.QTreeWidgetItemSup):
            self.__currentCurve = None
            self.refresh()
        elif isinstance(item,treeModule.QTreeWidgetItemCurve): 
            self.__currentCurve = item.getCurve()
            self.refresh()
        elif isinstance(item,treeModule.QTreeWidgetItem): 
            self.__currentCurve = None
            self.refresh()
            
            

    def setPlotSettings(self,plotSettings):
        self.__plotSettings = plotSettings

    
    def refresh(self):
        listToDeactivate = [self.label_Ccolor,self.sbox_Cwidth, \
                            self.cbox_MarkSize,self.cbox_Cstyle, \
                            self.cbox_MarkType,self.checkBox_MarkFill, \
                            self.button_Ccolor,self.label_Ccolor]        
        if self.__currentCurve == None:
            palette = self.label_Ccolor.palette()
            palette.setColor(self.label_Ccolor.backgroundRole(),Qt.gray )
            palette.setColor(self.label_Ccolor.foregroundRole(),Qt.gray ) 
            self.label_Ccolor.setPalette(palette)          
            for wid in listToDeactivate:
                wid.setEnabled(False)
                
            if isinstance(self.__currentItem,treeModule.QTreeWidgetItemSup):
                col=0
                self.cNameEdit.setEnabled(True)
                self.cNameEdit.setText(self.__currentItem.text(col))
            else:
                self.cNameEdit.setText('')
                self.cNameEdit.setEnabled(False)
                
            if isinstance(self.__currentItem,treeModule.QTreeWidgetItemSup):
                col=0
                self.cScalingEdit.setEnabled(True)
                self.cScalingEdit.setText(self.__currentItem.text(col))
            else:
                self.cScalingEdit.setText('')
                self.cScalingEdit.setEnabled(False)
                
        if self.__currentCurve != None:
            for wid in listToDeactivate:
                wid.setEnabled(True)
            
            self.cNameEdit.setEnabled(True)
            self.cScalingEdit.setEnabled(True)            
            # Mise à jour du contenu des widget
            # Epaisseur du trait
            self.sbox_Cwidth.setValue(self.__currentCurve.getLineW())    
            # Couleur de la courbe
            palette = self.label_Ccolor.palette()
            
            palette.setColor(self.label_Ccolor.backgroundRole(), self.__currentCurve.getColor() ) #Qt.yellow
            palette.setColor(self.label_Ccolor.foregroundRole(), self.__currentCurve.getColor() )
            self.label_Ccolor.setPalette(palette)    
            
            # Style de la courbe
            t1 = self.cbox_Cstyle.findData(self.__currentCurve.getLineS())
            self.cbox_Cstyle.setCurrentIndex(t1)

            # Type de marker
            self.cbox_MarkType.setCurrentIndex(self.__currentCurve.getMarker().type)
            # Taille du marker
            self.cbox_MarkSize.setValue(self.__currentCurve.getMarker().size)  
            # Fill du marker
            self.checkBox_MarkFill.setChecked(self.__currentCurve.getMarker().fill)
            
            self.cNameEdit.setText(self.__currentCurve.getName())
            
            self.cScalingEdit.setText(str(float(self.__currentCurve.getScaling())))

        
        # Nom des axes dans les label
        self.xLedit.setText(self.plotter2D.getXlabel())
        self.yLedit.setText(self.plotter2D.getYlabel())
        
        # Limite des axes :
        self.xMinLedit.setText(str(self.__plotSettings.getXmin()))
        self.xMaxLedit.setText(str(self.__plotSettings.getXmax()))
        
        self.yMinLedit.setText(str(self.__plotSettings.getYmin()))
        self.yMaxLedit.setText(str(self.__plotSettings.getYmax()))
        
        # Légende
        self.legendShow.setChecked(self.plotter2D.getLegend().getDisplay())
                
        t1 = self.plotter2D.getLegend().getPostion()
        if t1 == self.plotter2D.getLegend().NorthWest:
            self.nw_legendCb.setChecked(True)
        elif t1 == self.plotter2D.getLegend().NorthCenter:
            self.nc_legendCb.setChecked(True)
        elif t1 == self.plotter2D.getLegend().NorthEast:
            self.ne_legendCb.setChecked(True)
        elif t1 == self.plotter2D.getLegend().CenterWest:
            self.cw_legendCb.setChecked(True)
        elif t1 == self.plotter2D.getLegend().CenterEast:
            self.ce_legendCb.setChecked(True)
        elif t1 == self.plotter2D.getLegend().SouthWest:
            self.sw_legendCb.setChecked(True)
        elif t1 == self.plotter2D.getLegend().SouthCenter:
            self.sc_legendCb.setChecked(True)
        elif t1 == self.plotter2D.getLegend().SouthEast:
            self.se_legendCb.setChecked(True)
        
        
        self.fontSpinBox.setValue(self.plotter2D.getFontSize())
        
    def __updScaling(self):
        self.__currentCurve.scaling(float(self.cScalingEdit.text()))
        
    def __updLineStyle(self):
        t1 =  self.cbox_Cstyle.itemData(self.cbox_Cstyle.currentIndex())
        self.__currentCurve.setLineS(t1.toInt()[0]) # on récupère l'enum dans le QVariant renvoyé par ItemData
        self.callback()
        
    def __updWidth(self):
        self.__currentCurve.setLineW(self.sbox_Cwidth.value())
        self.callback()
        
    def __getColor(self):   
        color = QColorDialog.getColor(Qt.black, self)
        if color.isValid():
            self.__setColor(color)

    def __setColor(self,color):    
        self.__currentCurve.setColor(color)
        palette = self.label_Ccolor.palette()
        palette.setColor(self.label_Ccolor.backgroundRole(), self.__currentCurve.getColor() ) #Qt.yellow
        palette.setColor(self.label_Ccolor.foregroundRole(), self.__currentCurve.getColor() )
        self.label_Ccolor.setPalette(palette)   
        self.callback()   

    def __updMarkType(self):
        self.__currentCurve.getMarker().type = self.cbox_MarkType.currentIndex()
        self.callback()    

    def __updMarkerSize(self):  
        self.__currentCurve.getMarker().size = self.cbox_MarkSize.value()
        self.callback()   
        
    def __updMarkerFill(self):
        self.__currentCurve.getMarker().fill = self.checkBox_MarkFill.isChecked()      
        self.callback()   
        
    def __emitEditingFinishedSignal(self):
        self.emit(SIGNAL("updateTextInTree"), str(self.cNameEdit.text()))
        
    
    def __upd_AxesName(self):
        self.plotter2D.setXlabel(self.xLedit.text())
        self.plotter2D.setYlabel(self.yLedit.text())
        self.callback()  

    def __updFontSize(self):
        self.plotter2D.setFontSize(self.fontSpinBox.value())
        self.callback()  
        
        
    def __upd_AxesLimits(self):   
        self.__plotSettings.setXmin(float(self.xMinLedit.text()))
        self.__plotSettings.setXmax(float(self.xMaxLedit.text()))

        self.__plotSettings.setYmin(float(self.yMinLedit.text()))
        self.__plotSettings.setYmax(float(self.yMaxLedit.text()))        
        
        self.callback() 
    
    def __autoAdjustX(self): 
        vecXmin = []
        vecXmax = []   
        for c in self.__curveList:
            if c.getVisibility(): # uniquement si la courbe est affichée
                vecXmin.append(c.getXmin())
                vecXmax.append(c.getXmax())
        if len(vecXmin) == 0: # si la liste est vide -> pas d'ajustement car pas de courbe
            return                
        xMin = min(vecXmin)
        xMax = max(vecXmax) 
        dX = max(vecXmax) - min(vecXmin) 
        s = 0.02
        self.__plotSettings.setXmin(xMin-s*dX)
        self.__plotSettings.setXmax(xMax+s*dX)
        self.refresh()
        self.callback()        

        
    def __autoAdjustY(self):         
        vecYmin = []
        vecYmax = [] 
        for c in self.__curveList:
            if c.getVisibility(): # uniquement si la courbe est affichée       
                vecYmin.append(c.getYmin())
                vecYmax.append(c.getYmax())   
        if len(vecYmin) == 0: # si la liste est vide -> pas d'ajustement car pas de courbe
            return
        yMin = min(vecYmin)
        yMax = max(vecYmax) 
        dY = max(vecYmax) - min(vecYmin) 
        s = 0.02      
        self.__plotSettings.setYmin(yMin-s*dY)
        self.__plotSettings.setYmax(yMax+s*dY)
        self.refresh()
        self.callback()                
        
    def __updLegend(self):
        disp = self.legendShow.isChecked()         
        
        legend = self.plotter2D.getLegend()
        legend.setDisplay(disp)
        
        if self.nw_legendCb.isChecked():
            legend.setPostion(legend.NorthWest)
        elif self.nc_legendCb.isChecked():
            legend.setPostion(legend.NorthCenter)
        elif self.ne_legendCb.isChecked():
            legend.setPostion(legend.NorthEast)
        elif self.cw_legendCb.isChecked():
            legend.setPostion(legend.CenterWest)
        elif self.ce_legendCb.isChecked():
            legend.setPostion(legend.CenterEast)
        elif self.sw_legendCb.isChecked():
            legend.setPostion(legend.SouthWest)
        elif self.sc_legendCb.isChecked():
            legend.setPostion(legend.SouthCenter)
        elif self.se_legendCb.isChecked():
            legend.setPostion(legend.SouthEast)
        
        
        self.callback()   