define(["models/base"], function (Base) {
    "use strict";
    /**
     * A Backbone Model class for the MapImage datatype.
     * @class MapImage
     * @see <a href="http://localground.org/api/0/map-images/">http://localground.org/api/0/map-images/</a>
     */
    var MapImage = Base.extend({
        getNamePlural: function () {
            return "scans";
        }
    });
    return MapImage;
});
