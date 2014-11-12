define([
    "backbone-pageable",
    "models/record",
    "jquery"
], function (PageableCollection, Record, $) {
    "use strict";
    var Records = PageableCollection.extend({
        model: Record,
        columns: null,
        key: null,
        overlay_type: null,
        name: 'Records',
        query: '',
        url: null,
        initialize: function (recs, opts) {
            opts = opts || {};
            $.extend(this, opts);
            if (!this.url) {
                alert("The Records collection requires a url parameter upon initialization");
                return;
            }
            PageableCollection.prototype.initialize.apply(this, arguments);
        },
        state: {
            pageSize: 25,
            sortKey: 'id',
            order: 1
        },

        //  See documentation:
        //  https://github.com/backbone-paginator/backbone-pageable
        queryParams: {
            totalPages: null,
            totalRecords: null,
            sortKey: "ordering",
            pageSize: "page_size"
        },

        parseState: function (resp, queryParams, state, options) {
            return {
                totalRecords: resp.count
            };
        },

        parseRecords: function (response, options) {
            return response.results;
        },

        fetch: function (options) {
            //query
            if (this.query) {
                options.data = options.data || {};
                $.extend(options.data, { query: this.query });
            }

            PageableCollection.__super__.fetch.apply(this, arguments);
        }
    });
    return Records;
});
