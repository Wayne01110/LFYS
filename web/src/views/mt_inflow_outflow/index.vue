<template>
  <div class="page-container">
    <h1 class="page-title">美团点评流入流出分析</h1>

    <!-- 汇总 -->
    <div class="total-summary-wrapper">
      <el-card shadow="hover" class="summary-card inflow-card">
        <h3 class="summary-title">所有门店流入汇总</h3>
        <div class="summary-content">
          <div class="summary-item">
            <div class="summary-label">初诊人数</div>
            <div class="summary-value">{{ formatNumber(totalSummary.流入.初诊人数) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">初诊成交</div>
            <div class="summary-value">{{ formatNumber(totalSummary.流入.初诊成交) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">初复诊成交</div>
            <div class="summary-value">{{ formatNumber(totalSummary.流入.初复诊成交) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">新客业绩</div>
            <div class="summary-value">{{ formatInteger(null, null, totalSummary.流入.新客业绩) }}</div>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="summary-card outflow-card">
        <h3 class="summary-title">所有门店流出汇总</h3>
        <div class="summary-content">
          <div class="summary-item">
            <div class="summary-label">初诊人数</div>
            <div class="summary-value">{{ formatNumber(totalSummary.流出.初诊人数) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">初诊成交</div>
            <div class="summary-value">{{ formatNumber(totalSummary.流出.初诊成交) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">初复诊成交</div>
            <div class="summary-value">{{ formatNumber(totalSummary.流出.初复诊成交) }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">新客业绩</div>
            <div class="summary-value">{{ formatInteger(null, null, totalSummary.流出.新客业绩) }}</div>
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
        v-for="item in tableData"
        :key="item.点评来源"
        class="store-block"
      >
        <h2 class="store-title">{{ item.点评来源 }}</h2>
        <div class="basic-info">
          <span>门店CPC消耗：{{ formatNumber(item.门店CPC消耗) }}</span>
          <span>私信：{{ formatNumber(item.私信) }}</span>
          <span>初诊到诊率：{{ formatPercentStrOrNum(null, null, item.初诊到诊率) }}</span>
        </div>

        <!-- 流出明细 -->
        <div class="flow-table">
          <h3 class="flow-title">流出明细（门店 → 流出门店）</h3>
          <el-table
            :data="item.流出明细.concat(item.流出总计 ? [{ ...item.流出总计, 流出门店: '合计' }] : [])"
            size="small"
            border
            :row-key="row => row.流出门店"
            class="flow-el-table"
            max-height="320"
          >
            <el-table-column prop="流出门店" label="流出门店" width="170" />
            <el-table-column prop="初诊人数" label="初诊人数" width="85" />
            <el-table-column prop="初诊成交" label="初诊成交" width="85" />
            <el-table-column prop="初复诊成交" label="初复诊成交" width="85" />
            <el-table-column
              prop="初诊成交率"
              label="初诊成交率"
              width="110"
              :formatter="formatPercentStrOrNum"
            />
            <el-table-column
              prop="新客成交率"
              label="新客成交率"
              width="110"
              :formatter="formatPercentStrOrNum"
            />
            <el-table-column
              prop="新客业绩"
              label="新客业绩"
              width="110"
              :formatter="formatInteger"
            />
            <el-table-column
              prop="客单价"
              label="客单价"
              width="95"
              :formatter="formatInteger"
            />
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
            class="flow-el-table"
            max-height="320"
          >
            <el-table-column prop="点评来源" label="点评来源" width="170" />
            <el-table-column prop="初诊人数" label="初诊人数" width="85" />
            <el-table-column prop="初诊成交" label="初诊成交" width="85" />
            <el-table-column prop="初复诊成交" label="初复诊成交" width="85" />
            <el-table-column
              prop="初诊成交率"
              label="初诊成交率"
              width="110"
              :formatter="formatPercentStrOrNum"
            />
            <el-table-column
              prop="新客成交率"
              label="新客成交率"
              width="110"
              :formatter="formatPercentStrOrNum"
            />
            <el-table-column
              prop="新客业绩"
              label="新客业绩"
              width="110"
              :formatter="formatInteger"
            />
            <el-table-column
              prop="客单价"
              label="客单价"
              width="95"
              :formatter="formatInteger"
            />
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
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 24px auto;
  padding: 24px 20px 40px;
  font-family: 'Montserrat', sans-serif;
  background: #2b2e4a;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
  color: #f0f0f0;
  min-height: 100vh;
}

.page-title {
  font-size: 34px;
  font-weight: 900;
  color: #ffd600;
  text-align: center;
  margin-bottom: 36px;
  text-shadow: 0 0 12px #f8b500;
}

.total-summary-wrapper {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 36px;
  flex-wrap: nowrap;
  flex-shrink: 0;
}

.summary-card {
  border-radius: 12px;
  color: #fff;
  font-weight: 700;
  width: 380px;
  padding: 20px 16px;
  box-shadow: 0 6px 18px rgba(255 255 255 / 0.15);
  transition: box-shadow 0.3s ease;
  user-select: none;
}

.summary-card:hover {
  box-shadow: 0 10px 30px rgba(255 255 255 / 0.35);
}

.inflow-card {
  background: linear-gradient(135deg, #52d8a6, #3a7bd5);
}

.outflow-card {
  background: linear-gradient(135deg, #f56565, #b26a00);
}

.summary-title {
  font-size: 20px;
  font-weight: 900;
  margin-bottom: 20px;
  text-align: center;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.summary-content {
  display: flex;
  justify-content: space-around;
  gap: 14px;
  flex-wrap: wrap;
}

.summary-item {
  text-align: center;
  flex: 1 1 80px;
  background: rgba(255 255 255 / 0.15);
  padding: 14px 16px;
  margin: 6px 4px;
  border-radius: 10px;
  box-shadow: inset 0 0 10px rgba(255 255 255 / 0.12);
  font-size: 16px;
}

.summary-label {
  font-weight: 700;
  margin-bottom: 6px;
  color: #fff;
  text-shadow: 0 0 4px rgba(0,0,0,0.25);
}

.summary-value {
  font-size: 18px;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 0 6px rgba(0,0,0,0.4);
}

.upload-control-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.upload-box {
  flex-grow: 1;
  min-width: 280px;
  border-radius: 12px;
  font-size: 14px;
  color: #fff;
  background: rgba(255 255 255 / 0.07);
  box-shadow: 0 2px 8px rgba(255 214 0, 0.3);
  border: 1.5px solid rgba(255 214 0, 0.3);
  transition: box-shadow 0.3s ease;
  cursor: pointer;
}

.upload-box:hover:not(.is-disabled) {
  box-shadow: 0 6px 15px rgba(255 214 0, 0.6);
  border-color: rgba(255 214 0, 0.6);
}

.date-picker {
  min-width: 240px;
  margin-left: 12px;
  flex-shrink: 0;
}

.submit-btn {
  min-width: 140px;
  padding: 8px 24px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(255 214 0, 0.6);
  margin-left: 12px;
  white-space: nowrap;
  flex-shrink: 0;
}

.results {
  margin-top: 32px;
}

.store-block {
  margin-bottom: 36px;
  padding: 18px 24px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: inset 0 0 14px rgba(0, 0, 0, 0.18);
  user-select: none;
}

.store-title {
  font-size: 22px;
  font-weight: 900;
  margin-bottom: 12px;
  color: #ffd600;
  text-shadow: 0 0 8px #f8b500;
  border-bottom: 2px solid #ffd600;
  padding-bottom: 6px;
}

.basic-info {
  margin-bottom: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  font-size: 14px;
  color: #ccc;
}

.flow-table {
  margin-bottom: 30px;
}

.flow-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 12px;
  color: #ffd600;
  text-shadow: 0 0 6px #f8b500;
}

.flow-el-table {
  width: 100%;
  max-width: 100%;
  border-radius: 8px;
  overflow: hidden;
}

.el-table th,
.el-table td {
  font-size: 13.5px !important;
  padding: 8px 8px !important;
  color: #fff !important;
  user-select: none;
}

.el-table th {
  background-color: rgba(255 214 0 / 0.15) !important;
  font-weight: 700;
}

.el-table tr:hover > td {
  background-color: rgba(255 214 0 / 0.12) !important;
}
</style>
