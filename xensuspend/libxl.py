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

from ctypes import cdll, c_int, c_void_p, byref, POINTER, c_uint
from ctypes.util import find_library

libxenlight = cdll.LoadLibrary(find_library("xenlight"))
libxentoollog = cdll.LoadLibrary(find_library("xentoollog"))
libc = cdll.LoadLibrary(find_library("c"))

stderr = c_void_p.in_dll(libc, "stderr")

# xentoollog levels
XTL_PROGRESS = 4

libxentoollog.xtl_createlogger_stdiostream.argtypes = [c_void_p, c_int, c_uint]
libxentoollog.xtl_createlogger_stdiostream.restype = c_void_p
libxentoollog.xtl_logger_destroy.argtypes = [c_void_p]
libxentoollog.xtl_logger_destroy.restype = None

libxenlight.libxl_ctx_alloc.argtypes = [POINTER(c_void_p), c_int, c_uint, c_void_p]
libxenlight.libxl_ctx_alloc.restype = c_int
libxenlight.libxl_ctx_free.argtypes = [c_void_p]
libxenlight.libxl_ctx_free.restype = c_int
libxenlight.libxl_domain_shutdown.argtypes = [c_void_p, c_int, c_void_p]
libxenlight.libxl_domain_shutdown.restype = c_int
libxenlight.libxl_domain_suspend_only.argtypes = [c_void_p, c_int, c_void_p]
libxenlight.libxl_domain_suspend_only.restype = c_int
libxenlight.libxl_domain_resume.argtypes = [c_void_p, c_int, c_int, c_void_p]
libxenlight.libxl_domain_resume.restype = c_int

class libxl(object):
    def __enter__(self):
        self.ctx = c_void_p()
        self.logger = libxentoollog.xtl_createlogger_stdiostream(stderr, XTL_PROGRESS, 0)
        if not self.logger:
            raise Exception("Failed to create xentoollog logger")
        ret = libxenlight.libxl_ctx_alloc(byref(self.ctx), 0, 0, self.logger)
        if ret != 0:
            libxentoollog.xtl_logger_destroy(self.logger)
            self.logger = None
            raise Exception("Failed to create libxl ctx: {}".format(ret))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "logger") and self.logger:
            libxentoollog.xtl_logger_destroy(self.logger)
            self.logger = None
        libxenlight.libxl_ctx_free(self.ctx)

        return False

    def shutdown(self, domid):
        return libxenlight.libxl_domain_shutdown(self.ctx, domid, None)

    def suspend_trigger(self, domid):
        return libxenlight.libxl_domain_suspend_only(self.ctx, domid, None)

    def suspend_wakeup(self, domid):
        return libxenlight.libxl_domain_resume(self.ctx, domid, 1, None)
