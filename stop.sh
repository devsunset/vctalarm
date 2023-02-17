kill -9 $(ps aux | grep 'vctalarm' | awk '{print $2}')
echo "vctalarm stop..."
