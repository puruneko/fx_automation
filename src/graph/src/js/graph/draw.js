// https://github.com/whawker/react-jsx-highcharts/wiki

import React from 'react'
import Highstock from 'highcharts/highstock'
import boost from 'highcharts/modules/boost'

export default class Draw extends React.Component {

    constructor(props) {
        super(props)
        this.id = 'app'
        this.state = {}
        if (props.graphParam !== undefined) {
            this.state = {
                draw: props.draw,
                points: props.graphParam.points,
                xAxis: props.graphParam.xAxis,
                yAxis: props.graphParam.yAxis,
                ySeries: props.graphParam.ySeries,
            }
        }
        else {
            this.state = {
                draw: 0
            }
        }
        this.highchartUpdate = this.highchartUpdateHandler.bind(this)
    }

    shouldComponentUpdate(nextProps, nextState) {
        // 純粋な値の比較をしてdrawプロパティが変化していたら再描写
        if (nextProps.draw !== this.state.draw) {
            return true
        }
        return false
    }

    render() {
        console.log('---> Draw Render')
        console.log(this.state)
        return (
            <div key={`graph/${this.state.draw}`} style={{position: "relative", height: "100%", width: "100%"}}>
                <div id={this.id} style={{height: "100%", width: "100%", top: 0, right: 0, bottom: 0, left: 0}} />
            </div>
        )
    }

    highchartUpdateHandler() {
        if (this.state.draw != 0) {
            var axisMax = []
            var axisMin = []
            this.state.yAxis.forEach((axis, i) => {
                axisMax.push(0)
                axisMin.push(0)
                if (i >= 2) {
                    this.state.ySeries.forEach((series, j) => {
                        if (series.yAxis == i) {
                            axisMax[i] = Math.max(axisMax[i], Math.max.apply(null, series.data.map((x) => {return x[1] ? x[1] : 0})))
                            axisMin[i] = Math.min(axisMin[i], Math.min.apply(null, series.data.map((x) => {return x[1] ? x[1] : 0})))
                        }
                    })
                }
            })
            console.log("xAxis  ", this.state.xAxis)
            const config = {
                title: {
                        text: 'Sample'
                },
                legend: {
                    enabled: true,
                    align: 'right',
                    verticalAlign: 'top',
                    x: -10,
                    y: 50,
                    floating: true
                },
                series: this.state.ySeries,
                xAxis: this.state.xAxis,
                //xAxis: { ordinal: true, },
                yAxis: this.state.yAxis.map((axis, index) => {
                    if (index < 2) {
                        return axis
                    }
                    else {
                        var axisCopy = axis
                        axisCopy["tickPositioner"] = () => {
                            var dataMax = Math.max(Math.abs(axisMax[index]), Math.abs(axisMin[index]))
                            if (dataMax != 0) {
                                const n = Math.floor(Math.log10(dataMax))
                                return [-1.0, 0.0, 1.0].map((i) => {
                                    var x = (dataMax * i * Math.pow(10, -n) * 1.05)
                                    x = x > 0 ? Math.ceil(x) : Math.floor(x)
                                    x *= Math.pow(10, n)
                                    if (i == 1.0) {console.log(index, dataMax, n, x)}
                                    return x
                                })
                            }
                            else {
                                return [-1.0, 0.0, +1.0]
                            }
                        }
                        return axisCopy
                    }
                }),

                rangeSelector: {
                    enabled: false,
                    verticalAlign: 'top',
                    x: 0,
                    y: 0
                },
                navigator: {
                    enabled: true
                },
                scrollbar: {
                    enabled: true
                },
            }
            Highstock.chart(this.id, config)
        }
        console.log('<--- Draw Render')
    }

    componentDidMount() {
        this.highchartUpdate()
    }

    componentDidUpdate() {
        this.highchartUpdate()
    }

    componentWillUnmount() {
        delete this.state
    }
}
