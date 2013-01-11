# Game Jolt Trophy for Python 3.x
# by viniciusepiplon - vncastanheira@gmail.com
# version 0.4 beta

# This is a general Python module for manipulating user data and
# trophies (achievments) on GameJolt.
# Website: www.gamejolt.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.txt>.


import urllib.request
import hashlib
import json

class GameJoltTrophy(object):
	# The Class constructors. 
	# Username and user_token can be changed later, but the game id
	# and the private key must be defined first, as they won't change.
	def __init__(self, username, user_token, game_id, private_key):
		super(GameJoltTrophy, self).__init__()
		self.username = username
		self.user_token = user_token
		self.game_id = game_id
		self.private_key = private_key
		# The signature is modified during function calls.
		# Each URL request to GameJolt needs to generate a new signature.
		self.signature = None

#====== TOOLS ======#

	# Used for changing users, setting and/or fixing authentications
	def changeUsername(self, username):
		self.username = username
	# Used for changing users tokens, setting and/or fixing authentications
	def changeUserToken(self, user_token):
		self.user_token = user_token

	# Generates a signature from the url and returns the same address, with
	# the signature added to it
	# All singatures are generated with md5, but can be modified below.
	# This is the only function that generates the signature, so changing the
	# encoding to SHA1 or other format will affect all URL requests.
	def setSignature(self, url):
		link = url + str(self.private_key)
		link = link.encode('utf8')
		self.signature = hashlib.md5(link).hexdigest()
		url += '&'+'signature='+str(self.signature)
		return url

#====== USERS ======#
		
	# Fetches the infos of a user as a dictionary type.
	# ATTENTION: it returns the information for a single user and the
	# first of the list.
	# Support for a list of users will be implemented later.
	def fetchUserInfo(self):
		URL = 'http://gamejolt.com/api/game/v1/users/?format=json&game_id='+str(self.game_id)+'&'+'username='+str(self.username)
		URL = self.setSignature(URL)

		try:
			response = urllib.request.urlopen(URL)
			output = response.read().decode('utf8')
			dictionary = json.loads(output)['response']['users'][0]
			# Returns the parameters in a dictionary format
			# Then, the user defines how it will use the values received
			# Dictionary keys and values are strings
			return dictionary
		except URLError:
			print("Invalid URL")
		except UnicodeDecodeError:
			print("Error encoding to UTF-8")
		finally:
			print("Unknown Error.")

	def authenticateUser(self):
		URL = 'http://gamejolt.com/api/game/v1/users/auth/?format=json&game_id='+str(self.game_id)+'&'+'username='+str(self.username)+\
		'&'+'user_token='+str(self.user_token)
		URL = self.setSignature(URL)
		try:
			response = urllib.request.urlopen(URL)
			output = response.read().decode('utf8')
			# Since it returns a response in json format, checking if it is 
			# equal to true, in json language, makes it simpler to use in 
			# python programs, since the return value is a Python's boolean
			return (json.loads(output)['response']['success']) == 'true'
		except URLError:
			# Any URLError is considered a unsucessful authentication
			return False

#====== TROPHIES ======#

	# Fetch your trophies! Yay!
	def fetchTrophy(self, achieved=None, trophy=None):
		URL = 'http://gamejolt.com/api/game/v1/trophies/?format=json&'+\
		'game_id='+str(self.game_id)+'&'+'username='+str(self.username)+'&'+'user_token='+str(self.user_token)
		if achieved != None:
			URL += '&achieved='
			if achieved == True: URL += 'true'
			if achieved == False: URL += 'false'
		else:
			if trophy != None:
				if type(trophy) == int:
					URL += '&trophy_id='+str(trophy)+'&'
				elif type(trophy) == list:
					miniurl = '&trophy_id='
					for t in trophy:
						miniurl += str(t)+','
					miniurl = miniurl[:1]
					print(miniurl)
					URL += miniurl
				else:
					raise 'Invalid type for trophy: must be int or list.'

		URL = self.setSignature(URL)
		print(URL)
		response = urllib.request.urlopen(URL)
		output = response.read().decode('utf8')
		dictionary = json.loads(output)['response']
		# Returns the parameters in a dictionary format
		# Then, the user defines how it will use the values received
		# Dictionary keys and values are strings
		return dictionary

	# Sets a winning trophy for the user.
	# If the parameters are valid, returns True.
	# Otherwise, it returns False.
	# If an request error occurs, also returns False.
	def addAchieved(self, trophy_id):
		URL = 'http://gamejolt.com/api/game/v1/trophies/add-achieved/?'+\
		'game_id='+str(self.game_id)+'&'+'user_token='+str(self.user_token)+'&'+'username='+str(self.username)+\
		'&'+'trophy_id='+str(trophy_id)
		URL = self.setSignature(URL)

		try:
			response = urllib.request.urlopen(URL)
			return True
		except Exception:
			return False

#====== SCORES ======#

	def fetchScores(self, limit=10, table_id=None, user_info_only=False, ):
		URL = 'http://gamejolt.com/api/game/v1/scores/?format=json&game_id='+str(self.game_id)
		if user_info_only:
			URL += '&username='+str(self.username)+'&user_token='+str(self.user_token)
		# ID of the score table
		if table_id:
			URL += '&table_id='+str(table_id)
		# Maximum number of scores should be 100 according with the GJAPI
		if limit > 100:
			limit = 100
		URL += '&limit='+str(limit)

		URL = self.setSignature(URL)
		print(URL)
		response = urllib.request.urlopen(URL)
		output = response.read().decode('utf8')
		dictionary = json.loads(output)['response']
		# Returns the parameters in a dictionary format
		# Then, the user defines how it will use the values received
		# Dictionary keys and values are strings
		return dictionary

	# score: string with no blank spaces
	def addScores(self, score, sort, table_id=None, extra_data='', guest=False, guestname=''):
		URL = 'http://gamejolt.com/api/game/v1/scores/add/?format=json&game_id='+str(self.game_id)+\
		'&score='+str(score)+'&sort='+str(sort)
		if not guest:
			URL += '&username='+str(self.username)+'&user_token='+str(self.user_token)
		else:
			URL += '&guestname='+str(guestname)
		if extra_data:
			URL += '&extra_data='+extra_data
		if table_id:
			URL += '&table_id='+str(table_id)

		URL = self.setSignature(URL)
		print(URL)
		response = urllib.request.urlopen(URL)
		output = response.read().decode('utf8')
		dictionary = json.loads(output)['response']
		return dictionary

	# Returns a list of high score tables for a game.
	def scoreTable(self):
		URL = 'http://gamejolt.com/api/game/v1/scores/tables/?format=json&game_id='+str(self.game_id)
		URL = self.setSignature(URL)
		print(URL)
		response = urllib.request.urlopen(URL)
		output = response.read().decode('utf8')
		dictionary = json.loads(output)['response']
		return dictionary

#====== DATA STORE ======#

	# Untested. I don't know what key means and how I handle this, so I just setted the basic stuff.
	def dataFetch(self, key, user_info_only=False):
		URL = 'http://gamejolt.com/api/game/v1/data-store/?format=json&game_id='+str(self.game_id)+'&key='+str(key)
		if user_info_only:
			URL += '&username='+str(self.username)+'&user_token='+str(self.user_token)
		URL = self.setSignature(URL)
		response = urllib.request.urlopen(URL)
		output = response.read().decode('utf8')
		dictionary = json.loads(output)['response']
		return dictionary
