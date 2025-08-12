<template>
  <div class="container mx-auto p-6 max-w-6xl space-y-6 bg-white rounded-2xl shadow-lg">
    <div class="text-center mb-6">
      <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-purple-500 animate-pulse">
        靓范最强咨询师排行
      </h1>
    </div>

    <!-- 文件上传 -->
    <div class="mb-6 flex items-center space-x-4">
      <input
        type="file"
        multiple
        accept=".xlsx"
        @change="handleFileChange"
        class="border rounded p-2 w-2/3"
      />
      <button
        @click="handleUpload"
        :disabled="isLoading || files.length !== 2"
        class="bg-blue-500 text-white p-2 rounded hover:bg-blue-600 transition duration-300"
      >
        上传并分析
      </button>
    </div>

    <div class="mb-6">
      <p v-if="isLoading" class="text-blue-500 mt-2">上传中，请稍等...</p>
      <p v-if="message" :class="messageType === 'error' ? 'text-red-500' : 'text-green-500'" class="mt-2">
        {{ message }}
      </p>
    </div>

    <!-- 排名展示 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="(ranking, key) in rankings"
        :key="key"
        class="bg-gray-50 p-4 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 border border-gray-200"
      >
        <h2 class="text-xl font-semibold text-gray-700 mb-4 text-center">{{ ranking.title }}</h2>
        <table class="w-full border border-gray-300 rounded-lg shadow-sm overflow-hidden">
          <thead>
            <tr class="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-sm">
              <th class="border p-3">排名</th>
              <th class="border p-3">咨询师姓名</th>
              <th v-for="column in ranking.columns" :key="column" class="border p-3">{{ column }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(consultant, index) in ranking.data"
              :key="index"
              class="transition-colors duration-200 hover:bg-gray-100 text-center"
              :class="getRankClass(index)"
            >
              <td class="border p-2 font-semibold">{{ index + 1 }}</td>
              <td class="border p-2">{{ consultant.咨询师 }}</td>
              <td v-for="column in ranking.columns" :key="column" class="border p-2">
                {{ consultant[column] }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import axios from 'axios';

const consultants = ref<any[]>([]);
const isLoading = ref(false);
const files = ref<File[]>([]);
const message = ref('');
const messageType = ref<'success' | 'error' | null>(null);

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files) {
    const selectedFiles = Array.from(input.files);

    // 确保选中两个 .xlsx 文件
    if (selectedFiles.length !== 2 || selectedFiles.some(file => !file.name.endsWith('.xlsx'))) {
      message.value = '❌ 请选择两个有效的 Excel 文件 (.xlsx)';
      messageType.value = 'error';
      files.value = [];
      return;
    }

    files.value = selectedFiles;
    message.value = '✅ 文件选择成功！';
    messageType.value = 'success';
  }
};

const handleUpload = async () => {
  if (files.value.length !== 2) {
    message.value = '❌ 请先选择两个文件';
    messageType.value = 'error';
    return;
  }

  isLoading.value = true;
  message.value = '';
  const formData = new FormData();
  files.value.forEach(file => formData.append('files', file));

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/LFCustomerActivityView/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    consultants.value = response.data?.data?.data || [];
    message.value = '✅ 文件上传并分析成功！';
    messageType.value = 'success';
  } catch (error) {
    message.value = '❌ 上传失败，请重试。';
    messageType.value = 'error';
  } finally {
    isLoading.value = false;
  }
};

// **排名数据**
const rankings = computed(() => [
  {
    title: "顾客活跃度排名",
    columns: ["老客到院人数", "顾客总数不含E类", "顾客活跃度"],
    data: [...consultants.value].sort((a, b) => b.顾客活跃度 - a.顾客活跃度),
  },
  {
    title: "老客业绩排名",
    columns: ["老客业绩"],
    data: [...consultants.value].sort((a, b) => b.老客业绩 - a.老客业绩),
  },
  {
    title: "老客客单价排名",
    columns: ["老客客单价"],
    data: [...consultants.value].sort((a, b) => b.老客客单价 - a.老客客单价),
  },
  {
    title: "老客成交率排名",
    columns: ["老客成交人数", "老客到院人数", "老客成交率"],
    data: [...consultants.value].sort((a, b) => parseFloat(b.老客成交率) - parseFloat(a.老客成交率)),
  },
  {
    title: "初复诊业绩排名",
    columns: ["初复诊业绩"],
    data: [...consultants.value].sort((a, b) => b.初复诊业绩 - a.初复诊业绩),
  },
  {
    title: "初复诊客单价排名",
    columns: ["初复诊客单价"],
    data: [...consultants.value].sort((a, b) => b.初复诊客单价 - a.初复诊客单价),
  },
  {
    title: "初复诊成交率排名",
    columns: ["初复诊成交人数", "初复诊到院人数", "初复诊成交率"],
    data: [...consultants.value].sort((a, b) => parseFloat(b.初复诊成交率) - parseFloat(a.初复诊成交率)),
  },
  {
    title: "老带新业绩排名",
    columns: ["老带新业绩"],
    data: [...consultants.value].sort((a, b) => b.老带新业绩 - a.老带新业绩),
  },
  {
    title: "老带新客单价排名",
    columns: ["老带新客单价"],
    data: [...consultants.value].sort((a, b) => b.老带新客单价 - a.老带新客单价),
  },
  {
    title: "老带新成交率排名",
    columns: ["老带新成交人数", "老带新到院人数", "老带新成交率"],
    data: [...consultants.value].sort((a, b) => parseFloat(b.老带新成交率) - parseFloat(a.老带新成交率)),
  }
]);


// **前三名颜色标识**
const getRankClass = (index: number) => {
  if (index === 0) return "bg-red-200 font-bold text-red-600"; // 🥇 第一名（红色）
  if (index === 1) return "bg-blue-200 font-bold text-blue-600"; // 🥈 第二名（蓝色）
  if (index === 2) return "bg-yellow-200 font-bold text-yellow-600"; // 🥉 第三名（黄色）
  return ""; // 其他名次无特殊颜色
};
</script>

<style scoped>
.container {
  font-family: Arial, sans-serif;
  background-color: #f9fafb;
}

button:disabled {
  background-color: #d1d5db;
  cursor: not-allowed;
}

table {
  border-collapse: collapse;
  width: 100%;
}

th, td {
  padding: 12px;
  text-align: center;
}

th {
  background-color: #4c51bf;
  color: white;
}

td {
  border: 1px solid #ddd;
}

tr:hover {
  background-color: #f1f1f1;
}

/* **排名展示部分** */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); /* 控制一行2个 */
  gap: 1.5rem;
}
</style>
