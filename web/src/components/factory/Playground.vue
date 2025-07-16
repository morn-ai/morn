<script setup lang="ts">
import { onMounted, ref, nextTick, reactive } from "vue";
import {
  NButton,
  type DrawerPlacement,
  NDrawer,
  NDrawerContent,
  NAlert,
  NCard,
  NTabs,
  NTabPane,
  NImage,
  NModal,
} from "naive-ui";
import {
  Circle,
  CubicHorizontal,
  ExtensionCategory,
  Graph,
  NodeEvent,
  register,
  subStyleProps,
} from "@antv/g6";
import Overview from "./Overview.vue";

import printerImg from "../../assets/printer.jpg";
import aoiImg from "../../assets/aoi.jpg";
import chipMounterImg from "../../assets/chip-mounter.jpg";
import routerImg from "../../assets/router.jpg";
import reflowOvenImg from "../../assets/reflow-oven.jpg";
import spiImg from "../../assets/spi.jpg";
import warnImg from "../../assets/warn.jpg";
import flowImg from "../../assets/flow.png";
import { readEventStream1, readEventStream2 } from "./useAgent";

let graph1: any = null;
let graph2: any = null;
let graph3: any = null;

class FlyMarkerCubic extends CubicHorizontal {
  getMarkerStyle(attributes: any) {
    return {
      fill: "blue",
      size: 14,
      // y: 50,
      offsetPath: this.shapeMap.key,
      ...subStyleProps(attributes, "marker"),
    };
  }

  onCreate() {
    const marker: any = this.upsert(
      "marker",
      Circle,
      this.getMarkerStyle(this.attributes),
      this
    );
    marker.animate([{ offsetDistance: 0 }, { offsetDistance: 1 }], {
      duration: 3000,
      iterations: Infinity,
    });
  }
}

const currDevice = ref<any>();

function bindEvents(graph: any) {
  graph.on(NodeEvent.CLICK, (evt: any) => {
    const { target } = evt;
    const nodeData = graph.getNodeData(target.id);
    const reason = nodeData.data.reason;
    if (reason) {
      currDevice.value = nodeData;
      activate("right");
    }
  });
}

const nodes: any[] = [
  {
    id: "loader",
    data: {
      deviceId: "loader",
      deviceName: "上板机",
      img: printerImg,
      role: "将PCB板从料架或堆叠中自动取出并精准传送到后续工序",
    },
  },
  {
    id: "printer",
    data: {
      deviceId: "printer",
      deviceName: "锡膏印刷机",
      img: printerImg,
      role: "将锡膏精确地印刷到PCB板的焊盘上，为后续的元件贴装做准备",
    },
  },
  {
    id: "spi",
    data: {
      deviceId: "spi",
      deviceName: "锡膏检测仪（SPI）",
      img: spiImg,
      role: "检测锡膏印刷后的质量，确保焊盘上的锡膏厚度、体积、形状和位置符合要求，从而减少焊接缺陷，提高产品良率",
    },
  },
  {
    id: "chip-mounter",
    data: {
      deviceId: "chip-mounter",
      deviceName: "贴片机",
      img: chipMounterImg,
      role: "将电子元器件精准贴装到PCB板的焊盘上，完成电路组装的关键工序",
      // faultClass: "bg-red-700 text-white!",
      // reason: "设备chip-mounter-01异常"
    },
  },
  {
    id: "aoi_1",
    data: {
      deviceId: "aoi",
      deviceName: "自动光学检测仪（AOI）",
      img: aoiImg,
      role: "通过光学成像和图像分析技术，自动检测PCB组装过程中的各种缺陷，确保产品质量",
    },
  },
  {
    id: "reflow-oven",
    data: {
      deviceId: "reflow-oven",
      deviceName: "回流焊炉",
      img: reflowOvenImg,
      role: "通过精确控制的加热过程将锡膏熔化，使电子元件与PCB焊盘形成可靠的电气和机械连接",
    },
  },
  {
    id: "aoi_2",
    data: {
      deviceId: "aoi",
      deviceName: "自动光学检测仪（AOI）",
      img: aoiImg,
      role: "通过光学成像和图像分析技术，自动检测PCB组装过程中的各种缺陷，确保产品质量",
    },
  },
  {
    id: "router",
    data: {
      deviceId: "router",
      deviceName: "分板机",
      img: routerImg,
      role: "将拼板（Panel）形式的PCB分割成单个独立的单元板，同时确保分割过程不会对PCB和元器件造成损伤",
    },
  },
];

