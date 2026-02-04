#!/usr/bin/env python3
"""
Script to add new charts functionality to DashboardView.vue
Inserts: chart options, fetch methods, helpers, and updated refreshData
"""

import re

# Read current file
with open('Frontend/src/views/DashboardView.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add new chart options after inputUsageOption
chart_options = '''
// ========== New Advanced Charts ==========

const cropsByFarmOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} vùng ({d}%)' },
  legend: { orient: 'vertical', left: 'left', top: '10%' },
  series: [{
    name: 'Cây trồng',
    type: 'pie',
    radius: '60%',
    data: cropsByFarmData.value.length > 0 ? cropsByFarmData.value : [
      { value: 72, name: 'Sầu riêng' }, { value: 48, name: 'Xoài' },
      { value: 30, name: 'Nhãn' }, { value: 32, name: 'Khác' }
    ],
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
}))

const fertilizerUsageOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} lần ({d}%)' },
  legend: { bottom: '5%', left: 'center' },
  series: [{
    name: 'Phân bón', type: 'pie', radius: ['40%', '70%'],
    data: fertilizerUsageData.value,
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
}))

const pesticideUsageOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} lần ({d}%)' },
  legend: { bottom: '5%', left: 'center' },
  series: [{
    name: 'Thuốc BVTV', type: 'pie', radius: ['40%', '70%'],
    data: pesticideUsageData.value,
    emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)' } }
  }]
}))

const cropMarketOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: cropMarketData.value.series.map(s => s.name), bottom: '5%' },
  grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
  xAxis: { type: 'category', boundaryGap: false, data: cropMarketData.value.markets },
  yAxis: { type: 'value', name: 'Số vùng trồng' },
  series: cropMarketData.value.series
}))

const fruitInputOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'cross', crossStyle: { color: '#999' } } },
  legend: { data: ['Số vùng trồng', 'Phân bón (kg)', 'Thuốc BVTV (lần)'], bottom: '5%' },
  grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
  xAxis: { type: 'category', data: fruitInputData.value.fruits, axisPointer: { type: 'shadow' } },
  yAxis: [
    { type: 'value', name: 'Số vùng', axisLabel: { formatter: '{value}' } },
    { type: 'value', name: 'Vật tư', axisLabel: { formatter: '{value}' } }
  ],
  series: [
    { name: 'Số vùng trồng', type: 'bar', data: fruitInputData.value.fruit_counts, itemStyle: { color: '#5470c6' } },
    { name: 'Phân bón (kg)', type: 'line', yAxisIndex: 1, data: fruitInputData.value.fertilizer_usage, itemStyle: { color: '#91cc75' } },
    { name: 'Thuốc BVTV (lần)', type: 'line', yAxisIndex: 1, data: fruitInputData.value.pesticide_usage, itemStyle: { color: '#fac858' } }
  ]
}))

'''

# Insert after inputUsageOption
content = re.sub(
    r"(\}\)\))\s*\n\s*// Methods",
    r"\1\n\n" + chart_options + "// Methods",
    content
)

# 2. Add new fetch methods after existing ones
fetch_methods = '''
const fetchCropMarketData = async () => {
  try {
    const response = await analyticsService.getCropMarketRelationship()
    cropMarketData.value = response.data
  } catch (error) {
    console.log('CropMarket data:', error.message)
  }
}

const fetchFruitInputData = async () => {
  try {
    const response = await analyticsService.getFruitInputCorrelation()
    fruitInputData.value = response.data
  } catch (error) {
    console.log('FruitInput data:', error.message)
  }
}

const fetchFertilizerUsage = async () => {
  try {
    const response = await analyticsService.getInputUsageFrequency('fertilizer')
    fertilizerUsageData.value = response.data.data
  } catch (error) {
    console.log('Fertilizer data:', error.message)
  }
}

const fetchPesticideUsage = async () => {
  try {
    const response = await analyticsService.getInputUsageFrequency('pesticide')
    pesticideUsageData.value = response.data.data
  } catch (error) {
    console.log('Pesticide data:', error.message)
  }
}

const fetchRevokedAlerts = async () => {
  try {
    const response = await analyticsService.getRevokedAlerts(20)
    revokedAlerts.value = response.data.data
  } catch (error) {
    console.error('Error fetching revoked alerts:', error)
  }
}

'''

# Insert after fetchTopOwners
content = re.sub(
    r"(const fetchTopOwners = async.*?\n\})\s*\n",
    r"\1\n\n" + fetch_methods,
    content,
    flags=re.DOTALL
)

# 3. Add helper methods
helpers = '''
const formatAlertType = (type) => {
  const types = {
    benh_hai: 'Bệnh hại', thien_tai: 'Thiên tai',
    mua_kho: 'Mùa khô', suy_dinh_duong: 'Suy dinh dưỡng', khac: 'Khác'
  }
  return types[type] || type
}

const formatSeverity = (severity) => {
  const levels = {
    thap: 'Thấp', trung_binh: 'Trung bình', cao: 'Cao', rat_cao: 'Rất cao'
  }
  return levels[severity] || severity
}

const getSeverityBadge = (severity) => {
  const badges = {
    thap: 'badge badge-success', trung_binh: 'badge badge-info',
    cao: 'badge badge-warning', rat_cao: 'badge badge-error'
  }
  return badges[severity] || 'badge'
}

const handleChartClick = (chartType, event) => {
  console.log(`Clicked ${chartType}:`, event)
}

'''

# Insert before refreshData
content = re.sub(
    r"(const refreshData = async)",
    helpers + r"\1",
    content
)

# 4. Update refreshData to include new methods
new_refresh = '''const refreshData = async () => {
  loading.value = true
  chartsLoading.value = true
  
  try {
    await Promise.all([
      fetchKPIData(), fetchAlertData(), fetchMarketData(),
      fetchInputUsageData(), fetchTopOwners(),
      fetchRevokedAlerts(), fetchCropMarketData(), fetchFruitInputData(),
      fetchFertilizerUsage(), fetchPesticideUsage()
    ])
  } catch (error) {
    console.error('Error refreshing data:', error)
  } finally {
    loading.value = false
    chartsLoading.value = false
  }
}'''

content = re.sub(
    r"const refreshData = async \(\) => \{[^}]+\}",
    new_refresh,
    content,
    flags=re.DOTALL
)

# Write updated file
with open('Frontend/src/views/DashboardView.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ DashboardView.vue updated successfully")
print("Added: 5 chart options, 5 fetch methods, 4 helpers, updated refreshData()")
