# 线上双人五子棋对战游戏

这是一个基于Flask框架开发的在线双人五子棋对战游戏，支持实时对战和房间管理功能。

## 功能特性

- 🎮 实时双人对战
- 🏠 房间管理系统
- 📱 响应式设计，支持移动端
- 🎯 完整的五子棋游戏规则
- 🔄 实时游戏状态同步
- 🏆 获胜检测和结果显示

## 技术栈

- **后端**: Python + Flask
- **前端**: HTML5 + CSS3 + JavaScript
- **实时通信**: AJAX轮询
- **会话管理**: Flask Session

## 项目结构

```
multiplayer_game/
├── app.py              # Flask主应用文件
├── requirements.txt    # Python依赖包
├── README.md          # 项目说明文档
├── templates/         # HTML模板文件
│   ├── index.html    # 游戏主界面
│   └── lobby.html    # 大厅页面
└── static/           # 静态资源文件
    ├── css/
    │   └── style.css # 样式文件
    └── js/
        └── game.js   # 游戏逻辑脚本
```

## 安装和运行

### 1. 环境要求

- Python 3.7+
- pip包管理器

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
python app.py
```

### 4. 访问应用

打开浏览器访问: http://localhost:5000

## 使用说明

### 创建房间
1. 进入大厅页面
2. 点击"创建房间"按钮
3. 系统会自动生成房间代码并跳转到游戏页面

### 加入房间
1. 进入大厅页面
2. 输入朋友提供的8位房间代码
3. 点击"加入房间"按钮

### 游戏规则
- 黑子先行
- 两位玩家轮流在15×15的棋盘上下棋
- 率先连成五子（横、竖、斜）的一方获胜
- 棋子必须下在棋盘的交叉点上

## API接口

### 房间管理
- `POST /api/create_room` - 创建新房间
- `POST /api/join_room/<room_id>` - 加入房间
- `POST /api/leave_room/<room_id>` - 离开房间

### 游戏操作
- `POST /api/make_move/<room_id>` - 下棋
- `GET /api/game_state/<room_id>` - 获取游戏状态

## 开发计划

- [ ] 添加WebSocket支持实现实时通信
- [ ] 增加聊天功能
- [ ] 添加游戏回放功能
- [ ] 实现AI对手模式
- [ ] 增加用户账户系统
- [ ] 添加游戏统计数据

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License