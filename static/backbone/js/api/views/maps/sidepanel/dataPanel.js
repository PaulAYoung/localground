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
		eventManager: null,
		map: null,
		projectsMenu: null,
		dataViews: {},
		
		/**
		 * Initializes the dataPanel
		 * @param {Object} opts
		 * A dictionary of available options
		 * @param {google.maps.Map} opts.map
		 * A reference to the UI's Google Map object
		 * @param {localground.maps.managers.DataManager} opts.dataManager
		 * @param {Backbone.Events} opts.eventManager
		 * Coordinates the triggering and listening to events across shared
		 * objects.
		 *
		 */
		initialize: function(opts){
			var that = this;
			$.extend(this, opts);
			
			this.projectsMenu = new localground.maps.views.ProjectsMenu({
				dataManager: this.dataManager,
				eventManager: this.eventManager
			});
			
			// listen for changes in the selectedProjects, and re-render
			// accordingly
			this.dataManager.selectedProjects.on('add', this.render, this);
			this.dataManager.selectedProjects.on('remove', this.render, this);
						
			this.eventManager.on(localground.events.EventTypes.SHOW_ALL, function(key){
				that.dataViews[key]["isVisible"] = true;
			});
			this.eventManager.on(localground.events.EventTypes.HIDE_ALL, function(key){
				that.dataViews[key]["isVisible"] = false;
			});
			
			this.eventManager.on(localground.events.EventTypes.EXPAND, function(key){
				that.dataViews[key]["isExpanded"] = true;
			});
			this.eventManager.on(localground.events.EventTypes.CONTRACT, function(key){
				that.dataViews[key]["isExpanded"] = false;
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
					this.dataViews[key] = {
						items: new localground.maps.views.Items({
							collection: this.dataManager.collections[key],
							itemTemplateHtml: localground.config.Config[configKey].itemTemplateHtml,
							ItemView: localground.config.Config[configKey].ItemView,
							map: this.map,
							eventManager: this.eventManager
						}),
						isVisible: false,
						isExpanded: false
					};
				}
				this.$el.find('.pane-body')
					.append(
						this.dataViews[key]["items"].render({
							isVisible: this.dataViews[key]["isVisible"],
							isExpanded: this.dataViews[key]["isExpanded"]
						}).el);
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
