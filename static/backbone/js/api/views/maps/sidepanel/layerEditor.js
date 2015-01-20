define(["underscore",
        "jquery",
        "marionette",
        "form",
        "models/layer",
        "text!" + templateDir + "/sidepanel/layerEditor.html",
        "bootstrap-form-templates"
        ],
    function (_, $, Marionette, Form, Layer, LayerEditorTemplate) {
        'use strict';

        var LayerEditor = Marionette.ItemView.extend({

            events: {
                'click #marker_cancel': 'hide',
                'click .btn-primary': 'saveForm'
            },

            template: _.template(LayerEditorTemplate),

            initialize: function (opts) {
                $.extend(this, opts);
                if (_.isUndefined(this.model)) {
                    this.model = new Layer();
                }
            },

            onRender: function () {
                //this.$el.html(this.template());
                var ModelForm = Form.extend({
                    schema: {
                        name: { type: "Text", title: "Name" },
                        description: { type: "Text", title: "Description" },
                        //tags: { type: "Text", title: "Tags", help: "Tag your layer here" },
                        source: { type: "Text", title: "Source", help: "List of the underlying data sources" },
                        symbols: { type: "TextArea", title: "Symbols", help: "Add your symbol markup here" }
                    }
                });
                this.$el.html(this.template());
                this.form = new ModelForm({
                    model: this.model
                });
                this.form.render();
                this.$el.find('.form').append(this.form.$el);
            },

            saveForm: function (e) {
                //does validation
                this.form.commit();

                //add extras:
                //todo: slug doesn't make sense in this context. Remove.
                if (_.isUndefined(this.model.get("slug"))) {
                    this.model.set("slug", this.app.generateSlug());
                }
                if (_.isUndefined(this.model.get("project_id"))) {
                    this.model.set("project_id", this.app.getActiveProjectID());
                }
                //save to database:
                this.model.save();      //does database commit
                e.preventDefault();
            },

            ignore: function (e) {
                e.stopPropagation();
            },

            hide: function () {
                this.app.vent.trigger('show-layer-list');
            },

            show: function () {
                this.$el.show();
            }
        });
        return LayerEditor;
    });
