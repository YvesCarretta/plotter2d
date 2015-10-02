#!/usr/bin/env python
# -*- coding: latin-1; -*- 

from PyQt4.QtCore import *
from PyQt4.QtGui  import *

import os 

from curveModule import *
from math        import *


class QTreeCurveDisplay(QWidget):

    def __init__(self, plotter2D, callback, treeCurves):
        super(QTreeCurveDisplay, self).__init__()
        # Liste des courbes -> permet d'accéder aux propriétés 
        # des courbes pour mettre à jour les widget et modifier les
        # propriétés des courbes
        self.__plotter2D = plotter2D
                
        self.callback  = callback
        self.openRep   = os.getcwd()
        
        self.treeCurves    = treeCurves 
        self.treeNameEdit  = QLineEdit()
        self.selectAll_cb  = QCheckBox('Select/Deselect all')
        
        self.applyButton = QPushButton('Apply')
        
        vboxGlobal = QVBoxLayout() # layout global
        
        treeLayout = QVBoxLayout()
        treeLayout.addWidget(self.treeCurves)
        treeLayout.addWidget(self.treeNameEdit)    

        hLayout = QHBoxLayout() # layout global  
        hLayout.addWidget(self.selectAll_cb)        
        hLayout.addItem(QSpacerItem(50,5))
        hLayout.addWidget(self.applyButton)
        
        treeLayout.addItem(hLayout)
        
        # Layout des GroupBox:
        self.txtBrowser = QTextBrowser()
        
        vboxGlobal.addItem(treeLayout)
        self.setLayout(vboxGlobal)     

        self.connect(self.applyButton,
                     SIGNAL("clicked()"), self.__apply)        

        self.setWindowTitle("Load Curves")      
        
        self.connect(self.selectAll_cb, SIGNAL("stateChanged(int)")   , self.treeCurves.selectAll)        
        self.connect(self.treeNameEdit, SIGNAL("textChanged(QString)"), self.treeCurves.editItem)


    def __apply(self):
        self.__plotter2D.updCurveList() # On met à jour la liste de courbes à tracer
        self.callback()
    
    def getTreeCurves(self):
        return self.treeCurves

    def updateText(self,text):
        col=0
        item = self.treeCurves.currentItem()
        if isinstance(item,QTreeWidgetItemSup):
            item.setText(col,text)
        elif isinstance(item,QTreeWidgetItemCurve): 
            item.setText(col,text)
            item.getCurve().setName(text)
            item.updItemCurveInfo()
      
