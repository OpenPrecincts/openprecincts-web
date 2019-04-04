import sys

state = str(sys.argv[1])
popup = state + "_popup.txt"
svg = "C:/Users/conno/Documents/GitHub/openprecincts-web/static/img/state-maps/" + state + ".svg"

# Create new text file
f_popup = open(popup, "w")
f_error = open(state + '_errors.txt', "w")

# Open old file
f = open(svg, "r")
data = f.readlines()

for line in data:
	# Check that it is a path
	l = line.strip()
	if l[1:5] == "path":

		# Find the locality name

		# Get path id
		path_id = l.split('"')[1]

		# Remove state and change underscore to space
		name = path_id.split('__')[0].replace('_', ' ')


		# Write text
		t1 = '  <text x="10" y="50" font-size="50" fill="black" visibility="hidden">'
		t1 = t1 + name
		t2 = '    <set attributeName="visibility" from="visible" to="hidden" begin="county_group.mouseover"/>'
		t3 = '    <set attributeName="visibility" from="hidden" to="visible" begin="'
		t3 = t3 + path_id + '.mouseover" end="' + path_id + '.mouseout"/>'
		t4 = '  </text>'

		f_popup.write(t1 + '\n')
		f_popup.write(t2 + '\n')
		f_popup.write(t3 + '\n')
		f_popup.write(t4 + '\n')

		# if there is a hyphen or period in a path save the name to error text
		if '.' in path_id or '-' in path_id:
			f_error.write(path_id + '\n')
