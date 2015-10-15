/*
 * This file is part of Lifewatch DAAP.
 * Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
 *
 * Lifewatch DAAP is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Lifewatch DAAP is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * This file is part of Invenio.
 * Copyright (C) 2014, 2015 CERN.
 *
 * Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */

require([
    'jquery',
    ], function () {
      $('.table tr').click(function (ev) {
        if (this.children.length > 0) {
          var data = this.children[0].dataset;
          if (data.groupId) {
            window.location.href = "./" + data.groupId;
          }
        }
      });

      $('.panel #collapse').on("click", function () {
        results = $(this).parents('.panel').find('#g_search_results');
        console.info(results);
        if (results) {
          if ($(this).hasClass('panel-collapsed')) {
            results.slideDown();
            $(this).removeClass('panel-collapsed');
            $(this).find('i').removeClass('fa-chevron-down').addClass('fa-chevron-up');
          }
          else {
            // collapse the panel
            results.slideUp();
            $(this).addClass('panel-collapsed');
            $(this).find('i').removeClass('fa-chevron-up').addClass('fa-chevron-down');
          }
        }
      });
    });
