var widgets = require('jupyter-js-widgets');
var _ = require('underscore');

// Custom Model. Custom widgets models must at least provide default values
// for model attributes, including `_model_name`, `_view_name`, `_model_module`
// and `_view_module` when different from the base class.
//
// When serialiazing entire widget state for embedding, only values different from the
// defaults will be specified.

const BonoboModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend({}, widgets.DOMWidgetModel.prototype.defaults, {
        _model_name: 'BonoboModel',
        _view_name: 'BonoboView',
        _model_module: 'bonobo',
        _view_module: 'bonobo',
        value: []
    })
});


// Custom View. Renders the widget model.
const BonoboView = widgets.DOMWidgetView.extend({
    render: function () {
        this.value_changed();
        this.model.on('change:value', this.value_changed, this);
    },

    value_changed: function () {
        this.$el.html(
            '<div class="rendered_html"><table style="margin: 0; border: 1px solid black;">' + this.model.get('value').map((key, i) => {
                return `<tr><td>${key.status}</td><td>${key.name}</td><td>${key.stats}</td><td>${key.flags}</td></tr>`
            }).join('\n') + '</table></div>'
        );
    },
});


module.exports = {
    BonoboModel: BonoboModel,
    BonoboView: BonoboView
};
