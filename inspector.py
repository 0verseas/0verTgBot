#!/usr/bin/env python3


from telegram.ext import Updater, CommandHandler
from configparser import ConfigParser
import requests
import time
import threading


env = ConfigParser()
env.read('env.ini')
telegram_bot_token = env['inspector']['telegram_bot_token']
system_urls = env['inspector']['sys_urls']
telegram_group_id = env['inspector']['telegram_group_id']


listen_status = True;


updater = Updater(token=telegram_bot_token)


# 確認使用者是否為指定的 telegram 管理員
def is_telegram_admin(telegram_user_id):
	telegram_user_id = str(telegram_user_id)  # 當前使用者 user id
	telegram_admins = [str_val for str_val in env['inspector']['telegram_admin_id'].split(',')]
	return telegram_user_id in telegram_admins


def show_user_info(bot, update):
	user_info = ''
	user_info = user_info + '發送人 full name：{}\n'.format(update.message.from_user.full_name)
	user_info = user_info + '發送人 username：{}\n'.format(update.message.from_user.username)
	user_info = user_info + '發送人 id：{}\n'.format(update.message.from_user.id)
	user_info = user_info + 'message_id：{}\n'.format(update.message.message_id)
	user_info = user_info + '所在的聊天室 id：{}\n'.format(update.message.chat.id)
	user_info = user_info + '所在的聊天室 type：{}\n'.format(update.message.chat.type)
	
	update.message.reply_text(user_info)


def bot_status(bot, update):
	now_status = ''
	if listen_system.is_alive():
		sys_url_list = [url for url in system_urls.split('、')]
		now_status = now_status + '監視系統中（request 間隔 1 分鐘）\n'
		for url in sys_url_list:
			now_status = now_status + url + '\n'
	else:
		now_status = now_status + '放系統自己吃草\n'

	update.message.reply_text(now_status)


def start_work(bot, update):
	# 先檢查是不是 telegram 管理員
	if not is_telegram_admin(update.message.from_user.id):
		# 不是管理員用個X
		bot.sendMessage(telegram_group_id, '使用者 {}（username：{}）在{}嘗試操作機器人遭拒'.format(update.message.from_user.full_name, update.message.from_user.username, time.strftime("%Y/%m/%d %H:%M:%S")))
		update.message.reply_text('Permission denied!')
		return
	
	global listen_status, listen_system
	listen_status = True
	if not listen_system.is_alive():
		listen_system = threading.Thread(target = listen, args=(bot,))
		listen_system.start()
		if listen_system.is_alive():
			update.message.reply_text('OK, I go to work now QQ.')
		else:
			update.message.reply_text('Oh no, something went wrong.')
	else:
		update.message.reply_text('我已經在工作崗位上了不要再叫我去上班了啦嗚嗚嗚')


def unlisten(bot, update):
	# 先檢查是不是 telegram 管理員
	if not is_telegram_admin(update.message.from_user.id):
		# 不是管理員用個X
		bot.sendMessage(telegram_group_id, '使用者 {}（username：{}）在{}嘗試操作機器人遭拒'.format(update.message.from_user.full_name, update.message.from_user.username, time.strftime("%Y/%m/%d %H:%M:%S")))
		update.message.reply_text('Permission denied!')
		return
	
	global listen_system, listen_status
	listen_status = False
	if not listen_system.is_alive():
		update.message.reply_text('Oh no, something went wrong.')
	else:
		listen_system.join()
		print("thread killed")
		listen_system = threading.Thread(target = listen)
		if not listen_system.is_alive():
			update.message.reply_text('OK, now I get off work. YA~!')
		else:
			update.message.reply_text('Oh no, something went wrong.')


def listen(bot):
	print('thread')
	sys_url_list = [url for url in system_urls.split('、')]
	listen_interval = 60  # 每個 request 間隔秒數
	while listen_status:
		for url in sys_url_list:
			if not listen_status:
				break

			try:
				print(time.strftime("%Y/%m/%d %H:%M:%S"), url)
				r = requests.get(url, timeout=10)
			except requests.exceptions.Timeout:
				print("=== Timeout! ===")
				bot.sendMessage(telegram_group_id, 'OMG! 連線逾時啦')
				raise
			except:
				print("=== Connect failed! ===")
				bot.sendMessage(telegram_group_id, 'OMG! 網路好像壞掉惹一段時間')
				raise
			else:
				if r.status_code != 200:
					print("↑ return", r.status_code)
					bot.sendMessage(telegram_group_id, 'OMG! ' + url + ' return ' +str(r.status_code))
					return
				time.sleep(listen_interval)
	return


updater.dispatcher.add_handler(CommandHandler('info', show_user_info))
updater.dispatcher.add_handler(CommandHandler('status', bot_status))
updater.dispatcher.add_handler(CommandHandler('work', start_work))
updater.dispatcher.add_handler(CommandHandler('rest', unlisten))


listen_system = threading.Thread(target = listen)

updater.start_polling()
updater.idle()
