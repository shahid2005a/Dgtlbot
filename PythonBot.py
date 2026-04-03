import os
import subprocess
import shutil
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time
import json
from datetime import datetime, timedelta
import sys
import signal
import atexit
import platform
from collections import defaultdict

# ============ BANNER FUNCTION ============
def banner():
    # Mix of colors: Cyan, Yellow, Green, Purple, Blue
    colors = ["\033[1;36m", "\033[1;33m", "\033[1;32m", "\033[1;35m", "\033[1;34m"]
    
    lines = [
        "██████╗ ██╗   ██╗████████╗██╗  ██╗ ██████╗ ███╗   ██╗",
        "██╔══██╗╚██╗ ██╔╝╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║",
        "██████╔╝ ╚████╔╝    ██║   ███████║██║   ██║██╔██╗ ██║",
        "██╔═══╝   ╚██╔╝     ██║   ██╔══██║██║   ██║██║╚██╗██║",
        "██║        ██║      ██║   ██║  ██║╚██████╔╝██║ ╚████║",
        "╚═╝        ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝",
        "",
        "🔴 YouTube: https://www.youtube.com/@aryanafridi00",
        "🐙 GitHub:  https://github.com/shahid2005a"
    ]
    
    for i, line in enumerate(lines):
        if line and not line.startswith(("📺", "🐙")):
            color = colors[i % len(colors)]
            print(f"{color}{line}")
        elif line.startswith("📺"):
            print(f"\033[1;33m{line}\033[0m")
        elif line.startswith("🐙"):
            print(f"\033[1;34m{line}\033[0m")
        else:
            print(line)
    
    print("\033[0m")

    print("\033[1;32m        🐍 PYTHON BOT HOSTING 🐍")  # Green
    print("\033[1;36m        👨‍💻 Developed By : Aryan Afridi")  # Cyan
    print("\033[1;33m        🚀 Version       : 2.0")  # Yellow
    
    print("\033[1;34m" + "═" * 50)  # Blue
    print(f"\033[1;35m        📅 Started      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")  # Magenta
    
    # Python Version
    print(f"\033[1;36m        🐍 Python       : {sys.version.split()[0]}")
    
    # Platform
    print(f"        💻 Platform     : {platform.system()} {platform.release()}")
    
    print("\033[1;34m" + "═" * 50)  # Blue
    print("\033[0m")  # Reset color

# Call the banner
banner()

# ============ CONFIGURATION ============

# अपना बॉट टोकन यहाँ डालें
BOT_TOKEN = '1234567890'
bot = telebot.TeleBot(BOT_TOKEN)

# डेटाबेस फ़ाइल
DB_FILE = 'bot_database.json'
CONFIG_FILE = 'bot_config.json'

# यूजर डेटा स्टोरेज
user_files = {}
running_processes = {}
bot_stats = {
    'start_time': datetime.now().isoformat(),
    'total_executions': 0,
    'total_uploads': 0,
    'active_users': set(),
    'commands_used': defaultdict(int)
}

# Permanent bot storage
user_permanent_bots = {}

# कॉन्फ़िग लोड करें
def load_config():
    default_config = {
        'max_file_size': 10 * 1024 * 1024,
        'max_output_length': 4000,
        'auto_install_modules': True,
        'auto_start_bots': True,
        'admin_ids': [8416089909],
        'broadcast_enabled': True,
        'maintenance_mode': False
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
    except Exception as e:
        print(f"Config load error: {e}")
    
    return default_config

config = load_config()

# Android-compatible RAM and Storage Functions
def get_ram_usage():
    """Get RAM usage for Android"""
    try:
        if os.path.exists('/proc/meminfo'):
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().split()[0]
                        try:
                            meminfo[key] = int(value) * 1024
                        except:
                            pass
                
                total = meminfo.get('MemTotal', 0)
                available = meminfo.get('MemAvailable', meminfo.get('MemFree', total))
                used = total - available
                percent = (used / total * 100) if total > 0 else 0
                
                return {
                    'total': total,
                    'available': available,
                    'used': used,
                    'percent': percent,
                    'total_gb': total / (1024**3),
                    'used_gb': used / (1024**3),
                    'available_gb': available / (1024**3)
                }
    except:
        pass
    
    return {'total': 0, 'available': 0, 'used': 0, 'percent': 0, 'total_gb': 0, 'used_gb': 0, 'available_gb': 0}

def get_storage_usage():
    """Get storage usage"""
    try:
        stat = os.statvfs('/')
        total = stat.f_frsize * stat.f_blocks
        free = stat.f_frsize * stat.f_bfree
        used = total - free
        percent = (used / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'used': used,
            'free': free,
            'percent': percent,
            'total_gb': total / (1024**3),
            'used_gb': used / (1024**3),
            'free_gb': free / (1024**3)
        }
    except:
        return {'total': 0, 'used': 0, 'free': 0, 'percent': 0, 'total_gb': 0, 'used_gb': 0, 'free_gb': 0}

# कस्टम कीबोर्ड
def create_main_keyboard(user_id=None):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    buttons = [
        KeyboardButton("📤 UPLOAD FILE"),
        KeyboardButton("📂 MY FILES"),
        KeyboardButton("🔄 RUN AGAIN"),
        KeyboardButton("⏹️ STOP"),
        KeyboardButton("🗑️ DELETE"),
        KeyboardButton("📊 STATUS"),
        KeyboardButton("🤖 MY BOTS"),
        KeyboardButton("📊 SYSTEM STATS")
    ]
    
    if user_id in config.get('admin_ids', []):
        buttons.extend([
            KeyboardButton("👑 ADMIN"),
            KeyboardButton("📋 LOGS")
        ])
    
    markup.add(*buttons)
    return markup

def create_bots_keyboard(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    
    if user_id in user_permanent_bots and user_permanent_bots[user_id]:
        for idx, bot_info in enumerate(user_permanent_bots[user_id]):
            status = "🟢" if bot_info.get('running', False) else "🔴"
            markup.add(
                InlineKeyboardButton(f"{status} {bot_info['name'][:15]}", callback_data=f"bot_details_{idx}"),
                InlineKeyboardButton("⚙️", callback_data=f"bot_settings_{idx}")
            )
    
    markup.add(
        InlineKeyboardButton("🚀 START ALL", callback_data="start_all_bots"),
        InlineKeyboardButton("⏹️ STOP ALL", callback_data="stop_all_bots"),
        InlineKeyboardButton("🔄 RESTART ALL", callback_data="restart_all_bots"),
        InlineKeyboardButton("⚙️ AUTO-START", callback_data="auto_start_settings"),
        InlineKeyboardButton("📊 STATS", callback_data="bots_stats"),
        InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")
    )
    return markup

def create_bot_detail_keyboard(bot_index):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🚀 START", callback_data=f"bot_start_{bot_index}"),
        InlineKeyboardButton("⏹️ STOP", callback_data=f"bot_stop_{bot_index}"),
        InlineKeyboardButton("🔄 RESTART", callback_data=f"bot_restart_{bot_index}"),
        InlineKeyboardButton("📊 LOGS", callback_data=f"bot_logs_{bot_index}"),
        InlineKeyboardButton("🗑️ DELETE", callback_data=f"bot_delete_{bot_index}"),
        InlineKeyboardButton("🔙 BACK", callback_data="back_to_bots")
    )
    return markup

def create_admin_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 SERVER STATUS", callback_data="admin_server"),
        InlineKeyboardButton("👥 USER STATS", callback_data="admin_users"),
        InlineKeyboardButton("🤖 BOTS STATS", callback_data="admin_bots"),
        InlineKeyboardButton("📈 SYSTEM STATS", callback_data="admin_system"),
        InlineKeyboardButton("🔧 MAINTENANCE", callback_data="admin_maintenance"),
        InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast"),
        InlineKeyboardButton("🧹 CLEANUP", callback_data="admin_cleanup"),
        InlineKeyboardButton("📥 BACKUP", callback_data="admin_backup"),
        InlineKeyboardButton("⚙️ CONFIG", callback_data="admin_config"),
        InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")
    )
    return markup

