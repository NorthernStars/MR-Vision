#!/bin/bash

# check for dev-tools
dev_tool=pyqt4-dev-tools
gui_path=mainGUI.ui
gui_out=visionGui.py

PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $dev_tool | grep "install ok installed")

echo "Checking for: $dev_tool"
if [ "" == "$PKG_OK" ]; then
	echo "No $dev_tool. Setting up $dev_tool."
	sudo apt-get --force-yes --yes install $dev_tool
else
	echo "$dev_tool found"
fi

echo "Compiling gui-file $gui_path to $gui_out."
pyuic4 -o $gui_out $gui_path
echo "finished"