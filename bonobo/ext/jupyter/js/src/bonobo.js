var widgets = require('jupyter-js-widgets');
var _ = require('underscore');

// Custom Model. Custom widgets models must at least provide default values
// for model attributes, including `_model_name`, `_view_name`, `_model_module`
// and `_view_module` when different from the base class.
//
// When serialiazing entire widget state for embedding, only values different from the
// defaults will be specified.

var BonoboModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend({}, widgets.DOMWidgetModel.prototype.defaults, {
        _model_name: 'BonoboModel',
        _view_name: 'BonoboView',
        _model_module: 'bonobo',
        _view_module: 'bonobo',
        value: []
    })
});


// Custom View. Renders the widget model.
var BonoboView = widgets.DOMWidgetView.extend({
    render: function () {
        this.value_changed();
        this.model.on('change:value', this.value_changed, this);
    },

    value_changed: function () {
        this.$el.html(
            this.model.get('value').join('<br>')
        );
    },
});


module.exports = {
    BonoboModel: BonoboModel,
    BonoboView: BonoboView
};
