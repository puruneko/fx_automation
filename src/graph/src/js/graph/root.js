import React from 'react'
import Papa from 'papaparse'
import Drawer from '@material-ui/core/Drawer'
import Button from '@material-ui/core/Button'
import Input from '@material-ui/core/Input'
import InputBase from '@material-ui/core/InputBase'
import InputLabel from '@material-ui/core/InputLabel'
import Divider from '@material-ui/core/Divider'
import ExpandMoreIcon from '@material-ui/icons/ExpandMore'

import Draw from './draw'
import { List, ListItem, Select, MenuItem, TextField, Checkbox, Tooltip, ExpansionPanel, ExpansionPanelSummary, ExpansionPanelDetails, Typography } from '@material-ui/core';

export default class Root extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            draw: 0,
            drawer: false,
            fileName: 'C:/Users/Ryutaro/Dropbox/prog/git/github/fx_automation/src/realtime/tradeHistory.csv',
            start: 0,
            end: 1000,
            mainSectionCoef: 4,
            subplot_number_max: 3,
            graphParam: {
                points: 0,
                yAxis: [],
                ySeries: [],
                importParams: {},
                subplot_number: 0,
            },
        }
        this.toggleDrawerOpen = this.toggleDrawerOpenHandler.bind(this)
        this.toggleDrawerClose = this.toggleDrawerCloseHandler.bind(this)
        this.onSubmit = this.handleSubmit.bind(this)
        this.onDiscardGraph = this.handleDicardGraph.bind(this)
        this.onRedrawGraph = this.handleRedrawGraph.bind(this)
        this.onChangeSelector = this.handleChangeSelector.bind(this)
        this.onChangeCheckbox = this.handleChangeCheckbox.bind(this)
        this.createHighchartsConfig = this.createHighchartsConfigHandler.bind(this)
    }
    toggleDrawerOpenHandler() {
        this.setState({drawer: true})
    }
    toggleDrawerCloseHandler() {
        this.setState({drawer: false})
    }
    handleChangeSelector(event) {
        var graphParam = this.state.graphParam
        graphParam.ySeries[parseInt(event.target.name)].yAxis = parseInt(event.target.value)
        console.log(`handleChangeSelector: [${event.target.name}]  ${graphParam.ySeries[parseInt(event.target.name)].yAxis}`)
        this.setState({graphParam: graphParam})
    }
    handleChangeCheckbox(event) {
        var graphParam = this.state.graphParam
        console.log(`handleChangeCheckbox: [${event.target.name}]  ${graphParam}`)
        graphParam.ySeries[parseInt(event.target.name)].visible = event.target.checked
        this.setState({graphParam: graphParam})
    }
    handleSubmit(event) {
        console.log('---> clicked process')
        // 要素の値の取得
        var filename = document.getElementById('fileName').value
        const params = {
            fileName: filename ? filename : this.state.fileName,
            start: parseInt(document.getElementById('start').value),
            end: parseInt(document.getElementById('end').value),
            mainSectionCoef: parseInt(document.getElementById('mainSectionCoef').value),
        }
        // グラフの描画
        const promise = this.createHighchartsConfig(params)
        promise.then( (res) => {
            console.log('<--- clicked process')
            this.setState({
                draw: this.state.draw + 1,
                graphParam: res,
                // do not forget blow!
                fileName: params.fileName,
                start: params.start,
                end: params.end,
                mainSectionCoef: params.mainSectionCoef,
            })
        })
    }
    handleDicardGraph(event) {
        this.setState({draw: 0, graphParam: {mainSectionCoef: 4} })
    }
    handleRedrawGraph(event) {
        this.setState({
            draw: this.state.draw + 1
        })
    }
    createHighchartsConfigHandler(visualParams, graphParams) {
        const {fileName, start, end, mainSectionCoef} = visualParams
        console.log(`load CSV --->${fileName}`)
        console.log(`load ${start} <= itr < ${end}`)
    
        // ヘッダー文字のオプション部分を抜き出して辞書化
        const get_params = (key) => {
            var result = {
                title: '',
                settings: {}
            }
            var m = /^(.+?)[{](.*?)[}].*?/.exec(key)
            const unused = m[0]
            result.title = m[1]
            m[2].split(',').forEach( (keyvalue, index) => {
                var sp = keyvalue.split(':')
                result.settings[sp[0]] = sp[1]
            })
            if (!('display' in result.settings)) {
                result.settings['display'] = ''
            }
            if (!('position' in result.settings)) {
                result.settings['position'] = '0'
            }
            if (!('oppositeAxis' in result.settings)) {
                result.settings['oppositeAxis'] = "false"
            }
            return result
        }
        // NaNがあったらnullにするparseFloat
        const toFloat = (f) => {
            if (f == 'nan' || f == 'NaN'){
                return null
            }
            else {
                return parseFloat(f)
            }
        }
        
        // データを読み込んでコンフィグ作るまで待つ用のPromise
        const promise = new Promise((resolve, reject) => {
            $.get( fileName )
            .done( function(rawData) {
                const groupingUnits = [
                    [
                        'week',                         // unit name
                        [1]                             // allowed multiples
                    ], [
                        'month',
                        [1, 2, 3, 4, 6]
                    ]
                ]
                var points = 0
                var subplot_number = 0
                var yAxis = []
                var ySeries = []
    
                console.log('--> csv loading start')
                var csv = Papa.parse(rawData, {
                    delimiter: ','
                })
                console.log('<-- csv loading end')
                console.log('--> chart object creating start')
                csv.data.forEach( (line, itr_row) => {
                    // ヘッダーの処理
                    if (itr_row == 0) {
                        // ySeriesの初期化
                        ySeries.push({
                            type: 'candlestick',
                            name: 'OHLC',
                            data: [],
                            yAxis: 0,
                            visible: true,
                            dataGrouping: {
                                units: groupingUnits
                            },
                        })
                        for (var itr_col = 6; itr_col < line.length; itr_col++){
                            if (line[itr_col] == 'blank') {
                                break
                            }
                            var params = get_params(line[itr_col])
                            var marker = {enabled: false}
                            if (params.title.match(/TradeRecordTable/)) {
                                const size = 9
                                if (params.title.match(/long/)) {
                                    marker = {
                                        enabled: true,
                                        symbol: 'triangle',
                                        fillColor: '#EA1A47',
                                        lineColor: '#EA1A47',
                                        lineWidth: 0,
                                        radius: size,
                                    }
                                }
                                else if (params.title.match(/short/)) {
                                    marker = {
                                        enabled: true,
                                        symbol: 'triangle-down',
                                        fillColor: '#4647CC',
                                        lineColor: '#4647CC',
                                        lineWidth: 0,
                                        radius: size,
                                    }
                                }
                                else if (params.title.match(/release/)) {
                                    marker = {
                                        enabled: true,
                                        symbol: 'circle',
                                        fillColor: '#11A23C',
                                        lineColor: '#11A23C',
                                        lineWidth: 0,
                                        radius: size,
                                    }
                                }
                            }
                            ySeries.push({
                                //type: 'line',
                                name: params.title,
                                data: [],
                                yAxis: parseInt(params.settings['position'])*2 + (params.settings['oppositeAxis'] == 'true' ? 1 : 0),
                                visible: params.settings['display'] == 'false' ? false : true,
                                marker: marker,
                                dataGrouping: {
                                    units: groupingUnits
                                }
                            })
                            subplot_number = Math.max(subplot_number, parseInt(params.settings['position']))
                        }
                        console.log('subplot_number=',subplot_number)
                        // yAxisの初期化
                        const parSection = 100/(mainSectionCoef+subplot_number)
                        const margin = 2
                        let mainYAxisConfig = {
                            labels: {
                                align: 'right',
                                x: -3
                            },
                            title: {
                                text: 'OHLC'
                            },
                            height: `${parSection*mainSectionCoef - margin}%`,
                            lineWidth: 2,
                            resize: {
                                enabled: true
                            },
                            grid: {
                                enabled: true,
                            },
                            opposite: false,
                        }
                        var mainYAxisFoward = {}
                        Object.assign(mainYAxisFoward, mainYAxisConfig)
                        yAxis.push(mainYAxisFoward)
                        var mainYAxisOpposite = {}
                        Object.assign(mainYAxisOpposite, mainYAxisConfig)
                        mainYAxisOpposite.opposite = true
                        yAxis.push(mainYAxisOpposite)

                        for (var sub_no = 1; sub_no <= subplot_number; sub_no++){
                            let subYAxisConfig = {
                                labels: {
                                    align: 'right',
                                    x: -3
                                },
                                title: {
                                    text: `subplot[${sub_no}]`
                                },
                                top: `${parSection*(mainSectionCoef+(sub_no-1)) + margin}%`,
                                height: `${parSection - margin}%`,
                                offset: 0,
                                lineWidth: 2,
                                grid: {
                                    enabled: true,
                                },
                                opposite: false,
                            }
                            var subYAxisFoward = {}
                            Object.assign(subYAxisFoward, subYAxisConfig)
                            yAxis.push(subYAxisFoward)
                            var subYAxisOpposite = {}
                            Object.assign(subYAxisOpposite, subYAxisConfig)
                            subYAxisOpposite.opposite = true
                            yAxis.push(subYAxisOpposite)
                        }
                    }
                    // データ値の処理
                    else if (start <= itr_row && (itr_row < end || end == -1)) {
                        points += 1
                        var date = new Date(line[0])
                        ySeries[0].data.push([
                            date, // the date
                            toFloat(line[1]),
                            toFloat(line[2]),
                            toFloat(line[3]),
                            toFloat(line[4])
                        ])
                        for (var i = 1; i < ySeries.length; i++) {
                            ySeries[i].data.push([
                                date,
                                toFloat(line[i + 6 - 1])
                            ])
                        }
                    }
                })
                console.log('<-- chart object creating end')
    
                resolve({points: points, yAxis: yAxis, ySeries: ySeries, subplot_number: subplot_number})
            })
            .fail( function () {
                console.error(`${path} open failed.`)
                resolve({})
            })
        })
        return promise
    }

    render() {
        console.log('---> Root Render')
        console.log(this.state)
        const wrapperStyle = {
            position: "absolute",
            height: "100%",
            width: "100%",
            maxHeight: "100%",
            maxWidth: "100%",
            top: 0,
            right: 0,
            bottom: 0,
            left: 0,
        }
        const headerHeight = "40px"
        return (
        <div style={wrapperStyle}>
            <header style={{position: "absolute", height: headerHeight, width: "100%", backgroundColor: "#4169e1"}}>
                <Button variant="outlined" onClick={this.toggleDrawerOpen}> Menu </Button>
            </header>
            <div style={{position: "absolute", top: {headerHeight}, height: `calc(95% - ${headerHeight})`, width: "95%", right: 0, bottom: 0, left: 0}}>
                <Draw key={this.state.draw} draw={this.state.draw} graphParam={this.state.graphParam} />
            </div>
            <Drawer
                anchor="left"
                open={this.state.drawer}
                onClose={this.toggleDrawerClose}
                
            >
                <div style={{width: "40vw"}}>
                    <ExpansionPanel>
                        <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>Load Graph Panel</Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            <form action="javascript:void(0)" onSubmit={this.onSubmit}>
                                <List>
                                    <ListItem>
                                        <Button type="submit" variant="outlined"> Load Graph </Button>
                                    </ListItem>
                                    <ListItem style={{display: "flex", flexWrap:"nowrap"}}>
                                        <input
                                            accept="*.csv"
                                            id="fileName"
                                            type="file"
                                            hidden
                                        />
                                        <InputLabel htmlFor="fileButton" style={{flexGrow: 1}}>File : </InputLabel>
                                        <Button id="fileButton" component="span">
                                            {`...${this.state.fileName.slice(-25)}`}
                                        </Button>
                                    </ListItem>
                                    <ListItem style={{display: "flex", flexWrap:"nowrap"}}>
                                        <InputLabel htmlFor="start" style={{flexGrow: 1}}>Start : </InputLabel>
                                        <Input id="start" defaultValue={this.state.start} />
                                    </ListItem>
                                    <ListItem style={{display: "flex", flexWrap:"nowrap"}}>
                                        <InputLabel htmlFor="end" style={{flexGrow: 1}}>End : </InputLabel>
                                        <Input id="end" defaultValue={this.state.end} />
                                    </ListItem>
                                    <ListItem style={{display: "flex", flexWrap:"nowrap"}}>
                                        <InputLabel htmlFor="mainSectionCoef" style={{flexGrow: 1}}>Main Height : </InputLabel>
                                        <Input id="mainSectionCoef" defaultValue={this.state.mainSectionCoef} />
                                    </ListItem>
                                </List>
                            </form>
                        </ExpansionPanelDetails>
                    </ExpansionPanel>
                    <Divider />
                    <ExpansionPanel>
                        <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>Update Graph Panel</Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            {
                                this.state.graphParam.ySeries ?
                                (
                                    <div>
                                        <List disablePadding={true}>
                                            <ListItem>
                                                <Button variant="outlined" onClick={this.onRedrawGraph}> Update Graph </Button>
                                            </ListItem>
                                            {
                                                this.state.graphParam.ySeries.map((series, i) => {
                                                    return (
                                                        <ListItem key={`list${i}`} style={{display: "flex", justifyContent:"space-around", flexWrap:"nowrap"}}>
                                                            <Tooltip title="Indicator Name" placement="top">
                                                                <InputLabel htmlFor={`list${i}/Select`} style={{flexGrow: 1}}>{series.name}</InputLabel>
                                                            </Tooltip>
                                                            <Tooltip title="Y Axis Number (odd -> opposite axis)" placement="top">
                                                                <Select
                                                                    id={`list${i}/Select`}
                                                                    value={series.yAxis}
                                                                    onChange={this.onChangeSelector}
                                                                    inputProps={{name: `${i}`}}
                                                                    style={{marginLeft: "5px"}}
                                                                >
                                                                    {
                                                                        Array.apply(null, {length: (this.state.subplot_number_max+1)*2}).map(Number.call, Number).map((j) => {
                                                                            var label = `${j < 2 ? "Main" : `Sub${Math.floor(j/2)}` } ${j % 2 != 0 ? "[opp]" : "[fwd]"}`
                                                                            return (
                                                                                <MenuItem key={`list${i}/item${j}`} value={`${j}`}>{label}</MenuItem>
                                                                            )
                                                                        })
                                                                    }
                                                                </Select>
                                                            </Tooltip>
                                                            <Tooltip title="Visible" placement="top">
                                                                <Checkbox id={`list${i}/Checkbox`} checked={series.visible} inputProps={{name: `${i}`}} onChange={this.onChangeCheckbox}/>
                                                            </Tooltip>
                                                        </ListItem>
                                                    )
                                                })
                                            }
                                        </List>
                                    </div>
                                ) : <div></div>
                            }
                        </ExpansionPanelDetails>
                    </ExpansionPanel>
                    <ExpansionPanel>
                        <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography>Discard Graph Panel</Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            <Button variant="outlined" onClick={this.onDiscardGraph}> Discard Graph </Button>
                        </ExpansionPanelDetails>
                    </ExpansionPanel>
                </div>
            </Drawer>
        </div>
        )
    }
    componentDidMount() {
        console.log('<--- Root Render')
    }
    componentDidUpdate() {
        console.log('<--- Root Render')
    }
}