define(["backbone",
		"text!" + templateDir + "/sidepanel/dataPanelHeader.html",
		"views/maps/sidepanel/projectsMenu",
		"views/maps/sidepanel/items",
		"config"],
	   function(Backbone, dataPanelHeader) {
	/**
	 * A class that handles display and rendering of the
	 * data panel and projects menu
	 * @class DataPanel
	 */
	localground.maps.views.DataPanel = Backbone.View.extend({
		/**
		 * @lends localground.maps.views.DataPanel#
		 */
		
		template: _.template( dataPanelHeader ),
		dataManager: null,
		map: null,
		projectsMenu: null,
		dataViews: {},
		initialize: function(opts){
			$.extend(this, opts);
			
			this.projectsMenu = new localground.maps.views.ProjectsMenu({
				dataManager: this.dataManager
			});
			
			this.render();
		},
		/**
		 * render projects menu if it doesn't currently exist
		 */
		renderProjectsMenu: function(){
			if (this.$el.find('.projects-menu').get(0) == null) {
				this.$el.empty().append(this.template());
				this.$el.find('.projects-menu').append(
					this.projectsMenu.render().el
				);
			}	
		},
		
		/**
		 * Renders the HTML for the data panel. Called everytime
		 * project data changes. Note that the project panel is
		 * only rendered once.
		 */
		render: function() {
			//render projects menu:
			this.renderProjectsMenu();
			
			//render sub-views:
			this.$el.find('.pane-body').empty();
			for (key in this.dataManager.collections) {
				if (this.dataViews[key] == null) {
					var configKey = key.split("_")[0];
					this.dataViews[key] = new localground.maps.views.Items({
						collection: this.dataManager.collections[key],
						itemTemplateHtml: localground.config.Config[configKey].itemTemplateHtml,
						ItemView: localground.config.Config[configKey].ItemView,
						map: this.map
					});
				}
				this.$el.find('.pane-body').append(this.dataViews[key].render().el);
			}
			
			//re-attach event handlers:
			this.projectsMenu.delegateEvents();
			this.resize();
			return this;
		},
		
		resize: function(){
			this.$el.find('.pane-body').height($('body').height() - 140);
		}
	});
	return localground.maps.views.DataPanel;
});