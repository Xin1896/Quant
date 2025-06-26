// services/notification-service.js
import axios from 'axios'

export class NotificationService {
  constructor() {
    this.config = {
      // 微信小程序配置
      appId: 'YOUR_APP_ID',
      appSecret: 'YOUR_APP_SECRET',
      
      // 企业微信配置（可选）
      corpId: 'YOUR_CORP_ID',
      corpSecret: 'YOUR_CORP_SECRET',
      agentId: 'YOUR_AGENT_ID',
      
      // 群聊配置
      groupIds: ['GROUP_ID_1', 'GROUP_ID_2'],
      
      // 通知配置
      enablePush: true,
      enableGroupMessage: true
    }
    
    this.accessToken = null
    this.tokenExpireTime = 0
  }

  // 获取访问令牌
  async getAccessToken() {
    const now = Date.now()
    
    if (this.accessToken && now < this.tokenExpireTime) {
      return this.accessToken
    }

    try {
      const response = await axios.get('https://api.weixin.qq.com/cgi-bin/token', {
        params: {
          grant_type: 'client_credential',
          appid: this.config.appId,
          secret: this.config.appSecret
        }
      })

      if (response.data.access_token) {
        this.accessToken = response.data.access_token
        this.tokenExpireTime = now + (response.data.expires_in - 300) * 1000 // 提前5分钟刷新
        return this.accessToken
      } else {
        throw new Error('获取访问令牌失败: ' + JSON.stringify(response.data))
      }
    } catch (error) {
      console.error('获取访问令牌失败:', error)
      throw error
    }
  }

  // 发送群消息
  async sendGroupMessage(message, groupId = null) {
    if (!this.config.enableGroupMessage) {
      console.log('群消息功能已禁用')
      return
    }

    try {
      const token = await this.getAccessToken()
      const targetGroupId = groupId || this.config.groupIds[0]
      
      // 发送文本消息到群聊
      const response = await axios.post(
        `https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=${token}`,
        {
          touser: targetGroupId,
          msgtype: 'text',
          text: {
            content: message
          }
        }
      )

      if (response.data.errcode === 0) {
        console.log('群消息发送成功')
        return true
      } else {
        console.error('群消息发送失败:', response.data)
        return false
      }
    } catch (error) {
      console.error('发送群消息失败:', error)
      return false
    }
  }

  // 发送通知
  async sendNotification(notification) {
    if (!this.config.enablePush) {
      console.log('推送通知功能已禁用')
      return
    }

    try {
      // 微信小程序订阅消息
      await this.sendSubscribeMessage(notification)
      
      // 企业微信通知（如果配置了）
      if (this.config.corpId) {
        await this.sendWorkWechatMessage(notification)
      }
      
      console.log('通知发送成功')
      return true
    } catch (error) {
      console.error('发送通知失败:', error)
      return false
    }
  }

  // 发送订阅消息
  async sendSubscribeMessage(notification) {
    try {
      const token = await this.getAccessToken()
      
      const response = await axios.post(
        `https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token=${token}`,
        {
          touser: notification.userId,
          template_id: 'YOUR_TEMPLATE_ID', // 需要申请订阅消息模板
          page: 'pages/index/index',
          data: {
            thing1: { value: notification.title },
            thing2: { value: notification.content },
            time3: { value: new Date().toLocaleString() }
          }
        }
      )

      if (response.data.errcode === 0) {
        console.log('订阅消息发送成功')
        return true
      } else {
        console.error('订阅消息发送失败:', response.data)
        return false
      }
    } catch (error) {
      console.error('发送订阅消息失败:', error)
      return false
    }
  }

  // 发送企业微信消息
  async sendWorkWechatMessage(notification) {
    try {
      const token = await this.getWorkWechatToken()
      
      const response = await axios.post(
        `https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=${token}`,
        {
          touser: '@all',
          msgtype: 'text',
          agentid: this.config.agentId,
          text: {
            content: `${notification.title}\n${notification.content}`
          }
        }
      )

      if (response.data.errcode === 0) {
        console.log('企业微信消息发送成功')
        return true
      } else {
        console.error('企业微信消息发送失败:', response.data)
        return false
      }
    } catch (error) {
      console.error('发送企业微信消息失败:', error)
      return false
    }
  }

  // 获取企业微信访问令牌
  async getWorkWechatToken() {
    try {
      const response = await axios.get('https://qyapi.weixin.qq.com/cgi-bin/gettoken', {
        params: {
          corpid: this.config.corpId,
          corpsecret: this.config.corpSecret
        }
      })

      if (response.data.access_token) {
        return response.data.access_token
      } else {
        throw new Error('获取企业微信访问令牌失败: ' + JSON.stringify(response.data))
      }
    } catch (error) {
      console.error('获取企业微信访问令牌失败:', error)
      throw error
    }
  }

  // 发送生日祝福消息
  async sendBirthdayWishes(birthday, lunarInfo) {
    const message = this.generateBirthdayMessage(birthday, lunarInfo)
    
    // 发送到所有配置的群
    for (const groupId of this.config.groupIds) {
      await this.sendGroupMessage(message, groupId)
    }
    
    // 发送个人通知
    await this.sendNotification({
      title: '🎉 生日提醒',
      content: `今天是 ${birthday.name} 的生日！`,
      userId: birthday.userId,
      data: { type: 'birthday', birthdayId: birthday.id }
    })
  }

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
    
    if (birthday.message) {
      messages.push(`💌 ${birthday.message}`)
    }
    
    return messages.join('\n')
  }

  // 发送黄历信息
  async sendLunarInfo(lunarInfo, groupId = null) {
    const message = this.generateLunarMessage(lunarInfo)
    return await this.sendGroupMessage(message, groupId)
  }

  // 生成黄历消息
  generateLunarMessage(lunarInfo) {
    const messages = [
      `📅 今日黄历 (${lunarInfo.date.toLocaleDateString()})`,
      `农历：${lunarInfo.lunarDate}`,
      `生肖：${lunarInfo.zodiac}`,
      `星座：${lunarInfo.constellation}`,
      `宜：${lunarInfo.suitable.join('、')}`,
      `忌：${lunarInfo.unsuitable.join('、')}`,
      `描述：${lunarInfo.description}`
    ]
    
    if (lunarInfo.festivals.length > 0) {
      messages.push(`节日：${lunarInfo.festivals.join('、')}`)
    }
    
    if (lunarInfo.weather) {
      messages.push(`天气：${lunarInfo.weather.condition} ${lunarInfo.weather.temperature}`)
    }
    
    return messages.join('\n')
  }

  // 批量发送消息
  async sendBatchMessages(messages, groupId = null) {
    const results = []
    
    for (const message of messages) {
      const result = await this.sendGroupMessage(message, groupId)
      results.push(result)
      
      // 避免发送过快
      await this.delay(1000)
    }
    
    return results
  }

  // 延迟函数
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  // 更新配置
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig }
  }

  // 获取配置
  getConfig() {
    return { ...this.config }
  }

  // 启用/禁用功能
  enableFeature(feature, enabled = true) {
    switch (feature) {
      case 'push':
        this.config.enablePush = enabled
        break
      case 'groupMessage':
        this.config.enableGroupMessage = enabled
        break
      default:
        console.warn('未知功能:', feature)
    }
  }
} 