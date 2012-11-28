# Copyright 2012 John Sullivan
# Copyright 2012 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of Galah.
#
# Galah is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Galah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Galah.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

from mongoengine import *

class Invitation(Document):
    email = EmailField(required = True)
    class_ = ObjectIdField(required = True)
    expires = DateTimeField(required = True)
    accountType = StringField(required = True)
    
    meta = {
        "allow_inheritance": False
    }
    
    def __init__(self, *zargs, **zkwargs):
        Document.__init__(self, *zargs, **zkwargs)
        
        if self.expires < datetime.today():
            raise ValueError("Invitation is expired")
