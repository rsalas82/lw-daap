#!/bin/sh
# This file is part of Lifewatch DAAP.
# Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
#
# Lifewatch DAAP is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Lifewatch DAAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.

USER=jupyter

JUP_INSTALLER=`mktemp`
cat > $JUP_INSTALLER << EOF
#!/bin/sh

unset XDG_RUNTIME_DIR
unset XDG_SESSION_ID

. .venv/bin/activate

CONFIG_FILE=\`jupyter --config-dir\`/jupyter_notebook_config.py

ID=\$(curl http://169.254.169.254/openstack/latest/meta_data.json | \
     python2 -c "import json; import sys; print json.load(sys.stdin)['uuid']")
echo "c.NotebookApp.base_url = '/\$ID'" >> \$CONFIG_FILE

{% if app_env == 'jupyter-r' %}
export R_LIBS_USER=~/.R
Rscript -e "IRkernel::installspec()"
{% endif %}

jupyter notebook --no-browser --ip=0.0.0.0 &
EOF

chmod 755 $JUP_INSTALLER

su - $USER -c $JUP_INSTALLER
