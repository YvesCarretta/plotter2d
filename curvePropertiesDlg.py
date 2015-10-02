#!/usr/bin/env python
# -*- coding: latin-1; -*- 

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os

import curvePropModule as curProp
import loadTabModule   as loadModule

import treeModule

class CurvePropertiesDlg(QDialog):
    
    def __init__(self, plotter2D, callback, parent=None):
        super(CurvePropertiesDlg, self).__init__(parent)
                
        self.curPropTab = curProp.CurvePropWidget(plotter2D, callback)
        
        self.openRep = os.getcwd()
        loadTab      = loadModule.LoadFileTab(self.openRep,plotter2D)

        # Partie gauche de la boite de dialogue : 
        # Tree qui permet de visualiser le nom des courbes
        self.treeCurveDisplay = treeModule.QTreeCurveDisplay(plotter2D, callback, plotter2D.treeCurves)
        # mettre une getTreeCurves()        

        # Partie droite de la boite de dialogue :
        self.tabWidget = QTabWidget(self)
        self.tabWidget.addTab(self.curPropTab,'Curve Properties')
        self.tabWidget.addTab(loadTab   ,'Load curves')
         
        vertLayout = QVBoxLayout()
        vertLayout.addWidget(self.tabWidget)
        vertLayout.addStretch(50)
        
        # Layout de la boite de dialogue
        layout = QHBoxLayout()
        layout.addWidget(self.treeCurveDisplay,10)
        layout.addLayout(vertLayout,1)
        
        self.setLayout(layout)

        self.treeCurves = self.treeCurveDisplay.getTreeCurves()
        self.connect(self.treeCurves, SIGNAL("selectedItemToEdit"), self.curPropTab.editItem)
        
        
        self.connect(self.curPropTab, SIGNAL("updateTextInTree"), self.treeCurveDisplay.updateText)        
        
    def getCurvePropWidget(self):
        return self.curPropTab
        

        
        

        
             