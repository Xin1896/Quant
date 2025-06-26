import { Lunar } from 'lunar-javascript'
import axios from 'axios'

export class LunarService {
  constructor() {
    this.lunarCache = new Map()
  }

  // 获取今日黄历信息
  async getTodayLunar() {
    const today = new Date()
    const cacheKey = this.formatDate(today)
    
    if (this.lunarCache.has(cacheKey)) {
      return this.lunarCache.get(cacheKey)
    }

    try {
      const lunar = Lunar.fromDate(today)
      const lunarInfo = {
        date: today,
        lunarDate: `${lunar.getYearInChinese()}年${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`,
        year: lunar.getYear(),
        month: lunar.getMonth(),
        day: lunar.getDay(),
        yearName: lunar.getYearInChinese(),
        monthName: lunar.getMonthInChinese(),
        dayName: lunar.getDayInChinese(),
        zodiac: lunar.getYearShengXiao(),
        constellation: lunar.getXingZuo(),
        suitable: this.getSuitableActivities(lunar),
        unsuitable: this.getUnsuitableActivities(lunar),
        description: this.getDayDescription(lunar),
        festivals: this.getFestivals(lunar),
        weather: await this.getWeatherInfo(today)
      }

      this.lunarCache.set(cacheKey, lunarInfo)
      return lunarInfo
    } catch (error) {
      console.error('获取黄历信息失败:', error)
      return this.getDefaultLunarInfo(today)
    }
  }

  // 获取指定日期的黄历信息
  async getLunarByDate(date) {
    const cacheKey = this.formatDate(date)
    
    if (this.lunarCache.has(cacheKey)) {
      return this.lunarCache.get(cacheKey)
    }

    try {
      const lunar = Lunar.fromDate(date)
      const lunarInfo = {
        date: date,
        lunarDate: `${lunar.getYearInChinese()}年${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`,
        year: lunar.getYear(),
        month: lunar.getMonth(),
        day: lunar.getDay(),
        yearName: lunar.getYearInChinese(),
        monthName: lunar.getMonthInChinese(),
        dayName: lunar.getDayInChinese(),
        zodiac: lunar.getYearShengXiao(),
        constellation: lunar.getXingZuo(),
        suitable: this.getSuitableActivities(lunar),
        unsuitable: this.getUnsuitableActivities(lunar),
        description: this.getDayDescription(lunar),
        festivals: this.getFestivals(lunar)
      }

      this.lunarCache.set(cacheKey, lunarInfo)
      return lunarInfo
    } catch (error) {
      console.error('获取黄历信息失败:', error)
      return this.getDefaultLunarInfo(date)
    }
  }

  // 获取宜做的事情
  getSuitableActivities(lunar) {
    const activities = []
    
    // 根据农历日期判断宜做的事情
    const day = lunar.getDay()
    const month = lunar.getMonth()
    
    // 基础宜做事项
    activities.push('祭祀', '祈福', '求嗣')
    
    // 根据日期添加特定事项
    if (day === 1 || day === 15) {
      activities.push('斋醮', '开光')
    }
    
    if (day % 2 === 0) {
      activities.push('出行', '移徙')
    }
    
    if (day % 3 === 0) {
      activities.push('开市', '交易')
    }
    
    if (day % 5 === 0) {
      activities.push('纳财', '栽种')
    }
    
    // 特殊节日
    if (month === 1 && day === 1) {
      activities.push('拜年', '团圆')
    }
    
    if (month === 5 && day === 5) {
      activities.push('赛龙舟', '吃粽子')
    }
    
    if (month === 8 && day === 15) {
      activities.push('赏月', '团圆')
    }
    
    return activities.slice(0, 8) // 限制数量
  }