const edge = {
  type: "fly-marker-cubic",
  style: {
    lineDash: [10, 10],
    stroke: "blue",
    lineWidth: 2,
  },
};

function initGraph(id: string) {
  const graph = new Graph({
    container: id,
    data: {
      nodes: nodes,
      edges: [
        { source: "loader", target: "printer" },
        { source: "printer", target: "spi" },
        { source: "spi", target: "chip-mounter" },
        { source: "chip-mounter", target: "aoi_1" },
        { source: "aoi_1", target: "reflow-oven" },
        { source: "reflow-oven", target: "aoi_2" },
        { source: "aoi_2", target: "router" },
      ],
    },
    edge: edge,
    node: {
      type: "html",
      style: {
        size: [260, 80],
        innerHTML: (d) => {
          const {
            data: {
              deviceId,
              deviceName,
              faultClass,
              reason,
              img,
              role,
              argsHTML,
            },
          } = d;
          return `
            <div class="bg-white rounded-md pl-4 pr-4 pt-2 pb-2 shadow-2xl shadow-indigo-500/40 border-indigo-500/50 relative ${faultClass}">
              <img [data-reason]="${reason}" class="w-6 h-6 absolute top-2 right-2 cursor-pointer animate-ping" src="${warnImg}" style="display: ${
            reason ? "block" : "none"
          }"/>
              <div class="mb-2 block device-name font-bold text-lg">${deviceName}</div>
              <div class="mt-2 text-base text-current">${role}</div>
              <img src="${img}"/>
              <div class="">
                ${argsHTML || ""}
              </div>
            </div>
          `;
        },
      },
    },
    layout: {
      type: "snake",
      cols: 4,
      colGap: 160,
      rowGap: 320,
    },
    behaviors: ["drag-canvas", "drag-element"],
  });
  graph.render();

  bindEvents(graph);
  return graph;
}

const currProudctLine = ref(1);

const reqFlag = ref(false);
onMounted(() => {
  register(ExtensionCategory.EDGE, "fly-marker-cubic", FlyMarkerCubic);
  graph1 = initGraph("productLine1");

  window.addEventListener("message", (event) => {
    if (event.data === "showChat") {
      frameStyle.width = "640px";
      frameStyle.height = "640px";
    } else if (event.data === "hideChat") {
      frameStyle.width = "100px";
      frameStyle.height = "100px";
    } else if (event.data === "fullScreen") {
      frameStyle.width = "50vw";
      frameStyle.height = "100vh";
    } else if (event.data === "notFullScreen") {
      frameStyle.width = "640px";
      frameStyle.height = "640px";
    }
  });
});

function handleUpdateValue(value: number) {
  currProudctLine.value = value;
  nextTick().then(() => {
    if (value === 1) {
      graph1 = initGraph("productLine1");
    }
    if (value === 2) {
      graph2 = initGraph("productLine2");
    }
    if (value === 3) {
      graph3 = initGraph("productLine3");
    }
  });
}

async function check() {
  nodes.forEach((node) => {
    node.data.faultClass = "animate-pulse";
  });
  graph1.updateNodeData(nodes);
  graph1.draw();
  setTimeout(() => {
    nodes.forEach((node: any) => {
      if (node.id === "chip-mounter") {
        node.data.faultClass = "bg-red-700! text-white!";
        node.data.reason = "设备 chip-mounter-1-01(贴片机) 异常";
      } else {
        node.data.faultClass = "bg-gray-300!";
      }
    });
    graph1.updateNodeData(nodes);
    edge.style.stroke = "rgb(209,213,219)";
    edge.type = "line";
    graph1.setEdge(edge);
    graph1.draw();
  }, 2000);
}

function reset() {
  nodes.forEach((node: any) => {
    node.data.faultClass = "";
    node.data.reason = "";
  });
  graph1.updateNodeData(nodes);
  edge.style.stroke = "blue";
  edge.type = "fly-marker-cubic";
  graph1.setEdge(edge);
  graph1.draw();
}

const active = ref(false);
const active2 = ref(false);
const placement = ref<DrawerPlacement>("right");

const activate = (place: DrawerPlacement) => {
  active.value = true;
  placement.value = place;
};

