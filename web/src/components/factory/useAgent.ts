import { marked } from "marked";
import { nextTick, onMounted, reactive, ref } from "vue";

const excludes = ["开始调用工具", "工具ID", "工具执行错误"];
async function getData(input: string, thread_id: string) {
  let partialText = "";
  // 判断partialText中接下来是一个 Block 的起始位置
  let blockStartIndex = -1;

  /**
   * 从 partialText 中解析是否含有Block
   */
  function parsePartialText(blocks: any[]) {
    if (blockStartIndex === -1) {
      let textIndex = partialText.indexOf('{"type": "text"');
      let chartIndex = partialText.indexOf('{"type": "chart"');
      if (textIndex !== -1) {
        blockStartIndex = textIndex;
      }
      if (chartIndex !== -1) {
        blockStartIndex = chartIndex;
      }
    }
    if (blockStartIndex !== -1) {
      let subText = partialText.slice(blockStartIndex);

      let eventMessageIndex = subText.indexOf("event: message");
      let pingIndex = subText.indexOf(": ping");
      let endIndex = -1;
      if (eventMessageIndex !== -1) {
        endIndex = eventMessageIndex;
      }
      if (pingIndex !== -1) {
        endIndex = pingIndex;
      }
      if (endIndex !== -1) {
        try {
          const tempstr = partialText
            .slice(blockStartIndex, blockStartIndex + endIndex)
            .trim();

          blocks.push(JSON.parse(tempstr));
          partialText = partialText.slice(blockStartIndex + endIndex);
          // 处理一个message 多个type
          blockStartIndex = -1;
          parsePartialText(blocks);
        } catch (error) {}
      }
    }
  }
  const token = localStorage.getItem("access_token");
  const response = await fetch("/v5/8abffd416c89454bb526aecca2d7fd9e/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      thread_id,
      input,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  if (!response.body) {
    throw new Error("ReadableStream not supported in this browser.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let blocks: any[] = [];

  while (true) {
    const { done, value } = await reader.read();

    if (done) {
      break;
    }

    buffer = decoder.decode(value, { stream: true });
    partialText += buffer;

    const dataList = buffer
      .split("event: message")
      .map((item) => item.replace(/^[\r\n]*data: /, ""));
    dataList.forEach((item) => {
      parsePartialText(blocks);
    });
  }
  const result: any[] = [];
  blocks.forEach((t: any, index) => {
    const text = t?.text_content?.text;
    if (
      t.type === "text" &&
      !text.includes("[DONE]") &&
      excludes.every((str) => !text.includes(str))
    ) {
      t.text_content.text = marked.parse(text);
      result.push(t);
    }
    if (t.type === "chart") {
      t.id = `${new Date().getTime()}-${Math.random()}`;
      result.push(t);
    }
  });
  return result;
}

async function readEventStream2() {
  const result = await getData(
    `
          从事件记录表中统计模型ID:chip-mounter（贴片机）下每个设备的故障次数，将最终结果可视化为饼图, 饼图之前返回一个故障统计的标题
    统计策略：
        1、先查询chip-mounter（贴片机）模型下面所有的设备ID，分页参数limit=100
        2、将chip-mounter（贴片机）中的每个设备ID作为主键ID ，在eve_chip_mounter_reading_illegal表中进行故障统计，分页参数limit=1，统计只需要从返回的结果中获取count即可，可视化为饼图
    要求：
        1、禁止统计完毕后生成base64图片编码
        2、禁止生成结果后引导或者询问客户进行下一步操作
        3、最后做出总结
    `,
    `test-session-${Math.random()}`
  );
  return result;
}

async function readEventStream1() {
  const result = await getData(
    `
    首先查询工厂有多少条产线， 从视图中获取，结果强制用表格展示
    利用工具：list_views -> get_view -> query_view_nodes
    然后执行以下步骤：
    前提：第一步已经执行完毕，你已经找到了有哪些产线
    任务：从第一步获取到的产线中通过query_view_nodes（参数的node_id为第一步查询出的产线对应的node_id) 工具查询每个产线视图下有多少个实例（设备），可视化为柱状图
    要求：不必调用list_things
  要求：
  1、禁止统计完毕后生成base64图片编码
  2、禁止生成结果后引导或者询问客户进行下一步操作
  3、最后做出总结`,
    `test-session-${Math.random()}`
  );
  return result;
}

export { readEventStream1, readEventStream2 };
