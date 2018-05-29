# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DirekcioniUgao
                                 A QGIS plugin
 Racunanje direkcionog ugla i dužine
                              -------------------
        begin                : 2018-05-25
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Bojana Obrenović
        email                : bojana.n.obrenovic@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import csv
from PyQt4 import uic
from PyQt4.QtCore import*
from PyQt4.QtGui import*
from qgis.core import*
from qgis.gui import *
import math
from pyproj import Proj, transform
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from direkcioni_ugao_dialog import DirekcioniUgaoDialog
import os.path


class DirekcioniUgao:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DirekcioniUgao_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Relative Azimuth and Distance')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'RelativeAzimuthAndDistance')
        self.toolbar.setObjectName(u'RelativeAzimuthAndDistance')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DirekcioniUgao', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        # Create the dialog (after translation) and keep reference
        self.dlg = DirekcioniUgaoDialog()

        # Connecting SIGNAL/SLOTS for the Output button
        self.dlg.calculateButton.clicked.connect(self.fillTextEdit)
        self.dlg.clearButton.clicked.connect(self.clearTextEdit)
        self.dlg.clearButton.clicked.connect(self.cx1)
        self.dlg.clearButton.clicked.connect(self.cx2)
        self.dlg.clearButton.clicked.connect(self.cy1)
        self.dlg.clearButton.clicked.connect(self.cy2)
        self.dlg.pushButton.clicked.connect(self.t1)
        self.dlg.pushButton_2.clicked.connect(self.csv)
        self.dlg.pushButton_1.clicked.connect(self.koor)
        self.dlg.button_box.clicked.connect(self.kraj)

        self.dlg.x1Edit.setInputMask("#000000.00000")
        self.dlg.y1Edit.setInputMask("#000000.00000")
        self.dlg.x2Edit.setInputMask("#000000.00000")
        self.dlg.y2Edit.setInputMask("#000000.00000")

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/DirekcioniUgao/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Relative azimuth and distance'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Relative Azimuth and Distance'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def koor(self):
        currentLayer = self.iface.mapCanvas().currentLayer()
        if currentLayer:
            selectedFeatures = len(currentLayer.selectedFeatures())
            if selectedFeatures == 2:
                selectedFeature1 = currentLayer.selectedFeatures()[0]
                x1=selectedFeature1.geometry().asPoint().x()
                y1 = selectedFeature1.geometry().asPoint().y()
                selectedFeature2 = currentLayer.selectedFeatures()[1]
                x2=selectedFeature2.geometry().asPoint().x()
                y2 = selectedFeature2.geometry().asPoint().y()
                if self.dlg.comboBox.currentText() == 'Gaus-Kriger, EPSG:31277':
                    inProj = Proj(init='epsg:4326')
                    outProj = Proj(init='epsg:31277')
                    y11, x11 = transform(inProj, outProj, x1, y1)
                    y22, x22 = transform(inProj, outProj, x2, y2)
                    self.dlg.x2Edit.setText(str(x22))
                    self.dlg.y2Edit.setText(str(y22))
                    self.dlg.y1Edit.setText(str(y11))
                    self.dlg.x1Edit.setText(str(x11))
                elif self.dlg.comboBox.currentText() == 'UTM, EPSG:25834':
                    inProj = Proj(init='epsg:4326')
                    outProj = Proj(init='epsg:25834')
                    y11, x11 = transform(inProj, outProj, x1, y1)
                    y22, x22 = transform(inProj, outProj, x2, y2)
                    self.dlg.x2Edit.setText(str(x22))
                    self.dlg.y2Edit.setText(str(y22))
                    self.dlg.y1Edit.setText(str(y11))
                    self.dlg.x1Edit.setText(str(x11))
                elif self.dlg.comboBox.currentText() == 'Projection':
                    QMessageBox.warning(self.iface.mainWindow(), self.tr("Warning!"),
                                        self.tr("Choose a projection!"))
            else:
                QMessageBox.warning(self.iface.mainWindow(), self.tr("Warning!"),self.tr("You did not select TWO points. First select T1 then T2!"))
        else:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Warning!"),self.tr("Select TWO points - first T1 then T2!"))

    def izracunajDirekcioni(self):
        """Racuna direkcioni ugao
        """
        x1 = float(self.dlg.x1Edit.text())
        y1 = float(self.dlg.y1Edit.text())
        x2 = float(self.dlg.x2Edit.text())
        y2 = float(self.dlg.y2Edit.text())
        dx = x2 - x1
        dy = y2 - y1

        if (dx == 0 and dy > 0):
            pi = math.pi
            ugao1 = pi / 2
            ugao = ugao1 * 57.2957795130823
            return ugao
        elif (dx == 0 and dy < 0):
            pi = math.pi
            ug = 3 * pi / 2
            ugao = ug * 57.2957795130823
            return ugao
        elif (dy == 0 and dx < 0):
            pi = math.pi
            ugao = pi * 57.2957795130823
            return ugao
        elif (dy == 0 and dx > 0):
            pi = math.pi
            ugao = 2 * pi * 57.2957795130823
            return ugao
        elif (dx > 0 and dy > 0):
            ugao = (math.atan(dy / dx) * 57.2957795130823)
            return ugao
        elif (dy > 0 and dx < 0):
            u1 = abs(dx / dy)
            ugao = ((math.atan(u1)) + math.pi / 2) * 57.2957795130823
            return ugao
        elif (dy < 0 and dx < 0):
            u1 = abs(dy / dx)
            ugao = ((math.atan(u1)) + math.pi) * 57.2957795130823
            return ugao
        elif (dy < 0 and dx > 0):
            u1 = abs(dx / dy)
            pi = math.pi
            pii = 3 * pi / 2
            ugao = ((math.atan(u1)) + pii) * 57.2957795130823
            return ugao
        elif (dx == 0 and dy == 0):
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Warning!"),
                                self.tr("You have entered the coordinates of the same point twice!"))

    def izracunajrastojanje(self):
        """Racuna rastojanje iymedju dve tacke
        """
        x1 = float(self.dlg.x1Edit.text())
        y1 = float(self.dlg.y1Edit.text())
        x2 = float(self.dlg.x2Edit.text())
        y2 = float(self.dlg.y2Edit.text())
        dx = x2 - x1
        dy = y2 - y1
        r = math.sqrt((dx ** 2 + dy ** 2))
        rr = str(round(r, 4)).encode("utf-8")
        return rr

    def fillTextEdit(self):
        x1 = float(self.dlg.x1Edit.text())
        y1 = float(self.dlg.y1Edit.text())
        x2 = float(self.dlg.x2Edit.text())
        y2 = float(self.dlg.y2Edit.text())

        uga = self.izracunajDirekcioni()
        duz = self.izracunajrastojanje()
        uga2 = self.dd2dms(uga)
        rad = uga / 57.2957795130823

        self.dlg.textEdit.append("X1 = " + str(x1) + "\n")
        self.dlg.textEdit.append("Y1 = " + str(y1) + "\n")
        self.dlg.textEdit.append("X2 = " + str(x2) + "\n")
        self.dlg.textEdit.append("Y2 = " + str(y2) + "\n")
        self.dlg.textEdit.append("V1-2 = " + str(uga2) + "\n")
        self.dlg.textEdit.append("V1-2: " + str(uga) + u'°' "\n")
        self.dlg.textEdit.append("V1-2: " + str(rad) + " rad" + "\n")
        self.dlg.textEdit.append("Distance: " + str(duz) + " m" + "\n")

    def clearTextEdit(self):
        self.dlg.textEdit.clear()

    def cx1(self):
        self.dlg.x1Edit.clear()

    def cx2(self):
        self.dlg.x2Edit.clear()

    def cy1(self):
        self.dlg.y1Edit.clear()

    def cy2(self):
        self.dlg.y2Edit.clear()

    def dd2dms(self, dd):
        st = int(dd)
        minm = (dd - st) * 60
        min = int(minm)
        sek = ((minm - min) * 60)
        sekk = round(sek, 2)

        return (str(st) + chr(176) + " " +str(min) + " ' " + str(sekk) + " ''")

    def t1(self):
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ", "", '*.txt')
        self.dlg.lineEdit_5.setText(filename)
        output_file = open(filename, 'w')
        tt = self.dlg.textEdit
        ttt = (tt.toPlainText()).encode('utf-8')
        output_file.write(ttt)
        output_file.close()

    def csv(self):
        x1 = float(self.dlg.x1Edit.text())
        y1 = float(self.dlg.y1Edit.text())
        x2 = float(self.dlg.x2Edit.text())
        y2 = float(self.dlg.y2Edit.text())

        uga = self.izracunajDirekcioni()
        duz = self.izracunajrastojanje()
        uga2 = self.dd2dms(uga)
        rad = uga / 57.2957795130823

        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ", "", '*.csv')
        self.dlg.lineEdit_6.setText(filename)
        p2 = open(filename, 'w')
        fieldnames = ['Point', 'X', 'Y', 'V1-2['+chr(176)+']', 'V1-2 [rad]', 'Distance [m]']
        writer = csv.DictWriter(p2, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'Point': '1', 'X': x1, 'Y': y1, 'V1-2['+chr(176)+']': uga, 'V1-2 [rad]': rad, 'Distance [m]': duz})
        writer.writerow({'Point': '2', 'X': x2, 'Y': y2, 'V1-2['+chr(176)+']': uga, 'V1-2 [rad]': rad, 'Distance [m]': duz})

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def kraj(self):
        self.dlg.close()