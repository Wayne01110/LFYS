其他地方不用改，查询加个时间限制，不能超过3个月
<template>
  <div class="min-h-screen bg-gradient-to-br from-black via-purple-900 to-gray-900 text-white p-8 font-sans relative overflow-hidden">
    <!-- 背景光圈 -->
    <div class="absolute -top-40 -left-40 w-[400px] h-[400px] bg-cyan-400 blur-3xl opacity-20 rounded-full animate-pulse"></div>
    <div class="absolute -bottom-40 -right-40 w-[400px] h-[400px] bg-pink-500 blur-3xl opacity-20 rounded-full animate-pulse"></div>

    <!-- 标题 -->
    <h1 class="text-5xl font-black mb-10 text-center text-cyan-300 tracking-wide drop-shadow-lg">项目 · 套餐 · 医生划扣排行</h1>

    <!-- 时间选择 + 查询按钮 -->
    <div class="flex flex-col md:flex-row justify-center items-center gap-4 mb-12">
      <input type="date" v-model="startDate" class="bg-gray-800 text-white p-3 rounded-xl border border-cyan-500 w-48 text-center shadow-inner" />
      <input type="date" v-model="endDate" class="bg-gray-800 text-white p-3 rounded-xl border border-cyan-500 w-48 text-center shadow-inner" />
      <button
        :disabled="loading"
        @click="fetchData"
        class="bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-blue-400 hover:to-cyan-300 text-black font-extrabold py-3 px-8 rounded-xl shadow-2xl disabled:opacity-40 transition-all duration-300"
      >
        <span v-if="!loading">🚀 查询</span>
        <span v-else class="flex items-center">
          <svg class="animate-spin h-5 w-5 mr-2 text-black" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="black" stroke-width="4" fill="none" />
            <path class="opacity-75" fill="black" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          加载中...
        </span>
      </button>
    </div>

    <!-- 数据展示区 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- 卡片组件 -->
      <Card title="📦 项目排行" :items="data.项目排行" valueKey="achievement" />
      <Card title="🎁 套餐排行" :items="data.套餐排行" valueKey="achievement" />
      <Card title="🩺 医生划扣排行" :items="data.医生划扣数量排行" valueKey="划扣数量" isDoctor />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// 时间和加载状态
const startDate = ref('')
const endDate = ref('')
const loading = ref(false)

// 数据
const data = ref({
  项目排行: [],
  套餐排行: [],
  医生划扣数量排行: [],
})

// 获取数据
const fetchData = async () => {
  if (!startDate.value || !endDate.value) {
    alert("请选择起止时间")
    return
  }

  const start = new Date(startDate.value)
  const end = new Date(endDate.value)
  const diffDays = (end - start) / (1000 * 60 * 60 * 24)

  if (diffDays > 92) {
    alert("查询时间跨度不能超过3个月")
    return
  }

  loading.value = true
  try {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/api/LFProjectPackageDoctorView/`, {
      startChargeTime: startDate.value,
      endChargeTime: endDate.value
    })
    data.value = res.data.data
  } catch (err) {
    alert("请求失败：" + err.message)
  } finally {
    loading.value = false
  }
}

</script>

<script>
/* 卡片子组件 */
export default {
  components: {
    Card: {
      props: ['title', 'items', 'valueKey', 'isDoctor'],
      template: `
        <div class="rounded-2xl p-6 bg-gray-900 bg-opacity-70 border border-cyan-500 shadow-[0_0_20px_rgba(0,255,255,0.2)] transition-transform hover:scale-[1.02] duration-300">
          <h2 class="text-2xl font-bold text-cyan-300 mb-4 text-center">{{ title }}</h2>
          <div class="space-y-2 max-h-[500px] overflow-auto scrollbar-thin scrollbar-thumb-cyan-500 scrollbar-track-gray-700">
            <div
              v-for="(item, index) in items"
              :key="index"
              class="bg-gray-800 p-3 rounded-lg flex justify-between items-center text-sm lg:text-base"
            >
              <div class="truncate w-1/2">
                {{ index + 1 }}. {{ item.name }}
              </div>
              <div v-if="isDoctor" class="text-cyan-400 font-mono text-right space-x-4">
                <span>划扣数: {{ item.划扣数量 }}</span>
                <span>人次: {{ item.划扣人次 }}</span>
              </div>
              <div v-else class="text-cyan-400 font-mono text-right">
                {{ item[valueKey] }}
              </div>
            </div>
          </div>
        </div>
      `
    }
  }
}
</script>

<style scoped>
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: rgba(34, 211, 238, 0.7);
  border-radius: 3px;
}
</style>
