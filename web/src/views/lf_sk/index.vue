<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">水卡统计 - 出纳结算单上传</h1>
    
    <!-- 文件选择 -->
    <input type="file" @change="handleFileUpload" accept=".xlsx" class="mb-2" />

    <!-- 按钮区域 -->
    <div class="flex space-x-2 mb-4">
      <button 
        @click="uploadFile" 
        class="p-2 bg-blue-500 text-white rounded disabled:bg-blue-300"
        :disabled="isLoading || !file"
      >
        {{ isLoading ? '正在上传...' : '上传并分析' }}
      </button>
      <button 
        @click="clearResults" 
        class="p-2 bg-red-500 text-white rounded disabled:bg-red-300"
        :disabled="!results"
      >
        清空结果
      </button>
    </div>

    <!-- 上传进度条 -->
    <div v-if="isLoading" class="w-full bg-gray-200 rounded-full h-4 mb-4">
      <div 
        class="bg-blue-500 h-4 rounded-full transition-all" 
        :style="{ width: uploadProgress + '%' }"
      ></div>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" :class="{'text-green-600': messageType === 'success', 'text-red-600': messageType === 'error'}" class="mb-4">
      {{ message }}
    </div>

    <!-- 统计结果 -->
    <div v-if="results">
      <h2 class="text-xl font-bold mt-4">统计结果</h2>
      <div v-for="(data, name) in results" :key="name" class="mt-4 p-4 bg-white rounded shadow">
        <h3 class="font-bold text-lg mb-2">{{ name }}</h3>
        
        <!-- 原订单开单人（醒目显示） -->
        <div v-if="data['原订单开单人']" class="mb-4 p-3 border-2 border-yellow-400 bg-yellow-100 rounded">
          <span class="font-bold text-lg text-yellow-700">原订单开单人：</span>
          <span class="text-yellow-700">{{ data['原订单开单人'] }}</span>
        </div>

        <!-- 项目/商品/药品名称统计表 -->
        <div class="mb-4">
          <h4 class="font-bold mt-2">项目/商品/药品名称统计:</h4>
          <table class="table-auto border-collapse w-full mt-2 mb-4 text-sm text-gray-700">
            <thead>
              <tr class="bg-gray-100">
                <th class="border px-4 py-2">名称</th>
                <th class="border px-4 py-2">数量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(count, product) in data['项目/商品/药品名称统计']" :key="product">
                <td class="border px-4 py-2">{{ product }}</td>
                <td class="border px-4 py-2 text-center">{{ count }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 所属套餐统计表 -->
        <div>
          <h4 class="font-bold mt-2">所属套餐统计:</h4>
          <table class="table-auto border-collapse w-full mt-2 text-sm text-gray-700">
            <thead>
              <tr class="bg-gray-100">
                <th class="border px-4 py-2">套餐名称</th>
                <th class="border px-4 py-2">数量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(count, packageName) in data['所属套餐统计']" :key="packageName">
                <td class="border px-4 py-2">{{ packageName }}</td>
                <td class="border px-4 py-2 text-center">{{ count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';

const file = ref<File | null>(null);
const results = ref<any>(null);
const isLoading = ref(false);
const uploadProgress = ref(0);
const message = ref('');
const messageType = ref<'success' | 'error'>('success');

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    file.value = target.files[0];
  }
};

const uploadFile = async () => {
  if (!file.value) {
    alert('请先选择一个文件！');
    return;
  }
  isLoading.value = true;
  uploadProgress.value = 0;
  message.value = '';

  const formData = new FormData();
  formData.append('file', file.value);

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/LFSKViewSet/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        }
      }
    });

    results.value = response.data?.data?.data || null;
    message.value = '文件上传并分析成功！';
    messageType.value = 'success';
  } catch (error) {
    message.value = '文件上传或处理出错！';
    messageType.value = 'error';
  }

  isLoading.value = false;
};

const clearResults = () => {
  results.value = null;
  message.value = '';
  uploadProgress.value = 0;
};
</script>

<style scoped>
body {
  font-family: Arial, sans-serif;
}
</style>
