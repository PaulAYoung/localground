define(["underscore",
        "charts/chart",
        "highcharts"
    ],
    function (_, Chart) {
        "use strict";
        /**
         * The BarChart's job is to render a bar chart.
         */
        var BarChart = Chart.extend({
            initialMessage: 'Please drag at least one numeric variable onto the y-axis ' +
                            'and at least one other variable onto the x-axis',
            xAxis: null,
            yAxis: null,
            initialize: function (opts) {
                Chart.prototype.initialize.apply(this, arguments);
                this.xAxis = opts.xAxis;
                this.yAxis = opts.yAxis;
            },
            render: function () {
                if (this.yAxis.collection && this.yAxis.collection.length >= 1 &&
                        this.xAxis.collection.length == 1) {
                    this.renderChart();
                } else {
                    this.destroyChart();
                    this.showInitialMessage();
                }
            },
            transformDataAvg: function () {
                
            },
            transformData: function () {
                var collection = this.dataManager.getRecords(),
                    that = this,
                    i = 0;
                this.categories = [];
                this.seriesData = [];
                this.yAxis.collection.each(function (field) {
                    that.seriesData.push({
                        name: field.get("col_alias"),
                        data: []
                    });
                });
                collection.each(function (record) {
                    that.categories.push(record.get(that.xAxis.collection.at(0).get("col_name")));
                    i = 0;
                    that.yAxis.collection.each(function (field) {
                        that.seriesData[i].data.push(record.get(field.get("col_name")));
                        ++i;
                    });
                });
            },
            renderChart: function () {
                this.$el.css("height", "auto");
                this.setSize();
                this.transformData();
                var chartOpts = {
                    chart: {
                        type: 'column',
                        height: this.chartHeight
                    },
                    title: {
                        text: 'My Chart Title'
                    },
                    xAxis: {
                        categories: this.categories
                    },
                    yAxis: {
                        min: 0
                    },
                    plotOptions: {
                        column: {
                            pointPadding: 0.2,
                            borderWidth: 0
                        }
                    },
                    tooltip: {
                        headerFormat: '<span style="font-size:10px">{point.key}</span><table class="table table-condensed">',
                        pointFormat: '<tr><td>{series.name}: </td><td>{point.y}</td></tr>',
                        footerFormat: '</table>',
                        shared: true,
                        useHTML: true
                    }
                };
                _.extend(chartOpts, { series: this.seriesData });
                this.$el.highcharts(chartOpts);
            }
        });
        return BarChart;
    });