  // 获取忌做的事情
  getUnsuitableActivities(lunar) {
    const activities = []
    
    const day = lunar.getDay()
    const month = lunar.getMonth()
    
    // 基础忌做事项
    activities.push('动土', '破土')
    
    // 根据日期添加特定事项
    if (day === 7 || day === 14 || day === 21 || day === 28) {
      activities.push('安葬', '入殓')
    }
    
    if (day % 4 === 0) {
      activities.push('嫁娶', '开市')
    }
    
    if (day % 6 === 0) {
      activities.push('出行', '移徙')
    }
    
    // 特殊日期
    if (month === 7 && day === 15) {
      activities.push('嫁娶', '开市')
    }
    
    return activities.slice(0, 6) // 限制数量
  }

  // 获取日期描述
  getDayDescription(lunar) {
    const day = lunar.getDay()
    const month = lunar.getMonth()
    
    const descriptions = [
      '今日宜静不宜动，适合修身养性',
      '今日运势不错，适合开展新项目',
      '今日适合与人交往，增进感情',
      '今日财运亨通，适合投资理财',
      '今日适合学习进修，提升自我',
      '今日适合运动健身，保持健康',
      '今日适合整理家务，清洁环境',
      '今日适合与家人团聚，享受天伦',
      '今日适合户外活动，亲近自然',
      '今日适合冥想打坐，净化心灵'
    ]
    
    return descriptions[day % descriptions.length]
  }

  // 获取节日信息
  getFestivals(lunar) {
    const festivals = []
    const day = lunar.getDay()
    const month = lunar.getMonth()
    
    // 传统节日
    if (month === 1 && day === 1) {
      festivals.push('春节')
    }
    
    if (month === 1 && day === 15) {
      festivals.push('元宵节')
    }
    
    if (month === 2 && day === 2) {
      festivals.push('龙抬头')
    }
    
    if (month === 5 && day === 5) {
      festivals.push('端午节')
    }
    
    if (month === 7 && day === 7) {
      festivals.push('七夕节')
    }
    
    if (month === 8 && day === 15) {
      festivals.push('中秋节')
    }
    
    if (month === 9 && day === 9) {
      festivals.push('重阳节')
    }
    
    if (month === 12 && day === 8) {
      festivals.push('腊八节')
    }
    
    if (month === 12 && day === 23) {
      festivals.push('小年')
    }
    
    return festivals
  }

  // 获取天气信息（需要配置天气API）
  async getWeatherInfo(date) {
    try {
      // 这里需要配置天气API，比如和风天气、高德天气等
      // const response = await axios.get(`https://api.weatherapi.com/v1/forecast.json?key=YOUR_API_KEY&q=Beijing&dt=${this.formatDate(date)}`)
      // return response.data
      
      // 临时返回模拟数据
      return {
        condition: '晴天',
        temperature: '20°C',
        humidity: '60%',
        wind: '微风'
      }
    } catch (error) {
      console.error('获取天气信息失败:', error)
      return null
    }
  }

  // 格式化日期
  formatDate(date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  }

  // 获取默认黄历信息
  getDefaultLunarInfo(date) {
    return {
      date: date,
      lunarDate: '获取失败',
      year: date.getFullYear(),
      month: date.getMonth() + 1,
      day: date.getDate(),
      yearName: '未知',
      monthName: '未知',
      dayName: '未知',
      zodiac: '未知',
      constellation: '未知',
      suitable: ['祭祀', '祈福'],
      unsuitable: ['动土', '破土'],
      description: '今日宜静不宜动',
      festivals: []
    }
  }

  // 清除缓存
  clearCache() {
    this.lunarCache.clear()
  }

  // 获取农历月份天数
  getLunarMonthDays(year, month) {
    try {
      const lunar = Lunar.fromYmd(year, month, 1)
      return lunar.getMonthDays()
    } catch (error) {
      console.error('获取农历月份天数失败:', error)
      return 30
    }
  }

  // 获取农历年份信息
  getLunarYearInfo(year) {
    try {
      const lunar = Lunar.fromYmd(year, 1, 1)
      return {
        year: year,
        isLeap: lunar.getYearLeap(),
        leapMonth: lunar.getYearLeapMonth(),
        totalDays: lunar.getYearDays()
      }
    } catch (error) {
      console.error('获取农历年份信息失败:', error)
      return null
    }
  }
} 