# Pour réimplémenter des évènements comme des drags and drop        
class QTreeWidgetCurve(QTreeWidget):
    def __init__(self):
        super(QTreeWidget, self).__init__()
        
        self.setHeaderLabels(["Curve Name"])
        self.setItemsExpandable(True)        
        
        self.setSelectionMode(self.ExtendedSelection)
        self.setDragDropMode(self.InternalMove)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        
        root = self.invisibleRootItem()
        root.setFlags(root.flags() & ~Qt.ItemIsDropEnabled)        

        self.connect(self, SIGNAL("itemChanged (QTreeWidgetItem*,int)"),self.__clickCheck)   
        # This signal is emitted when the contents of the column in the specified item changes.
        self.connect(self, SIGNAL("itemSelectionChanged()"), self.__itSelectChanged)

    def addCurve(self, curve, setName='UserData'):
        oldState = self.blockSignals(True)       
        # on ajoute la courbe "curve" dans l'ensemble setName
        it = QTreeWidgetItemIterator(self)
        while it.value():
            if isinstance(it.value(), QTreeWidgetItemSup):
                if it.value().text(0) == setName:
                    it.value().addCurve(curve)
                    self.blockSignals(oldState)
                    return
            it.__iadd__(1)        
        # Si on arrive ici, c'est que le nom setName ne correspond  
        # pas au nom de l'item de haut niveau dans l'arborescence      
        item1 = QTreeWidgetItemSup(self, setName)
        item1.addCurve(curve)
        
        self.blockSignals(oldState)

    def contextMenuEvent(self, event):
        self.menu    = QMenu(self)
        removeAction = QAction('Remove', self)
        removeAction.triggered.connect(self.removeSlot)
       
        self.menu.addAction(removeAction)
        self.menu.popup(QCursor.pos())

    def removeSlot(self):
        # save the selected items
        selection = [QPersistentModelIndex(i)
                     for i in self.selectedIndexes()]
        itemSuppr = self.currentItem()                     
        parent = itemSuppr.parent()
        parent_index = self.indexFromItem(parent)
        if parent_index in selection:
            return False
        # remove the selected items
        taken = []
        for index in reversed(selection):
            item = self.itemFromIndex(QModelIndex(index))
            if item is None or item.parent() is None:
                self.takeTopLevelItem(index.row())
            elif isinstance(item,QTreeWidgetItemCurve): 
                # je ne vaux pas qu'on puisse supprimer le QTreeWidgetItem 
                # associé à chaque QTreeWidgetItemCurve lorsqu'on clique 
                # uniquement sur QTreeWidgetItem
                item.parent().removeChild(item)
      
    # Fonction à optimiser -> changer uniquement l'item sélectionné
    def __clickCheck(self, item, col):
        it = QTreeWidgetItemIterator(self)
        while it.value():
            if isinstance(it.value(), QTreeWidgetItemCurve):
                it.value().updCurveVisibility() 
            it.__iadd__(1)
        
    def selectAll(self,state):
        # je fais tout sans les signaux dans un 1er temps
        oldState = self.blockSignals(True) 
        itemD = self.currentItem()
        
        if isinstance(itemD,QTreeWidgetItemSup):        
            child_count = itemD.childCount()
            for i in range(child_count):
                itemC = itemD.child(i)     
                if isinstance(itemC, QTreeWidgetItemCurve) and state == 0 :
                    itemC.getCurve().hide() 
                    itemC.updCheckState()
                elif isinstance(itemC, QTreeWidgetItemCurve) and state == 2 :
                    itemC.getCurve().show() 
                    itemC.updCheckState()   
        
        self.blockSignals(oldState)        
               
    def __itSelectChanged(self):
        item = self.currentItem()
        col = 0 # colonne de l'item
        self.emit(SIGNAL("selectedItemToEdit"), item)        

    def editItem(self,text):
        item = self.currentItem()   
        if (isinstance(item,QTreeWidgetItemSup) or \
            isinstance(item,QTreeWidgetItemCurve)): 
            item.editText(0,text)       
        

class QTreeWidgetItemSup(QTreeWidgetItem):
    def __init__(self, QTreeWidget, name):   
        super(QTreeWidgetItemSup, self).__init__(QTreeWidget, [name])
        self.tree = QTreeWidget
        col=0
        self.setFlags(self.flags() & ~Qt.ItemIsDragEnabled)     

    def addCurve(self, curve):
        item2 = QTreeWidgetItemCurve(self,curve)
        item2.updCheckState()        
        self.tree.setCurrentItem(item2)  

    def editText(self,col,text):
        super(QTreeWidgetItemSup, self).setText(col,text)
        
                
class QTreeWidgetItemCurve(QTreeWidgetItem):
    
    def __init__(self, tree, curve):
        super(QTreeWidgetItemCurve, self).__init__(tree)
        self.__curve       = curve
        
        # super pour éviter d'aller changer le nom de la courbe
        # après avoir changé le nom de l'item (comportement qu'on aurait eu en
        # utilisant self.setText(0,self.__curve.getName())
        self.setText(0,self.__curve.getName())
                
        # empêche cet objet d'être la cible d'un drop
        self.setFlags(self.flags() & ~Qt.ItemIsDropEnabled)
        
        # Onglet contenant les infos sur la courbe: 
        self.__item3 = QTreeWidgetItem(self,[self.__curve.getInfo()])             
        self.__item3.setFlags(self.__item3.flags() & ~Qt.ItemIsDropEnabled)     
        
    def updCheckState(self):
        if self.__curve.getVisibility(): # courbe visible
            state = 2 
        else: # courbe pas visible
            state = 0 
        self.setCheckState(0, state) # le 1er argument est le numéro de la colonne
                                     # Qt.Unchecked -> the item is unchecked.
                                     # Qt.Checked   -> the item is checked.        
    def updCurveVisibility(self):
        state = self.checkState(0) # 0 car la checkbox est dans la colonne 0
        if state == 2: # courbe visible
            self.__curve.show()
        elif state == 0: # courbe pas visible
            self.__curve.hide()
            
    def editText(self,col,text):
        super(QTreeWidgetItemCurve, self).setText(col,text)
        self.__curve.setName(text)
    
    def getCurve(self): 
        return self.__curve
        
    def updItemCurveInfo(self): 
        self.__item3.setText(0, self.__curve.getInfo())          
        

    

   
        
        
         