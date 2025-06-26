// config/config.js

// 微信小程序配置
export const WECHAT_CONFIG = {
  // 小程序配置
  APP_ID: 'YOUR_APP_ID',
  APP_SECRET: 'YOUR_APP_SECRET',
  
  // 企业微信配置（可选）
  CORP_ID: 'YOUR_CORP_ID',
  CORP_SECRET: 'YOUR_CORP_SECRET',
  AGENT_ID: 'YOUR_AGENT_ID',
  
  // 群聊配置
  GROUP_IDS: ['GROUP_ID_1', 'GROUP_ID_2'],
  
  // 订阅消息模板ID
  TEMPLATE_ID: 'YOUR_TEMPLATE_ID'
}

// 功能开关配置
export const FEATURE_CONFIG = {
  // 消息功能
  ENABLE_PUSH: true,
  ENABLE_GROUP_MESSAGE: true,
  ENABLE_SUBSCRIBE_MESSAGE: true,
  ENABLE_WORK_WECHAT: false,
  
  // 生日功能
  ENABLE_BIRTHDAY_REMINDER: true,
  ENABLE_AUTO_SEND_WISHES: true,
  
  // 黄历功能
  ENABLE_LUNAR_CALENDAR: true,
  ENABLE_WEATHER_INFO: false,
  
  // 缓存配置
  ENABLE_CACHE: true,
  CACHE_EXPIRE_TIME: 24 * 60 * 60 * 1000 // 24小时
}

// 提醒配置
export const REMINDER_CONFIG = {
  // 默认提醒天数
  DEFAULT_REMINDER_DAYS: [0, 1, 7],
  
  // 提醒时间
  REMINDER_TIME: '09:00',
  
  // 消息模板
  BIRTHDAY_MESSAGE_TEMPLATE: [
    '🎉 今天是 {name} 的生日！',
    '🎂 祝 {name} 生日快乐，身体健康，万事如意！',
    '🌟 愿你的每一天都充满阳光和快乐！',
    '📅 今日黄历：',
    '农历：{lunarDate}',
    '宜：{suitable}',
    '忌：{unsuitable}',
    '💝 今天是个好日子，适合庆祝生日！'
  ],
  
  // 自定义祝福语
  CUSTOM_WISHES: [
    '生日快乐！愿你的生活如诗如画，美好如初！',
    '祝你生日快乐！愿你的笑容永远灿烂，幸福永远相伴！',
    '生日快乐！愿你的梦想都能实现，愿望都能成真！',
    '祝你生日快乐！愿你的每一天都充满惊喜和快乐！',
    '生日快乐！愿你的未来更加精彩，人生更加美好！'
  ]
}

// 黄历配置
export const LUNAR_CONFIG = {
  // 宜做事项
  SUITABLE_ACTIVITIES: [
    '祭祀', '祈福', '求嗣', '斋醮', '开光', '出行', '移徙',
    '开市', '交易', '纳财', '栽种', '纳畜', '入殓', '破土',
    '安葬', '嫁娶', '纳采', '订盟', '会亲友', '进人口',
    '出火', '拆卸', '修造', '动土', '上梁', '开柱眼',
    '纳畜', '造畜椆栖', '入殓', '除服', '成服', '移柩',
    '启钻', '安葬', '谢土', '除服', '成服'
  ],
  
  // 忌做事项
  UNSUITABLE_ACTIVITIES: [
    '动土', '破土', '安葬', '入殓', '嫁娶', '开市',
    '出行', '移徙', '纳采', '订盟', '会亲友', '进人口',
    '出火', '拆卸', '修造', '上梁', '开柱眼', '纳畜',
    '造畜椆栖', '除服', '成服', '移柩', '启钻', '谢土'
  ],
  
  // 传统节日
  TRADITIONAL_FESTIVALS: {
    '1-1': '春节',
    '1-15': '元宵节',
    '2-2': '龙抬头',
    '5-5': '端午节',
    '7-7': '七夕节',
    '8-15': '中秋节',
    '9-9': '重阳节',
    '12-8': '腊八节',
    '12-23': '小年'
  }
}

// 天气API配置
export const WEATHER_CONFIG = {
  // 天气API配置（可选）
  API_KEY: 'YOUR_WEATHER_API_KEY',
  API_URL: 'https://api.weatherapi.com/v1/forecast.json',
  CITY: 'Beijing',
  
  // 天气图标映射
  WEATHER_ICONS: {
    'sunny': '☀️',
    'cloudy': '☁️',
    'rainy': '🌧️',
    'snowy': '❄️',
    'foggy': '🌫️',
    'windy': '💨'
  }
}

// 存储键名配置
export const STORAGE_KEYS = {
  BIRTHDAYS: 'birthdays',
  USER_INFO: 'userInfo',
  SETTINGS: 'settings',
  CACHE: 'lunar_cache'
}

// 错误消息配置
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  API_ERROR: '接口调用失败，请稍后重试',
  PERMISSION_ERROR: '权限不足，请检查相关设置',
  DATA_ERROR: '数据加载失败，请刷新重试',
  SAVE_ERROR: '保存失败，请重试',
  DELETE_ERROR: '删除失败，请重试'
}

// 成功消息配置
export const SUCCESS_MESSAGES = {
  SAVE_SUCCESS: '保存成功',
  DELETE_SUCCESS: '删除成功',
  SEND_SUCCESS: '发送成功',
  UPDATE_SUCCESS: '更新成功'
}

// 开发环境配置
export const DEV_CONFIG = {
  // 调试模式
  DEBUG: true,
  
  // 模拟数据
  MOCK_DATA: false,
  
  // 日志级别
  LOG_LEVEL: 'info', // debug, info, warn, error
  
  // 测试配置
  TEST_MODE: false
}

// 导出所有配置
export default {
  WECHAT_CONFIG,
  FEATURE_CONFIG,
  REMINDER_CONFIG,
  LUNAR_CONFIG,
  WEATHER_CONFIG,
  STORAGE_KEYS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  DEV_CONFIG
} 