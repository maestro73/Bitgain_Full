import asyncio, websockets, json, time, requests
from pprint import pprint

deribit_public = 'vwfyxeIV'
deribit_secret = 'RhGoowkhuL5Y-HqEqyzIU0Ss1UmKTg4v5DghS6Ld8iE'

async def call_deribit_market(size, side='buy',key='vwfyxeIV', secret='RhGoowkhuL5Y-HqEqyzIU0Ss1UmKTg4v5DghS6Ld8iE', test=True):

	auth_msg = {
		"jsonrpc" : "2.0",
		"id" : 9929,
		"method" : "public/auth",
		"params" : {
			"grant_type" : "client_credentials",
			"client_id" : key,
			"client_secret" : secret
		}
	}

	buy_msg = {   
		"jsonrpc" : "2.0",
		"id" : 5275,
		"method" : f"private/{side}",
		"params" : {
			"instrument_name" : "BTC-27DEC19",
			"amount" : f"{size}",
			"type" : "market",
			"label" : "market1238"
		}
	}

	api_url = 'wss://test.deribit.com/ws/api/v2'
	if test == False:
		api_url = 'wss://www.deribit.com/ws/api/v2'

	async with websockets.connect(api_url) as websocket:
		await websocket.send(json.dumps(auth_msg))
		response1 = await websocket.recv()
		
		await websocket.send(json.dumps(buy_msg))
		#while websocket.open:
		response2 = await websocket.recv()
		# do something with the response...
		#pprint(json.loads(response1))
		return(json.loads(response2))

async def call_deribit_limit(price, size=1000, side='buy', key='vwfyxeIV', secret='RhGoowkhuL5Y-HqEqyzIU0Ss1UmKTg4v5DghS6Ld8iE', test=True):

	auth_msg = {
		"jsonrpc" : "2.0",
		"id" : 9929,
		"method" : "public/auth",
		"params" : {
			"grant_type" : "client_credentials",
			"client_id" : key,
			"client_secret" : secret
		}
	}

	buy_msg = {   
		"jsonrpc" : "2.0",
		"id" : 5275,
		"method" : f"private/{side}",
		"params" : {
			"instrument_name" : "BTC-27DEC19",
			"amount" : f"{size}",
			"type" : "limit",
			"price": f"{price}",
			"label" : "limit1238"
		}
	}

	api_url = 'wss://test.deribit.com/ws/api/v2'
	if test == False:
		api_url = 'wss://www.deribit.com/ws/api/v2'

	async with websockets.connect(api_url) as websocket:
		await websocket.send(json.dumps(auth_msg))
		response1 = await websocket.recv()
		
		await websocket.send(json.dumps(buy_msg))
		#while websocket.open:
		response2 = await websocket.recv()
		# do something with the response...
		#pprint(json.loads(response1))
		#pprint(json.loads(response2))
		return(json.loads(response2))

async def call_deribit_auth(key, secret, test=True):

	auth_msg = {
		"jsonrpc" : "2.0",
		"id" : 9929,
		"method" : "public/auth",
		"params" : {
			"grant_type" : "client_credentials",
			"client_id" : key,
			"client_secret" : secret
		}
	}

	api_url = 'wss://test.deribit.com/ws/api/v2'
	if test == False:
		api_url = 'wss://www.deribit.com/ws/api/v2'

	async with websockets.connect(api_url) as websocket:
		await websocket.send(json.dumps(auth_msg))
		#while websocket.open:
		response = await websocket.recv()
		# do something with the response...
		pprint(json.loads(response))

async def call_deribit_btc_futures(test=True):

	msg = {
		"jsonrpc" : "2.0",
		"id" : 9344,
		"method" : "public/get_book_summary_by_currency",
			"params" : {
			"currency" : "BTC",
			"kind" : "future"
		}
	}

	api_url = 'wss://test.deribit.com/ws/api/v2'
	if test == False:
		api_url = 'wss://www.deribit.com/ws/api/v2'

	async with websockets.connect(api_url) as websocket:
		await websocket.send(json.dumps(msg))
		response = await websocket.recv()
		#while websocket.open:
			#response = await websocket.recv()
			# do something with the response...
		#pprint(response)
		return(json.loads(response))

async def get_order_state_by_id(order_id, test=True):

	msg = {
		"jsonrpc" : "2.0",
		"id" : 4316,
		"method" : "private/get_order_state",
		"params" : {
			"order_id" : order_id
		}
	}

	api_url = 'wss://test.deribit.com/ws/api/v2'
	if test == False:
		api_url = 'wss://www.deribit.com/ws/api/v2'

	async with websockets.connect(api_url) as websocket:
		###############
		# Before sending message, make sure that your connection
		# is authenticated (use public/auth call before) 
		###############
		await websocket.send(json.dumps(msg))
		response = await websocket.recv()
		# do something with the response...
		return(json.loads(response))

async def get_open_by_instrument(instrument, key='vwfyxeIV', secret='RhGoowkhuL5Y-HqEqyzIU0Ss1UmKTg4v5DghS6Ld8iE', test=True):
	msg = {
		"jsonrpc" : "2.0",
		"id" : 8442,
		"method" : "private/get_open_orders_by_instrument",
		"params" : {
			"instrument_name" : instrument
		}
	}

	auth_msg = {
		"jsonrpc" : "2.0",
		"id" : 9929,
		"method" : "public/auth",
		"params" : {
			"grant_type" : "client_credentials",
			"client_id" : key,
			"client_secret" : secret
		}
	}

	api_url = 'wss://test.deribit.com/ws/api/v2'
	if test == False:
		api_url = 'wss://www.deribit.com/ws/api/v2'

	async with websockets.connect(api_url) as websocket:
	###############
	# Before sending message, make sure that your connection
	# is authenticated (use public/auth call before) 
	###############
		await websocket.send(json.dumps(auth_msg))
		response1 = await websocket.recv()
		await websocket.send(json.dumps(msg))
		response = await websocket.recv()
		# do something with the response...
		return(json.loads(response))

async def close_deribit_d27(key='vwfyxeIV', secret='RhGoowkhuL5Y-HqEqyzIU0Ss1UmKTg4v5DghS6Ld8iE', test=True):
	msg = {
		"jsonrpc" : "2.0",
		"id" : 6130,
		"method" : "private/close_position",
		"params" : {
			"instrument_name" : "BTC-27DEC19",
			"type" : "market"
		}
	}

	auth_msg = {
		"jsonrpc" : "2.0",
		"id" : 9929,
		"method" : "public/auth",
		"params" : {
			"grant_type" : "client_credentials",
			"client_id" : key,
			"client_secret" : secret
		}
	}

	api_url = 'wss://test.deribit.com/ws/api/v2'
	if test == False:
		api_url = 'wss://www.deribit.com/ws/api/v2'

	async with websockets.connect(api_url) as websocket:
	###############
	# Before sending message, make sure that your connection
	# is authenticated (use public/auth call before) 
	###############
		await websocket.send(json.dumps(auth_msg))
		response1 = await websocket.recv()
		await websocket.send(json.dumps(msg))
		response = await websocket.recv()
		# do something with the response...
		return(json.loads(response))