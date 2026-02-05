from flask import Flask, render_template, request, jsonify, session
import uuid
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 在生产环境中应该使用环境变量

# 存储游戏房间信息
games = {}
players = {}

class GomokuGame:
    def __init__(self, room_id):
        self.room_id = room_id
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.current_player = 1  # 1为黑子，2为白子
        self.game_status = "waiting"  # waiting, playing, finished
        self.players = {}  # {player_id: {'color': 1 or 2, 'name': str}}
        self.winner = None
        self.move_history = []
    
    def make_move(self, row, col, player_id):
        """下棋"""
        if self.board[row][col] != 0:
            return False, "该位置已有棋子"
        
        if self.players[player_id]['color'] != self.current_player:
            return False, "不是你的回合"
        
        self.board[row][col] = self.current_player
        self.move_history.append({
            'row': row,
            'col': col,
            'player': self.current_player,
            'timestamp': datetime.now().isoformat()
        })
        
        # 检查是否获胜
        if self.check_winner(row, col):
            self.game_status = "finished"
            self.winner = self.current_player
            return True, "获胜！"
        
        # 切换玩家
        self.current_player = 3 - self.current_player  # 1->2, 2->1
        return True, "成功"
    
    def check_winner(self, row, col):
        """检查是否有玩家获胜"""
        directions = [
            [(0, 1), (0, -1)],   # 水平
            [(1, 0), (-1, 0)],   # 垂直
            [(1, 1), (-1, -1)],  # 对角线 \
            [(1, -1), (-1, 1)]   # 对角线 /
        ]
        
        current_color = self.board[row][col]
        
        for direction_pair in directions:
            count = 1  # 包含当前棋子
            
            # 向两个方向检查
            for dx, dy in direction_pair:
                r, c = row + dx, col + dy
                while (0 <= r < 15 and 0 <= c < 15 and 
                       self.board[r][c] == current_color):
                    count += 1
                    r += dx
                    c += dy
            
            if count >= 5:
                return True
        
        return False
    
    def get_game_state(self):
        """获取游戏状态"""
        return {
            'board': self.board,
            'current_player': self.current_player,
            'game_status': self.game_status,
            'players': self.players,
            'winner': self.winner,
            'move_history': self.move_history[-5:]  # 只返回最近5步
        }
    
    def restart_game(self):
        """重新开始游戏"""
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.current_player = 1
        self.game_status = "playing" if len(self.players) == 2 else "waiting"
        self.winner = None
        self.move_history = []
        return self.get_game_state()

@app.route('/')
def index():
    """主页 - 大厅"""
    return render_template('lobby.html')

@app.route('/game/<room_id>')
def game_room(room_id):
    """游戏房间页面"""
    if room_id not in games:
        return "房间不存在", 404
    
    # 如果用户没有session，创建新的
    if 'player_id' not in session:
        session['player_id'] = str(uuid.uuid4())
    
    player_id = session['player_id']
    
    # 如果玩家不在游戏中，加入游戏
    if player_id not in games[room_id].players:
        game = games[room_id]
        if len(game.players) < 2:
            color = 1 if len(game.players) == 0 else 2
            game.players[player_id] = {
                'color': color,
                'name': f"玩家{len(game.players) + 1}"
            }
            
            if len(game.players) == 2:
                game.game_status = "playing"
        else:
            return "房间已满", 400
    
    return render_template('index.html', room_id=room_id)

@app.route('/api/create_room', methods=['POST'])
def create_room():
    """创建新房间"""
    room_id = str(uuid.uuid4())[:8]
    games[room_id] = GomokuGame(room_id)
    
    # 自动加入创建者
    if 'player_id' not in session:
        session['player_id'] = str(uuid.uuid4())
    
    player_id = session['player_id']
    games[room_id].players[player_id] = {
        'color': 1,
        'name': "房主"
    }
    
    return jsonify({'room_id': room_id})

@app.route('/api/join_room/<room_id>', methods=['POST'])
def join_room(room_id):
    """加入房间"""
    if room_id not in games:
        return jsonify({'error': '房间不存在'}), 404
    
    if 'player_id' not in session:
        session['player_id'] = str(uuid.uuid4())
    
    player_id = session['player_id']
    game = games[room_id]
    
    if len(game.players) >= 2:
        return jsonify({'error': '房间已满'}), 400
    
    if player_id in game.players:
        return jsonify({'success': True})
    
    color = 2  # 第二个玩家是白子
    game.players[player_id] = {
        'color': color,
        'name': f"玩家{len(game.players) + 1}"
    }
    
    if len(game.players) == 2:
        game.game_status = "playing"
    
    return jsonify({'success': True})

@app.route('/api/make_move/<room_id>', methods=['POST'])
def make_move(room_id):
    """下棋"""
    if room_id not in games:
        return jsonify({'error': '房间不存在'}), 404
    
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    if 'player_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    player_id = session['player_id']
    game = games[room_id]
    
    if player_id not in game.players:
        return jsonify({'error': '你不在这个游戏中'}), 403
    
    success, message = game.make_move(row, col, player_id)
    
    return jsonify({
        'success': success,
        'message': message,
        'game_state': game.get_game_state()
    })

@app.route('/api/game_state/<room_id>')
def get_game_state(room_id):
    """获取游戏状态"""
    if room_id not in games:
        return jsonify({'error': '房间不存在'}), 404
    
    game = games[room_id]
    return jsonify(game.get_game_state())

@app.route('/api/leave_room/<room_id>', methods=['POST'])
def leave_room(room_id):
    """离开房间"""
    if room_id in games and 'player_id' in session:
        player_id = session['player_id']
        if player_id in games[room_id].players:
            del games[room_id].players[player_id]
            
            # 如果房间没人了，删除房间
            if len(games[room_id].players) == 0:
                del games[room_id]
    
    return jsonify({'success': True})

@app.route('/api/restart_game/<room_id>', methods=['POST'])
def restart_game(room_id):
    """重新开始游戏"""
    if room_id not in games:
        return jsonify({'error': '房间不存在'}), 404
    
    game = games[room_id]
    new_state = game.restart_game()
    
    return jsonify({
        'success': True,
        'message': '游戏已重新开始',
        'game_state': new_state
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)