function openAgent() {
  active.value = false;
  postMessage(currDevice.value.data.reason);
}

const showModal = ref(false);
const modalLoading = ref(false);
let blocks = reactive<any[]>([]);
async function showModalBox() {
  if (modalLoading.value) return;
  blocks.length = 0;
  // emit("postMessage", "工厂整体状况");
  modalLoading.value = true;
  Promise.all([readEventStream1(), readEventStream2()]).then(
    ([result1, result2]) => {
      blocks.push(...result1, ...result2);
      nextTick().then(() => {
        modalLoading.value = false;
        showModal.value = true;
      });
    }
  );
}

function postMessage(msg) {
  const iframe: any = document.getElementById("agent");
  iframe.contentWindow.postMessage(msg, "*");
}

const frameStyle = reactive({
  width: "100px",
  height: "100px",
  position: "fixed",
  bottom: 0,
  right: 0,
});

const iframeurl =
  import.meta.env.MODE === "development"
    ? "http://localhost:4200"
    : `${window.location.origin}/iiot-agent`;
</script>

<template>
  <div class="playground relative">
    <div class="content">
      <div class="flex align-middle mt-4">
        <div class="text-white pl-16 font-bold mb-2 text-lg">SMT 工厂:</div>
        <n-image width="240" class="ml-8!" :src="flowImg" />
        <n-button
          type="warning"
          :loading="modalLoading"
          class="ml-8!"
          @click="showModalBox()"
        >
          {{ modalLoading ? "分析中" : "一键分析" }}
        </n-button>
        <n-button type="info" class="ml-8!" @click="check()">
          故障检测
        </n-button>
      </div>
      <div class="fixed! z-10">
        <n-button
          :type="currProudctLine === 1 ? 'error' : 'info'"
          class="block! mt-4!"
          @click="handleUpdateValue(1)"
        >
          产线 1
        </n-button>
        <n-button
          :type="currProudctLine === 2 ? 'error' : 'info'"
          class="block! mt-4!"
          @click="handleUpdateValue(2)"
        >
          产线 2
        </n-button>
        <n-button
          :type="currProudctLine === 3 ? 'error' : 'info'"
          class="block! mt-4!"
          @click="handleUpdateValue(3)"
        >
          产线 3
        </n-button>
      </div>
      <div
        id="productLine1"
        v-if="currProudctLine === 1"
        class="productLine"
      ></div>
      <div
        id="productLine2"
        v-if="currProudctLine === 2"
        class="productLine"
      ></div>
      <div
        id="productLine3"
        v-if="currProudctLine === 3"
        class="productLine"
      ></div>

      <n-drawer v-model:show="active" :width="502" :placement="placement">
        <n-drawer-content :title="currDevice.data.deviceName">
          <n-alert title="故障原因" type="error">
            设备 chip-mounter-1-01(贴片机) 发生故障
          </n-alert>
          <n-alert
            title="和小哞对话寻找具体的故障原因"
            type="info"
            class="mt-4"
          >
            <n-button type="info" class="mg-4" @click="openAgent()">
              点击和小哞进行对话
            </n-button>
          </n-alert>
        </n-drawer-content>
      </n-drawer>
    </div>

    <n-modal v-model:show="showModal">
      <n-card
        style="width: 1000px"
        title="工厂概况"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <Overview :blocks="blocks"></Overview>
      </n-card>
    </n-modal>
  </div>
  <iframe
    :src="iframeurl"
    frameborder="0"
    id="agent"
    :style="frameStyle"
  ></iframe>
</template>

<style scoped lang="less">
.playground {
  width: 100vw;
  height: 100vh;
  background: url("../assets/factory.jpg") 100%/100% repeat-y;
  overflow: hidden;
  .flow {
    height: 200px;
    position: relative;
    img {
      width: 50%;
      margin: 0 auto;
    }
  }
  .content {
    height: 100vh;
    overflow: hidden;
    #productLine {
      height: 100%;
    }
    .productLine {
      height: 2000px;
      width: 100%;
    }
    :deep(.n-card-header) {
      padding-bottom: 0;
    }
    :deep(.n-card-header__main) {
      color: #fff;
      font-weight: bold;
    }
    :deep(.n-tabs-tab__label) {
      color: blue;
      font-size: 16px;
    }
  }
  :deep(.bg-red-700\! .text-red-400) {
    color: #ffffff !important;
  }
}
</style>
