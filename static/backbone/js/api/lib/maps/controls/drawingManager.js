define(["underscore", "jquery", "models/marker", "config"], function (_, $, Marker, Config) {
    "use strict";
    /**
     * Class that lets users update geometries and merge objects together.
     * @class DrawingManager
     * @param {options} opts
     *
     */
    var DrawingManager = function (opts, basemap) {
        this.dm = null;
        this.polygonOptions = {
            strokeWeight: 0,
            fillOpacity: 0.45,
            editable: true
        };
        this.polylineOptions = {
            editable: true
        };
        this.markerOptions = {
            draggable: true,
            icon: {
                fillColor: '#999',
                strokeColor: "#FFF",
                strokeWeight: 1.5,
                fillOpacity: 1,
                path: 'M16,3.5c-4.142,0-7.5,3.358-7.5,7.5c0,4.143,7.5,18.121,7.5,18.121S23.5,15.143,23.5,11C23.5,6.858,20.143,3.5,16,3.5z M16,14.584c-1.979,0-3.584-1.604-3.584-3.584S14.021,7.416,16,7.416S19.584,9.021,19.584,11S17.979,14.584,16,14.584z',
                scale: 1.6,
                anchor: new google.maps.Point(16, 30),      // anchor (x, y)
                size: new google.maps.Size(15, 30),         // size (width, height)
                origin: new google.maps.Point(0, 0)        // origin (x, y)
            }
        };

        this.initialize = function (opts, basemap) {
            this.app = opts.app;
            this.basemap = basemap;
            this.dm = new google.maps.drawing.DrawingManager({
                //drawingMode: google.maps.drawing.OverlayType.MARKER,
                markerOptions: this.markerOptions,
                polylineOptions: this.polylineOptions,
                polygonOptions: this.polygonOptions,
                drawingControl: true,
                drawingControlOptions: {
                    position: google.maps.ControlPosition.TOP_LEFT,
                    drawingModes: [
                        google.maps.drawing.OverlayType.MARKER,
                        google.maps.drawing.OverlayType.POLYLINE,
                        google.maps.drawing.OverlayType.POLYGON
                    ]
                },
                map: null
            });
            this.attachEventHandlers();
        };

        this.attachEventHandlers = function () {
            var that = this;

            //add listeners:
            this.app.vent.on("mode-change", this.changeMode.bind(this));
            this.app.vent.on("dragging", this.showDragHighlighting.bind(this));
            this.app.vent.on("drag-ended", this.saveDragChange.bind(this));
            this.app.vent.on("georeference-from-div", this.dropItem.bind(this));

            google.maps.event.addListener(this.dm, 'overlaycomplete', function (e) {
                that.addMarker(e.overlay);
            });
        };

        this.changeMode = function () {
            if (this.app.getMode() === "view") {
                this.hide();
            } else {
                this.show();
            }
        };

        this.show = function () {
            this.dm.setMap(this.app.getMap());
        };

        this.hide = function () {
            this.dm.setMap(null);
        };

        this.addMarker = function (googleOverlay) {
            var that = this,
                model = new Marker({
                    project_id: this.app.getActiveProjectID(),
                    color: "999999"
                });
            model.setGeometry(googleOverlay);
            model.save({}, {
                success: function (model, response) {
                    //notify the dataManager that a new data element has been added:
                    model.generateUpdateSchema(response.update_metadata);
                    that.app.vent.trigger("marker-added", {
                        key: "markers",
                        models: [ model ]
                    });

                    // update map overlays to reflect new state:
                    googleOverlay.setMap(null);
                    that.dm.setDrawingMode(null);
                    model.trigger("show-overlay");
                    model.trigger("show-item");
                }
            });
        };

        this.getMarkerOverlays = function () {
            var overlayGroup = this.basemap.overlayManager.getMarkerOverlays();
            return overlayGroup.children;
        };

        this.showDragHighlighting = function (opts) {
            this.getMarkerOverlays().each(function (marker) {
                if (marker.intersects(opts.latLng)) {
                    marker.highlight();
                } else {
                    marker.unHighlight();
                }
            });
        };

        this.dropItem = function (opts) {
            function elementContainsPoint(domElement, x, y) {
                return x > domElement.offsetLeft && x < domElement.offsetLeft + domElement.offsetWidth &&
                    y > domElement.offsetTop && y < domElement.offsetTop + domElement.offsetHeight;

            }
            var event = opts.event,
                model = opts.model,
                overlayView = this.app.getOverlayView(),
                map = this.app.getMap(),
                e = event.originalEvent,
                mapContainer = map.getDiv(),
                point,
                projection,
                latLng;
            e.stopPropagation();

            if (elementContainsPoint(mapContainer, e.pageX, e.pageY)) {
                point = new google.maps.Point(e.pageX - mapContainer.offsetLeft,
                    e.pageY - mapContainer.offsetTop);
                projection = overlayView.getProjection();
                latLng = projection.fromContainerPixelToLatLng(point);
                model.setGeometry(latLng);
                model.save();
                model.trigger('show-item');
                model.trigger('show-overlay');
            }
        };

        this.saveDragChange = function (opts) {
            var model = opts.model,
                latLng = opts.latLng,
                attached = false;
            this.getMarkerOverlays().each(function (marker) {
                marker.unHighlight();
                if (marker.intersects(latLng)) {
                    attached = true;
                    marker.model.attach(model, function () {
                        model.trigger('hide-item');
                        marker.model.fetch();
                    });
                }
            });
            if (!attached) {
                model.setGeometry(latLng);
                model.save();
            }
        };

        //call initialization function:
        this.initialize(opts, basemap);
    };


    //extend prototype so that this function is visible to the CORE:
    _.extend(DrawingManager.prototype, {
        destroy: function () {
            this.hide();
        }
    });
    return DrawingManager;
});