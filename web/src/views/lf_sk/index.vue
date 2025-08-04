<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">水卡统计 - 文件上传</h1>
    <input type="file" @change="handleFileUpload" accept=".xlsx" class="mb-2" />
    <div class="flex space-x-2 mb-4">
      <button @click="uploadFile" class="p-2 bg-blue-500 text-white rounded">上传并分析</button>
      <button @click="clearResults" class="p-2 bg-red-500 text-white rounded">清空结果</button>
    </div>

    <div v-if="isLoading" class="text-gray-500">文件上传中，请稍候...</div>

    <div v-if="results">
      <h2 class="text-xl font-bold mt-4">统计结果</h2>
      <div v-for="(data, name) in results" :key="name" class="mt-4">
        <h3 class="font-bold">{{ name }}</h3>
        <div class="ml-4">
          <h4 class="font-bold mt-2">项目/商品/药品名称统计:</h4>
          <table class="table-auto border-collapse w-full">
            <thead>
              <tr>
                <th class="border px-4 py-2">名称</th>
                <th class="border px-4 py-2">数量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(count, product) in data['项目/商品/药品名称统计']" :key="product">
                <td class="border px-4 py-2">{{ product }}</td>
                <td class="border px-4 py-2">{{ count }}</td>
              </tr>
            </tbody>
          </table>

          <h4 class="font-bold mt-2">所属套餐统计:</h4>
          <table class="table-auto border-collapse w-full">
            <thead>
              <tr>
                <th class="border px-4 py-2">名称</th>
                <th class="border px-4 py-2">数量</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(count, packageName) in data['所属套餐统计']" :key="packageName">
                <td class="border px-4 py-2">{{ packageName }}</td>
                <td class="border px-4 py-2">{{ count }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ref } from 'vue';

export default {
  setup() {
    const file = ref(null);
    const results = ref(null);
    const isLoading = ref(false);

    const handleFileUpload = (event) => {
      file.value = event.target.files[0];
    };

    const uploadFile = async () => {
      if (!file.value) {
        alert('请先选择一个文件！');
        return;
      }
      isLoading.value = true;
      const formData = new FormData();
      formData.append('file', file.value);

      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/LFSKViewSet/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        results.value = response.data.data;
      } catch (error) {
        alert('文件上传或处理出错！');
      }
      isLoading.value = false;
    };

    const clearResults = () => {
      results.value = null;
    };

    return {
      file,
      results,
      isLoading,
      handleFileUpload,
      uploadFile,
      clearResults
    };
  }
};
</script>

<style>
body {
  font-family: Arial, sans-serif;
}
</style>