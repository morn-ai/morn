<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from "vue";
import * as echarts from "echarts";
import {
  chartBarOptions,
  chartLineOptions,
  chartPieOptions,
  chartScatterOptions,
} from "./constants";
import { marked } from "marked";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";

const { blocks } = defineProps(["blocks"]);

function renderLine(selector: string, content: any) {
  let chart: echarts.ECharts;
  const el = document.getElementById(selector);
  chart = echarts.init(el);
  const option: any = chartLineOptions;
  option.xAxis.data = content.labels;
  option.series = content.datasets.map((item: any) => {
    return { type: "line", name: item.label, smooth: true, data: item.data };
  });
  chart.setOption(option);
}

function renderPie(selector: any, content: any) {
  let chart: echarts.ECharts;
  const el = document.getElementById(selector);
  chart = echarts.init(el);
  const option: any = chartPieOptions;
  option.series[0].name = content.datasets?.[0]?.label;
  option.series[0].data = content.labels.map((item: any, index: number) => {
    return {
      value: content.datasets?.[0]?.data[index],
      name: item,
    };
  });
  chart.setOption(option);
}

function renderBar(selector: any, content: any) {
  let chart: echarts.ECharts;
  const el = document.getElementById(selector);
  chart = echarts.init(el);
  const option: any = chartBarOptions;
  option.xAxis.data = content.labels;
  option.series = content.datasets.map((item: any) => {
    return {
      type: "bar",
      name: item.label,
      data: item.data,
    };
  });
  chart.setOption(option);
}

function renderScatter(selector: string, content: any) {
  let chart: echarts.ECharts;
  const el = document.getElementById(selector);
  chart = echarts.init(el);
  const option: any = chartScatterOptions;
  option.series = content.datasets.map((item: any) => {
    return {
      symbolSize: 10,
      type: "scatter",
      data: item.data.map((itemd: any, index: number) => {
        return [content.labels[index], itemd];
      }),
    };
  });
  chart.setOption(option);
}

function render(
  type: "table" | "line" | "pie" | "bar" | "scatter",
  selector: string,
  data: any
) {
  const fn: any = {
    line: () => renderLine(selector, data),
    pie: () => renderPie(selector, data),
    bar: () => renderBar(selector, data),
    scatter: () => renderScatter(selector, data),
  };

  return fn[type]();
}

async function rederPromise(blocks: any) {
  for (const block of blocks) {
    if (block.type === "chart") {
      setTimeout(async () => {
        render(block.chart_content.chart_type, block.id, block?.chart_content);
      });
    }
  }
}

onMounted(() => {
  marked.use(
    markedHighlight({
      langPrefix: "hljs language-",
      highlight(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : "plaintext";
        return hljs.highlight(code, { language }).value;
      },
    })
  );

  console.log(blocks, "@@@@@@@@@");

  nextTick().then(() => {
    rederPromise(blocks);
  });
});
</script>

<template>
  <div>
    <div v-for="block in blocks">
      <div
        class="table-wrapper"
        v-if="block.type === 'text'"
        v-html="block.text_content.text"
      ></div>
      <div v-if="block.type === 'chart'" class="chart" :id="block.id"></div>
    </div>
  </div>
</template>

<style scoped lang="less">
.chart {
  height: 240px;
  width: 100%;
  margin: 16px 0;
}

/* 表格容器 */
:deep(*) {
  .table-wrapper {
    overflow-x: auto;
    /* 表格样式 */
    table {
      width: 100%;
      border-collapse: collapse;
      border-spacing: 0;
      margin-top: 12px;
    }

    th,
    td {
      padding: 0.75rem;
      border: 1px solid #ddd;
      text-align: left;
    }
    thead tr {
      background-color: #fff !important;
    }

    /* 斑马纹 */
    tr:nth-child(odd) {
      background-color: #fcfcfc;
    }

    /* 悬停效果 */
    tr:hover {
      background-color: #f1f1f1;
    }
  }
}

:deep(pre) {
  code.hljs {
    display: block;
    overflow-x: auto;
    padding: 1em;
  }
  code.hljs {
    padding: 3px 5px;
  }
  .hljs {
    color: #383a42;
    background: #fafafa;
  }
  .hljs-comment,
  .hljs-quote {
    color: #a0a1a7;
    font-style: italic;
  }
  .hljs-doctag,
  .hljs-keyword,
  .hljs-formula {
    color: #a626a4;
  }
  .hljs-section,
  .hljs-name,
  .hljs-selector-tag,
  .hljs-deletion,
  .hljs-subst {
    color: #e45649;
  }
  .hljs-literal {
    color: #0184bb;
  }
  .hljs-string,
  .hljs-regexp,
  .hljs-addition,
  .hljs-attribute,
  .hljs-meta .hljs-string {
    color: #50a14f;
  }
  .hljs-attr,
  .hljs-variable,
  .hljs-template-variable,
  .hljs-type,
  .hljs-selector-class,
  .hljs-selector-attr,
  .hljs-selector-pseudo,
  .hljs-number {
    color: #986801;
  }
  .hljs-symbol,
  .hljs-bullet,
  .hljs-link,
  .hljs-meta,
  .hljs-selector-id,
  .hljs-title {
    color: #4078f2;
  }
  .hljs-built_in,
  .hljs-title.class_,
  .hljs-class .hljs-title {
    color: #c18401;
  }
  .hljs-emphasis {
    font-style: italic;
  }
  .hljs-strong {
    font-weight: bold;
  }
  .hljs-link {
    text-decoration: underline;
  }
}
</style>
