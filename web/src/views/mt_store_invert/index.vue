<template>
  <div class="min-h-screen bg-gradient-to-br from-white via-sky-50 to-blue-100 text-gray-800 p-8 overflow-x-hidden">
    <h1 class="text-4xl font-extrabold text-center text-blue-600 drop-shadow mb-8">
      ✨ 美团门店转化 ✨
    </h1>

    <!-- 上传 -->
    <div class="flex justify-center">
      <el-upload
        class="upload-block bright-border"
        drag
        multiple
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".xlsx, .xls"
      >
        <div class="el-upload__text">拖拽或点击上传 3 个 Excel 文件</div>
      </el-upload>
    </div>

    <div class="flex justify-center mt-4">
      <el-button type="primary" :loading="loading" @click="analyzeData" :disabled="files.length < 3">
        {{ loading ? '分析中...' : '开始分析' }}
      </el-button>
    </div>

    <!-- 汇总 -->
    <div v-if="summary" class="mt-10 bg-white rounded-2xl p-6 shadow-lg hover:scale-[1.01] transition">
      <h2 class="text-2xl font-bold text-blue-600 mb-6 text-center">📊 所有门店汇总</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <SummaryBlock title="📢 推广数据" color="text-orange-500" :data="summary['推广数据']" />
        <SummaryBlock title="🔄 流出 - 新客" color="text-green-500" :data="summary['流出-新客']" />
      </div>
    </div>

    <!-- 门店数据 -->
    <div v-if="stores.length" class="mt-10 grid grid-cols-1 md:grid-cols-2 gap-8">
      <div v-for="store in stores" :key="store['点评来源']"
           class="bg-white rounded-2xl p-6 shadow-lg hover:scale-[1.03] transition">
        <h2 class="text-xl font-bold text-blue-500 mb-4">🏪 {{ store['点评来源'] }}</h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <DataBlock title="📢 推广数据" color="text-orange-500" :data="store['推广数据']" />
          <DataBlock title="🔄 流出 - 新客" color="text-green-500" :data="store['流出-新客']" />
          <DataBlock title="💹 投产比" color="text-cyan-500" :data="store['投产比']" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import { ElMessage } from "element-plus";

const files = ref([]);
const stores = ref([]);
const summary = ref(null);
const loading = ref(false);

const handleFileChange = (uploadFile) => {
  files.value = uploadFile.raw ? [uploadFile.raw, ...files.value] : uploadFile;
};

const analyzeData = async () => {
  if (files.value.length < 3) {
    ElMessage.warning("请上传完整的三个文件");
    return;
  }
  loading.value = true;
  const formData = new FormData();
  files.value.forEach((file) => formData.append("files", file));

  try {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/MTStoreInvertView/`, formData);
    if (res.data.code === 2000) {
      stores.value = res.data.data.data;
      summary.value = res.data.data["所有门店汇总"];
    } else {
      ElMessage.error(res.data.msg || "分析失败");
    }
  } catch {
    ElMessage.error("请求失败");
  } finally {
    loading.value = false;
  }
};
</script>

<script>
export default {
  components: {
    SummaryBlock: {
      props: ["title", "color", "data"],
      methods: {
        format(key, val) {
          if (val === null || val === undefined) return "";
          if (!isNaN(parseFloat(val))) {
            const fixed = parseFloat(val).toFixed(2);
            if (key.includes("率") || key.includes("比")) {
              return `${fixed}%`;
            }
            return fixed;
          }
          return val;
        },
        valueClass(key, val) {
          if (key.includes("客单价") && !isNaN(parseFloat(val))) {
            return parseFloat(val) >= 3500 ? "text-green-500" : "text-red-500";
          }
          return "text-gray-900";
        }
      },
      template: `
        <div>
          <h3 :class="['text-lg','font-semibold',color,'mb-2']">{{ title }}</h3>
          <ul class="space-y-1 text-sm">
            <li v-for="(val, key) in data" :key="key" class="flex justify-between">
              <span class="text-gray-600">{{ key }}</span>
              <span :class="[valueClass(key, val),'font-medium']">{{ format(key, val) }}</span>
            </li>
          </ul>
        </div>
      `
    },
    DataBlock: {
      props: ["title", "color", "data"],
      methods: {
        format(key, val) {
          if (val === null || val === undefined) return "";
          if (!isNaN(parseFloat(val))) {
            const fixed = parseFloat(val).toFixed(2);
            if (key.includes("率") || key.includes("比")) {
              return `${fixed}%`;
            }
            return fixed;
          }
          return val;
        },
        valueClass(key, val) {
          if (key.includes("客单价") && !isNaN(parseFloat(val))) {
            return parseFloat(val) >= 3500 ? "text-green-500" : "text-red-500";
          }
          return "text-gray-900";
        }
      },
      template: `
        <div class="bg-gray-50 rounded-xl p-4 shadow-sm">
          <h3 :class="['text-base','font-semibold',color,'mb-2']">{{ title }}</h3>
          <ul class="space-y-1 text-sm">
            <li v-for="(val, key) in data" :key="key" class="flex justify-between">
              <span class="text-gray-600">{{ key }}</span>
              <span :class="[valueClass(key, val),'font-medium']">{{ format(key, val) }}</span>
            </li>
          </ul>
        </div>
      `
    }
  }
}
</script>

<style scoped>
.upload-block {
  background-color: rgba(255, 255, 255, 0.7);
  border: 2px dashed #3b82f6;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  color: #1f2937;
  width: 340px;
  transition: all 0.3s ease;
}
.upload-block:hover {
  border-color: #2563eb;
  background-color: rgba(219, 234, 254, 0.85);
}
.bright-border {
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.6);
}
</style>
