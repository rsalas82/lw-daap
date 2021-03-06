# -*- coding: utf-8 -*-
#
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

# This file is part of Zenodo.
# Copyright (C) 2012, 2013 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""License field."""

import json
from operator import itemgetter

from wtforms import SelectField

from lw_daap.modules.invenio_deposit.field_base import WebDepositField
from lw_daap.modules.invenio_deposit.processor_utils import set_flag
from invenio.modules.knowledge.api import get_kb_mappings

__all__ = ['LicenseField']


def _kb_license_choices(domain_data=True, domain_content=True,
                        domain_software=True):
    def _mapper(x):
        license = json.loads(x['value'])
        if (license['domain_data'] and domain_data) or \
                (license['domain_content'] and domain_content) or \
                (license['domain_software'] and domain_software):
            return (x['key'], license['title'])
        else:
            return None
    return sorted(
        filter(lambda x: x is not None,
               map(_mapper, get_kb_mappings('licenses', '', ''))),
        key=itemgetter(1),
    )


class LicenseField(WebDepositField, SelectField):

    """License field."""

    def __init__(self, **kwargs):
        """Initialize license field."""
        kwargs.setdefault("icon", "icon-certificate")

        if 'choices' not in kwargs:
            license_filter = {}
            for opt in ['domain_data', 'domain_content', 'domain_software']:
                if opt in kwargs:
                    license_filter[opt] = kwargs[opt]
                    del kwargs[opt]
            kwargs['choices'] = _kb_license_choices(**license_filter)
        kwargs['processors'] = [set_flag('touched'), ]
        super(LicenseField, self).__init__(**kwargs)
