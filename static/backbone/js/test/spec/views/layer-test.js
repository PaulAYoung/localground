define([
    "underscore",
    "views/maps/overlays/layer",
    "lib/maps/data/dataManager",
    "lib/maps/overlays/symbolized",
    "../../../test/spec-helper"
],
    function (_, LayerView, DataManager, Symbolized) {
        'use strict';

        function initLayerView(scope) {
            scope.app.map = new google.maps.Map(document.getElementById('map_canvas'), {
                center: { lat: -34, lng: 150 }
            });
            var layerView = new LayerView({
                app: scope.app,
                model: scope.layers.at(1) //cat & dog layer
            });
            //add data to the dataManager:
            layerView.dataManager.updateCollections(scope.projects.at(0));
            layerView.dataManager.updateCollections(scope.projects.at(1));
            return layerView;
        }
        describe("Layer view: Map Layer can be initialized & drawn", function () {

            it("Can initialize a map layer", function () {
                var layerView,
                    that = this;
                expect(function () {
                    layerView = initLayerView(that);
                }).not.toThrow();
                expect(layerView.dataManager).toEqual(jasmine.any(DataManager));
                expect(_.isObject(layerView.overlayMap)).toBeTruthy();
            });

            it("Correctly renders \"Symbolized\" overlays on initialization", function () {
                var layerView = initLayerView(this);

                //ensure that the underlying model has 2 symbols (sanity check):
                expect(layerView.model.getSymbols().length).toBe(2);

                //the dog symbol has one dog model and the cat symbol has one cat model:
                _.each(layerView.overlayMap, function (val) {
                    expect(val.length).toBe(1);
                    expect(val[0]).toEqual(jasmine.any(Symbolized));
                });
            });
        });

        describe("Layer view: event handlers correctly add and remove layers", function () {
            it("Listens for toggle symbol checkbox", function () {
                var layerView = initLayerView(this),
                    rule = 'tags contains cat';
                expect(layerView.getSymbolOverlays(rule).length).toBe(1);
                _.each(layerView.getSymbolOverlays(rule), function (overlay) {
                    expect(overlay.isShowingOnMap()).toBeFalsy();
                });

                //emulate the behavior of a checkbox click:
                layerView.model.getSymbol(rule).isShowingOnMap = true;
                layerView.model.trigger('symbol-change', rule);
                expect(layerView.getSymbolOverlays(rule).length).toBe(1);
                _.each(layerView.getSymbolOverlays(rule), function (overlay) {
                    expect(overlay.isShowingOnMap()).toBeTruthy();
                });

                //do it again:
                //emulate the behavior of a checkbox click:
                layerView.model.getSymbol(rule).isShowingOnMap = false;
                layerView.model.trigger('symbol-change', rule);
                expect(layerView.getSymbolOverlays(rule).length).toBe(1);
                _.each(layerView.getSymbolOverlays(rule), function (overlay) {
                    expect(overlay.isShowingOnMap()).toBeFalsy();
                });
            });

            it("Listens for toggle layer checkbox", function () {
                var layerView = initLayerView(this);
                expect(layerView.getLayerOverlays().length).toBe(2);
                _.each(layerView.getLayerOverlays(), function (overlay) {
                    expect(overlay.isShowingOnMap()).toBeFalsy();
                });

                //emulate the behavior of a checkbox click:
                layerView.model.set("isShowingOnMap", true);
                expect(layerView.getLayerOverlays().length).toBe(2);
                _.each(layerView.getLayerOverlays(), function (overlay) {
                    expect(overlay.isShowingOnMap()).toBeTruthy();
                });

                //do it again:
                //emulate the behavior of a checkbox click:
                layerView.model.set("isShowingOnMap", false);
                expect(layerView.getLayerOverlays().length).toBe(2);
                _.each(layerView.getLayerOverlays(), function (overlay) {
                    expect(overlay.isShowingOnMap()).toBeFalsy();
                });
            });
        });

        describe("Layer view: event handlers correctly zoom", function () {
            it("Listens for zoom to extent button click", function () {
                //workaround that allows Jasmine spies to work with Backbone's
                //modelEvent listeners. Spy on Class.prototype:
                spyOn(LayerView.prototype, "zoomToExtent");
                var layerView = initLayerView(this);
                layerView.model.trigger('zoom-to-layer');
                expect(layerView.zoomToExtent).toHaveBeenCalled();
            });
        });

    });
