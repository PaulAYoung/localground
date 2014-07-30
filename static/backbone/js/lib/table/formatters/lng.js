define(["lib/table/formatters/latlng"], function(LatLngFormatter) {
	var LngFormatter = {
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
	return LngFormatter;
});