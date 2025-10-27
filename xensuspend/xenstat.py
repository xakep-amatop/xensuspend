# Copyright (C) 2019, 2025 EPAM Systems
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from ctypes import cdll, c_char_p, c_void_p, c_int
from ctypes.util import find_library

xenstatlib = cdll.LoadLibrary(find_library("xenstat"))
xenstatlib.xenstat_domain_name.restype = c_char_p
xenstatlib.xenstat_domain_name.argtypes = [c_void_p]
xenstatlib.xenstat_init.restype = c_void_p
xenstatlib.xenstat_get_node.argtypes = [c_void_p, c_int]
xenstatlib.xenstat_get_node.restype = c_void_p
xenstatlib.xenstat_free_node.argtypes = [c_void_p]
xenstatlib.xenstat_uninit.argtypes = [c_void_p]
xenstatlib.xenstat_node_domain.argtypes = [c_void_p, c_int]
xenstatlib.xenstat_node_domain.restype = c_void_p
xenstatlib.xenstat_domain_shutdown.argtypes = [c_void_p]
xenstatlib.xenstat_domain_shutdown.restype = c_int

class xenstat(object):
    def __enter__(self):
        self.handle = xenstatlib.xenstat_init()
        if self.handle == 0:
            raise Exception("Failed to initialize xenstat library")

        self.node = xenstatlib.xenstat_get_node(self.handle, 1)
        if self.node == 0:
            xenstatlib.xenstat_uninit(self.handle)
            raise Exception("Failed to get xenstat node")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        xenstatlib.xenstat_free_node(self.node)
        xenstatlib.xenstat_uninit(self.handle)

        return False


    class xenstat_domain(object):
        def __init__(self, domain_ptr, domid):
            if not domain_ptr:
                raise ValueError("xenstat returned NULL domain pointer for {}".format(domid))
            self.domain = domain_ptr
            self.domid = domid

        def name(self):
            name = xenstatlib.xenstat_domain_name(self.domain)
            if not name:
                return "<unknown:{}>".format(self.domid)
            return name.decode()

        def shutdown(self):
            return bool(xenstatlib.xenstat_domain_shutdown(self.domain))

    def domain(self, domid):
        domain_ptr = xenstatlib.xenstat_node_domain(self.node, domid)
        if not domain_ptr:
            return None
        return self.xenstat_domain(domain_ptr, domid)
