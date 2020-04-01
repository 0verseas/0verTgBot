#!/usr/bin/env python3


from telegram.ext import Updater, CommandHandler
from configparser import ConfigParser
import requests
import time
import threading


env = ConfigParser()
env.read('env.ini')
telegram_bot_token = env['inspector']['telegram_bot_token']


listen_status = True;


updater = Updater(token=telegram_bot_token)  # 呼叫 bot 用


# 確認使用者是否為指定的 telegram 管理員
def is_telegram_admin(telegram_user_id):
	telegram_user_id = str(telegram_user_id)  # 當前使用者 user id
	telegram_admins = [str_val for str_val in env['inspector']['telegram_admin_id'].split(',')]
	return telegram_user_id in telegram_admins


def show_user_info(bot, update):
	user_info = ''
	user_info = user_info + '發送人 first name：{}\n'.format(update.message.from_user.first_name)
	user_info = user_info + '發送人 last name：{}\n'.format(update.message.from_user.last_name)
	user_info = user_info + '發送人 full name：{}\n'.format(update.message.from_user.full_name)
	user_info = user_info + '發送人 username：{}\n'.format(update.message.from_user.username)
	user_info = user_info + '發送人 id：{}\n'.format(update.message.from_user.id)
	user_info = user_info + 'message_id：{}\n'.format(update.message.message_id)
	user_info = user_info + '所在的聊天室 id：{}\n'.format(update.message.chat.id)
	user_info = user_info + '所在的聊天室 type：{}\n'.format(update.message.chat.type)
	user_info = user_info + '訊息內容：{}\n'.format(update.message.text)
	
	update.message.reply_text(user_info)


def bot_status(bot, update):
	now_status = ''
	if listen_system.is_alive():
		now_status = now_status + '監視系統中\n'
	else:
		now_status = now_status + '放系統自己吃草\n'

	update.message.reply_text(now_status)


def start_work(bot, update):
	# 先檢查是不是 telegram 管理員
	if not is_telegram_admin(update.message.from_user.id):
		# 不是管理員用個X
		# TODO: 發通知到群組？
		update.message.reply_text('Permission denied!')
		return
	
	global listen_status
	listen_status = True
	if not listen_system.is_alive():
		listen_system.start()  # 開新執行緒
		# 確認執行緒是不是真的開啟了
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
		# TODO: 發通知到群組？
		update.message.reply_text('Permission denied!')
		return
	
	global listen_system, listen_status
	listen_status = False
	if not listen_system.is_alive():
		update.message.reply_text('Oh no, something went wrong.')
	else:
		listen_system.join()  # 關閉執行緒
		print("thread killed")
		listen_system = threading.Thread(target = listen)  # 重新設定執行緒
		if not listen_system.is_alive():
			update.message.reply_text('OK, now I get off work. YA~!')
		else:
			update.message.reply_text('Oh no, something went wrong.')


def listen():
	print('thread')
	while True:
		if listen_status:
			# TODO: 監視系統有沒有呼吸
			pass
		else:
			return


updater.dispatcher.add_handler(CommandHandler('info', show_user_info))  # 顯示使用者資訊
updater.dispatcher.add_handler(CommandHandler('status', bot_status))
updater.dispatcher.add_handler(CommandHandler('work', start_work))
updater.dispatcher.add_handler(CommandHandler('rest', unlisten))


listen_system = threading.Thread(target = listen)  # 採用多執行緒來監聽


updater.start_polling()
updater.idle()
