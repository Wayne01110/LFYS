<template>
  <div
    class="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-800 to-pink-900 text-white p-6 font-sans relative flex flex-col items-center"
  >
    <!-- 背景光圈 -->
    <div
      class="absolute -top-40 -left-40 w-[450px] h-[450px] bg-pink-500 blur-3xl opacity-25 rounded-full animate-pulse"
      aria-hidden="true"
    ></div>
    <div
      class="absolute -bottom-40 -right-40 w-[500px] h-[500px] bg-blue-500 blur-3xl opacity-20 rounded-full animate-pulse"
      aria-hidden="true"
    ></div>

    <!-- 标题 -->
    <h1
      class="text-5xl font-extrabold mb-8 text-center drop-shadow-2xl select-none text-gradient"
      style="background: linear-gradient(90deg,#ffed4a,#f43f5e,#8b5cf6); -webkit-background-clip: text; color: transparent;"
    >
      ✨ 美团佣金 ✨
    </h1>

    <!-- 上传区域 -->
    <el-upload
      v-model:file-list="fileList"
      drag
      multiple
      :limit="5"
      accept=".xls,.xlsx"
      :auto-upload="false"
      class="mb-10 max-w-4xl mx-auto upload-box"
    >
      <el-icon class="upload-icon"><upload-filled /></el-icon>
      <p class="el-upload__text text-lg mt-4">
        将 Excel 文件拖到此处，或
        <em class="text-yellow-400 underline cursor-pointer">点击上传</em>
      </p>
      <p class="el-upload__tip mt-1 text-sm text-gray-300">
        支持最多5个文件，格式 .xls 或 .xlsx
      </p>
    </el-upload>

    <!-- 查询按钮 -->
    <div class="flex justify-center mb-12">
      <el-button
        type="gradient"
        size="large"
        :loading="loading"
        :disabled="fileList.length === 0"
        @click="handleSubmit"
        class="shadow-2xl"
      >
        查询分析
      </el-button>
    </div>

    <!-- 表格容器 -->
    <div class="w-full max-w-[100vw] overflow-x-auto">
      <div
        ref="tableWrapperRef"
        class="transform origin-top-left"
        :style="{
          transform: `scale(${scale.value})`,
          width: rawTableWidth + 'px',
          margin: '0 auto',
        }"
      >
        <el-table
          :data="tableData"
          border
          stripe
          size="medium"
          :row-class-name="rowClassName"
          style="width: 1340px; background-color: #1c1c2e; border-radius: 12px;"
          :header-cell-style="headerCellStyle"
          :cell-style="cellStyle"
        >
          <el-table-column prop="验证门店" label="验证门店" :min-width="180" fixed />
          <el-table-column prop="佣金数据.标准额度" label="标准额度" :min-width="120" :formatter="formatMoney" />
          <el-table-column
            prop="佣金数据.实付核销金额（不含直播/刷单）"
            label="实付核销金额（不含直播/刷单）"
            :min-width="180"
            :formatter="formatMoney"
          />
          <el-table-column prop="佣金数据.差额" label="差额" :min-width="120" :formatter="formatSignedMoney" />
          <el-table-column
            prop="佣金数据.实际佣金（不含直播/刷单）"
            label="实际佣金（不含直播/刷单）"
            :min-width="180"
            :formatter="formatMoney"
          />
          <el-table-column prop="佣金数据.广告消耗" label="广告消耗" :min-width="120" :formatter="formatMoney" />
          <el-table-column prop="佣金数据.总消耗" label="总消耗" :min-width="120" :formatter="formatMoney" />
          <el-table-column prop="佣金数据.订单量" label="订单量" :min-width="80" :formatter="formatNumber" />
          <el-table-column
            prop="佣金数据.门店订单占比"
            label="门店订单占比"
            :min-width="120"
            :formatter="formatPercent"
          />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const fileList = ref([])
const loading = ref(false)
const resultData = ref(null)

const rawTableWidth = 1340
const scale = ref(1)

const tableData = computed(() => {
  if (!resultData.value) return []
  const list = [...resultData.value.data]
  if (resultData.value['所有门店汇总']) {
    list.push({
      验证门店: '合计',
      佣金数据: resultData.value['所有门店汇总'],
    })
  }
  return list
})

const updateScale = () => {
  const maxW = window.innerWidth
  scale.value = maxW < rawTableWidth ? maxW / rawTableWidth : 1
}

onMounted(() => {
  updateScale()
  window.addEventListener('resize', updateScale)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', updateScale)
})

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

function formatMoney(_, __, val) {
  const v = Number(val)
  return isNaN(v) ? '/' : v.toLocaleString()
}
function formatSignedMoney(_, __, val) {
  const v = Number(val)
  return isNaN(v) ? '/' : (v >= 0 ? '+' : '') + v.toLocaleString()
}
function formatNumber(_, __, val) {
  return val ?? '/'
}
function formatPercent(_, __, val) {
  return val || '/'
}

function rowClassName({ row }) {
  if (row.验证门店 === '合计') return 'total-row'
  const delta = row.佣金数据?.差额
  if (delta < 0) return 'row-negative'
  if (delta > 0) return 'row-positive'
  return ''
}
function headerCellStyle() {
  return {
    background: 'linear-gradient(90deg,#6d28d9,#9333ea)',
    color: '#fdf2ff',
    fontWeight: '700',
    fontSize: '13px',
    userSelect: 'none',
  }
}
function cellStyle() {
  return {
    background: '#1a1a2e',
    color: '#e0d7ff',
    fontWeight: '500',
    fontSize: '12px',
  }
}
</script>

<style scoped>
.upload-box {
  background-color: rgba(255, 255, 255, 0.08);
  border: 3px dashed #8b5cf6;
  border-radius: 24px;
  padding: 40px 24px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 0 30px rgba(139,92,246,0.3);
}
.upload-box:hover {
  border-color: #f472b6;
  box-shadow: 0 0 40px rgba(244,114,182,0.5);
}
.upload-icon {
  font-size: 60px;
  color: #c084fc;
  opacity: 0.9;
}
.upload-box:hover .upload-icon {
  color: #f472b6;
}
.el-button[type='gradient'] {
  background: linear-gradient(90deg,#8b5cf6,#f472b6);
  border: none;
  box-shadow: 0 0 30px #f472b6cc;
  font-weight: 600;
  transition: all 0.3s ease;
}
.el-button[type='gradient']:hover:not(:disabled) {
  box-shadow: 0 0 50px #f472b6;
}

/* 行样式 */
.total-row > td {
  background: linear-gradient(90deg, #9333ea, #f472b6) !important;
  color: #fff !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  user-select: none;
}
.row-negative > td:nth-child(4) {
  color: #f87171 !important;
  font-weight: 700;
}
.row-positive > td:nth-child(4) {
  color: #34d399 !important;
  font-weight: 700;
}

/* 滚动条隐藏美化 */
::-webkit-scrollbar {
  height: 8px;
}
::-webkit-scrollbar-thumb {
  background: rgba(139,92,246,0.5);
  border-radius: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
</style>
