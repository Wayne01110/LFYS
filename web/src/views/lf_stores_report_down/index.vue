<template>
  <div class="report-container">
    <h2 class="title">门店报表导出</h2>

    <!-- 咨询接诊记录时间选择，仅在需要时显示 -->
    <transition name="fade">
      <div v-if="showDatePicker" class="date-picker">
        <label>起始日期：</label>
        <input type="date" v-model="startTime" />
        <label>结束日期：</label>
        <input type="date" v-model="endTime" />
        <button class="confirm-btn" @click="confirmDownload">确认导出</button>
      </div>
    </transition>

    <!-- 按钮区域 -->
    <div class="button-group">
      <button :disabled="loading" @click="handleClientAsset">📊 客户资产保有统计</button>
      <button :disabled="loading" @click="handleConsultation">📋 咨询接诊记录</button>
    </div>

    <!-- 加载提示 -->
    <div v-if="loading" class="loading">
      <p>生成中，请稍候...</p>
      <progress max="100" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 状态管理
const loading = ref(false)
const showDatePicker = ref(false)
const startTime = ref('')
const endTime = ref('')
const baseURL = `${import.meta.env.VITE_API_URL}/api/LFStoresReportDown/`

// 下载 blob 文件
const downloadBlobFile = async (url, payload, filename) => {
  loading.value = true
  try {
    const response = await axios.post(url, payload, {
      responseType: 'blob'
    })

    const blob = new Blob([response.data])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)
  } catch (e) {
    alert('导出失败：' + (e.response?.data || e.message))
  } finally {
    loading.value = false
    showDatePicker.value = false
  }
}

// 客户资产按钮
const handleClientAsset = () => {
  showDatePicker.value = false
  downloadBlobFile(baseURL, { action: 'client_asset' }, '客户资产保有统计.xlsx')
}

// 咨询按钮（仅显示日期选择）
const handleConsultation = () => {
  showDatePicker.value = true
  startTime.value = ''
  endTime.value = ''
}

// 确认导出咨询记录
const confirmDownload = () => {
  if (!startTime.value || !endTime.value) {
    alert('请选择起止时间')
    return
  }
  downloadBlobFile(
    baseURL,
    {
      action: 'consultation_admission',
      startTime: startTime.value,
      endTime: endTime.value
    },
    '咨询接诊记录.xlsx'
  )
}
</script>

<style scoped>
.report-container {
  padding: 50px 30px;
  max-width: 600px;
  margin: auto;
  text-align: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f7f9fc;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.title {
  font-size: 28px;
  margin-bottom: 30px;
  color: #333;
}

.date-picker {
  margin-bottom: 25px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.confirm-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background-color: #10b981;
  border: none;
  border-radius: 5px;
  color: white;
  font-weight: bold;
  cursor: pointer;
}
.confirm-btn:hover {
  background-color: #059669;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 20px;
}

button {
  padding: 12px 24px;
  font-size: 16px;
  background-color: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

button:hover {
  background-color: #3730a3;
}

button:disabled {
  background-color: #a5b4fc;
  cursor: not-allowed;
}

.loading p {
  margin-bottom: 10px;
  color: #555;
}

progress {
  width: 240px;
  height: 18px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
