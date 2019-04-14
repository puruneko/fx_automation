// https://github.com/whawker/react-jsx-highcharts/wiki


// ↓ defined at HTML on global
import Highcharts from 'highcharts'//'highcharts/highstock'
import Highstock from 'highcharts/highstock'
import React from 'react'
import {
  HighchartsStockChart, Chart, withHighcharts, XAxis, YAxis, Title, Legend,
  AreaSplineSeries, CandlestickSeries, SplineSeries, Navigator, RangeSelector, Tooltip, Boost,
} from 'react-jsx-highstock'

const th = 100000
Highcharts.plotOptions = {
  series: {
    threashold: th,
    turboThreashold: th
  }
}

class Processing extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
          points: props.graphParam.points,
          axis: props.graphParam.axis,
          series: props.graphParam.series,
        }
    }
    render() {
      const createDataPoint = (time = Date.now(), magnitude = 1000, offset = 0) => {
        return [
          time + offset * magnitude,
          Math.round((Math.random() * 100) * 2) / 2
        ];
      };
    
      const createRandomData = (time, magnitude, points = 100) => {
        const data = [];
        let i = (points * -1) + 1;
        for (i; i <= 0; i++) {
          data.push(createDataPoint(time, magnitude, i));
          }
          return data;
      }
      const now = Date.now()
      const {dummy1, dummy2} = this.state.series
      console.log(this.state)
      return (
        <div className="app">
          <HighchartsStockChart>

            <Chart zoomType="x" />
  
            <Title>Highstocks Example</Title>
  
            <Legend>
              <Legend.Title>Key</Legend.Title>
            </Legend>
  
            <RangeSelector>
              <RangeSelector.Button count={1} type="day">1d</RangeSelector.Button>
              <RangeSelector.Button count={7} type="day">7d</RangeSelector.Button>
              <RangeSelector.Button count={1} type="month">1m</RangeSelector.Button>
              <RangeSelector.Button type="all">All</RangeSelector.Button>
              <RangeSelector.Input boxBorderColor="#7cb5ec" />
            </RangeSelector>
  
            <Tooltip />
  
            <XAxis>
              <XAxis.Title>Time</XAxis.Title>
            </XAxis>
  
            <YAxis>
              <YAxis.Title>Price</YAxis.Title>
              <CandlestickSeries id="profit" name="Profit" data={dummy1} />
            </YAxis>
  
            <YAxis opposite>
              <YAxis.Title>Social Buzz</YAxis.Title>
              <SplineSeries id="twitter" name="Twitter mentions" data={dummy2} />
            </YAxis>
  
            <Navigator>
              <Navigator.Series seriesId="profit" />
              <Navigator.Series seriesId="twitter" />
            </Navigator>
          </HighchartsStockChart>
        </div>
      )
    }
}

export default withHighcharts(Processing, Highstock);
