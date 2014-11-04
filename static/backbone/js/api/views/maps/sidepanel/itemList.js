/**
 * Created by zmmachar on 10/15/14.
 */
define(["marionette",
        "underscore",
        "jquery",
        "text!" + templateDir + "/sidepanel/collectionHeader.html",
        "views/maps/sidepanel/items/item",
        "config"
    ],
    function (Marionette, _, $, collectionHeader, Item, Config) {
        "use strict";

        var ItemList = Marionette.CompositeView.extend({

            template: _.template(collectionHeader),


            childView: Item,

            childViewContainer: ".collection-data",

            /** tracks # of times this view is rendered (important for restoring state) */
            numRenderings: 0,

            state: {},

            events: {
                'click .show-hide': 'toggleShow',
                'click .check-all': 'toggleShowAll',
                'click .zoom-to-extent': 'zoomToExtent'
            },
            //Until models are added, a given list is hidden
            className: "hidden",

            hidden: true,


            initialize: function (opts) {
                this.app = opts.app;
                this.id = 'sidebar-header' + opts.collection.key;
                this.opts = opts;
                this.collection = opts.collection;
                if (this.collection.key) {
                    var configKey = this.collection.key.split("_")[0];
                    this.childView = Config[configKey].ItemView;
                    this.childViewOptions = $.extend(opts, {template: _.template(Config[configKey].ItemTemplate)});
                }
                this.restoreState();
                this.listenTo(this.app.vent, 'toggle-project', this.toggleProjectData);
            },

            templateHelpers: function () {
                return {
                    name: this.collection.name,
                    key: this.collection.key,
                    isVisible: this.isVisible(),
                    isExpanded: this.isExpanded()
                };
            },

            zoomToExtent: function () {
                this.collection.trigger('zoom-to-extent');
            },

            isVisible: function () {
                var isVisible = !this.hidden && this.opts.collection.length > 0 &&
                                    this.$el.find('.check-all').is(':checked');
                // ensures that localStorage flag is only honored on initialization.
                if (this.isFirstRendering()) {
                    isVisible = isVisible || this.state.isVisible;
                }
                return isVisible;
            },

            isExpanded: function () {
                var isExpanded = this.$el.find('.show-hide').hasClass('fa-caret-down');
                // ensures that localStorage flag is only honored on initialization.
                if (this.isFirstRendering()) {
                    isExpanded = isExpanded || this.state.isExpanded;
                }
                return isExpanded;
            },

            onAddChild: function () {
                if (this.hidden) {
                    this.$el.removeClass('hidden');
                    this.hidden = false;
                }
            },

            onRemoveChild: function () {
                if (this.collection.length === 0 && !this.hidden) {
                    this.hidden = true;
                    this.$el.addClass('hidden');
                }
            },

            toggleShow: function () {
                this.$el.find(this.childViewContainer).toggleClass('hidden');
                if (this.isExpanded()) {
                    this.$el.find('.show-hide').removeClass('fa-caret-down').addClass('fa-caret-right');
                } else {
                    this.$el.find('.show-hide').removeClass('fa-caret-right').addClass('fa-caret-down');
                }
                this.saveState();
            },

            toggleShowAll: function () {
                if (this.$el.find('.check-all').is(':checked')) {
                    this.children.each(function (child) {
                        child.checkItem();
                    });
                } else {
                    this.children.each(function (child) {
                        child.uncheckItem();
                    });
                }
                this.saveState();

            },

            toggleProjectData: function (id, visible) {
                this.collection.each(function (model) {
                    if (model.get('project_id') === Number(id)) {
                        model.set('isVisible', visible);
                    }
                });
                this.hidden = !this.collection.any(function (model) { return model.get('isVisible'); });
                if (this.hidden) {
                    this.$el.addClass('hidden');

                } else {
                    this.$el.removeClass('hidden');
                    //this.toggleShowAll();
                }
                this.saveState();
            },

            onRender: function () {
                ++this.numRenderings;
            },

            isFirstRendering: function () {
                return this.numRenderings < 1;
            },

            saveState: function () {
                this.app.saveState(
                    this.id,
                    {
                        isVisible: this.isVisible(),
                        isExpanded: this.isExpanded()
                    },
                    false
                );
            },

            restoreState: function () {
                this.state = this.app.restoreState(this.id);
                if (!this.state) {
                    this.state = {
                        isVisible: false,
                        isExpanded: false
                    };
                }
            }

        });

        return ItemList;
    });