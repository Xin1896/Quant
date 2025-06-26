import { BirthdayService } from '../../services/birthday-service'
import { LunarService } from '../../services/lunar-service'

Page({
  data: {
    todayLunar: null,
    todayBirthdays: [],
    upcomingBirthdays: [],
    loading: true,
    userInfo: null,
    hasUserInfo: false,
    canIUseGetUserProfile: false
  },

  onLoad() {
    if (wx.getUserProfile) {
      this.setData({
        canIUseGetUserProfile: true
      })
    }
    
    this.loadData()
  },

  onShow() {
    this.loadData()
  },

  // 加载数据
  async loadData() {
    this.setData({ loading: true })
    
    try {
      const birthdayService = getApp().globalData.birthdayService
      const lunarService = getApp().globalData.lunarService
      
      // 获取今日黄历
      const todayLunar = await lunarService.getTodayLunar()
      
      // 获取今日生日
      const todayBirthdays = birthdayService.getTodayBirthdays()
      
      // 获取即将到来的生日
      const upcomingBirthdays = birthdayService.getUpcomingBirthdays(7)
      
      this.setData({
        todayLunar,
        todayBirthdays,
        upcomingBirthdays,
        loading: false
      })
    } catch (error) {
      console.error('加载数据失败:', error)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    }
  },

  // 获取用户信息
  getUserProfile() {
    wx.getUserProfile({
      desc: '用于完善会员资料',
      success: (res) => {
        this.setData({
          userInfo: res.userInfo,
          hasUserInfo: true
        })
        getApp().globalData.userInfo = res.userInfo
      }
    })
  },

  // 获取用户信息（兼容旧版本）
  getUserInfo(e) {
    this.setData({
      userInfo: e.detail.userInfo,
      hasUserInfo: true
    })
    getApp().globalData.userInfo = e.detail.userInfo
  },

  // 跳转到生日管理页面
  goToBirthday() {
    wx.switchTab({
      url: '/pages/birthday/birthday'
    })
  },

  // 跳转到黄历页面
  goToCalendar() {
    wx.switchTab({
      url: '/pages/calendar/calendar'
    })
  },

  // 添加生日
  addBirthday() {
    wx.navigateTo({
      url: '/pages/birthday/add/add'
    })
  },

  // 查看生日详情
  viewBirthday(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/birthday/detail/detail?id=${id}`
    })
  },

  // 分享今日黄历
  shareLunar() {
    const { todayLunar } = this.data
    if (!todayLunar) return
    
    const message = `📅 今日黄历\n农历：${todayLunar.lunarDate}\n宜：${todayLunar.suitable.join('、')}\n忌：${todayLunar.unsuitable.join('、')}`
    
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  // 发送生日祝福
  async sendBirthdayWish(e) {
    const { id } = e.currentTarget.dataset
    const birthday = this.data.todayBirthdays.find(b => b.id === id)
    
    if (!birthday) return
    
    try {
      const notificationService = getApp().globalData.notificationService
      const lunarService = getApp().globalData.lunarService
      
      const lunarInfo = await lunarService.getTodayLunar()
      await notificationService.sendBirthdayWishes(birthday, lunarInfo)
      
      wx.showToast({
        title: '祝福已发送',
        icon: 'success'
      })
    } catch (error) {
      console.error('发送生日祝福失败:', error)
      wx.showToast({
        title: '发送失败',
        icon: 'error'
      })
    }
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadData().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 分享给朋友
  onShareAppMessage() {
    const { todayLunar } = this.data
    return {
      title: '生日提醒机器人 - 今日黄历',
      path: '/pages/index/index',
      imageUrl: '/images/share.png'
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    const { todayLunar } = this.data
    return {
      title: `今日黄历：${todayLunar?.lunarDate || '农历信息'} - 生日提醒机器人`,
      imageUrl: '/images/share.png'
    }
  }
}) 