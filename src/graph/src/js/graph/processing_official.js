
// ↓ defined at HTML on global
import Highcharts from 'highcharts'//'highcharts/highstock'
import Highstock from 'highcharts/highstock'
import React from 'react'
import HighchartsReact from 'highcharts-react-official'
import Papa from 'papaparse'y

export default class Processing extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            path: props.path,
            config: {},
        }
        const promise = this.createHighchartsConfig()
        promise.then((config) => {
            this.setState({config: config})
        })
    }

    createHighchartsConfig() {
        const promise = new Promise((resolve, reject) => {
            var config = {}
            $.get( this.state.path )
            .done( function(rawData) {
                console.log(rawData)
            //$.getJSON('https://www.highcharts.com/samples/data/aapl-ohlcv.json', function (data) {

                // split the data set into ohlc and volume
                /*var ohlc = [],
                    volume = [],
                    dataLength = data.length,*/
                    // set the allowed units for data grouping
                var dummy1 = []
                var dummy2 = []
                var groupingUnits = [[
                        'week',                         // unit name
                        [1]                             // allowed multiples
                    ], [
                        'month',
                        [1, 2, 3, 4, 6]
                    ]]
                var subplot_number = 0
                var yAxis = []
                var ySeries = []

                const get_params = (key) => {
                    var result = {
                        title: '',
                        settings: {}
                    }
                    var m = /^(.+?)[{](.*?)[}].*?/.exec(key)
                    result.title = m[0]
                    m[1].split(',').forEach( (keyvalue, index) => {
                        var sp = keyvalue.split(':')
                        result.settings[sp[0]] = sp[1]
                    })
                    if (!('display' in result.settings)) {
                        result.settings['display'] =  ''
                    }
                    if (!('position' in result.settings)) {
                        result.settings['position'] =  '0'
                    }
                    return result
                }

                console.log('--> csv loading start')
                var csv = Papa.parse(rawData, {
                    delimiter: ','
                })
                console.log('<-- csv loading end')
                console.log('--> chart object creating start')
                csv.data.forEach( (line, itr_row) => {
                    if (itr_row == 0) {
                        // ySeriesの初期化
                        ySeries.push({
                            type: 'candlestick',
                            name: 'MainChart',
                            data: [],
                            dataGrouping: {
                                units: groupingUnits
                            }
                        })
                        for (var itr_col = 6; itr_col < line.length; itr_col++){
                            if (line[itr_col] == 'blank') {
                                break
                            }
                            var params = get_params(line[itr_col])
                            subplot_number = Math.max([subplot_number, parseInt(params.settings['position'])])
                            ySeries.push({
                                //type: 'line',
                                name: params.title,
                                data: [],
                                yAxis: parseInt(params.settings['position']),
                                visible: params.settings['display'] == 'false' ? false : true,
                                dataGrouping: {
                                    units: groupingUnits
                                }
                            })
                        }
                        // subplotの数を計算
                        subplot_number = 0
                        // yAxisの初期化
                        yAxis.push({
                            labels: {
                                align: 'right',
                                x: -3
                            },
                            title: {
                                text: 'OHLC'
                            },
                            height: `${100/(4+subplot_number)*4}%`,
                            lineWidth: 2,
                            resize: {
                                enabled: true
                            }
                        })
                        for (var sub_no = 1; sub_no <= subplot_number; sub_no++){
                            yAxis.push({
                                labels: {
                                    align: 'right',
                                    x: -3
                                },
                                title: {
                                    text: `subplot[${sub_no+1}]`
                                },
                                top: '65%',
                                height: '35%',
                                offset: 0,
                                lineWidth: 2
                            })
                        }
                    }
                    else {
                        var date = new Date(line[0])
                        ySeries[0].data.push([
                            date, // the date
                            parseFloat(line[1]), // open
                            parseFloat(line[2]), // high
                            parseFloat(line[3]), // low
                            parseFloat(line[4]) // close
                        ])
                        dummy1.push([
                            date, // the date
                            parseFloat(line[1]), // open
                            parseFloat(line[2]), // high
                            parseFloat(line[3]), // low
                            parseFloat(line[4]) // close
                        ])
                        dummy2.push([
                            date, // the date
                            parseFloat(line[5]) // the volume
                        ])
                        for (var i = 1; i < ySeries.length; i++) {
                            ySeries[i].data.push([
                                date,
                                parseFloat(line[i + 6 - 1])
                            ])
                        }
                    }
                    ///////
                    if (itr_row > 10) {
                        return true
                    }
                    else {
                        console.log(line[0])
                    }
                })
                console.log('<-- chart object creating end')
                
                console.log('--> chart setting start')
                // create the chart
                //Highcharts.stockChart('container', {
                config = {

                    rangeSelector: {
                        selected: 1
                    },

                    title: {
                        text: 'AAPL Historical'
                    },

                    yAxis: /*yAxis,*/[{
                        labels: {
                            align: 'right',
                            x: -3
                        },
                        title: {
                            text: 'OHLC'
                        },
                        height: '60%',
                        lineWidth: 2,
                        resize: {
                            enabled: true
                        }
                    }, {
                        labels: {
                            align: 'right',
                            x: -3
                        },
                        title: {
                            text: 'Volume'
                        },
                        top: '65%',
                        height: '35%',
                        offset: 0,
                        lineWidth: 2
                    }],

                    tooltip: {
                        split: true
                    },

                    series: /*ySeries,*/[{
                        type: 'candlestick',
                        name: 'AAPL',
                        data: dummy1,
                        dataGrouping: {
                            units: groupingUnits
                        }
                    }, {
                        //type: 'column',
                        name: 'Volume',
                        data: dummy2,
                        yAxis: 1,
                        dataGrouping: {
                            units: groupingUnits
                        }
                    }]
                }
                console.log('<-- chart setting end')
                resolve(config)
            })
            .fail( function () {
                console.error(`${this.state.path} open failed.`)
                resolve({})
            })
        })
        return promise
    }

    render() {
        console.log(this.state.config)
        return (
            <HighchartsReact highcharts={Highstock} options={this.state.config} />
        )
    }
}