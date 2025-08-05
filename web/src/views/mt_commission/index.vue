<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white p-8 font-sans relative overflow-x-hidden">
    <!-- 背景光圈 -->
    <div class="absolute -top-40 -left-40 w-[400px] h-[400px] bg-pink-400 blur-3xl opacity-20 rounded-full animate-pulse"></div>

    <!-- 标题 -->
    <h1 class="text-5xl font-extrabold mb-8 text-center drop-shadow-lg">✨ 美团佣金分析 ✨</h1>

    <!-- 上传区域 -->
    <el-upload
      v-model:file-list="fileList"
      drag
      multiple
      :limit="5"
      accept=".xls,.xlsx"
      :auto-upload="false"
      class="mb-8 max-w-3xl mx-auto upload-box"
    >
      <el-icon class="upload-icon"><upload-filled /></el-icon>
      <p class="el-upload__text text-lg mt-4">
        将 Excel 文件拖到此处，或 <em class="text-yellow-400 underline cursor-pointer">点击上传</em>
      </p>
      <p class="el-upload__tip mt-1 text-sm text-gray-400">支持最多5个文件，格式 .xls 或 .xlsx</p>
    </el-upload>

    <!-- 操作按钮 -->
    <div class="flex justify-center mb-10">
      <el-button
        type="gradient"
        size="large"
        :loading="loading"
        :disabled="fileList.length === 0"
        @click="handleSubmit"
        class="shadow-lg"
      >
        查询分析
      </el-button>
    </div>

    <!-- 结果展示 -->
    <div v-if="resultData && resultData.data && resultData.data.length" class="max-w-6xl mx-auto space-y-10">
      <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
      >
        <el-card
          v-for="(item, idx) in resultData.data"
          :key="idx"
          shadow="hover"
          class="bg-gradient-to-br from-purple-900 to-pink-800 rounded-3xl hover:scale-[1.03] transition-transform duration-300"
        >
          <h2 class="text-xl font-bold text-yellow-400 mb-4 truncate">{{ item['验证门店'] }}</h2>
          <ul class="text-white space-y-1">
            <li>标准额度: <span class="font-semibold text-green-400">{{ item['佣金数据']['标准额度'] }}</span></li>
            <li>实付核销金额（不含直播/刷单）: <span class="font-semibold text-cyan-400">{{ item['佣金数据']['实付核销金额（不含直播/刷单）'] }}</span></li>
            <li>差额: <span :class="{'text-red-500': item['佣金数据']['差额'] < 0, 'text-green-400': item['佣金数据']['差额'] >= 0}">
              {{ item['佣金数据']['差额'] }}
            </span></li>
            <li>实际佣金（不含直播/刷单）: <span class="font-semibold text-purple-400">{{ item['佣金数据']['实际佣金（不含直播/刷单）'] }}</span></li>
            <li>广告消耗: <span class="font-semibold text-pink-400">{{ item['佣金数据']['广告消耗'] }}</span></li>
            <li>总消耗: <span class="font-semibold text-red-400">{{ item['佣金数据']['总消耗'] }}</span></li>
            <li>订单量: <span class="font-semibold text-yellow-300">{{ item['佣金数据']['订单量'] }}</span></li>
            <li>门店订单占比: <span class="font-semibold text-green-300">{{ item['佣金数据']['门店订单占比'] }}</span></li>
          </ul>
        </el-card>
      </div>

      <!-- 汇总 -->
      <el-card
        shadow="always"
        class="bg-gradient-to-tr from-indigo-900 via-purple-900 to-pink-900 rounded-3xl max-w-4xl mx-auto p-8 text-white text-center text-2xl font-bold drop-shadow-lg"
      >
        <div class="mb-4">🧾 <span class="underline">所有门店汇总</span></div>
        <el-row :gutter="24" justify="center" align="middle">
          <el-col :span="8" class="py-3">
            标准额度<br />
            <span class="text-green-400 text-3xl">{{ resultData['所有门店汇总']['标准额度'] }}</span>
          </el-col>
          <el-col :span="8" class="py-3">
            实付核销金额（不含直播/刷单）<br />
            <span class="text-cyan-400 text-3xl">{{ resultData['所有门店汇总']['实付核销金额（不含直播/刷单）'] }}</span>
          </el-col>
          <el-col :span="8" class="py-3">
            差额<br />
            <span :class="{'text-red-500': resultData['所有门店汇总']['差额'] < 0, 'text-green-400': resultData['所有门店汇总']['差额'] >= 0}" class="text-3xl">
              {{ resultData['所有门店汇总']['差额'] }}
            </span>
          </el-col>
        </el-row>
        <el-row :gutter="24" justify="center" align="middle" class="mt-6">
          <el-col :span="8" class="py-3">
            实际佣金（不含直播/刷单）<br />
            <span class="text-purple-400 text-3xl">{{ resultData['所有门店汇总']['实际佣金（不含直播/刷单）'] }}</span>
          </el-col>
          <el-col :span="8" class="py-3">
            广告消耗<br />
            <span class="text-pink-400 text-3xl">{{ resultData['所有门店汇总']['广告消耗'] }}</span>
          </el-col>
          <el-col :span="8" class="py-3">
            总消耗<br />
            <span class="text-red-400 text-3xl">{{ resultData['所有门店汇总']['总消耗'] }}</span>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const fileList = ref([])
const loading = ref(false)
const resultData = ref(null)

const handleSubmit = async () => {
  if (!fileList.value.length) {
    ElMessage.warning('请先上传文件')
    return
  }
  loading.value = true
  const formData = new FormData()
  fileList.value.forEach((file) => formData.append('files', file.raw))

  try {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/MTCommissionView/`, formData)
    if (res.data.code === 2000) {
      resultData.value = res.data.data
      ElMessage.success('分析完成 🎉')
    } else {
      ElMessage.error(res.data.msg || '接口返回异常')
    }
  } catch (error) {
    ElMessage.error('分析失败，请检查文件格式和网络')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.upload-box {
  background-color: rgba(255, 255, 255, 0.07);
  border: 3px dashed #a855f7;
  border-radius: 20px;
  padding: 40px 20px;
  text-align: center;
  transition: border-color 0.3s ease;
}
.upload-box:hover {
  border-color: #f43f5e;
}
.upload-icon {
  font-size: 56px;
  color: #d946ef;
  opacity: 0.85;
  transition: color 0.3s ease;
}
.upload-box:hover .upload-icon {
  color: #f43f5e;
}
.el-button[type='gradient'] {
  background: linear-gradient(90deg, #a855f7 0%, #ec4899 100%);
  border: none;
  box-shadow: 0 0 15px #ec4899aa;
  font-weight: 600;
  transition: box-shadow 0.3s ease;
}
.el-button[type='gradient']:hover:not(:disabled) {
  box-shadow: 0 0 30px #f43f5e;
}
</style>
