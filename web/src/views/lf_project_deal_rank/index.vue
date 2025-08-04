<template>
  <div class="min-h-screen bg-gradient-to-r from-cyan-500 to-indigo-600 py-12 px-8">
    <!-- 大标题 -->
    <h1 class="text-6xl font-extrabold text-center text-white mb-12 tracking-tight drop-shadow-2xl hover:opacity-80 transition-opacity duration-300">
      ✨ 咨询师项目业绩排行榜
    </h1>

    <!-- 查询区 -->
    <el-form :inline="true" class="mb-14 flex justify-center flex-wrap gap-8" @submit.prevent="fetchData">
      <el-form-item label="日期范围" label-width="90px">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始"
          end-placeholder="结束"
          :disabled-date="disabledDate"
          @change="handleDateChange"
          class="rounded-lg"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" size="large" class="btn-query" @click="fetchData">🎯 查询</el-button>
      </el-form-item>
    </el-form>

    <!-- 数据区域 -->
    <div v-if="Object.keys(rankData).length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
      <div
        v-for="(groupData, projectName) in rankData"
        :key="projectName"
        class="relative bg-gradient-to-br from-indigo-600 via-purple-500 to-pink-400 text-white rounded-3xl p-6 hover:scale-[1.05] hover:shadow-2xl transition-transform duration-300"
      >
        <h2 class="text-2xl font-bold mb-4 transform transition-transform duration-300 hover:translate-x-3">
          {{ projectName }}
        </h2>

        <!-- 项目标签 -->
        <div v-if="groupData['项目列表']" class="flex flex-wrap gap-3 mb-6">
          <span
            v-for="(item, idx) in groupData['项目列表']"
            :key="idx"
            class="bg-gradient-to-l from-yellow-400 to-pink-500 text-white px-4 py-2 rounded-full text-sm shadow-lg transition duration-300 ease-in-out transform hover:scale-105"
          >
            {{ item }}
          </span>
        </div>

        <!-- 各类排名展示 -->
        <div
          v-for="type in getRankTypes(groupData)"
          :key="type"
          class="mb-5"
        >
          <h3 class="text-xl font-semibold mb-3 text-indigo-200 hover:text-indigo-300 transition duration-300">
            {{ type }}
          </h3>

          <ul class="space-y-2">
            <li
              v-for="([name, info], index) in sortedEntries(groupData[type])"
              :key="name"
              class="flex justify-between items-center p-4 rounded-xl bg-opacity-40 hover:bg-opacity-50 transition-all duration-300 cursor-pointer transform hover:scale-105"
            >
              <div class="flex items-center gap-4">
                <span
                  class="w-8 h-8 rounded-full bg-gradient-to-tr from-pink-400 to-orange-400 text-white text-lg font-bold flex items-center justify-center shadow-lg"
                >
                  {{ index + 1 }}
                </span>
                <span class="font-medium">{{ name }}</span>
              </div>
              <div class="text-right">
                <span class="font-bold text-xl text-indigo-100">￥{{ info['结算业绩'].toFixed(2) }}</span>
                <span class="ml-1 text-xs text-indigo-200">({{ info['成交人次'] }}人次)</span>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 无数据提示 -->
    <div v-else class="text-center text-white mt-28 text-lg font-medium">
      🎈 请先选择时间范围，然后点击查询即可查看数据
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const dateRange = ref([])
const rankData = ref({})

const disabledDate = (time) => {
  const sixMonthsAgo = dayjs().subtract(6, 'month')
  return time.getTime() < sixMonthsAgo.valueOf() || time.getTime() > Date.now()
}

const handleDateChange = ([start, end]) => {
  const diff = dayjs(end).diff(dayjs(start), 'month', true)
  if (diff > 6) {
    ElMessage.warning('最多查询 6 个月内的数据')
    dateRange.value = []
  }
}

const fetchData = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请先选择时间范围')
    return
  }

  try {
    const [start, end] = dateRange.value
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/LFProjectDealRankView/`, {
      startChargeTime: dayjs(start).format('YYYY-MM-DD 00:00:00'),
      endChargeTime: dayjs(end).format('YYYY-MM-DD 23:59:59'),
    })

    if (res.data.code === 2000) {
      rankData.value = res.data.data || {}
    } else {
      ElMessage.error('数据加载失败，请稍后重试')
    }
  } catch (err) {
    ElMessage.error('获取数据失败')
  }
}

const sortedEntries = (consultants) => {
  return Object.entries(consultants).sort((a, b) => b[1]['结算业绩'] - a[1]['结算业绩'])
}

const getRankTypes = (groupData) => {
  return Object.keys(groupData).filter((key) => key !== '项目列表')
}
</script>

<style scoped>
.el-date-editor {
  background-color: rgba(255, 255, 255, 0.4);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.el-button {
  background-color: #6c5ce7;
  color: white;
  border-radius: 50px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.el-button:hover {
  background-color: #a29bfe;
  transform: scale(1.05);
}

.el-date-picker {
  background-color: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  backdrop-filter: blur(5px);
}

.el-form-item label {
  font-size: 16px;
  font-weight: bold;
}
</style>
