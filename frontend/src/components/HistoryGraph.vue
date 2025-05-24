<template>
  <div class="history-graph">
    <Bar :data="chartData" :options="chartOptions" style="width: 100%;" />
  </div>
</template>

<script setup>
import { Bar } from 'vue-chartjs'
import { computed } from 'vue'
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

// Props: expects an array of messages with { createdDateTime, from: { user: { id } } }
const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  }
})

// Compute distinct users per day
const usersPerDay = computed(() => {
  const dayMap = {}
  props.messages.forEach(msg => {
    if (msg.createdDateTime && msg.from?.user?.id) {
      const day = new Date(msg.createdDateTime).toISOString().split('T')[0]
      if (!dayMap[day]) dayMap[day] = new Set()
      dayMap[day].add(msg.from.user.id)
    }
  })
  // Convert to arrays for chart
  const labels = Object.keys(dayMap).sort()
  const data = labels.map(day => dayMap[day].size)
  return { labels, data }
})

const chartData = computed(() => ({
  labels: usersPerDay.value.labels,
  datasets: [
    {
      label: 'Distinct Users per Day',
      backgroundColor: '#42b983',
      data: usersPerDay.value.data
    }
  ]
}))

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: true }
  },
  scales: {
    y: { beginAtZero: true, title: { display: true, text: 'Users' } },
    x: { title: { display: true, text: 'Date' } }
  },
  options: {
    maintainAspectRatio: false,
    animation: {
      duration: 500,
      easing: 'easeInOutQuad'
    }
  }
}
</script>
<style scoped>
.history-graph {
  width: 100%;
  height: 100%;
  position: relative;
}
</style>