// app.js
import { BirthdayService } from './services/birthday-service'
import { LunarService } from './services/lunar-service'
import { NotificationService } from './services/notification-service'

App({
  globalData: {
    userInfo: null,
    birthdayService: null,
    lunarService: null,
    notificationService: null
  },

  onLaunch() {
    console.log('生日提醒机器人启动')
    
    // 初始化服务
    this.globalData.birthdayService = new BirthdayService()
    this.globalData.lunarService = new LunarService()
    this.globalData.notificationService = new NotificationService()
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 启动定时任务
    this.startScheduledTasks()
  },

  onShow() {
    console.log('小程序显示')
  },

  onHide() {
    console.log('小程序隐藏')
  },

  onError(msg) {
    console.error('小程序错误:', msg)
  },

  // 检查登录状态
  checkLoginStatus() {
    wx.getSetting({
      success: (res) => {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: (res) => {
              this.globalData.userInfo = res.userInfo
            }
          })
        }
      }
    })
  },

  // 启动定时任务
  startScheduledTasks() {
    // 每天凌晨检查生日提醒
    this.checkBirthdayReminders()
    
    // 每小时检查一次
    setInterval(() => {
      this.checkBirthdayReminders()
    }, 60 * 60 * 1000)
  },

  // 检查生日提醒
  async checkBirthdayReminders() {
    try {
      const today = new Date()
      const birthdays = await this.globalData.birthdayService.getTodayBirthdays()
      
      if (birthdays.length > 0) {
        for (const birthday of birthdays) {
          await this.sendBirthdayWishes(birthday)
        }
      }
    } catch (error) {
      console.error('检查生日提醒失败:', error)
    }
  },

  // 发送生日祝福
  async sendBirthdayWishes(birthday) {
    try {
      const lunarInfo = await this.globalData.lunarService.getTodayLunar()
      const message = this.generateBirthdayMessage(birthday, lunarInfo)
      
      // 发送群消息
      await this.globalData.notificationService.sendGroupMessage(message)
      
      // 发送通知
      await this.globalData.notificationService.sendNotification({
        title: '生日提醒',
        content: `${birthday.name} 今天生日！`,
        data: { type: 'birthday', userId: birthday.userId }
      })
    } catch (error) {
      console.error('发送生日祝福失败:', error)
    }
  },

  // 生成生日祝福消息
  generateBirthdayMessage(birthday, lunarInfo) {
    const messages = [
      `🎉 今天是 ${birthday.name} 的生日！`,
      `🎂 祝 ${birthday.name} 生日快乐，身体健康，万事如意！`,
      `🌟 愿你的每一天都充满阳光和快乐！`,
      `📅 今日黄历：`,
      `农历：${lunarInfo.lunarDate}`,
      `宜：${lunarInfo.suitable.join('、')}`,
      `忌：${lunarInfo.unsuitable.join('、')}`,
      `💝 今天是个好日子，适合庆祝生日！`
    ]
    
    return messages.join('\n')
  }
}) 