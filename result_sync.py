# This software is Copyright (c) 2015,
# The Regents of the University of California.
#
# Developed by the UCSD CFAR BIT Core (bitcore@ucsd.edu)
#
# Core Developers:
#   Sergei L Kosakovsky Pond (spond@ucsd.edu)
#   Jason A Young (jay007@ucsd.edu)
#   Marco A Martinez (mam002@ucsd.edu)
#   Steven Weaver (sweaver@ucsd.edu)
#   Zachary Smith (z4smith@ucsd.edu)
#
# Significant contributions from:
#   David Mote (davidmote [at] gmail [dot] com)
#   Jennifer Rodriguez-Mueller (almostlikethat [at] gmail [dot] com)
#   Drew Allen (asallen@ucsd.edu)
#   Andrew Dang (a7dang [at] gmail [dot] com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
This script synchronizes newer database for the bandaid with Results from
the older database from the OCCAMS connection. The purpose for this
is to allow clinicians and testers access to patient results from 
before the bandaid.
"""

import sqlite3
import os, getopt, sys


def main(argv):
	old_db_path = ''
	new_db_path = ''
	try:
		opts, args = getopt.getopt(argv,"hi:o:",["odb=","ndb="])
	except getopt.GetoptError:
		print 'test.py -i <old database> -o <new database>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'test.py -i <old database> -o <new database>'
			sys.exit()
		elif opt in ("-i", "--odb"):
			old_db_path = arg
		elif opt in ("-o", "--ndb"):
			new_db_path = arg

	if not (os.path.exists(old_db_path) and os.path.exists(new_db_path)):
		print "Err. The paths to these files do no exist. Please try again."
		sys.exit(2)

	old_db_path = os.path.abspath(old_db_path)
	new_db_path = os.path.abspath(new_db_path)

	print "Establishing connection with both databases..."
	try:
		old_db = sqlite3.connect(old_db_path)
		old_db.row_factory = sqlite3.Row
		new_db = sqlite3.connect(new_db_path)

	except sqlite3.Error, err:
		print "Err. %s" % err
		print "Exiting..."
		sys.exit(2)

	# Create cursors for the db connections
	old_db_cursor = old_db.cursor()
	new_db_cursor = new_db.cursor()

	# Fetch all result records from old db
	old_db_cursor.execute("SELECT * FROM result")
	old_db_list = old_db_cursor.fetchall()
	print "Fetching all result records from old database..."

	# Iterate each result, store the data in a python vars, create a list of these vars
	result_list = []
	for result in old_db_list:
		site_code = result["site_code"]
		reference_number = result["reference_number"]

		hbs = result["hbs"]
		aby = result["aby"]
		rpr = result["rpr"]
		hiv = result["hiv"]
		hbc = result["hbc"]
		ht1 = result["ht1"]
		hcv = result["hcv"]
		cmv = result["cmv"]
		nat = result["nat"]
		wnv = result["wnv"]
		abo = result["abo"]
		cgs = result["cgs"]
		dhiv = result["dhiv"]
		dhcv = result["dhcv"]
		dhbv = result["dhbv"]

		test_date = result["test_date"]
		draw_date = result["draw_date"]
		location = result["location"]
		file = result["file"]
		version = result["version"]

		temp_list = [site_code, reference_number, hbs, aby, rpr, hiv, hbc, ht1, hcv, cmv, nat, wnv, abo, 
						cgs, dhiv, dhcv, dhbv, test_date, draw_date, location, file, version]
		result_list.append(temp_list)

	# Fetch all draw records from old database
	old_db_cursor.execute("SELECT * FROM draw")
	old_db_list = old_db_cursor.fetchall()

	print "Fetching all draw records from old database"
	
	# Iterate each result, store the data in a python vars, create a list of these vars
	draw_list = []
	for draw in old_db_list:
		site_code = draw["site_code"]
		reference_number = draw["reference_number"]

		draw_date = draw["draw_date"]
		has_result = int(1)

		temp_list = [site_code, reference_number, draw_date, has_result]
		draw_list.append(temp_list)

	# Make INSERT commands to new_db
	print "Executing INSERT into the new database..."
	try:
		new_db_cursor.executemany('''INSERT INTO result(site_code, reference_number, hbs, aby, rpr, hiv, 
									hbc, ht1, hcv, cmv, nat, wnv, abo, cgs, dhiv, dhcv, dhbv, test_date, 
									draw_date, location, file, version) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, 
									?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (result_list))
		new_db_cursor.executemany('''INSERT INTO draw(site_code, reference_number, draw_date, has_result) 
									VALUES(?, ?, ?, ?)''', (draw_list))


		print "Attempting to commit changes to new database..."
		new_db.commit()
	except sqlite3.Error as e:
		new_db.rollback()
		print "An error occurred:", e.args[0]
		print "Rolling back changes..."
	finally:
		print "Closing old and new database connections..."
		old_db.close()
		new_db.close()

	print "Exiting script..."





if __name__ == "__main__":
	main(sys.argv[1:])