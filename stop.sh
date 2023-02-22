kill -9 $(ps aux | grep 'vcts_data' | awk '{print $2}')
echo "vcts_data stop..."
