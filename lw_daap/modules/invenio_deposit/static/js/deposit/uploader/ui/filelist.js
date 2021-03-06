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
 * Copyright (C) 2014 CERN.
 *
 * Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */
'use strict';

/**
 * Presents current file list.
 *
 * @requires mustache/mustache
 * @requires templates/fileListRow.html
 *
 * @returns {Component} FileList
 */
define(function(require) {
    return require('flight/lib/component')(FileList);

    function FileList() {


        this.attributes({
            tableBodySelector: '.filelist-placeholder',
            get_file_url: ''
        });

        var fileListRow = require('hgn!../../templates/file_list_row'),
            $ = require('jquery');

        /**
         * Event handlers.
         */

        function handleFilesAddedToFileList(ev, files) {
            var that = this;
            var html = "";

            $.each(files, function(i, file) {
                var downloadable = (file.status === 5) ? true : false;
                html += fileListRow({
                    file: file,
                    downloadable: downloadable,
                    get_file_url: that.attr.get_file_url
                });
            });

            this.select('tableBodySelector').append(html);
        }

        function handleFileProgressUpdatedOnFileList(ev, data) {
            var selector = "#progress-bar-" + data.file.id;
            var info = "#progress-info-" + data.file.id;
            $(this.$node.find(info)).html(data.file.percent.toString() + "%  " + data.upload_speed);
            $(this.$node.find(selector)).css('width', data.file.percent.toString() + "%");
            $(this.$node.find(selector)).addClass("progress-bar-striped");
        }

        function handleItemClick(ev) {
            if ($(ev.target).hasClass("rmlink")) {
                var fileId = ev.target.dataset.fileId;
                var selector = '#' + fileId;

                this.trigger('fileRemovedByUser', {
                    fileId: fileId
                });
                $(selector).fadeOut(200, function() {
                    $(this).remove();
                });
            }
        }

        function handleUploadCompleted(ev, files) {
            var that = this;
            $.each(files, function(key, file) {
                if (file.status === 5) {
                    var selector = '#download-link-' + file.id;
                    var $elem = $(that.$node.find(selector));
                    $elem.append("<a href='" + that.attr.get_file_url + "?file_id=" + file.server_id + "' class='btn btn-default'><i class='fa fa-cloud-download'></i> Download</a>");
                }
            });
            $('#upload-speed').html('');
        };

        function handleFileUploadCompleted(ev, data) {
            var selector = "#file-id-" + data.file.id;
            $(selector).val(data.file.server_id);
        }

        function handleMouseOver(ev) {
            if ($(ev.target).hasClass("sortlink")) {
                $("#sortable").sortable("enable");
            }
        }

        function handleItemMouseUp(ev) {
            if ($(ev.target).hasClass("sortlink")) {
                $("#sortable").sortable("disable");
            }
        }

        function handleUpdateGetFileUrl(ev, data) {
            this.attr.get_file_url = data.get_file_url;
        }

        this.after('initialize', function() {
            var that = this;
            $("#sortable").sortable({
                forceHelperSize: true,
                forcePlaceholderSize: true,
                disabled: true,

                start: function(event, ui) {
                    var header_ths = $("#uploader-filelist thead th"),
                        item_tds = $(ui.helper).find("td");
                    for (var i = 0; i < header_ths.length; i++) {
                        $(item_tds[i]).width($(header_ths[i]).width());
                    }
                    $(ui.placeholder).height(ui.item.height());
                    $(ui.helper).width(ui.item.width());
                },

                update: function(event, ui) {
                    that.trigger('fileListUpdated');
                }
            });
            $("#sortable").disableSelection();

            this.on('filesAddedToFileList', handleFilesAddedToFileList);
            this.on('fileProgressUpdatedOnFileList', handleFileProgressUpdatedOnFileList);
            this.on('uploadCompleted', handleUploadCompleted);
            this.on('fileUploadCompleted', handleFileUploadCompleted);
            this.on('click', handleItemClick);
            this.on('mouseover', handleMouseOver);
            this.on('mouseup', handleItemMouseUp);
            this.on('updateGetFileUrl', handleUpdateGetFileUrl);

            this.trigger('fileListInitialized');
        });
    }
});
