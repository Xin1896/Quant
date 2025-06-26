import { Lunar } from 'lunar-javascript'
import dayjs from 'dayjs'

export class BirthdayService {
  constructor() {
    this.birthdays = []
    this.loadBirthdays()
  }

  // 加载生日数据
  loadBirthdays() {
    try {
      const data = wx.getStorageSync('birthdays')
      this.birthdays = data || []
    } catch (error) {
      console.error('加载生日数据失败:', error)
      this.birthdays = []
    }
  }

  // 保存生日数据
  saveBirthdays() {
    try {
      wx.setStorageSync('birthdays', this.birthdays)
    } catch (error) {
      console.error('保存生日数据失败:', error)
    }
  }

  // 添加生日
  addBirthday(birthday) {
    const newBirthday = {
      id: Date.now().toString(),
      name: birthday.name,
      lunarMonth: birthday.lunarMonth,
      lunarDay: birthday.lunarDay,
      userId: birthday.userId,
      groupId: birthday.groupId,
      reminderDays: birthday.reminderDays || [0, 1, 7], // 提前提醒天数
      message: birthday.message || '',
      createdAt: new Date().toISOString()
    }

    this.birthdays.push(newBirthday)
    this.saveBirthdays()
    return newBirthday
  }

  // 更新生日
  updateBirthday(id, updates) {
    const index = this.birthdays.findIndex(b => b.id === id)
    if (index !== -1) {
      this.birthdays[index] = { ...this.birthdays[index], ...updates }
      this.saveBirthdays()
      return this.birthdays[index]
    }
    return null
  }

  // 删除生日
  deleteBirthday(id) {
    const index = this.birthdays.findIndex(b => b.id === id)
    if (index !== -1) {
      this.birthdays.splice(index, 1)
      this.saveBirthdays()
      return true
    }
    return false
  }

  // 获取所有生日
  getAllBirthdays() {
    return this.birthdays
  }

  // 获取今天的生日
  getTodayBirthdays() {
    const today = new Date()
    const lunarToday = Lunar.fromDate(today)
    
    return this.birthdays.filter(birthday => {
      return birthday.lunarMonth === lunarToday.getMonth() && 
             birthday.lunarDay === lunarToday.getDay()
    })
  }

  // 获取即将到来的生日
  getUpcomingBirthdays(days = 30) {
    const today = new Date()
    const upcoming = []

    for (let i = 0; i < days; i++) {
      const date = dayjs(today).add(i, 'day').toDate()
      const lunarDate = Lunar.fromDate(date)
      
      const birthdays = this.birthdays.filter(birthday => {
        return birthday.lunarMonth === lunarDate.getMonth() && 
               birthday.lunarDay === lunarDate.getDay()
      })

      if (birthdays.length > 0) {
        upcoming.push({
          date: date,
          lunarDate: lunarDate,
          birthdays: birthdays
        })
      }
    }

    return upcoming
  }

  // 农历转公历
  lunarToSolar(lunarMonth, lunarDay, year = new Date().getFullYear()) {
    try {
      const lunar = Lunar.fromYmd(year, lunarMonth, lunarDay)
      return lunar.getSolar().toDate()
    } catch (error) {
      console.error('农历转公历失败:', error)
      return null
    }
  }

  // 公历转农历
  solarToLunar(date) {
    try {
      const lunar = Lunar.fromDate(date)
      return {
        year: lunar.getYear(),
        month: lunar.getMonth(),
        day: lunar.getDay(),
        monthName: lunar.getMonthInChinese(),
        dayName: lunar.getDayInChinese()
      }
    } catch (error) {
      console.error('公历转农历失败:', error)
      return null
    }
  }

  // 获取生日距离今天的天数
  getDaysUntilBirthday(birthday) {
    const today = new Date()
    const lunarToday = Lunar.fromDate(today)
    
    // 计算今年的生日日期
    let birthdayYear = today.getFullYear()
    let birthdayDate = this.lunarToSolar(birthday.lunarMonth, birthday.lunarDay, birthdayYear)
    
    // 如果今年的生日已经过了，计算明年的
    if (birthdayDate < today) {
      birthdayYear++
      birthdayDate = this.lunarToSolar(birthday.lunarMonth, birthday.lunarDay, birthdayYear)
    }
    
    const diffTime = birthdayDate.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    return diffDays
  }

  // 检查是否需要提醒
  shouldRemind(birthday) {
    const daysUntil = this.getDaysUntilBirthday(birthday)
    return birthday.reminderDays.includes(daysUntil)
  }

  // 获取需要提醒的生日
  getReminderBirthdays() {
    return this.birthdays.filter(birthday => this.shouldRemind(birthday))
  }
} 