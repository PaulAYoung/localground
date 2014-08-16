require.config({
	baseUrl: "js/api",
	paths: {
		'jquery': '//code.jquery.com/jquery-1.8.0.min',
		'backbone': '../external/backbone-min',
		'underscore': '../external/underscore-min',
		'text': '../external/text',
		'jquery.bootstrap': '//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min',
        'backgrid': '../external/backgrid.min',
		'backgrid-paginator': '../external/backgrid-paginator-svw-debugged',
		'form': '../external/backbone-forms',
		'bootstrap-form-templates': '../external/backbone-forms-bootstrap3-templates',
		'backbone-bootstrap-modal': '../external/backbone.bootstrap-modal',
		'colResizable': '../external/colResizable-1.3.source',
		'backbone-pageable': '../external/backbone-pageable',
		'backbone-paginator': '../external/backbone.paginator'
	},
	//waitSeconds: 0,
	shim: {
		'underscore' : {
            exports : "_"
        },
		'backbone' : {
            deps    : [ "jquery", "underscore" ],
            exports : "Backbone"
        },
		'jquery.bootstrap': {
			deps: ['jquery']
		},
		'backgrid': {
			deps: ['backbone'],
			exports: 'Backgrid'
		},
		'bootstrap-form-templates': {
			deps: ['backbone'],
		},
		'backbone-bootstrap-modal': {
			deps: ['backbone', 'jquery.bootstrap'],
		},
		'colResizable': {
			deps: ['jquery'],
			exports: 'colResizable'
		}
	},
	urlArgs: "bust=" + (new Date()).getTime()
});

/** Javascript template directory */
var templateDir = '/static/backbone/js/templates';

/** Namespace definition */
var localground = {
	maps: {
		tiles: {},
		controls: {},
		data: {},
		views: {}
	},
	tables: {},
	config: {},
	models: {},
	collections: {}
};


/**
 * Global: cookie getter
 * @param {String} name of the cookie
 * @returns {String} cookie value
 */
function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

