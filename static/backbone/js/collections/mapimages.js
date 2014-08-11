define(["jquery", "backbone", "models/mapimage"], function($, Backbone, MapImage) {
    var MapImages = Backbone.Collection.extend({
        model: MapImage,
        name: 'Map Images',
        url: '/api/0/map-images/',
		parse : function(response) {
            return response.results;
        },
    });
    return MapImages;
});
