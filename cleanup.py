def main():

	file = open("distinct_bldgnames_order.txt", "r")

	for line in file:
		building = line.split("<option>")[1].split("</option>")[0]
		newval = 'value = "' + building + '"'
		print "<option " + newval + "> " + building + "</option>"
	file.close()



main()