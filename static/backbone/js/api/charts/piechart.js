define(["charts/chart",
        "highcharts"
    ],
    function (Chart) {
        "use strict";
        /**
         * The PieChart's job is to render a pie chart.
         */
        var PieChart = Chart.extend({
            initialMessage: 'Please drag one (and only one) variable onto the x-axis',
            xAxis: null,
            seriesName: null,
            initialize: function (opts) {
                Chart.prototype.initialize.apply(this, arguments);
                this.xAxis = opts.xAxis;
                this.render();
            },
            render: function () {
                if (this.xAxis.collection.length == 1) {
                    this.renderChart();
                } else {
                    this.destroyChart();
                    this.showInitialMessage();
                }
            },
            transformData: function () {
                var collection = this.dataManager.getRecords(),
                    key = this.xAxis.collection.at(0).get("col_name"),
                    lookup = {};
                this.seriesName = this.xAxis.collection.at(0).get("col_alias");
                this.seriesData = [];

                // loop that counts the number of times a particular
                // value appears in the collection:
                collection.each(function (record) {
                    if (lookup[record.get(key)] == null) {
                        lookup[record.get(key)] = 0;
                    }
                    lookup[record.get(key)] += 1;
                });

                // converts to form that is useable for highcharts
                for (key in lookup) {
                    this.seriesData.push([ key, lookup[key]]);
                }
            },
            renderChart: function () {
                this.$el.css("height", "auto");
                this.setSize();
                this.transformData();
                var chartOpts = {
                    chart: {
                        height: this.chartHeight
                    },
                    title: {
                        text: 'My Chart Title'
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                    plotOptions: {
                        series: 
                        {
                            cursor: 'pointer',
                            point: 
                            {
                                events: 
                                {
                                    click: function()
                                    {

                                        //$('#myModal').modal('show')
                                        // self.imageModal = new ui.dialog({
                                        //     id: 'image-modal',
                                        //     width: 740,
                                        //     height: 350,
                                        //     overflowY: 'auto',
                                        //     showTitle: false,
                                        // });
                                        // self.imageModal.show();

                                        //   var button = $(event.relatedTarget) // Button that triggered the modal
                                        //   var recipient = button.data('whatever') // Extract info from data-* attributes
                                        //   
                                        //   var modal = $(this)
                                        //   modal.find('.modal-title').text('New message to ' + recipient)
                                        //   modal.find('.modal-body input').val(recipient)
                                        // })
                                        // var modal = $(this)
                                        // modal.find('.modal-title').text('New message to ' + recipient)
                                        // modal.find('.modal-body input').val(recipient)

                                        var userColor = prompt('Please enter a color');//replace with modal and find out how to do colorpicker
                                        //make sure to include color_picker js color 

                                        // console.log(userColor);
                                        // console.log(that.$el.highcharts());
                                        // console.log(that.$el.highcharts().series[0].data);
                                        that.$el.highcharts().series[0].update({
                                            color: userColor});
                                        
                                    }
                                }
                            }
                        },
                        pie: {
                            allowPointSelect: true,
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: true,
                                format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                            }
                        }
                    },
                    series: [{
                        type: 'pie',
                        name: this.seriesName,
                        data: this.seriesData
                    }]
                };
                this.$el.highcharts(chartOpts);
            }
        });
        return PieChart;
    });