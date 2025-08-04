<template>
  <div class="min-h-screen relative bg-gradient-to-br from-black via-gray-900 to-purple-900 text-white p-8 overflow-x-hidden">
    <!-- 背景光圈 -->
    <div class="absolute -top-40 -left-40 w-[400px] h-[400px] bg-pink-400 blur-3xl opacity-20 rounded-full animate-ping"></div>
    <div class="absolute bottom-0 right-0 w-[300px] h-[300px] bg-cyan-400 blur-3xl opacity-20 rounded-full animate-pulse"></div>

    <h1 class="text-4xl font-extrabold text-center text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-pink-500 to-cyan-400 drop-shadow-lg mb-8">
      ✨ 美团门店转化 ✨
    </h1>

    <!-- 上传区域 -->
    <div class="flex justify-center">
      <el-upload
        class="upload-block neon-border"
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

    <!-- 所有门店汇总 -->
    <div
      v-if="summary"
      class="mt-10 bg-white/5 backdrop-blur-md rounded-2xl p-6 shadow-2xl ring-1 ring-white/10 transition hover:scale-[1.01]"
    >
      <h2 class="text-2xl font-bold text-cyan-400 mb-6 text-center">📊 所有门店汇总</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- 推广数据 -->
        <div>
          <h3 class="text-lg font-semibold text-pink-400 mb-2">📢 推广数据</h3>
          <ul class="space-y-1 text-sm">
            <li v-for="(val, key) in summary['推广数据']" :key="key" class="flex justify-between">
              <span class="text-gray-300">{{ key }}</span>
              <span class="text-white font-medium">{{ format(key, val) }}</span>
            </li>
          </ul>
        </div>
        <!-- 流出数据 -->
        <div>
          <h3 class="text-lg font-semibold text-yellow-400 mb-2">🔄 流出 - 新客</h3>
          <ul class="space-y-1 text-sm">
            <li v-for="(val, key) in summary['流出-新客']" :key="key" class="flex justify-between">
              <span class="text-gray-300">{{ key }}</span>
              <span class="text-white font-medium">{{ format(key, val) }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 每个点评来源门店列表（两列） -->
    <div v-if="stores.length" class="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-8">
      <div
        v-for="store in stores"
        :key="store['点评来源']"
        class="bg-white/5 backdrop-blur-md rounded-2xl p-6 shadow-2xl ring-1 ring-white/10 transition hover:scale-[1.03] hover:shadow-cyan-400/50 cursor-pointer"
      >
        <h2 class="text-xl font-bold text-lime-400 mb-4 select-none">🏪 {{ store['点评来源'] }}</h2>

        <!-- 推广数据 -->
        <div>
          <h3 class="text-base font-semibold text-pink-400 mb-2">📢 推广数据</h3>
          <ul class="space-y-1 text-sm">
            <li v-for="(val, key) in store['推广数据']" :key="key" class="flex justify-between">
              <span class="text-gray-300">{{ key }}</span>
              <span class="text-white font-medium">{{ format(key, val) }}</span>
            </li>
          </ul>
        </div>

        <div class="border-t border-white/20 my-3"></div>

        <!-- 流出 - 新客 -->
        <div>
          <h3 class="text-base font-semibold text-yellow-400 mb-2">🔄 流出 - 新客</h3>
          <ul class="space-y-1 text-sm">
            <li v-for="(val, key) in store['流出-新客']" :key="key" class="flex justify-between">
              <span class="text-gray-300">{{ key }}</span>
              <span class="text-white font-medium">{{ format(key, val) }}</span>
            </li>
          </ul>
        </div>

        <div class="border-t border-white/20 my-3"></div>

        <!-- 投产比 -->
        <div>
          <h3 class="text-base font-semibold text-cyan-400 mb-2">💹 投产比</h3>
          <ul class="space-y-1 text-sm">
            <li v-for="(val, key) in store['投产比']" :key="key" class="flex justify-between">
              <span class="text-gray-300">{{ key }}</span>
              <span class="text-white font-medium">{{ format(key, val) }}</span>
            </li>
          </ul>
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
    const res = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/MTStoreInvertView/`,
      formData
    );
    if (res.data.code === 2000) {
      stores.value = res.data.data.data;
      summary.value = res.data.data["所有门店汇总"];
    } else {
      ElMessage.error(res.data.msg || "分析失败");
    }
  } catch (err) {
    ElMessage.error("请求失败");
  } finally {
    loading.value = false;
  }
};

// 这里给所有“率”字段添加百分号，数字统一保留两位小数
const format = (key, val) => {
  if (val === null || val === undefined) return "";
  if (typeof val === "number") {
    const fixed = val.toFixed(2);
    if (key.includes("率")) {
      return `${fixed}%`;
    }
    return fixed;
  }
  // 处理字符串类型数字
  if (!isNaN(parseFloat(val))) {
    const fixed = parseFloat(val).toFixed(2);
    if (key.includes("率")) {
      return `${fixed}%`;
    }
    return fixed;
  }
  return val;
};
</script>

<style scoped>
.upload-block {
  background-color: rgba(255, 255, 255, 0.03);
  border: 2px dashed #7c3aed;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  color: #ddd;
  width: 340px;
  transition: all 0.3s ease;
}
.upload-block:hover {
  border-color: #a78bfa;
  background-color: rgba(255, 255, 255, 0.05);
}
.neon-border {
  box-shadow: 0 0 15px #a78bfa;
}
</style>
