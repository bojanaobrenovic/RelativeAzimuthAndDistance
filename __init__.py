# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DirekcioniUgao
                                 A QGIS plugin
 Racunanje direkcionog ugla i dužine
                             -------------------
        begin                : 2018-05-25
        copyright            : (C) 2018 by Bojana Obrenović
        email                : bojana.n.obrenovic@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DirekcioniUgao class from file DirekcioniUgao.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .direkcioni_ugao import DirekcioniUgao
    return DirekcioniUgao(iface)
