#!/bin/sh
# .+
# .context    : Binary Timed Signal Processing Library
# .title      : website publish script
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	9-Dec-2013
# .copyright  :	(c) 2013 Fabrizio Pollastri
# .license    : GNU General Public License (see below)
#
# .note
# needs addition of "<username> ALL=NOPASSWD:/usr/bin/rsync" at
# the end of /etc/sudoers on server machine.
#
# .usage
# CMD: ./website_publish.sh
#
# This file is part of "Bitis, Binary Timed Signal Processing Library".
#
# Bitis is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Bitis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.
#
# .-

SOURCE="./doc/_build/html/"
DESTINATION="fabrizio@serzot.inrim.it:/var/www/bitis"
SWITCHES="-avuxzO"

# required argument test
if [ ! -d "$SOURCE" ]; then
    echo ERROR: missing source: exiting
    exit 1
fi

# do rsync command
rsync $SWITCHES -e "ssh -p4522" --rsync-path="sudo rsync" \
  --delete --force $SOURCE $DESTINATION

#### end
