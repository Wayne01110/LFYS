<template>
  <div
    class="min-h-screen bg-gradient-to-br from-black via-purple-900 to-gray-900 text-white p-6 font-sans flex flex-col items-center"
  >
    <!-- 标题 -->
    <h1
      class="text-4xl md:text-5xl font-extrabold mb-6 bg-gradient-to-r from-cyan-400 via-pink-500 to-purple-600 text-transparent bg-clip-text max-w-xl text-center leading-tight select-none drop-shadow-lg"
    >
      ⚡小程序客户统计
    </h1>

    <!-- 查询控件 -->
    <div
      class="flex flex-col sm:flex-row justify-center items-center gap-3 mb-12 w-full max-w-md bg-black bg-opacity-40 p-4 rounded-3xl shadow-lg border border-purple-700"
    >
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        format="YYYY-MM-DD"
        unlink-panels
        :disabled="loading"
        :picker-options="pickerOptions"
        class="flex-grow max-w-[300px]"
      />
      <el-button
        type="primary"
        :loading="loading"
        @click="fetchData"
        :disabled="loading || !dateRange || dateRange.length !== 2"
        class="w-24 h-12"
      >
        查询
      </el-button>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      class="mb-6 max-w-xl mx-auto"
      closable
      @close="error = ''"
      :style="{background: 'rgba(255,0,0,0.15)', borderColor: 'rgba(255,0,0,0.5)'}"
    ></el-alert>

    <!-- 集团汇总 -->
    <transition name="fade">
      <section
        v-if="data"
        class="bg-gradient-to-tr from-purple-900 via-pink-900 to-purple-800 p-6 rounded-3xl shadow-2xl mb-8 max-w-4xl w-full"
      >
        <h2 class="text-2xl font-bold text-cyan-400 mb-5 select-none drop-shadow">
          🏢 集团汇总
        </h2>
        <div
          class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 text-sm sm:text-base"
        >
          <div
            class="bg-purple-700 bg-opacity-80 p-5 rounded-2xl shadow-inner flex flex-col justify-center items-center"
          >
            <span class="text-white font-semibold mb-1">客户总数</span>
            <span class="text-3xl font-bold text-cyan-400">{{ data.groupSummary.totalCustomers }}</span>
          </div>
          <div
            class="bg-pink-700 bg-opacity-80 p-5 rounded-2xl shadow-inner flex flex-col justify-center items-center"
          >
            <span class="text-white font-semibold mb-1">积分总和</span>
            <span class="text-3xl font-bold text-pink-300">{{ data.groupSummary.totalIntegral }}</span>
          </div>
          <div
            class="col-span-full sm:col-span-2 md:col-span-4 bg-black bg-opacity-30 rounded-2xl p-4 max-h-48 overflow-auto shadow-inner"
          >
            <h3 class="text-lg font-semibold text-pink-300 mb-3 select-none">
              会员等级统计
            </h3>
            <ul class="space-y-1 text-gray-300">
              <li
                v-for="(count, level) in data.groupSummary.memberLevelCount"
                :key="level"
                class="flex justify-between px-3 py-1 rounded hover:bg-purple-700 cursor-default select-text"
              >
                <span>👤 {{ level }}</span>
                <span>{{ count }} 人，积分：{{ data.groupSummary.memberLevelIntegral[level] || 0 }}</span>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </transition>

    <!-- 门店明细 -->
    <transition-group
      name="fade"
      tag="section"
      v-if="data?.storeSummary?.length"
      class="max-w-4xl w-full mx-auto grid grid-cols-1 md:grid-cols-2 gap-8"
    >
      <article
        v-for="store in data.storeSummary"
        :key="store.tenantName"
        class="bg-gradient-to-tr from-purple-900 via-pink-900 to-purple-800 p-5 rounded-3xl shadow-2xl"
      >
        <h2
          class="text-xl font-bold text-pink-400 mb-5 select-none drop-shadow"
        >
          🏬 {{ store.tenantName }}
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm sm:text-base">
          <div
            class="bg-purple-600 bg-opacity-70 p-4 rounded-xl flex flex-col items-center"
          >
            <span class="text-white font-semibold mb-1">客户数</span>
            <span class="text-2xl font-bold text-purple-200">{{ store.totalCustomers }}</span>
          </div>
          <div
            class="bg-cyan-600 bg-opacity-70 p-4 rounded-xl flex flex-col items-center"
          >
            <span class="text-white font-semibold mb-1">积分总和</span>
            <span class="text-2xl font-bold text-cyan-200">{{ store.totalIntegral }}</span>
          </div>
          <div
            class="col-span-full bg-black bg-opacity-25 rounded-xl p-3 max-h-40 overflow-auto text-gray-300"
          >
            <h3 class="text-lg font-semibold mb-2 select-none">等级分布</h3>
            <ul>
              <li
                v-for="(count, level) in store.memberLevelCount"
                :key="level"
                class="flex justify-between py-1 px-2 rounded hover:bg-purple-700 cursor-default select-text"
              >
                <span>🎖️ {{ level }}</span>
                <span>{{ count }} 人，积分：{{ store.memberLevelIntegral[level] || 0 }}</span>
              </li>
            </ul>
          </div>
        </div>
      </article>
    </transition-group>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import dayjs from 'dayjs'
import 'element-plus/theme-chalk/el-date-picker.css'
import 'element-plus/theme-chalk/el-button.css'
import 'element-plus/theme-chalk/el-alert.css'

const dateRange = ref([])
const data = ref(null)
const loading = ref(false)
const error = ref('')

const pickerOptions = {
  disabledDate(time) {
    return time.getTime() > Date.now()
  },
}

const fetchData = async () => {
  error.value = ''
  if (!dateRange.value || dateRange.value.length !== 2) {
    error.value = '请选择有效的日期范围'
    return
  }
  loading.value = true
  data.value = null
  try {
    const start = dayjs(dateRange.value[0]).format('YYYY-MM-DD 00:00:00')
    const end = dayjs(dateRange.value[1]).format('YYYY-MM-DD 23:59:59')
    const res = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/LFXcxClientInfoView/`,
      {
        bindDateStart: start,
        bindDateEnd: end,
      }
    )
    if (res.data.code === 2000) {
      data.value = res.data.data
    } else {
      error.value = res.data.msg || '请求失败'
    }
  } catch (e) {
    error.value = '请求异常：' + e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
body {
  font-family: 'Orbitron', sans-serif;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
