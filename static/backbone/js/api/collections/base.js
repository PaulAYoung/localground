define(["underscore", "backbone", "jquery", "collections/baseMixin"],
    function (_, Backbone, $, CollectionMixin) {
        "use strict";
        /**
         * An "abstract" Backbone Collection; the root of all of the other
         * localground.collections.* classes. Has some helper methods that help
         * Backbone.Collection objects more easily interat with the Local Ground
         * Data API.
         * @class localground.collections.Base
         */
        var Base = Backbone.Collection.extend({
            key: null,
            defaults: {
                isVisible: true
            },
            initialize: function (model, opts) {
                $.extend(this, opts);
            },
            parse: function (response) {
                return response.results;
            }

        });
        console.log(CollectionMixin.prototype);
        _.extend(Base.prototype, CollectionMixin);

        return Base;
    });
