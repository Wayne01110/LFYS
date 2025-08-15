<template>
  <div class="page-container">
    <h1 class="page-title">美团点评流入流出</h1>

    <!-- 汇总 -->
    <div class="total-summary-wrapper">
      <el-card shadow="hover" class="summary-card inflow-card">
        <h3 class="summary-title">所有门店流入汇总</h3>
        <div class="summary-content">
          <div class="summary-item">
            <div class="summary-label">初诊人数</div>
            <div class="summary-value inflow-color">{{ formatNumber(totalSummary.流入.初诊人数) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">初诊成交</div>
            <div class="summary-value inflow-color">{{ formatNumber(totalSummary.流入.初诊成交) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">初复诊成交</div>
            <div class="summary-value inflow-color">{{ formatNumber(totalSummary.流入.初复诊成交) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">新客业绩</div>
            <div class="summary-value inflow-color">{{ formatInteger(null, null, totalSummary.流入.新客业绩) }}</div>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="summary-card outflow-card">
        <h3 class="summary-title">所有门店流出汇总</h3>
        <div class="summary-content">
          <div class="summary-item">
            <div class="summary-label">初诊人数</div>
            <div class="summary-value outflow-color">{{ formatNumber(totalSummary.流出.初诊人数) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">初诊成交</div>
            <div class="summary-value outflow-color">{{ formatNumber(totalSummary.流出.初诊成交) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">初复诊成交</div>
            <div class="summary-value outflow-color">{{ formatNumber(totalSummary.流出.初复诊成交) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">新客业绩</div>
            <div class="summary-value outflow-color">{{ formatInteger(null, null, totalSummary.流出.新客业绩) }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 上传 + 日期 + 按钮 -->
    <div class="upload-control-group">
      <el-upload
        multiple
        :auto-upload="false"
        :before-upload="handleBeforeUpload"
        :on-change="handleFileChange"
        :file-list="fileList"
        drag
        class="upload-box"
        accept=".xls,.xlsx"
        :disabled="loading"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">拖拽或点击上传多个 Excel 文件</div>
        <div class="el-upload__tip">支持xls、xlsx格式，最多10个文件</div>
      </el-upload>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="YYYY-MM-DD"
        class="date-picker"
        unlink-panels
        :picker-options="pickerOptions"
        :disabled="loading"
      />

      <el-button
        type="primary"
        :loading="loading"
        :disabled="fileList.length === 0 || !dateRange || dateRange.length !== 2 || loading"
        @click="handleSubmit"
        class="submit-btn"
      >
        生成分析
      </el-button>
    </div>

    <!-- 门店明细 -->
    <div v-if="tableData.length" class="results">
      <div
        v-for="(item, index) in tableData"
        :key="item.点评来源"
        class="store-block"
        :style="{ background: storeBlockGradient(index) }"
      >
        <h2 class="store-title">{{ item.点评来源 }}</h2>
        <div class="basic-info">
          <span class="info-cpc">门店CPC消耗：{{ formatNumber(item.门店CPC消耗) }}</span>
          <span class="info-msg">私信：{{ formatNumber(item.私信) }}</span>
          <span class="info-rate">初诊到诊率：{{ formatPercentStrOrNum(null, null, item.初诊到诊率) }}</span>
        </div>

        <!-- 流出明细 -->
        <div class="flow-table">
          <h3 class="flow-title">流出明细（门店 → 流出门店）</h3>
          <el-table
            :data="item.流出明细.concat(item.流出总计 ? [{ ...item.流出总计, 流出门店: '合计' }] : [])"
            size="small"
            border
            :row-key="row => row.流出门店"
            class="flow-el-table el-table-flow-out"
            max-height="320"
            :cell-style="cellStyle"
          >
            <el-table-column prop="流出门店" label="流出门店" />
            <el-table-column prop="初诊人数" label="初诊人数" />
            <el-table-column prop="初诊成交" label="初诊成交" />
            <el-table-column prop="初复诊成交" label="初复诊成交" />
            <el-table-column prop="初诊成交率" label="初诊成交率" :formatter="formatPercentStrOrNum" />
            <el-table-column prop="新客成交率" label="新客成交率" :formatter="formatPercentStrOrNum" />
            <el-table-column prop="新客业绩" label="新客业绩" :formatter="formatInteger" />
            <el-table-column prop="客单价" label="客单价" :formatter="formatInteger" />
          </el-table>
        </div>

        <!-- 流入明细 -->
        <div class="flow-table">
          <h3 class="flow-title">流入明细（点评来源 → 门店）</h3>
          <el-table
            :data="item.流入明细.concat(item.流入总计 ? [{ ...item.流入总计, 点评来源: '合计' }] : [])"
            size="small"
            border
            :row-key="row => row.点评来源"
            class="flow-el-table el-table-flow-in"
            max-height="320"
            :cell-style="cellStyle"
          >
            <el-table-column prop="点评来源" label="点评来源" />
            <el-table-column prop="初诊人数" label="初诊人数" />
            <el-table-column prop="初诊成交" label="初诊成交" />
            <el-table-column prop="初复诊成交" label="初复诊成交" />
            <el-table-column prop="初诊成交率" label="初诊成交率" :formatter="formatPercentStrOrNum" />
            <el-table-column prop="新客成交率" label="新客成交率" :formatter="formatPercentStrOrNum" />
            <el-table-column prop="新客业绩" label="新客业绩" :formatter="formatInteger" />
            <el-table-column prop="客单价" label="客单价" :formatter="formatInteger" />
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const fileList = ref([])
const dateRange = ref([])
const tableData = ref([])
const loading = ref(false)

const totalSummary = ref({
  流入: { 初诊人数: 0, 初诊成交: 0, 初复诊成交: 0, 新客业绩: 0 },
  流出: { 初诊人数: 0, 初诊成交: 0, 初复诊成交: 0, 新客业绩: 0 }
})

const pickerOptions = {
  disabledDate(time) {
    return time.getTime() > Date.now()
  }
}

const handleFileChange = (file, files) => {
  fileList.value = files
}

const handleBeforeUpload = () => false

function formatPercentStrOrNum(row, column, cellValue) {
  if (typeof cellValue === 'string') {
    if (cellValue.includes('%')) return cellValue
    const num = parseFloat(cellValue)
    if (!isNaN(num)) return (num * 100).toFixed(2) + '%'
    return '0.00%'
  }
  if (typeof cellValue === 'number') {
    return (cellValue * 100).toFixed(2) + '%'
  }
  return '0.00%'
}
function formatInteger(row, column, cellValue) {
  const val = Number(cellValue)
  if (isNaN(val)) return '0'
  return Math.round(val).toLocaleString()
}

function formatNumber(val) {
  if (typeof val === 'number') return val.toLocaleString()
  return val || '0'
}

const handleSubmit = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择日期范围')
    return
  }
  if (fileList.value.length === 0) {
    ElMessage.warning('请上传文件')
    return
  }

  loading.value = true
  const formData = new FormData()
  fileList.value.forEach(file => formData.append('files', file.raw))
  formData.append('start_date', dateRange.value[0] + ' 00:00:00')
  formData.append('end_date', dateRange.value[1] + ' 23:59:59')

  try {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/MTInflowOutflowView/`, formData)
    if (res.data.code === 2000) {
      tableData.value = res.data.data.data
      totalSummary.value = res.data.data['所有门店汇总'] || totalSummary.value
      ElMessage.success('分析成功')
    } else {
      ElMessage.error('分析失败: ' + (res.data.msg || '未知错误'))
    }
  } catch (error) {
    ElMessage.error('请求失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

function storeBlockGradient(index) {
  const colors = [
    'linear-gradient(135deg, #fffaf0, #ffd591)',
    'linear-gradient(135deg, #f0fcff, #a0e0ff)',
    'linear-gradient(135deg, #fff0f7, #ff92d2)',
    'linear-gradient(135deg, #f0fff4, #92ffb3)',
    'linear-gradient(135deg, #f5f0ff, #b392ff)'
  ]
  return colors[index % colors.length]
}

// 在 <script setup> 内定义即可
const cellStyle = ({ row, column }) => {
  if (column.property === '客单价') {
    if (Number(row['客单价']) < 3500) {
      return { color: 'red', fontWeight: 'bold' }
    } else if (Number(row['客单价']) >= 3500) {
      return { color: 'green', fontWeight: 'bold' }
    }
  }
  return {}
}

</script>

<style scoped>
.page-container {
  max-width: 1300px;
  margin: 24px auto;
  padding: 32px 28px 48px;
  font-family: 'Montserrat', sans-serif;
  background: linear-gradient(135deg, #f0f8ff, #e6f0ff);
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
  color: #333;
  min-height: 100vh;
}

.page-title {
  font-size: 44px;
  font-weight: 900;
  color: #5a4de8;
  text-align: center;
  margin-bottom: 48px;
  text-shadow: 0 0 18px rgba(90, 77, 232, 0.35);
}

.inflow-color { color: #2e7d32; font-weight: 800; }
.outflow-color { color: #d32f2f; font-weight: 800; }

.total-summary-wrapper {
  display: flex;
  justify-content: center;
  gap: 26px;
  margin-bottom: 48px;
  flex-wrap: wrap;
}

.summary-card {
  border-radius: 20px;
  font-weight: 700;
  width: 420px;
  padding: 32px 24px;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.08);
  transition: transform 0.25s ease, box-shadow 0.35s ease;
  color: #222;
}

.summary-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.15);
}

.inflow-card {
  background: linear-gradient(135deg, #d6f9d6, #80e080);
}

.outflow-card {
  background: linear-gradient(135deg, #ffd6e0, #ff80a0);
}

.summary-title {
  font-size: 28px;
  font-weight: 900;
  margin-bottom: 28px;
  text-align: center;
}

.summary-content {
  display: flex;
  justify-content: space-around;
  gap: 18px;
  flex-wrap: wrap;
}

.summary-item {
  text-align: center;
  flex: 1 1 100px;
  background: rgba(255, 255, 255, 0.8);
  padding: 18px 20px;
  margin: 6px 6px;
  border-radius: 16px;
  box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.05);
  font-size: 18px;
}

.summary-label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #555;
}

.summary-value {
  font-size: 22px;
  font-weight: 900;
}

.upload-control-group {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 44px;
  flex-wrap: wrap;
}

.upload-box {
  flex-grow: 1;
  min-width: 300px;
  border-radius: 16px;
  font-size: 15px;
  color: #555;
  background: linear-gradient(135deg, #f7f9fa, #e8f0f5);
  box-shadow: 0 4px 14px rgba(90, 77, 232, 0.15);
  border: 1.5px solid rgba(90, 77, 232, 0.3);
  cursor: pointer;
  transition: box-shadow 0.3s ease;
}

.upload-box:hover:not(.is-disabled) {
  box-shadow: 0 10px 24px rgba(90, 77, 232, 0.3);
  border-color: rgba(90, 77, 232, 0.5);
}

.date-picker { min-width: 250px; }

.submit-btn {
  min-width: 160px;
  padding: 12px 32px;
  font-weight: 700;
  font-size: 16px;
  background: linear-gradient(135deg, #6ed0ff, #4a90e2);
  border: none;
  color: white;
  box-shadow: 0 6px 20px rgba(74, 144, 226, 0.35);
}

.results { margin-top: 44px; }

.store-block {
  margin-bottom: 44px;
  padding: 28px 32px;
  border-radius: 20px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.25s ease, box-shadow 0.3s ease;
}

.store-block:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.12);
}

.store-title {
  font-size: 28px;
  font-weight: 900;
  margin-bottom: 18px;
  color: #5a4de8;
  border-bottom: 3px solid #5a4de8;
  padding-bottom: 6px;
}

.basic-info {
  margin-bottom: 26px;
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  font-size: 16px;
  color: #444;
}

.flow-table {
  margin-bottom: 38px;
}

.flow-title {
  font-size: 21px;
  font-weight: 800;
  margin-bottom: 18px;
  color: #222;
}

.flow-el-table {
  width: 100%;
  border-radius: 14px;
  overflow: hidden;
  font-size: 15px;
}

.el-table th,
.el-table td {
  font-size: 15px !important;
  padding: 12px 14px !important;
  color: #222 !important;
}

.el-table th {
  background-color: rgba(90, 77, 232, 0.1) !important;
  font-weight: 700;
}

.el-table tr:hover > td {
  background-color: rgba(189, 255, 102, 0.12) !important;
}

.el-table-flow-in td { color: #10f0f4 !important; font-weight: 700; }
.el-table-flow-out td { color: #d42a6a !important; font-weight: 700; }
</style>
