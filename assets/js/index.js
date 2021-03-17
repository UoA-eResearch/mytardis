"use strict";

require("jquery");
require("expose-loader?$!jquery");
require("expose-loader?jQuery!jquery");
require("jquery-ui-dist/jquery-ui.min");
require("bootstrap");
require("bootstrap-3-typeahead");
require("underscore/underscore-min");
require("expose-loader?_!underscore/underscore-min");
require("underscore.string/dist/underscore.string");
require("expose-loader?s!underscore.string/dist/underscore.string");
require("backbone/backbone");
require("expose-loader?Backbone!backbone/backbone");
require("../js/tardis_portal/backbone-models");
require("expose-loader?MyTardis!./tardis_portal/backbone-models");
require("backbone-forms/distribution/backbone-forms");
require("backbone-forms/distribution/templates/bootstrap3");
require("mustache");
require("expose-loader?Mustache!mustache");
require("sprintf-js/dist/sprintf.min");
require("expose-loader?sprintf!sprintf-js/dist/sprintf.min");
require("clipboard");
require("expose-loader?ClipboardJS!clipboard/dist/clipboard");
//css
require("bootstrap/dist/css/bootstrap.css");
require("../css/jquery-ui/jquery-ui-1.8.18.custom.css");
require("font-awesome/css/font-awesome.css");
require("../css/default.css");
require("../css/facility-overview.css");
require("blueimp-file-upload/css/jquery.fileupload.css");
require("select2/dist/css/select2.css");
require("select2/dist/js/select2.js");
import "@apps/cart/initialiseCartLink";