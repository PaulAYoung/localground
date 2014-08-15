define(["lib/table/formatters/latlng"], function(LatLngFormatter) {
	/** 
     * Custom formatter for handling latitudes (in light of a corresponding
     * latitude value)
     * @class LngFormatter
     */
	localground.tables.LngFormatter = {
		fromRaw: function (rawValue, model) {
			try {
				return rawValue.coordinates[0].toFixed(4);
			} catch(e) {
				return model.lng || "";
			}
		},
		toRaw: function (formattedData, model) {
			return LatLngFormatter.update(formattedData, model, "lng", 0);
		}
	};
	return localground.tables.LngFormatter;
});