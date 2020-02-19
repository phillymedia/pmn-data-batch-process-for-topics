#!/usr/bin/env python

"""
   Magnet API Client
   
   Compatible with Python 3.6
   
   Copyright 2018, Klangoo Inc.
"""

#import urllib	# python 2.x
import urllib.parse # python 3.x
import urllib.request # python 3.x
import hashlib
import hmac
import time
import base64 # python 3.x
 
class MagnetAPIClient:
	
	def __init__(self, endpoint_uri, calk, secret_key = None):
		self.endpoint_uri = endpoint_uri
		self.calk = calk
		self.secret_key = secret_key
		
	def callwebmethod(self, method_name, request, request_method):
		if self.__has_calk(request) == False:
			request['calk'] = self.calk
		
		signed_querystring = self.__get_signed_querystring(method_name, request, request_method)
		
		# python 2.x begin
		#if request_method.lower() == 'post':
		#	return urllib.urlopen(self.endpoint_uri + '/' + method_name, signed_querystring).read()
		#else:
		#	return urllib.urlopen(self.endpoint_uri + '/' + method_name + '?' + signed_querystring).read()
		# python 2.x end
		
		resp = None
		
		# python 3.x begin
		if request_method.lower() == 'post':
			with urllib.request.urlopen(self.endpoint_uri + '/' + method_name, signed_querystring.encode("utf-8")) as f:
				resp = f.read()
		else:
			with urllib.request.urlopen(self.endpoint_uri + '/' + method_name + '?' + signed_querystring) as f:
				resp = f.read()
		# python 3.x end
		
		return resp;
		
	""" Private Functions """
	def __get_signed_querystring(self, method_name, request, request_method):
		request['timestamp'] = self.__get_timestamp()
		
		# Construct the canonicalized query
		# The params need to be sorted by the key
		sortedRequest = self.__ksort(request)
		
		canonicalized_query = ''
		
		if len(sortedRequest) > 0:
			for entry in sortedRequest:
				canonicalized_query += self.__percent_encode_rfc3986(entry[0])
				canonicalized_query += '='
				canonicalized_query += self.__percent_encode_rfc3986(entry[1])
				canonicalized_query += '&'
			canonicalized_query = canonicalized_query[:-1]
			
		string_to_sign = request_method.lower() + '\n' + self.endpoint_uri.lower() + '\n' + \
			method_name.lower() + '\n' + canonicalized_query
		
		signed_query_string = canonicalized_query
		
		if self.secret_key != None:
			# calculate the signature using HMAC, SHA256 and base64-encoding
			
			# python 2.x
			#signature = hmac.new(self.secret_key, string_to_sign, hashlib.sha256).digest().encode("base64").rstrip('\n')
			
			# python 3.x
			hashed = hmac.new(self.secret_key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256)
			signature = base64.b64encode(hashed.digest()).decode()
	
			#encode the signature for the request
			signature = self.__percent_encode_rfc3986(signature)
		
			signed_query_string += '&signature=' + signature
	
		return signed_query_string
		
		
	def __ksort(self, d):
		return [(k,d[k]) for k in sorted(d.keys())]
	 
	def __get_timestamp(self):
		return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
	
	def __has_calk(self, request):
		for key in request:
			if key.lower() == 'calk':
				return True
		return False
		
	def __percent_encode_rfc3986(self, s):
		#return urllib.quote(s).replace('%7E', '~').replace('/', '%2F') # python 2.x
		return urllib.parse.quote(s).replace('%7E', '~').replace('/', '%2F') # python 3.x
		