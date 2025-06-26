import { BirthdayService } from '../../services/birthday-service'

Page({
  data: {
    birthdays: [],
    loading: true,
    searchText: '',
    filterType: 'all' // all, today, upcoming
  },

  onLoad() {
    this.loadBirthdays()
  },

  onShow() {
    this.loadBirthdays()
  },

  // 加载生日数据
  loadBirthdays() {
    this.setData({ loading: true })
    
    try {
      const birthdayService = getApp().globalData.birthdayService
      const allBirthdays = birthdayService.getAllBirthdays()
      
      this.setData({
        birthdays: allBirthdays,
        loading: false
      })
    } catch (error) {
      console.error('加载生日数据失败:', error)
      this.setData({ loading: false })
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    }
  },

  // 搜索生日
  onSearch(e) {
    const searchText = e.detail.value
    this.setData({ searchText })
    this.filterBirthdays()
  },

  // 切换筛选类型
  onFilterChange(e) {
    const filterType = e.currentTarget.dataset.type
    this.setData({ filterType })
    this.filterBirthdays()
  },

  // 筛选生日
  filterBirthdays() {
    const { searchText, filterType } = this.data
    const birthdayService = getApp().globalData.birthdayService
    let birthdays = birthdayService.getAllBirthdays()

    // 按类型筛选
    switch (filterType) {
      case 'today':
        birthdays = birthdayService.getTodayBirthdays()
        break
      case 'upcoming':
        birthdays = birthdayService.getUpcomingBirthdays(30)
          .flatMap(item => item.birthdays)
        break
      default:
        break
    }

    // 按搜索文本筛选
    if (searchText) {
      birthdays = birthdays.filter(birthday => 
        birthday.name.includes(searchText)
      )
    }

    this.setData({ birthdays })
  },

  // 添加生日
  addBirthday() {
    wx.navigateTo({
      url: '/pages/birthday/add/add'
    })
  },

  // 编辑生日
  editBirthday(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/birthday/edit/edit?id=${id}`
    })
  },

  // 删除生日
  deleteBirthday(e) {
    const { id, name } = e.currentTarget.dataset
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除 ${name} 的生日记录吗？`,
      success: (res) => {
        if (res.confirm) {
          try {
            const birthdayService = getApp().globalData.birthdayService
            const success = birthdayService.deleteBirthday(id)
            
            if (success) {
              wx.showToast({
                title: '删除成功',
                icon: 'success'
              })
              this.loadBirthdays()
            } else {
              wx.showToast({
                title: '删除失败',
                icon: 'error'
              })
            }
          } catch (error) {
            console.error('删除生日失败:', error)
            wx.showToast({
              title: '删除失败',
              icon: 'error'
            })
          }
        }
      }
    })
  },

  // 查看生日详情
  viewBirthday(e) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/birthday/detail/detail?id=${id}`
    })
  },

  // 发送生日祝福
  async sendBirthdayWish(e) {
    const { id } = e.currentTarget.dataset
    const birthday = this.data.birthdays.find(b => b.id === id)
    
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
    this.loadBirthdays().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 获取生日距离天数
  getDaysUntilBirthday(birthday) {
    const birthdayService = getApp().globalData.birthdayService
    return birthdayService.getDaysUntilBirthday(birthday)
  },

  // 格式化生日日期
  formatBirthdayDate(birthday) {
    return `农历${birthday.lunarMonth}月${birthday.lunarDay}日`
  }
}) 