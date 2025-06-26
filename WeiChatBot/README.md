# 生日提醒机器人 - 微信小程序

一个功能完整的微信小程序，用于生日提醒和黄历查询。支持农历生日管理、自动提醒、群消息发送等功能。

## 功能特性

### 🎂 生日管理
- 支持农历生日录入和管理
- 自动计算生日距离天数
- 生日提醒设置（提前1天、7天等）
- 生日祝福消息自定义

### 📅 黄历功能
- 实时农历日期显示
- 宜忌事项查询
- 传统节日提醒
- 生肖星座信息
- 天气信息集成

### 🤖 智能提醒
- 自动生日提醒
- 群消息发送
- 订阅消息推送
- 企业微信集成

### 💬 消息功能
- 群聊消息发送
- 生日祝福模板
- 黄历信息分享
- 批量消息处理

## 技术架构

### 核心服务
- `BirthdayService`: 生日管理服务
- `LunarService`: 黄历查询服务  
- `NotificationService`: 消息通知服务

### 依赖库
- `lunar-javascript`: 农历转换
- `dayjs`: 日期处理
- `axios`: HTTP请求

## 安装部署

### 1. 环境准备
```bash
# 安装依赖
npm install

# 或使用yarn
yarn install
```

### 2. 配置设置
在 `services/notification-service.js` 中配置：
```javascript
this.config = {
  appId: 'YOUR_APP_ID',           // 微信小程序AppID
  appSecret: 'YOUR_APP_SECRET',   // 微信小程序AppSecret
  corpId: 'YOUR_CORP_ID',         // 企业微信CorpID（可选）
  corpSecret: 'YOUR_CORP_SECRET', // 企业微信Secret（可选）
  agentId: 'YOUR_AGENT_ID',       // 企业微信应用ID（可选）
  groupIds: ['GROUP_ID_1'],       // 群聊ID列表
}
```

### 3. 微信开发者工具
1. 打开微信开发者工具
2. 导入项目目录
3. 配置AppID
4. 编译运行

## 使用说明

### 添加生日
1. 进入"生日管理"页面
2. 点击"添加生日"
3. 填写姓名和农历生日
4. 设置提醒时间
5. 保存

### 查看黄历
1. 首页显示今日黄历
2. 点击"黄历详情"查看完整信息
3. 支持分享黄历信息

### 消息配置
1. 在通知服务中配置群ID
2. 设置企业微信（可选）
3. 申请订阅消息模板
4. 配置消息发送权限

## 页面结构

```
pages/
├── index/          # 首页
├── birthday/       # 生日管理
├── calendar/       # 黄历详情
└── profile/        # 个人中心
```

## API接口

### 生日相关
- `getTodayBirthdays()`: 获取今日生日
- `getUpcomingBirthdays(days)`: 获取即将到来的生日
- `addBirthday(birthday)`: 添加生日
- `updateBirthday(id, updates)`: 更新生日
- `deleteBirthday(id)`: 删除生日

### 黄历相关
- `getTodayLunar()`: 获取今日黄历
- `getLunarByDate(date)`: 获取指定日期黄历
- `getSuitableActivities(lunar)`: 获取宜做事项
- `getUnsuitableActivities(lunar)`: 获取忌做事项

### 消息相关
- `sendGroupMessage(message, groupId)`: 发送群消息
- `sendNotification(notification)`: 发送通知
- `sendBirthdayWishes(birthday, lunarInfo)`: 发送生日祝福

## 配置说明

### 微信小程序配置
1. 在微信公众平台申请小程序
2. 获取AppID和AppSecret
3. 配置服务器域名
4. 申请订阅消息模板

### 企业微信配置（可选）
1. 注册企业微信
2. 创建应用
3. 获取CorpID和Secret
4. 配置应用权限

### 群聊配置
1. 获取群聊ID
2. 配置机器人权限
3. 设置消息发送频率

## 开发指南

### 添加新功能
1. 在对应服务中添加方法
2. 创建页面文件（.js/.wxml/.wxss）
3. 在app.json中注册页面
4. 更新导航和路由

### 自定义样式
1. 修改对应页面的.wxss文件
2. 使用rpx单位适配不同屏幕
3. 遵循微信小程序设计规范

### 调试测试
1. 使用微信开发者工具调试
2. 真机测试功能
3. 检查网络请求和权限

## 注意事项

1. **权限配置**: 确保小程序有发送消息的权限
2. **频率限制**: 遵守微信API调用频率限制
3. **数据安全**: 敏感信息不要硬编码在代码中
4. **用户体验**: 添加加载状态和错误处理
5. **兼容性**: 考虑不同微信版本的兼容性

## 更新日志

### v1.0.0
- 初始版本发布
- 基础生日管理功能
- 黄历查询功能
- 消息发送功能

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或联系开发者。 