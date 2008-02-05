#!/usr/bin/env python

# reader.py - vote reader for Super Tuesday

import private
import re
import urllib
import csv
import states
from template import *

from candidates import candidates

parties = {
	'dem': { 'name':'Democrats' },
	'gop': { 'name':'Republicans' }
}

def fetchData():
	#urllib.urlretrieve( private.csvFeedUrl, 'text_output_for_mapping.csv' )
	pass

def readVotes():
	print 'Processing vote data'
	#reader = csv.reader( open( 'test.csv', 'rb' ) )
	reader = csv.reader( open( 'text_output_for_mapping.csv', 'rb' ) )
	header = []
	while header == []:
		header = reader.next()
	#print header
	for row in reader:
		if len(row) < 2: continue
		if row[1] != '*': continue
		setData( header, row )

def setData( header, row ):
	state = states.byAbbr[ row[0] ]
	setVotes( state, header, row )

def getPrecincts( row ):
	return {
		'reporting': int(row[3]),
		'total': int(row[2])
	}

def setVotes( entity, header, row ):
	for col in xrange( 4, len(header) ):
		if col >= len(row) or row[col] == '': continue
		name = header[col]
		if name == 'guiliani': name = 'giuliani'
		candidate = candidates['byname'][name]
		party = candidate['party']
		p = entity['parties'][party]
		if 'precincts' not in p: p['precincts'] = getPrecincts( row )
		if 'votes' not in p: p['votes'] = {}
		p['votes'][name] = int(row[col])

def linkParty( party, match ):
	name = parties[party]['name']
	if party == match:
		return T('''
			<span style="font-weight:bold;">
				%(name)s
			</span>
		''', { 'name': name } )
	else:
		return T('''
			<a href="#" onclick="refresh('%(party)s'); return false;">
				%(name)s
			</a>
		''', { 'name': name, 'party': party } )

def makeMini():
	short = makeMiniVersion( 'short', 'Election&nbsp;Coverage', 'CA NY IL MA' )
	long = makeMiniVersion( 'long', 'Results', 'AL AK AZ AR CA CO CT DE GA ID IL KS MA MN MO MT NJ NM NY ND OK TN UT' )
	
def makeMiniVersion( kind, title, statenames ):
	writeMiniParty( kind, title, statenames, 'dem', 'clinton obama' )
	writeMiniParty( kind, title, statenames,'gop' , 'huckabee mccain paul romney' )

def writeMiniParty( kind, title, statenames, partyname, names ):
	text = makeMiniParty( kind, title, statenames, partyname, names )
	write( 'miniresults-%s-%s.html' %( kind, partyname ), text )

def makeMiniParty( kind, title, statenames, partyname, names ):
	statelist = statenames.split()
	names = names.split()
	style = 'font-weight:normal; background-color:#E0E0E0;'
	head = [ '<th style="text-align:left; %s">State</th>' % style ]
	for name in names:
		head.append( T('''
			<th style="%(style)s">
				%(name)s
			</th>
		''', {
			'name': candidates['byname'][name]['lastName'],
			'style': style
		} ) )
	rows = []
	for stateabbr in statelist:
		state = states.byAbbr[stateabbr]
		cols = []
		winner = { 'name': None, 'votes': 0 }
		total = 0
		party = state['parties'][partyname]
		if 'votes' not in party: continue
		votes = party['votes']
		for name in votes:
			vote = votes[name]
			total += vote
			if vote > winner['votes']:
				winner = { 'name': name, 'votes': vote }
		precincts = party['precincts']
		for name in names:
			win = check = ''
			if name == winner['name']:
				if partyname == 'dem':
					win = 'color:white; background-color:#3366CC;'
				else:
					win = 'color:white; background-color:#AA0031;'
				#if precincts['reporting'] == precincts['total']:
				#	check = 'check'
			if name in votes:
				percent = int( 100 * votes[name] / total )
			else:
				percent = 0
			cols.append( T('''
				<td style="width:%(width)s%%; text-align:center; %(win)s%(check)s">
					<div>
						%(percent)s%%
					</div>
				</td>
			''', {
				'width': 80 / len(names),
				'win': win,
				'check': check,
				'percent': percent
			}) )
		reporting = int( 100 * precincts['reporting'] / precincts['total'] )
		rows.append( T('''
			<tr style="background-color:#F1EFEF;">
				<td style="width:20%%;">
					<div>
						<span>
							%(state)s&nbsp;
						</span>
						<span style="font-size:11px; color:#666666;">
							%(reporting)s%%
						</span>
					</div>
				</td>
				%(cols)s
			</tr>
		''', {
			'state': stateabbr,
			'reporting': reporting,
			'cols': ''.join(cols)
		}) )
	if kind == 'short':
		details = S('''
			<a href="http://news.google.com/?ned=us&topic=el" target="_top" style="color:green;">
				Full election coverage and results &raquo;
			</a>
			&nbsp;&nbsp;&nbsp;&nbsp;
		''')
	else:
		details = ''
	return T('''
		<div style="font-family:arial,sans-serif; font-size:13px;">
			<div style="margin-bottom:4px;">
				<table style="width:100%%;">
					<tbody>
						<tr style="vertical-align: baseline;">
							<td>
								<div style="font-size:16px; font-weight:bold;">
									%(title)s
								</div>
							</td>
							<td style="text-align:right;">
								<div style="font-size:13px;">
									%(dem)s&nbsp;|&nbsp;%(gop)s
								</div>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
			<table style="width:100%%; font-size:13px;">
				<thead>
					%(head)s
				</thead>
				<tbody>
					%(rows)s
				</tbody>
			</table>
			<div>
				%(details)s
				<a href="http://maps.google.com/decision2008" target="_top" style="color:green;">
					View on a map &raquo;
				</a>
			</div>
		</div>
		''', {
			'title': title + ': ',
			'dem': linkParty( 'dem', partyname ),
			'gop': linkParty( 'gop', partyname ),
			'head': ''.join(head),
			'rows': ''.join(rows),
			'details': details
		})

def write( name, text ):
	print 'Writing ' + name
	f = open( name, 'w' )
	f.write( text )
	f.close()
	
def main():
	print 'Retrieving data...'
	fetchData()
	print 'Parsing data...'
	readVotes()
	print 'Creating Mini Gadget HTML...'
	makeMini()
	#print 'Checking in Maps JSON...'
	#os.system( 'svn ci -m "Vote update" fl_text_output_for_mapping.csv data.js results_democrat.js results_republican.js' )
	print 'Done!'

if __name__ == "__main__":
    main()