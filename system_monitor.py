import psutil
from datetime import datetime
import time

# Create a function to log system monitoring data
def log_system_stats(cpu_usage, memory_info, disk_info, net_speed_up, net_speed_down, active_interfaces, top_processes):   
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Create a timestamp

    # Log entries of system monitoring data
    log_entry = (
        f"{timestamp} - "
        f"CPU Usage: {cpu_usage}% | "
        f"Total Memory: {memory_info.total / (1024**3):.2f} GB |"
        f"Available Memory: {memory_info.available / (1024**3):.2f} GB |"
        f"Memory in use: {memory_info.percent} % |"
        f"Total Disk Space: {disk_info.total / (1024**3):.2f} GB |"
        f"Disk Space Used: {disk_info.used / (1024**3):.2f} GB |"
        f"Disk Free Space: {disk_info.free / (1024**3):.2f} GB |"
        f"Usage Percentage: {disk_info.percent} %\n"
        f"Upload Speed: {net_speed_up:.2f} MB/s | "
        f"Download Speed: {net_speed_down:.2f} MB/s | "
        f"Active Interfaces: {', '.join(active_interfaces)} | "
        f"Top Processes: {', '.join(top_processes)}\n"
    )

    # To append logs to the file every time on running the test
    with open("system_stats.log", "a") as log_file:
        log_file.write(log_entry)

# Function to calculate network speed
def calculate_network_speed(interval=5):
    # Get initial network stats
    net_io_1 = psutil.net_io_counters()
    time.sleep(interval)  # Sleep for the specified interval
    net_io_2 = psutil.net_io_counters()

    # Upload and Download speeds in MB/s
    upload_speed = (net_io_2.bytes_sent - net_io_1.bytes_sent) / (1024**2) / interval
    download_speed = (net_io_2.bytes_recv - net_io_1.bytes_recv) / (1024**2) / interval
    
    # If there's no significant data transfer, return 0
    if upload_speed < 0.01 and download_speed < 0.01:
        return 0.00, 0.00
    
    return upload_speed, download_speed

# Function to get Active Network Interfaces
def get_active_network_interfaces():
    interfaces = psutil.net_if_stats()
    active_interfaces = [iface for iface, stats in interfaces.items() if stats.isup]
    return active_interfaces

# Function to get Top processes by Network Usage
def get_top_network_processes(limit=5):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'io_counters']):
        try:
            net_io = proc.info.get('io_counters')
            if net_io:
                # Fix: check if io_counters exist and access bytes_sent / bytes_recv
                if hasattr(net_io, 'bytes_sent') and hasattr(net_io, 'bytes_recv'):
                    processes.append((proc.info['name'], net_io.bytes_sent + net_io.bytes_recv))
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            continue

    # Sort processes by network usage (descending) and limit results
    top_processes = sorted(processes, key=lambda x: x[1], reverse=True)[:limit]
    
    # If no active processes found, return empty list
    if not top_processes:
        return ["No network activity"]

    return [f"{name} ({usage / (1024**2):.2f} MB)" for name, usage in top_processes]

# To monitor system's realtime stats & printing results to the console
def display_and_log_system_stats():
    # Get CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_usage}%\n")

    # Get memory info
    memory_info = psutil.virtual_memory()
    print(f"Total memory: {memory_info.total / (1024**3):.2f} GB")
    print(f"Available memory: {memory_info.available / (1024**3):.2f} GB")
    print(f"Memory in use: {memory_info.percent} %\n")

    # Get disk info
    disk_info = psutil.disk_usage('/')
    print(f"Total disk space: {disk_info.total / (1024**3):.2f} GB")
    print(f"Space Used: {disk_info.used / (1024**3):.2f} GB")
    print(f"Free space: {disk_info.free / (1024**3):.2f} GB")
    print(f"Usage percentage: {disk_info.percent} %\n")

    # Get network speed
    net_speed_up, net_speed_down = calculate_network_speed(interval=5)  # Increased interval for more meaningful data
    print(f"Upload Speed: {net_speed_up:.2f} MB/s")
    print(f"Download Speed: {net_speed_down:.2f} MB/s")

    # Get active network interfaces
    active_interfaces = get_active_network_interfaces()
    print(f"Active Interfaces: {', '.join(active_interfaces)}")

    # Get top processes by network usage
    top_processes = get_top_network_processes()
    print(f"Top Processes: {', '.join(top_processes)}\n")

    # Log the data
    log_system_stats(cpu_usage, memory_info, disk_info, net_speed_up, net_speed_down, active_interfaces, top_processes)
    print("System monitoring data has been logged successfully!")

# Entry point
if __name__ == "__main__":
    display_and_log_system_stats()

