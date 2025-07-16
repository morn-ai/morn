import * as echarts from "echarts";
export const chartLineOptions: echarts.EChartsOption = {
  grid: {
    left: 40,
    top: 40,
    bottom: 20,
    right: 20,
    containLabel: true,
  },
  legend: {
    show: true,
  },
  tooltip: {
    show: true,
    trigger: "axis",
  },
  xAxis: {
    type: "category",
    boundaryGap: false,
    data: [],
  },
  yAxis: {
    type: "value",
  },
  series: [],
};

export const chartPieOptions: echarts.EChartsOption = {
  // title: {
  //   text: 'Referer of a Website',
  //   subtext: 'Fake Data',
  //   left: 'center'
  // },
  tooltip: {
    trigger: "item",
  },
  legend: {
    orient: "vertical",
    left: "right",
  },
  label: {
    show: true,
    formatter: "{b}\n{d}%",
  },
  series: [
    {
      type: "pie",
      radius: "50%",
      data: [
        { value: 1048, name: "Search Engine" },
        { value: 735, name: "Direct" },
        { value: 580, name: "Email" },
        { value: 484, name: "Union Ads" },
        { value: 300, name: "Video Ads" },
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: "rgba(0, 0, 0, 0.5)",
        },
      },
    },
  ],
};

export const chartBarOptions = {
  grid: {
    left: 40,
    top: 40,
    bottom: 20,
    right: 20,
  },
  tooltip: {
    show: true,
  },
  legend: {
    show: true,
  },
  xAxis: {
    type: "category",
    data: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  },
  yAxis: {
    type: "value",
  },
  label: {
    show: true,
    position: "top",
  },
  series: [
    {
      data: [120, 200, 150, 80, 70, 110, 130],
      type: "bar",
    },
  ],
};

export const chartScatterOptions = {
  xAxis: {
    type: "category",
  },
  yAxis: {},
  // series: [
  //   {
  //     symbolSize: 20,
  //     data: [
  //       [10.0, 8.04],
  //       [8.07, 6.95],
  //       [13.0, 7.58],
  //       [9.05, 8.81],
  //       [11.0, 8.33],
  //       [14.0, 7.66],
  //       [13.4, 6.81],
  //       [10.0, 6.33],
  //       [14.0, 8.96],
  //       [12.5, 6.82],
  //       [9.15, 7.2],
  //       [11.5, 7.2],
  //       [3.03, 4.23],
  //       [12.2, 7.83],
  //       [2.02, 4.47],
  //       [1.05, 3.33],
  //       [4.05, 4.96],
  //       [6.03, 7.24],
  //       [12.0, 6.26],
  //       [12.0, 8.84],
  //       [7.08, 5.82],
  //       [5.02, 5.68],
  //     ],
  //     type: 'scatter',
  //   },
  // ],
};