def create_config_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔄 AUTO-INSTALL", callback_data="config_auto_install"),
        InlineKeyboardButton("🚀 AUTO-START", callback_data="config_auto_start"),
        InlineKeyboardButton("📢 BROADCAST", callback_data="config_broadcast"),
        InlineKeyboardButton("👮 ADMIN ADD", callback_data="config_admin_add"),
        InlineKeyboardButton("💾 SAVE CONFIG", callback_data="config_save"),
        InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin")
    )
    return markup

def check_code_security(file_path):
    dangerous_patterns = [
        'os.system', 'subprocess.call', 'subprocess.Popen',
        '__import__', 'eval(', 'exec(', 'compile(',
        'rm -rf', 'shutdown', 'reboot', 'halt'
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        
        found_dangerous = []
        for pattern in dangerous_patterns:
            if pattern in content:
                found_dangerous.append(pattern)
        
        return found_dangerous
    except:
        return []

def check_and_install_modules(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        builtin_modules = [
            'os', 'sys', 'math', 'datetime', 'json', 'random', 'time',
            're', 'collections', 'itertools', 'functools', 'typing',
            'string', 'hashlib', 'base64', 'csv', 'io', 'pathlib'
        ]
        
        required_external = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                continue
            
            if 'import' in line:
                if line.startswith('import '):
                    imports = line[7:].split(',')
                    for imp in imports:
                        module = imp.strip().split()[0].split('.')[0]
                        if module and module not in builtin_modules and module not in required_external:
                            required_external.append(module)
                
                elif line.startswith('from '):
                    parts = line.split('import')
                    if len(parts) >= 2:
                        module = parts[0][5:].strip().split()[0].split('.')[0]
                        if module and module not in builtin_modules and module not in required_external:
                            required_external.append(module)
        
        module_mapping = {
            'telegram': 'pyTelegramBotAPI',
            'bs4': 'beautifulsoup4',
            'PIL': 'Pillow',
            'cv2': 'opencv-python',
            'requests': 'requests',
            'flask': 'flask'
        }
        
        final_modules = []
        for module in required_external:
            if module in module_mapping:
                final_modules.append(module_mapping[module])
            else:
                final_modules.append(module)
        
        return list(set(final_modules))
        
    except Exception as e:
        print(f"Module check error: {e}")
        return []

def install_python_modules(modules):
    success = []
    failures = []
    
    for module in modules:
        try:
            module_name = module.split('-')[0].replace('.', '_')
            try:
                __import__(module_name)
                success.append(module)
                continue
            except ImportError:
                pass
            
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--quiet', module],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                success.append(module)
            else:
                failures.append(module)
                
        except Exception as e:
            failures.append(module)
    
    return success, failures

@bot.message_handler(commands=['start', 'help', 'menu'])
def send_welcome(message):
    user_id = message.from_user.id
    bot_stats['active_users'].add(user_id)
    bot_stats['commands_used']['start'] += 1
    
    welcome_text = f"""
🚀 *Python Bot Hosting* 🚀

👤 User: `{user_id}`
📅 Joined: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

*Features:*
• 🤖 Permanent Bot Hosting
• 📦 Auto Module Install
• 🔄 Auto Restart
• 🧠 RAM/Storage Monitor

*Commands:*
📤 UPLOAD FILE - Upload .py files
📂 MY FILES - View files
🤖 MY BOTS - Manage bots
📊 STATUS - Bot status
📊 SYSTEM STATS - System resources
    """
    
    bot.send_message(message.chat.id, welcome_text, 
                     parse_mode='Markdown', 
                     reply_markup=create_main_keyboard(user_id))
    save_database()

@bot.message_handler(func=lambda message: message.text == "📤 UPLOAD FILE")
def ask_for_upload(message):
    warning_text = """📤 *Send Python Bot File*

⚠️ *Limits:*
• Size: 10MB
• Time: 24×7
• Output: 4000 chars

✅ Auto-install modules
✅ Auto-restart on crash

File will run automatically after upload!"""
    
    bot.send_message(message.chat.id, warning_text, 
                     parse_mode='Markdown',
                     reply_markup=create_main_keyboard(message.from_user.id))

@bot.message_handler(func=lambda message: message.text == "📊 SYSTEM STATS")
def system_stats(message):
    user_id = message.from_user.id
    bot_stats['commands_used']['system_stats'] += 1
    
    ram = get_ram_usage()
    storage = get_storage_usage()
    
    stats_text = "📈 *System Statistics*\n\n"
    
    if ram['total_gb'] > 0:
        stats_text += "🧠 *RAM*\n"
        stats_text += f"├─ Total: {ram['total_gb']:.2f} GB\n"
        stats_text += f"├─ Used: {ram['used_gb']:.2f} GB ({ram['percent']:.1f}%)\n"
        stats_text += f"└─ Available: {ram['available_gb']:.2f} GB\n\n"
        
        bar_length = 20
        filled = int(bar_length * ram['percent'] / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        stats_text += f"   [{bar}] {ram['percent']:.1f}%\n\n"
    else:
        stats_text += "🧠 *RAM*\n   ℹ️ Not available\n\n"
    
    stats_text += "💾 *Storage*\n"
    stats_text += f"├─ Total: {storage['total_gb']:.2f} GB\n"
    stats_text += f"├─ Used: {storage['used_gb']:.2f} GB ({storage['percent']:.1f}%)\n"
    stats_text += f"└─ Free: {storage['free_gb']:.2f} GB\n\n"
    
    bar_length = 20
    filled = int(bar_length * storage['percent'] / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    stats_text += f"   [{bar}] {storage['percent']:.1f}%\n\n"
    
    stats_text += "🤖 *Bot Stats*\n"
    stats_text += f"├─ Users: {len(user_files)}\n"
    stats_text += f"├─ Files: {sum(len(f) for f in user_files.values())}\n"
    stats_text += f"├─ Permanent Bots: {sum(len(b) for b in user_permanent_bots.values())}\n"
    stats_text += f"└─ Running: {sum(1 for b in user_permanent_bots.values() for bot in b if bot.get('running'))}\n"
    
    if storage['percent'] > 90:
        stats_text += "\n⚠️ *CRITICAL: Storage Almost Full!* ⚠️\n"
        stats_text += "⚠️ Please delete old files immediately! ⚠️"
    elif storage['percent'] > 85:
        stats_text += "\n⚠️ *Warning: Low Storage Space!* ⚠️"
    
    bot.send_message(message.chat.id, stats_text, parse_mode='Markdown',
                    reply_markup=create_main_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "🤖 MY BOTS")
def my_bots_menu(message):
    user_id = message.from_user.id
    
    if user_id not in user_permanent_bots or not user_permanent_bots[user_id]:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📤 UPLOAD FILE", callback_data="upload_now"))
        
        bot.send_message(message.chat.id,
                        "🤖 *No permanent bots found!*\n\n"
                        "Upload a Python file and make it permanent.",
                        parse_mode='Markdown',
                        reply_markup=markup)
        return
    
    bots_text = "🤖 *Your Permanent Bots:*\n\n"
    for idx, bot_info in enumerate(user_permanent_bots[user_id], 1):
        status = "🟢" if bot_info.get('running', False) else "🔴"
        auto_start = "✅" if bot_info.get('auto_start', True) else "❌"
        
        bots_text += f"{idx}. {status} `{bot_info['name']}`\n"
        bots_text += f"   📅 Created: {bot_info['created_time']}\n"
        bots_text += f"   🔄 Auto-start: {auto_start}\n"
        if bot_info.get('last_start'):
            bots_text += f"   🕐 Last: {bot_info['last_start']}\n"
        bots_text += "\n"
    
    bot.send_message(message.chat.id, bots_text,
                    parse_mode='Markdown',
                    reply_markup=create_bots_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "📂 MY FILES")
def check_files(message):
    user_id = message.from_user.id
    
    if user_id in user_files and user_files[user_id]:
        files_list = "📂 *Your Files:*\n\n"
        markup = InlineKeyboardMarkup(row_width=3)
        
        for idx, file_info in enumerate(user_files[user_id], 1):
            is_permanent = False
            if user_id in user_permanent_bots:
                for bot_info in user_permanent_bots[user_id]:
                    if bot_info['file_path'] == file_info['path']:
                        is_permanent = True
                        break
            
            perm_status = "🤖" if is_permanent else ""
            status = "✅" if file_info.get('last_run_status') == 'success' else "❌" if file_info.get('last_run_status') == 'error' else "⏳"
            
            files_list += f"{idx}. {status}{perm_status} `{file_info['name']}`\n"
            files_list += f"   📅 Upload: {file_info['upload_time']}\n"
            files_list += f"   📏 Size: {file_info['size']/(1024**2):.1f} MB\n"
            files_list += "\n"
            
            markup.row(
                InlineKeyboardButton(f"▶️{idx}", callback_data=f"run_{idx-1}"),
                InlineKeyboardButton(f"🤖{idx}", callback_data=f"make_permanent_{idx-1}"),
                InlineKeyboardButton(f"🗑️{idx}", callback_data=f"delete_file_{idx-1}")
            )
        
        markup.row(
            InlineKeyboardButton("🗑️ DELETE ALL", callback_data="delete_all_files"),
            InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")
        )
        
        bot.send_message(message.chat.id, files_list, 
                        parse_mode='Markdown',
                        reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 
                        "❌ *No files found!*\nUpload a file first 📤",
                        parse_mode='Markdown',
                        reply_markup=create_main_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "🔄 RUN AGAIN")
def run_again(message):
    user_id = message.from_user.id
    
    if user_id in user_files and user_files[user_id]:
        last_file = None
        for file_info in reversed(user_files[user_id]):
            if 'last_run' in file_info:
                last_file = file_info
                break
        
        if last_file:
            bot.send_message(message.chat.id,
                           f"🔄 *Running:* `{last_file['name']}`",
                           parse_mode='Markdown')
            
            thread = threading.Thread(target=run_python_file, 
                                     args=(message.chat.id, user_id, 
                                           last_file['path'], last_file['name'], False))
            thread.start()
        else:
            bot.send_message(message.chat.id,
                           "❌ *No file has been run before!*",
                           parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id,
                        "❌ *No files found!*",
                        parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "⏹️ STOP")
def stop_script(message):
    user_id = message.from_user.id
    
    if user_id in running_processes and running_processes[user_id]:
        try:
            process = running_processes[user_id]
            process.terminate()
            time.sleep(1)
            if process.poll() is None:
                process.kill()
            
            del running_processes[user_id]
            
            bot.send_message(message.chat.id, 
                           "✅ *Script stopped successfully!*",
                           parse_mode='Markdown')
        except Exception as e:
            bot.send_message(message.chat.id, 
                           f"❌ *Error:* {str(e)}",
                           parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 
                       "ℹ️ *No script is running!*",
                       parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🗑️ DELETE")
def delete_files_menu(message):
    user_id = message.from_user.id
    
    if user_id in user_files and user_files[user_id]:
        markup = InlineKeyboardMarkup(row_width=2)
        
        for idx, file_info in enumerate(user_files[user_id]):
            markup.add(InlineKeyboardButton(
                f"🗑️ {file_info['name'][:20]}", 
                callback_data=f"delete_file_{idx}"
            ))
        
        markup.add(InlineKeyboardButton(
            "🗑️ DELETE ALL", 
            callback_data="delete_all_files"
        ))
        markup.add(InlineKeyboardButton(
            "🔙 BACK", 
            callback_data="back_to_main"
        ))
        
        bot.send_message(message.chat.id, 
                        "🗑️ *Select file to delete:*", 
                        parse_mode='Markdown',
                        reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 
                        "❌ *No files found!*",
                        parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📊 STATUS")
def check_status(message):
    user_id = message.from_user.id
    
    ram = get_ram_usage()
    storage = get_storage_usage()
    
    start_time = datetime.fromisoformat(bot_stats['start_time'])
    uptime = datetime.now() - start_time
    
    status_text = "📊 *System Status*\n\n"
    status_text += f"⏱️ Uptime: {str(uptime).split('.')[0]}\n"
    status_text += f"👤 Your ID: `{user_id}`\n\n"
    
    if ram['total_gb'] > 0:
        status_text += "🧠 *RAM*\n"
        status_text += f"├─ Used: {ram['used_gb']:.1f}/{ram['total_gb']:.1f} GB ({ram['percent']:.1f}%)\n"
        bar_length = 15
        filled = int(bar_length * ram['percent'] / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        status_text += f"└─ [{bar}]\n\n"
    else:
        status_text += "🧠 *RAM*\n   ℹ️ Not available\n\n"
    
    status_text += "💾 *Storage*\n"
    status_text += f"├─ Used: {storage['used_gb']:.1f}/{storage['total_gb']:.1f} GB ({storage['percent']:.1f}%)\n"
    bar_length = 15
    filled = int(bar_length * storage['percent'] / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    status_text += f"└─ [{bar}]\n\n"
    
    file_count = len(user_files.get(user_id, []))
    total_size = sum(f['size'] for f in user_files.get(user_id, []))
    status_text += f"📂 Your Files: {file_count} ({total_size/(1024**2):.1f} MB)\n"
    
    permanent_count = len(user_permanent_bots.get(user_id, []))
    running_bots = sum(1 for bot in user_permanent_bots.get(user_id, []) if bot.get('running'))
    status_text += f"🤖 Permanent Bots: {permanent_count} ({running_bots} running)\n"
    
    status_text += f"\n📈 Total Executions: {bot_stats.get('total_executions', 0)}\n"
    status_text += f"📤 Total Uploads: {bot_stats.get('total_uploads', 0)}\n"
    
    if storage['percent'] > 85:
        status_text += "\n⚠️ *Storage Alert!* ⚠️"
    
    bot.send_message(message.chat.id, status_text, 
                    parse_mode='Markdown',
                    reply_markup=create_main_keyboard(user_id))

@bot.message_handler(func=lambda message: message.text == "👑 ADMIN")
def admin_panel(message):
    user_id = message.from_user.id
    
    if user_id not in config.get('admin_ids', []):
        bot.send_message(message.chat.id,
                        "⛔ *Access Denied!*",
                        parse_mode='Markdown')
        return
    
    ram = get_ram_usage()
    storage = get_storage_usage()
    
    total_users = len(user_files)
    total_bots = sum(len(b) for b in user_permanent_bots.values())
    running_bots = sum(1 for bots in user_permanent_bots.values() for bot in bots if bot.get('running'))
    
    admin_text = f"""
👑 *Admin Panel*

📊 *Stats:*
• Users: {total_users}
• Bots: {total_bots} ({running_bots} running)
• Executions: {bot_stats.get('total_executions', 0)}
• Uploads: {bot_stats.get('total_uploads', 0)}

🧠 *Resources:*
• RAM: {ram['used_gb']:.1f}/{ram['total_gb']:.1f} GB ({ram['percent']:.1f}%)
• Storage: {storage['used_gb']:.1f}/{storage['total_gb']:.1f} GB ({storage['percent']:.1f}%)

Select an option below:
    """
    
    bot.send_message(message.chat.id, admin_text,
                    parse_mode='Markdown',
                    reply_markup=create_admin_keyboard())

@bot.message_handler(func=lambda message: message.text == "📋 LOGS")
def view_logs(message):
    user_id = message.from_user.id
    
    if user_id not in config.get('admin_ids', []):
        bot.send_message(message.chat.id,
                        "⛔ *Access Denied!*",
                        parse_mode='Markdown')
        return
    
    log_file = 'bot_logs.txt'
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.read()
        if len(logs) > 4000:
            logs = logs[-4000:]
        if not logs.strip():
            logs = "No logs available."
    else:
        logs = "No logs file found."
    
    bot.send_message(message.chat.id, f"📋 *Logs*\n```\n{logs}\n```",
                    parse_mode='Markdown')

@bot.message_handler(content_types=['document'])
def handle_py_file(message):
    user_id = message.from_user.id
    
    if config.get('maintenance_mode', False) and user_id not in config.get('admin_ids', []):
        bot.send_message(message.chat.id, "🔧 *Maintenance Mode*", parse_mode='Markdown')
        return
    
    if message.document.file_size > config['max_file_size']:
        bot.send_message(message.chat.id, 
                        f"❌ File too large! Max {config['max_file_size']//(1024*1024)}MB",
                        parse_mode='Markdown')
        return
    
    file_name = message.document.file_name
    if not file_name.endswith('.py'):
        bot.send_message(message.chat.id, "❌ Only Python (.py) files!", parse_mode='Markdown')
        return
    
    try:
        bot.send_message(message.chat.id, f"📥 Downloading `{file_name}`...", parse_mode='Markdown')
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        timestamp = int(time.time())
        safe_name = file_name.replace(' ', '_')
        file_path = f"user_{user_id}_{timestamp}_{safe_name}"
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        if user_id not in user_files:
            user_files[user_id] = []
        
        file_data = {
            'name': file_name,
            'path': file_path,
            'size': os.path.getsize(file_path),
            'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'run_count': 0,
            'last_run': None,
            'last_run_status': None
        }
        
        user_files[user_id].append(file_data)
        bot_stats['total_uploads'] += 1
        
        bot.send_message(message.chat.id, 
                        f"✅ *Uploaded!*\n`{file_name}`\nRunning now...",
                        parse_mode='Markdown')
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🤖 MAKE PERMANENT", callback_data=f"make_permanent_{len(user_files[user_id])-1}"),
            InlineKeyboardButton("▶️ RUN ONCE", callback_data=f"run_{len(user_files[user_id])-1}"),
            InlineKeyboardButton("⏰ LATER", callback_data="back_to_main")
        )
        
        bot.send_message(message.chat.id,
                        "🤖 *Make this a permanent bot?*\n24×7 with auto-restart!",
                        parse_mode='Markdown',
                        reply_markup=markup)
        
        thread = threading.Thread(target=run_python_file,
                                 args=(message.chat.id, user_id, file_path, file_name, False))
        thread.start()
        
        save_database()
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ *Error:* {str(e)}", parse_mode='Markdown')

def run_python_file(chat_id, user_id, file_path, file_name, is_permanent=False):
    try:
        file_index = None
        if user_id in user_files:
            for idx, file_info in enumerate(user_files[user_id]):
                if file_info['path'] == file_path:
                    file_index = idx
                    break
        
        if config.get('auto_install_modules', True):
            required_modules = check_and_install_modules(file_path)
            if required_modules:
                install_python_modules(required_modules)
        
        process = subprocess.Popen(
            ['python', '-u', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='ignore'
        )
        
        if is_permanent:
            if user_id in user_permanent_bots:
                for bot_info in user_permanent_bots[user_id]:
                    if bot_info['file_path'] == file_path:
                        bot_info['running'] = True
                        bot_info['process_id'] = process.pid
                        bot_info['last_start'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        break
            
            bot.send_message(chat_id, f"🚀 *Permanent Bot Started!*\n`{file_name}`\nPID: {process.pid}",
                           parse_mode='Markdown')
            
            thread = threading.Thread(target=monitor_permanent_bot,
                                     args=(process, user_id, file_path, chat_id, file_name))
            thread.daemon = True
            thread.start()
        else:
            running_processes[user_id] = process
            bot_stats['total_executions'] += 1
            
            start_time = time.time()
            output_lines = []
            error_lines = []
            
            def read_output():
                for line in iter(process.stdout.readline, ''):
                    if line:
                        output_lines.append(line)
            
            def read_error():
                for line in iter(process.stderr.readline, ''):
                    if line:
                        error_lines.append(line)
            
            output_thread = threading.Thread(target=read_output, daemon=True)
            error_thread = threading.Thread(target=read_error, daemon=True)
            output_thread.start()
            error_thread.start()
            
            process.wait()
            
            stdout = ''.join(output_lines)
            stderr = ''.join(error_lines)
            execution_time = time.time() - start_time
            
            if file_index is not None:
                user_files[user_id][file_index]['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_files[user_id][file_index]['run_count'] += 1
                user_files[user_id][file_index]['last_run_status'] = 'success' if process.returncode == 0 else 'error'
            
            result_text = f"✅ *Execution Complete!*\n`{file_name}`\n\n"
            
            max_output = config['max_output_length']
            
            if stdout:
                if len(stdout) > max_output:
                    result_text += f"📤 **Output:**\n```\n{stdout[:max_output]}...\n```\n"
                else:
                    result_text += f"📤 **Output:**\n```\n{stdout}\n```\n"
            
            if stderr:
                if len(stderr) > max_output:
                    result_text += f"❌ **Errors:**\n```\n{stderr[:max_output]}...\n```\n"
                else:
                    result_text += f"❌ **Errors:**\n```\n{stderr}\n```\n"
            
            result_text += f"⏱️ Time: {execution_time:.1f}s\n"
            
            bot.send_message(chat_id, result_text, parse_mode='Markdown',
                           reply_markup=create_main_keyboard(user_id))
            
            if user_id in running_processes:
                del running_processes[user_id]
        
        save_database()
        
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Error:* `{str(e)}`", parse_mode='Markdown')
        if user_id in running_processes:
            del running_processes[user_id]

def start_permanent_bot(user_id, bot_index, chat_id):
    try:
        if user_id in user_permanent_bots and bot_index < len(user_permanent_bots[user_id]):
            bot_info = user_permanent_bots[user_id][bot_index]
            file_path = bot_info['file_path']
            file_name = bot_info['name']
            
            if not os.path.exists(file_path):
                bot.send_message(chat_id, f"❌ File not found: `{file_name}`", parse_mode='Markdown')
                return
            
            process = subprocess.Popen(
                ['python', '-u', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='ignore'
            )
            
            bot_info['running'] = True
            bot_info['process_id'] = process.pid
            bot_info['last_start'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            bot_info['restart_count'] = bot_info.get('restart_count', 0) + 1
            
            bot.send_message(chat_id, f"🚀 *Bot Started!*\n`{file_name}`\nPID: {process.pid}",
                           parse_mode='Markdown')
            
            thread = threading.Thread(target=monitor_permanent_bot,
                                     args=(process, user_id, file_path, chat_id, file_name))
            thread.daemon = True
            thread.start()
            
            save_database()
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ *Error:* {str(e)}", parse_mode='Markdown')

def monitor_permanent_bot(process, user_id, file_path, chat_id, file_name):
    try:
        process.wait()
        
        should_restart = False
        if user_id in user_permanent_bots:
            for bot_info in user_permanent_bots[user_id]:
                if bot_info['file_path'] == file_path and bot_info.get('auto_start', True):
                    should_restart = True
                    break
        
        if should_restart:
            time.sleep(5)
            
            for bot_info in user_permanent_bots[user_id]:
                if bot_info['file_path'] == file_path:
                    bot_info['running'] = False
                    bot_info['process_id'] = None
                    break
            
            if chat_id:
                bot.send_message(chat_id, f"⚠️ *Bot Restarting*\n`{file_name}`", parse_mode='Markdown')
            
            time.sleep(5)
            
            for idx, bot_info in enumerate(user_permanent_bots[user_id]):
                if bot_info['file_path'] == file_path and bot_info.get('auto_start', True):
                    start_permanent_bot(user_id, idx, chat_id)
                    break
        else:
            for bot_info in user_permanent_bots[user_id]:
                if bot_info['file_path'] == file_path:
                    bot_info['running'] = False
                    bot_info['process_id'] = None
                    break
            
            save_database()
            
    except Exception as e:
        print(f"Monitor error: {e}")

def auto_start_all_bots():
    print("🚀 Auto-starting permanent bots...")
    for user_id in user_permanent_bots:
        for idx, bot_info in enumerate(user_permanent_bots[user_id]):
            if bot_info.get('auto_start', True) and not bot_info.get('running', False):
                try:
                    if os.path.exists(bot_info['file_path']):
                        process = subprocess.Popen(
                            ['python', '-u', bot_info['file_path']],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            bufsize=1,
                            encoding='utf-8',
                            errors='ignore'
                        )
                        
                        bot_info['running'] = True
                        bot_info['process_id'] = process.pid
                        bot_info['last_start'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        print(f"✅ Started: {bot_info['name']} (PID: {process.pid})")
                        
                        thread = threading.Thread(target=monitor_permanent_bot,
                                                args=(process, user_id, bot_info['file_path'], None, bot_info['name']))
                        thread.daemon = True
                        thread.start()
                        
                except Exception as e:
                    print(f"Error starting bot: {e}")
    save_database()

def ram_monitor_job():
    alert_sent = False
    while True:
        try:
            storage = get_storage_usage()
            
            if storage['percent'] > 85 and not alert_sent:
                for admin_id in config.get('admin_ids', []):
                    try:
                        bot.send_message(admin_id,
                                       f"⚠️ *STORAGE ALERT!*\n\n"
                                       f"Usage: {storage['percent']:.1f}%\n"
                                       f"Free: {storage['free_gb']:.2f} GB\n"
                                       f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                       parse_mode='Markdown')
                    except:
                        pass
                alert_sent = True
            elif storage['percent'] < 70:
                alert_sent = False
            
        except Exception as e:
            print(f"Monitor error: {e}")
        
        time.sleep(300)

def cleanup_old_files():
    deleted_count = 0
    current_time = time.time()
    
    for filename in os.listdir('.'):
        if filename.startswith('user_') and filename.endswith('.py'):
            try:
                if os.path.getmtime(filename) < (current_time - 86400):
                    os.remove(filename)
                    deleted_count += 1
            except:
                pass
    
    for user_id in list(user_files.keys()):
        valid_files = []
        for file_info in user_files[user_id]:
            if os.path.exists(file_info['path']):
                if os.path.getmtime(file_info['path']) > (current_time - 86400):
                    valid_files.append(file_info)
        if valid_files:
            user_files[user_id] = valid_files
        else:
            del user_files[user_id]
    
    return deleted_count

def scheduled_cleanup():
    while True:
        try:
            deleted = cleanup_old_files()
            if deleted > 0:
                print(f"Cleaned {deleted} old files")
            save_database()
        except Exception as e:
            print(f"Cleanup error: {e}")
        time.sleep(3600)

def auto_save_job():
    while True:
        try:
            save_database()
            time.sleep(300)
        except:
            time.sleep(60)

def load_database():
    global user_files, user_permanent_bots, bot_stats
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                user_files = {int(k): v for k, v in data.get('user_files', {}).items()}
                user_permanent_bots = {int(k): v for k, v in data.get('user_permanent_bots', {}).items()}
                bot_stats.update(data.get('bot_stats', {}))
                bot_stats['active_users'] = set(bot_stats.get('active_users', []))
            print(f"Loaded: {len(user_files)} users, {sum(len(b) for b in user_permanent_bots.values())} bots")
    except Exception as e:
        print(f"Load error: {e}")

def save_database():
    try:
        data = {
            'user_files': user_files,
            'user_permanent_bots': user_permanent_bots,
            'bot_stats': {
                'start_time': bot_stats['start_time'],
                'total_executions': bot_stats.get('total_executions', 0),
                'total_uploads': bot_stats.get('total_uploads', 0),
                'active_users': list(bot_stats.get('active_users', set())),
                'commands_used': dict(bot_stats['commands_used'])
            }
        }
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Save error: {e}")

def log_action(user_id, action, details=""):
    try:
        with open('bot_logs.txt', 'a') as f:
            f.write(f"[{datetime.now()}] User:{user_id} {action} {details}\n")
    except:
        pass

def add_admin_step(message):
    try:
        admin_id = int(message.text)
        if admin_id not in config['admin_ids']:
            config['admin_ids'].append(admin_id)
            bot.send_message(message.chat.id, f"✅ Admin {admin_id} added!")
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        else:
            bot.send_message(message.chat.id, f"ℹ️ Already exists!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid ID!")

def cleanup_on_exit():
    print("\n🛑 Shutting down...")
    save_database()
    print("✅ Saved. Goodbye!")

# CALLBACK HANDLER - FIXED BACK BUTTONS
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    
    try:
        # BACK BUTTONS - FIXED
        if call.data == "back_to_main":
            bot.edit_message_text(
                "🏠 *Main Menu*",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=create_main_keyboard(user_id)
            )
            bot.answer_callback_query(call.id)
            return
        
        elif call.data == "back_to_bots":
            bot.edit_message_text(
                "🤖 *Your Bots*",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=create_bots_keyboard(user_id)
            )
            bot.answer_callback_query(call.id)
            return
        
        elif call.data == "back_to_admin":
            ram = get_ram_usage()
            storage = get_storage_usage()
            total_users = len(user_files)
            total_bots = sum(len(b) for b in user_permanent_bots.values())
            running_bots = sum(1 for bots in user_permanent_bots.values() for bot in bots if bot.get('running'))
            
            admin_text = f"""
👑 *Admin Panel*

📊 *Stats:*
• Users: {total_users}
• Bots: {total_bots} ({running_bots} running)
• Executions: {bot_stats.get('total_executions', 0)}
• Uploads: {bot_stats.get('total_uploads', 0)}

🧠 *Resources:*
• RAM: {ram['used_gb']:.1f}/{ram['total_gb']:.1f} GB ({ram['percent']:.1f}%)
• Storage: {storage['used_gb']:.1f}/{storage['total_gb']:.1f} GB ({storage['percent']:.1f}%)

Select an option below:
            """
            bot.edit_message_text(
                admin_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=create_admin_keyboard()
            )
            bot.answer_callback_query(call.id)
            return
        
        # Handle file operations
        elif call.data.startswith('delete_file_'):
            idx = int(call.data.split('_')[2])
            if user_id in user_files and idx < len(user_files[user_id]):
                deleted = user_files[user_id].pop(idx)
                if os.path.exists(deleted['path']):
                    os.remove(deleted['path'])
                bot.answer_callback_query(call.id, f"✅ {deleted['name']} deleted!")
                bot.edit_message_text("✅ File deleted!", call.message.chat.id, call.message.message_id)
                save_database()
        
        elif call.data == 'delete_all_files':
            if user_id in user_files:
                for f in user_files[user_id]:
                    try:
                        if os.path.exists(f['path']):
                            os.remove(f['path'])
                    except:
                        pass
                user_files[user_id] = []
                bot.answer_callback_query(call.id, "✅ All files deleted!")
                bot.edit_message_text("✅ All files deleted!", call.message.chat.id, call.message.message_id)
                save_database()
        
        elif call.data.startswith('run_'):
            idx = int(call.data.split('_')[1])
            if user_id in user_files and idx < len(user_files[user_id]):
                file_info = user_files[user_id][idx]
                bot.answer_callback_query(call.id, f"▶️ Running {file_info['name']}")
                thread = threading.Thread(target=run_python_file,
                                         args=(call.message.chat.id, user_id,
                                               file_info['path'], file_info['name'], False))
                thread.start()
        
        elif call.data.startswith('make_permanent_'):
            idx = int(call.data.split('_')[2])
            if user_id in user_files and idx < len(user_files[user_id]):
                file_info = user_files[user_id][idx]
                
                if user_id not in user_permanent_bots:
                    user_permanent_bots[user_id] = []
                
                bot_info = {
                    'name': file_info['name'],
                    'file_path': file_info['path'],
                    'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'running': False,
                    'auto_start': True,
                    'last_start': None,
                    'restart_count': 0,
                    'process_id': None
                }
                
                user_permanent_bots[user_id].append(bot_info)
                bot.answer_callback_query(call.id, f"🤖 Permanent bot created!")
                bot.edit_message_text(f"✅ {file_info['name']} is now permanent!", 
                                    call.message.chat.id, call.message.message_id)
                save_database()
        
        # Handle bot operations
        elif call.data.startswith('bot_'):
            parts = call.data.split('_')
            if len(parts) >= 3:
                op = parts[1]
                idx = int(parts[2])
                
                if user_id in user_permanent_bots and idx < len(user_permanent_bots[user_id]):
                    bot_info = user_permanent_bots[user_id][idx]
                    
                    if op == 'details':
                        status = "🟢 RUNNING" if bot_info.get('running') else "🔴 STOPPED"
                        text = f"🤖 *{bot_info['name']}*\n\n"
                        text += f"Status: {status}\n"
                        text += f"Created: {bot_info['created_time']}\n"
                        text += f"Auto-start: {'✅' if bot_info.get('auto_start') else '❌'}\n"
                        if bot_info.get('last_start'):
                            text += f"Last: {bot_info['last_start']}\n"
                        text += f"Restarts: {bot_info.get('restart_count', 0)}"
                        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                                            parse_mode='Markdown', reply_markup=create_bot_detail_keyboard(idx))
                    
                    elif op == 'start':
                        bot.answer_callback_query(call.id, "🚀 Starting...")
                        thread = threading.Thread(target=start_permanent_bot,
                                                 args=(user_id, idx, call.message.chat.id))
                        thread.start()
                    
                    elif op == 'stop':
                        if bot_info.get('process_id'):
                            try:
                                os.kill(bot_info['process_id'], signal.SIGTERM)
                            except:
                                pass
                        bot_info['running'] = False
                        bot_info['process_id'] = None
                        bot.answer_callback_query(call.id, "⏹️ Stopped!")
                        bot.edit_message_text(f"✅ {bot_info['name']} stopped!",
                                            call.message.chat.id, call.message.message_id)
                        save_database()
                    
                    elif op == 'restart':
                        bot.answer_callback_query(call.id, "🔄 Restarting...")
                        if bot_info.get('process_id'):
                            try:
                                os.kill(bot_info['process_id'], signal.SIGTERM)
                            except:
                                pass
                        bot_info['running'] = False
                        bot_info['process_id'] = None
                        time.sleep(2)
                        thread = threading.Thread(target=start_permanent_bot,
                                                 args=(user_id, idx, call.message.chat.id))
                        thread.start()
                    
                    elif op == 'delete':
                        if bot_info.get('process_id'):
                            try:
                                os.kill(bot_info['process_id'], signal.SIGTERM)
                            except:
                                pass
                        user_permanent_bots[user_id].pop(idx)
                        bot.answer_callback_query(call.id, "🗑️ Deleted!")
                        bot.edit_message_text(f"✅ {bot_info['name']} deleted!",
                                            call.message.chat.id, call.message.message_id)
                        save_database()
        
        # Handle admin operations
        elif call.data.startswith('admin_'):
            action = call.data.replace('admin_', '')
            
            if action == 'server':
                ram = get_ram_usage()
                storage = get_storage_usage()
                text = "🖥️ *Server Status*\n\n"
                if ram['total_gb'] > 0:
                    text += f"🧠 RAM: {ram['used_gb']:.1f}/{ram['total_gb']:.1f} GB ({ram['percent']:.1f}%)\n"
                text += f"💾 Storage: {storage['used_gb']:.1f}/{storage['total_gb']:.1f} GB ({storage['percent']:.1f}%)\n"
                text += f"🐍 Python: {platform.python_version()}\n"
                text += f"📱 OS: {platform.system()}"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
                bot.answer_callback_query(call.id)
            
            elif action == 'users':
                total_users = len(user_files)
                active_users = len(bot_stats['active_users'])
                text = f"👥 *User Stats*\n\nTotal: {total_users}\nActive: {active_users}\nFiles: {sum(len(f) for f in user_files.values())}\nBots: {sum(len(b) for b in user_permanent_bots.values())}"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
                bot.answer_callback_query(call.id)
            
            elif action == 'bots':
                total_bots = sum(len(b) for b in user_permanent_bots.values())
                running_bots = sum(1 for bots in user_permanent_bots.values() for bot in bots if bot.get('running'))
                text = f"🤖 *Bot Stats*\n\nTotal: {total_bots}\nRunning: {running_bots}\nStopped: {total_bots - running_bots}"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
                bot.answer_callback_query(call.id)
            
            elif action == 'system':
                start = datetime.fromisoformat(bot_stats['start_time'])
                uptime = datetime.now() - start
                ram = get_ram_usage()
                storage = get_storage_usage()
                text = f"📈 *System Stats*\n\nUptime: {str(uptime).split('.')[0]}\n"
                text += f"Executions: {bot_stats.get('total_executions', 0)}\n"
                text += f"Uploads: {bot_stats.get('total_uploads', 0)}\n\n"
                if ram['total_gb'] > 0:
                    text += f"RAM: {ram['percent']:.1f}%\n"
                text += f"Storage: {storage['percent']:.1f}%"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
                bot.answer_callback_query(call.id)
            
            elif action == 'maintenance':
                text = "🔧 *Maintenance*\n\n"
                text += f"Mode: {'🔴 ACTIVE' if config.get('maintenance_mode') else '🟢 INACTIVE'}"
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("🔧 TOGGLE", callback_data="toggle_maintenance"))
                markup.add(InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin"))
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                                    parse_mode='Markdown', reply_markup=markup)
                bot.answer_callback_query(call.id)
            
            elif action == 'broadcast':
                text = "📢 *Broadcast*\n\nSend message to all users:"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
                msg = bot.send_message(call.message.chat.id, "📝 Type your broadcast message:")
                bot.register_next_step_handler(msg, broadcast_message)
                bot.answer_callback_query(call.id)
            
            elif action == 'cleanup':
                deleted = cleanup_old_files()
                bot.answer_callback_query(call.id, f"🧹 Cleaned {deleted} files")
                bot.edit_message_text(f"✅ Cleaned {deleted} old files!",
                                    call.message.chat.id, call.message.message_id)
            
            elif action == 'backup':
                try:
                    with open(DB_FILE, 'rb') as f:
                        bot.send_document(call.message.chat.id, f, caption="📥 Database Backup")
                    bot.answer_callback_query(call.id, "✅ Backup sent!")
                except:
                    bot.answer_callback_query(call.id, "❌ Backup failed!")
            
            elif action == 'config':
                config_text = "⚙️ *Configuration*\n\n"
                config_text += f"Auto Install: {'✅' if config.get('auto_install_modules') else '❌'}\n"
                config_text += f"Auto Start: {'✅' if config.get('auto_start_bots') else '❌'}\n"
                config_text += f"Broadcast: {'✅' if config.get('broadcast_enabled') else '❌'}\n"
                config_text += f"Admins: {len(config.get('admin_ids', []))}"
                bot.edit_message_text(config_text, call.message.chat.id, call.message.message_id,
                                    parse_mode='Markdown', reply_markup=create_config_keyboard())
                bot.answer_callback_query(call.id)
        
        elif call.data.startswith('config_'):
            action = call.data.replace('config_', '')
            
            if action == 'auto_install':
                config['auto_install_modules'] = not config.get('auto_install_modules', True)
                bot.answer_callback_query(call.id, f"✅ Auto-install: {'ON' if config['auto_install_modules'] else 'OFF'}")
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                handle_callback(type('Call', (), {'data': 'admin_config', 'from_user': call.from_user,
                                                 'message': call.message})())
            
            elif action == 'auto_start':
                config['auto_start_bots'] = not config.get('auto_start_bots', True)
                bot.answer_callback_query(call.id, f"✅ Auto-start: {'ON' if config['auto_start_bots'] else 'OFF'}")
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                handle_callback(type('Call', (), {'data': 'admin_config', 'from_user': call.from_user,
                                                 'message': call.message})())
            
            elif action == 'broadcast':
                config['broadcast_enabled'] = not config.get('broadcast_enabled', True)
                bot.answer_callback_query(call.id, f"✅ Broadcast: {'ON' if config['broadcast_enabled'] else 'OFF'}")
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                handle_callback(type('Call', (), {'data': 'admin_config', 'from_user': call.from_user,
                                                 'message': call.message})())
            
            elif action == 'admin_add':
                msg = bot.send_message(call.message.chat.id, "Send admin ID (numeric):")
                bot.register_next_step_handler(msg, add_admin_step)
                bot.answer_callback_query(call.id)
            
            elif action == 'save':
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                bot.answer_callback_query(call.id, "✅ Config saved!")
        
        elif call.data == 'start_all_bots':
            if user_id in user_permanent_bots:
                count = 0
                for idx in range(len(user_permanent_bots[user_id])):
                    if not user_permanent_bots[user_id][idx].get('running'):
                        thread = threading.Thread(target=start_permanent_bot,
                                                 args=(user_id, idx, call.message.chat.id))
                        thread.start()
                        count += 1
                        time.sleep(1)
                bot.answer_callback_query(call.id, f"🚀 Starting {count} bots...")
        
        elif call.data == 'stop_all_bots':
            if user_id in user_permanent_bots:
                for bot_info in user_permanent_bots[user_id]:
                    if bot_info.get('process_id'):
                        try:
                            os.kill(bot_info['process_id'], signal.SIGTERM)
                        except:
                            pass
                    bot_info['running'] = False
                    bot_info['process_id'] = None
                save_database()
                bot.answer_callback_query(call.id, "⏹️ All bots stopped!")
        
        elif call.data == 'restart_all_bots':
            if user_id in user_permanent_bots:
                for bot_info in user_permanent_bots[user_id]:
                    if bot_info.get('process_id'):
                        try:
                            os.kill(bot_info['process_id'], signal.SIGTERM)
                        except:
                            pass
                    bot_info['running'] = False
                    bot_info['process_id'] = None
                time.sleep(2)
                for idx in range(len(user_permanent_bots[user_id])):
                    thread = threading.Thread(target=start_permanent_bot,
                                             args=(user_id, idx, call.message.chat.id))
                    thread.start()
                    time.sleep(1)
                bot.answer_callback_query(call.id, "🔄 Restarting all bots...")
        
        elif call.data == 'auto_start_settings':
            if user_id in user_permanent_bots:
                markup = InlineKeyboardMarkup(row_width=1)
                for idx, bot_info in enumerate(user_permanent_bots[user_id]):
                    status = "✅" if bot_info.get('auto_start', True) else "❌"
                    markup.add(InlineKeyboardButton(f"{status} {bot_info['name'][:20]}", 
                                                   callback_data=f"toggle_auto_{idx}"))
                markup.add(InlineKeyboardButton("🔙 BACK", callback_data="back_to_bots"))
                bot.edit_message_text("⚙️ *Auto-Start Settings*", call.message.chat.id, call.message.message_id,
                                    parse_mode='Markdown', reply_markup=markup)
                bot.answer_callback_query(call.id)
        
        elif call.data == 'bots_stats':
            if user_id in user_permanent_bots:
                running = sum(1 for bot in user_permanent_bots[user_id] if bot.get('running'))
                auto = sum(1 for bot in user_permanent_bots[user_id] if bot.get('auto_start', True))
                restarts = sum(bot.get('restart_count', 0) for bot in user_permanent_bots[user_id])
                text = f"📊 *Bot Stats*\n\nTotal: {len(user_permanent_bots[user_id])}\nRunning: {running}\nAuto-start: {auto}\nTotal restarts: {restarts}"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
                bot.answer_callback_query(call.id)
        
        elif call.data.startswith('toggle_auto_'):
            idx = int(call.data.split('_')[2])
            if user_id in user_permanent_bots and idx < len(user_permanent_bots[user_id]):
                current = user_permanent_bots[user_id][idx].get('auto_start', True)
                user_permanent_bots[user_id][idx]['auto_start'] = not current
                save_database()
                bot.answer_callback_query(call.id, f"✅ Auto-start: {'ON' if not current else 'OFF'}")
                handle_callback(type('Call', (), {'data': 'auto_start_settings', 'from_user': call.from_user,
                                                 'message': call.message})())
        
        elif call.data == 'toggle_maintenance':
            config['maintenance_mode'] = not config.get('maintenance_mode', False)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            bot.answer_callback_query(call.id, f"✅ Maintenance: {'ON' if config['maintenance_mode'] else 'OFF'}")
            handle_callback(type('Call', (), {'data': 'admin_maintenance', 'from_user': call.from_user,
                                             'message': call.message})())
        
        elif call.data == 'upload_now':
            ask_for_upload(call.message)
            bot.answer_callback_query(call.id)
        
        else:
            bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Callback error: {e}")
        try:
            bot.answer_callback_query(call.id, f"❌ Error")
        except:
            pass

def broadcast_message(message):
    user_id = message.from_user.id
    if user_id not in config.get('admin_ids', []):
        return
    
    if not config.get('broadcast_enabled', True):
        bot.send_message(message.chat.id, "❌ Broadcast is disabled!")
        return
    
    msg_text = message.text
    if not msg_text:
        return
    
    count = 0
    for uid in user_files.keys():
        try:
            bot.send_message(uid, f"📢 *Announcement*\n\n{msg_text}", parse_mode='Markdown')
            count += 1
            time.sleep(0.1)
        except:
            pass
    
    bot.send_message(message.chat.id, f"✅ Broadcast sent to {count} users!")

atexit.register(cleanup_on_exit)

if __name__ == '__main__':
    print("🚀 Python Bot Hosting starting...")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    load_database()
    
    ram = get_ram_usage()
    storage = get_storage_usage()
    if ram['total_gb'] > 0:
        print(f"🧠 RAM: {ram['used_gb']:.1f}/{ram['total_gb']:.1f} GB ({ram['percent']:.1f}%)")
    print(f"💾 Storage: {storage['used_gb']:.1f}/{storage['total_gb']:.1f} GB ({storage['percent']:.1f}%)")
    
    if storage['percent'] > 90:
        print("⚠️ WARNING: Storage is critically low!")
    elif storage['percent'] > 85:
        print("⚠️ WARNING: Storage is running low!")
    
    if config.get('auto_start_bots', True):
        auto_start_all_bots()
    
    cleanup_thread = threading.Thread(target=scheduled_cleanup, daemon=True)
    cleanup_thread.start()
    
    autosave_thread = threading.Thread(target=auto_save_job, daemon=True)
    autosave_thread.start()
    
    monitor_thread = threading.Thread(target=ram_monitor_job, daemon=True)
    monitor_thread.start()
    
    print("🤖 Bot started! Press Ctrl+C to stop")
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=30)
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Restarting in 5 seconds...")
            time.sleep(5)
