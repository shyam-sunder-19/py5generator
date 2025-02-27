# *****************************************************************************
#
#   Part of the py5 library
#   Copyright (C) 2020-2023 Jim Schmitz
#
#   This library is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 2.1 of the License, or (at
#   your option) any later version.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
#   General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this library. If not, see <https://www.gnu.org/licenses/>.
#
# *****************************************************************************
# *** FORMAT PARAMS ***
from __future__ import annotations

import weakref

py5mouseevent_class_members_code = None  # DELETE


class Py5MouseEvent:
    """$classdoc_Py5MouseEvent
    """
    _py5_object_cache = weakref.WeakSet()

    def __new__(cls, pmouseevent):
        for o in cls._py5_object_cache:
            if pmouseevent == o._instance:
                return o
        else:
            o = object.__new__(Py5MouseEvent)
            o._instance = pmouseevent
            cls._py5_object_cache.add(o)
            return o


{py5mouseevent_class_members_code}
